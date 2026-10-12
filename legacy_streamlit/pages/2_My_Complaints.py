import streamlit as st
import pandas as pd

from database.database import get_complaints_by_student


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="My Complaints | Campus Guardian AI",
    page_icon="📋",
    layout="wide"
)


# =========================================================
# DARK UI
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

institute_id = student[1]
student_id = student[2]
student_name = student[3]
student_email = student[4]
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
# GET ONLY THIS STUDENT'S COMPLAINTS
# =========================================================

complaints = get_complaints_by_student(
    student_id,
    institute_id
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## 🛡️ Campus Guardian AI")

    st.caption("Student Portal")

    st.divider()

    st.markdown("### 👤 Student")

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

    if st.button(
        "🔍 Track Complaint",
        use_container_width=True
    ):

        st.switch_page(
            "pages/4_Track_Complaint.py"
        )

    st.divider()

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state.student_logged_in = False
        st.session_state.student_user = None

        st.rerun()


# =========================================================
# PAGE HEADER
# =========================================================

st.title("📋 My Complaints")

st.write(
    "View and track all complaints submitted by you."
)

st.divider()


# =========================================================
# COMPLAINT COUNTS
# =========================================================

total = len(complaints)

pending = sum(
    1 for complaint in complaints
    if complaint[11] == "Pending"
)

in_progress = sum(
    1 for complaint in complaints
    if complaint[11] == "In Progress"
)

resolved = sum(
    1 for complaint in complaints
    if complaint[11] == "Resolved"
)

rejected = sum(
    1 for complaint in complaints
    if complaint[11] == "Rejected"
)


col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("📋 Total", total)

with col2:
    st.metric("⏳ Pending", pending)

with col3:
    st.metric("🔄 In Progress", in_progress)

with col4:
    st.metric("✅ Resolved", resolved)

with col5:
    st.metric("❌ Rejected", rejected)


st.divider()


# =========================================================
# NO COMPLAINTS
# =========================================================

if not complaints:

    with st.container(border=True):

        st.info(
            "📭 You have not submitted any complaint yet."
        )

        st.write(
            "Use the Report Issue page to submit your first complaint."
        )

    st.stop()


# =========================================================
# CONVERT TO DATAFRAME
# =========================================================

columns = [
    "Database ID",
    "Complaint ID",
    "Institute ID",
    "Student ID",
    "Title",
    "Description",
    "Location",
    "Category",
    "Priority",
    "Anonymous",
    "Image",
    "Status",
    "Created At"
]

df = pd.DataFrame(
    complaints,
    columns=columns
)


# =========================================================
# COMPLAINT TABLE
# =========================================================

st.subheader("📊 Complaint History")

display_df = df[
    [
        "Complaint ID",
        "Title",
        "Location",
        "Category",
        "Priority",
        "Status",
        "Created At"
    ]
]

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# COMPLAINT DETAILS
# =========================================================

st.divider()

st.subheader("🔎 Complaint Details")

complaint_options = df["Complaint ID"].tolist()

selected_id = st.selectbox(
    "Select Complaint ID",
    complaint_options
)

selected_complaint = df[
    df["Complaint ID"] == selected_id
].iloc[0]


# =========================================================
# DETAILS
# =========================================================

col1, col2 = st.columns(2)

with col1:

    st.write(
        f"**🆔 Complaint ID:** {selected_complaint['Complaint ID']}"
    )

    st.write(
        f"**📝 Title:** {selected_complaint['Title']}"
    )

    st.write(
        f"**📍 Location:** {selected_complaint['Location']}"
    )

    st.write(
        f"**🏷️ Category:** {selected_complaint['Category']}"
    )

with col2:

    st.write(
        f"**⚠️ Priority:** {selected_complaint['Priority']}"
    )

    # IMPORTANT:
    # Status comes from column 11
    st.write(
        f"**📌 Status:** {selected_complaint['Status']}"
    )

    # IMPORTANT:
    # Created At comes from column 12
    st.write(
        f"**📅 Submitted:** {selected_complaint['Created At']}"
    )


# =========================================================
# DESCRIPTION
# =========================================================

st.markdown("### 📝 Description")

st.info(
    selected_complaint["Description"]
)


# =========================================================
# STATUS MESSAGE
# =========================================================

st.markdown("### 📌 Current Status")

status = selected_complaint["Status"]

if status == "Pending":

    st.warning(
        "⏳ Your complaint has been submitted and is waiting for review."
    )

elif status == "In Progress":

    st.info(
        "🔄 Your complaint is currently being processed."
    )

elif status == "Resolved":

    st.success(
        "✅ Your complaint has been resolved successfully."
    )

elif status == "Rejected":

    st.error(
        "❌ Your complaint has been rejected by the administrator."
    )

else:

    st.info(
        f"Current Status: {status or 'Pending'}"
    )


# =========================================================
# TRACK BUTTON
# =========================================================

st.divider()

if st.button(
    "🔍 Track This Complaint",
    use_container_width=True
):

    st.session_state["track_complaint_id"] = (
        selected_complaint["Complaint ID"]
    )

    st.switch_page(
        "pages/4_Track_Complaint.py"
    )


# =========================================================
# SECURITY
# =========================================================

st.divider()

st.success(
    "🔐 For your privacy, this page shows only complaints submitted by your account."
)

st.caption(
    f"Student ID: {student_id} • Institute ID: {institute_id}"
)

st.divider()

st.caption(
    "🛡️ Campus Guardian AI • Student Safety Platform"
)