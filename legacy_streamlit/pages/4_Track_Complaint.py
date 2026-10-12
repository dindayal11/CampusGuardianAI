import streamlit as st

from database.database import get_complaint_by_id


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Track Complaint | Campus Guardian AI",
    page_icon="🔎",
    layout="wide"
)


# =========================================================
# DARK GRADIENT UI
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background:
            radial-gradient(
                circle at 10% 10%,
                rgba(37, 99, 235, 0.20),
                transparent 30%
            ),
            radial-gradient(
                circle at 90% 20%,
                rgba(124, 58, 237, 0.18),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #020617 0%,
                #071333 45%,
                #0b1028 70%,
                #120b2e 100%
            );

        color: #f8fafc;
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
        box-shadow: none !important;
        border: none !important;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #020617 0%,
                #06133b 55%,
                #0b0924 100%
            );

        border-right: 1px solid rgba(59, 130, 246, 0.35);
    }

    section[data-testid="stSidebar"] * {
        color: #e2e8f0;
    }

    h1, h2, h3, h4 {
        color: #f8fafc !important;
    }

    p {
        color: #cbd5e1;
    }

    div[data-testid="stMetric"] {
        background:
            linear-gradient(
                145deg,
                rgba(15, 23, 42, 0.95),
                rgba(23, 37, 84, 0.80)
            );

        border: 1px solid rgba(59, 130, 246, 0.38);
        border-radius: 17px;
        padding: 18px;
        min-height: 110px;
    }

    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
    }

    div[data-testid="stMetricValue"] {
        color: #f8fafc !important;
        font-weight: 800;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background:
            linear-gradient(
                145deg,
                rgba(15, 23, 42, 0.88),
                rgba(15, 23, 42, 0.72)
            );

        border: 1px solid rgba(59, 130, 246, 0.28);
        border-radius: 18px;
    }

    div.stButton > button {
        width: 100%;
        min-height: 45px;
        border-radius: 13px;

        background:
            linear-gradient(
                135deg,
                #111827,
                #172554
            );

        color: #f8fafc;
        border: 1px solid rgba(59, 130, 246, 0.45);
        font-weight: 650;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SESSION STATE
# =========================================================

if "student_logged_in" not in st.session_state:
    st.session_state.student_logged_in = False

if "student_user" not in st.session_state:
    st.session_state.student_user = None


# =========================================================
# LOGIN CHECK
# =========================================================

if not st.session_state.student_logged_in:

    st.error("🔒 Access Denied")

    st.info(
        "Please login through the Student Login page."
    )

    st.stop()


# =========================================================
# STUDENT DATA
# =========================================================

student = st.session_state.student_user

# users table:
# 0 id
# 1 institute_id
# 2 user_id
# 3 name
# 4 email
# 5 password
# 6 role
# 7 status
# 8 created_at
# 9 last_login

institute_id = student[1]
student_id = student[2]
student_name = student[3]
student_status = student[7]


# =========================================================
# ACCOUNT STATUS CHECK
# =========================================================

if student_status != "Active":

    st.error(
        "🔒 Your account is currently not active."
    )

    st.warning(
        f"Account Status: {student_status}"
    )

    st.info(
        "Please contact your Institute Admin for assistance."
    )

    st.stop()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## 🛡️ Campus Guardian AI")

    st.caption("Student Portal")

    st.divider()

    st.markdown("### 👤 Logged in as")

    st.markdown(
        f"**{student_name}**"
    )

    st.caption(student_id)

    st.divider()

    if st.button(
        "🏠 Dashboard",
        use_container_width=True
    ):

        st.switch_page(
            "pages/11_Student_Dashboard.py"
        )

    if st.button(
        "🚨 Report Issue",
        use_container_width=True
    ):

        st.switch_page(
            "pages/1_Report_Issue.py"
        )

    st.divider()

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state.student_logged_in = False
        st.session_state.student_user = None

        # Clear any previously selected complaint
        st.session_state.pop(
            "track_complaint_id",
            None
        )

        st.rerun()


# =========================================================
# PAGE HEADER
# =========================================================

st.title("🔎 Track Your Complaint")

st.write(
    "Enter your Complaint ID to check the current status of your complaint."
)

st.divider()


# =========================================================
# AUTO TRACK FROM STUDENT DASHBOARD
# =========================================================

dashboard_complaint_id = st.session_state.get(
    "track_complaint_id"
)

if dashboard_complaint_id:

    complaint_id = dashboard_complaint_id

    st.info(
        f"🔎 Tracking complaint: **{complaint_id}**"
    )

else:

    complaint_id = st.text_input(
        "Complaint ID",
        placeholder="Example: CG-2026-0001"
    )


# =========================================================
# TRACK BUTTON
# =========================================================

track_button = st.button(
    "🔎 Track Complaint",
    use_container_width=True
)


# =========================================================
# TRACK COMPLAINT
# =========================================================

should_track = (
    track_button
    or dashboard_complaint_id is not None
)


if should_track:

    if not complaint_id or not complaint_id.strip():

        st.error(
            "Please enter your Complaint ID."
        )

    else:

        complaint = get_complaint_by_id(
            complaint_id.strip(),
            institute_id
        )

        # =================================================
        # SECURITY CHECK
        # =================================================

        if complaint is None:

            st.error(
                "❌ Complaint not found or you do not have permission to view it."
            )

        # Current complaint tuple:
        # 0  id
        # 1  complaint_id
        # 2  institute_id
        # 3  student_id
        # 4  title
        # 5  description
        # 6  location
        # 7  category
        # 8  priority
        # 9  anonymous
        # 10 image_path
        # 11 status
        # 12 created_at

        elif complaint[3] != student_id:

            st.error(
                "🔒 You can only track complaints submitted by your account."
            )

        else:

            st.success(
                "✅ Complaint found successfully!"
            )

            st.divider()


            # =============================================
            # COMPLAINT HEADER
            # =============================================

            st.subheader(
                f"📋 Complaint: {complaint[1]}"
            )


            # =============================================
            # SUMMARY
            # =============================================

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Status",
                    complaint[11] or "Pending"
                )

            with col2:

                st.metric(
                    "Priority",
                    complaint[8] or "Normal"
                )

            with col3:

                st.metric(
                    "Category",
                    complaint[7] or "General"
                )


            st.divider()


            # =============================================
            # COMPLAINT DETAILS
            # =============================================

            st.subheader(
                "📄 Complaint Details"
            )

            col1, col2 = st.columns(2)

            with col1:

                st.write(
                    f"**Title:** {complaint[4]}"
                )

                st.write(
                    f"**Location:** {complaint[6]}"
                )

                st.write(
                    f"**Category:** {complaint[7] or 'General'}"
                )

            with col2:

                st.write(
                    f"**Priority:** {complaint[8] or 'Normal'}"
                )

                st.write(
                    f"**Submitted On:** {complaint[12]}"
                )

                if complaint[9] == 1:

                    st.write(
                        "**Submission:** Anonymous"
                    )

                else:

                    st.write(
                        "**Submission:** Identified"
                    )


            st.write("### Description")

            st.info(
                complaint[5]
            )


            st.divider()


            # =============================================
            # STATUS TIMELINE
            # =============================================

            st.subheader(
                "📌 Complaint Progress"
            )

            status = complaint[11] or "Pending"


            if status == "Pending":

                st.warning(
                    "🟡 Pending — Your complaint has been submitted and is waiting for review."
                )

                st.success(
                    f"📅 Submitted On: {complaint[12]}"
                )


            elif status == "In Progress":

                st.success(
                    "🟢 Submitted"
                )

                st.caption(
                    f"📅 Submitted On: {complaint[12]}"
                )

                st.info(
                    "🟠 In Progress — Your complaint is currently being processed."
                )


            elif status == "Resolved":

                st.success(
                    "🟢 Submitted"
                )

                st.caption(
                    f"📅 Submitted On: {complaint[12]}"
                )

                st.success(
                    "🟠 In Progress — Complaint was processed."
                )

                st.success(
                    "✅ Resolved — Your complaint has been resolved successfully."
                )


            elif status == "Rejected":

                st.success(
                    "🟢 Submitted"
                )

                st.caption(
                    f"📅 Submitted On: {complaint[12]}"
                )

                st.error(
                    "❌ Rejected — This complaint has been rejected by the administrator."
                )


            else:

                st.info(
                    f"📌 Current Status: {status}"
                )

                st.caption(
                    f"📅 Submitted On: {complaint[12]}"
                )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🛡️ Campus Guardian AI • Student Safety Platform"
)

st.caption(
    "Your Campus. Your Voice. Your Safety."
)