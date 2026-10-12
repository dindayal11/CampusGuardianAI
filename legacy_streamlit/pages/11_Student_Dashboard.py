import streamlit as st

from database.database import (
    get_complaints_by_student,
    get_notifications,
    get_unread_notification_count,
    mark_notification_as_read,
    mark_all_notifications_as_read,
    get_notification_preferences,
    update_notification_preferences,
    delete_notification,
    clear_read_notifications
)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Student Dashboard | Campus Guardian AI",
    page_icon="🛡️",
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

    [data-testid="stHeader"] {
        background-color: transparent !important;
    }

    [data-testid="stToolbar"] {
        background: transparent !important;
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

.welcome-box .main-title {
    font-size: 34px !important;
    font-weight: 800 !important;
    color: #ffffff !important;
    margin-bottom: 4px !important;
}

.welcome-box .main-subtitle {
    font-size: 15px !important;
    font-weight: 400 !important;
    color: #94a3b8 !important;
    margin-top: 8px !important;
    margin-bottom: 0 !important;
    line-height: 1.5 !important;
}

    .section-title {
        font-size: 21px;
        font-weight: 750;
        color: #f8fafc;
        margin-top: 28px;
        margin-bottom: 15px;
    }

    .welcome-box {
        background:
            linear-gradient(
                120deg,
                rgba(15, 23, 42, 0.96),
                rgba(30, 27, 75, 0.92),
                rgba(30, 64, 175, 0.80)
            );

        border: 1px solid rgba(59, 130, 246, 0.55);
        border-radius: 22px;

        padding: 30px;

        box-shadow:
            0 0 30px rgba(37, 99, 235, 0.16),
            inset 0 0 30px rgba(99, 102, 241, 0.08);

        margin-bottom: 25px;
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

        box-shadow:
            0 8px 30px rgba(0, 0, 0, 0.25);

        padding: 5px;
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

        box-shadow:
            0 5px 25px rgba(0, 0, 0, 0.25);

        min-height: 110px;
    }

    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
    }

    div[data-testid="stMetricValue"] {
        color: #f8fafc !important;
        font-weight: 800;
    }

    div.stButton > button {
        width: 100%;
        min-height: 48px;

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

        transition: all 0.2s ease;
    }

    div.stButton > button:hover {
        border-color: #38bdf8;

        background:
            linear-gradient(
                135deg,
                #172554,
                #312e81
            );

        box-shadow:
            0 0 18px rgba(59, 130, 246, 0.30);

        transform: translateY(-1px);
    }

    input, textarea {
        background-color: #0f172a !important;
        color: #f8fafc !important;
    }

    .status-pending {
        color: #fbbf24;
        font-weight: 700;
        font-size: 17px;
    }

    .status-progress {
        color: #38bdf8;
        font-weight: 700;
        font-size: 17px;
    }

    .status-resolved {
        color: #34d399;
        font-weight: 700;
        font-size: 17px;
    }

    .status-rejected {
        color: #fb7185;
        font-weight: 700;
        font-size: 17px;
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

if "show_notifications" not in st.session_state:
    st.session_state["show_notifications"] = False

if "notification_refresh" not in st.session_state:
    st.session_state["notification_refresh"] = 0


# =========================================================
# LOGIN CHECK
# =========================================================

if not st.session_state.student_logged_in:
    st.error("🔒 Access Denied")
    st.info("Please login through the Student Login page.")
    st.stop()


# =========================================================
# STUDENT DATA
# =========================================================

student = st.session_state.student_user

student_db_id = student[0]
institute_id = student[1]
student_id = student[2]
student_name = student[3]
student_email = student[4]
student_role = student[6]
student_status = student[7]


# =========================================================
# BLOCKED ACCOUNT CHECK
# =========================================================

if student_status != "Active":

    st.error("🔒 Your account is currently not active.")

    st.warning(
        f"Account Status: {student_status}"
    )

    st.info(
        "Please contact your Institute Admin for assistance."
    )

    if st.button("🚪 Logout", use_container_width=True):

        st.session_state.student_logged_in = False
        st.session_state.student_user = None

        st.rerun()

    st.stop()


# =========================================================
# GET ONLY THIS STUDENT'S COMPLAINTS
# =========================================================

complaints = get_complaints_by_student(
    student_id,
    institute_id
)


# =========================================================
# COMPLAINT COUNTS
# =========================================================

total_complaints = len(complaints)

pending_count = 0
progress_count = 0
resolved_count = 0
rejected_count = 0

for complaint in complaints:

    # Current schema:
    # complaint[11] = Status
    status = complaint[11]

    if status == "Pending":
        pending_count += 1

    elif status == "In Progress":
        progress_count += 1

    elif status == "Resolved":
        resolved_count += 1

    elif status == "Rejected":
        rejected_count += 1


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## 🛡️ Campus Guardian AI")

    st.caption("Student Portal")

    st.divider()

    st.markdown("### 👤 Logged in as")

    st.markdown(f"**{student_name}**")

    st.caption(student_id)

    st.divider()

    st.markdown("### 📊 Quick Stats")

    st.write(f"📋 Total — **{total_complaints}**")
    st.write(f"⏳ Pending — **{pending_count}**")
    st.write(f"🔄 In Progress — **{progress_count}**")
    st.write(f"✅ Resolved — **{resolved_count}**")
    st.write(f"❌ Rejected — **{rejected_count}**")

    st.divider()

    if st.button("🚪 Logout", use_container_width=True):

        st.session_state.student_logged_in = False
        st.session_state.student_user = None

        st.rerun()


# =========================================================
# WELCOME BANNER
# =========================================================

st.markdown(
    f'<div class="welcome-box">'
    f'<div class="main-title">👋 Welcome, {student_name}!</div>'
    f'<div class="main-subtitle">Your campus safety dashboard</div>'
    f'</div>',
    unsafe_allow_html=True
)


# =========================================================
# QUICK ACTIONS
# =========================================================

st.markdown(
    '<div class="section-title">⚡ Quick Actions</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)

with col1:

    if st.button(
        "🚨 Report an Issue",
        use_container_width=True
    ):

        st.switch_page(
            "pages/1_Report_Issue.py"
        )


with col2:

    if st.button(
        "🔍 Track Complaint",
        use_container_width=True
    ):

        st.switch_page(
            "pages/4_Track_Complaint.py"
        )


with col3:

    unread_count = get_unread_notification_count(
        student_id,
        institute_id
    )

    notification_label = (
        f"🔔 Notifications ({unread_count})"
        if unread_count > 0
        else "🔔 Notifications"
    )

    if st.button(
        notification_label,
        use_container_width=True
    ):

        st.session_state["show_notifications"] = True
        st.session_state["notification_refresh"] += 1
        st.rerun()


with col4:

    if st.button(
        "📢 Announcements",
        use_container_width=True
    ):

        st.switch_page(
            "pages/16_Announcements.py"
        )


# =========================================================
# NOTIFICATIONS
# =========================================================

if st.session_state["show_notifications"]:

    st.markdown('<div class="section-title">🔔 Notifications & Alerts</div>', unsafe_allow_html=True)

    unread_count = get_unread_notification_count(student_id, institute_id)
    all_notifications = get_notifications(student_id, institute_id)
    notification_types = sorted({n[4] for n in all_notifications if n[4]})

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("🔔 Unread", unread_count)
    with c2:
        if st.button("✓ Mark All Read", use_container_width=True, disabled=unread_count == 0, key="mark_all_notifications_read"):
            mark_all_notifications_as_read(student_id, institute_id)
            st.rerun()
    with c3:
        if st.button("🗑️ Clear Read", use_container_width=True, disabled=not any(n[7] for n in all_notifications), key="clear_read_notifications"):
            clear_read_notifications(student_id, institute_id)
            st.rerun()

    f1, f2 = st.columns(2)
    with f1:
        read_filter = st.selectbox("Show", ["All", "Unread", "Read"], key="student_notification_read_filter")
    with f2:
        type_filter = st.selectbox("Type", ["All"] + notification_types, key="student_notification_type_filter")

    if read_filter == "Unread":
        visible = get_notifications(student_id, institute_id, unread_only=True, notification_type=type_filter)
    else:
        visible = get_notifications(student_id, institute_id, notification_type=type_filter)
        if read_filter == "Read":
            visible = [n for n in visible if n[7]]

    st.caption(f"Showing **{len(visible)}** notification(s).")

    if not visible:
        with st.container(border=True):
            st.info("🔔 No notifications match the selected filter.")
    else:
        for notification in visible[:50]:
            notification_id, _, _, complaint_id, notification_type, title, message, is_read, created_at = notification
            with st.container(border=True):
                st.markdown(f"### {'🔵' if not is_read else '⚪'} {title}")
                st.write(message)
                meta = f"{notification_type} • {created_at}"
                if complaint_id:
                    meta += f" • Complaint: {complaint_id}"
                st.caption(meta)
                a1, a2, a3 = st.columns(3)
                with a1:
                    if complaint_id and st.button("📋 View Complaint", use_container_width=True, key=f"student_view_notification_{notification_id}"):
                        st.session_state["track_complaint_id"] = complaint_id
                        if not is_read:
                            mark_notification_as_read(notification_id, student_id, institute_id)
                        st.session_state["show_notifications"] = False
                        st.switch_page("pages/4_Track_Complaint.py")
                with a2:
                    if not is_read:
                        if st.button("✓ Mark Read", use_container_width=True, key=f"read_notification_{notification_id}"):
                            mark_notification_as_read(notification_id, student_id, institute_id)
                            st.rerun()
                    else:
                        st.caption("✓ Read")
                with a3:
                    if st.button("🗑️ Delete", use_container_width=True, key=f"delete_notification_{notification_id}"):
                        delete_notification(notification_id, student_id, institute_id)
                        st.rerun()

    with st.expander("⚙️ Notification Preferences", expanded=False):
        pref = get_notification_preferences(student_id, institute_id)
        p1 = st.checkbox("🔔 Enable in-app notifications", bool(pref["in_app_enabled"]), key="student_pref_in_app")
        p2 = st.checkbox("📋 Complaint updates", bool(pref["complaint_updates"]), key="student_pref_updates")
        p3 = st.checkbox("🚨 Priority / critical alerts", bool(pref["priority_alerts"]), key="student_pref_priority")
        p4 = st.checkbox("🆕 Administrative alerts", bool(pref["admin_alerts"]), key="student_pref_admin_alerts")
        if st.button("💾 Save Preferences", use_container_width=True, key="student_save_notification_preferences"):
            update_notification_preferences(student_id, institute_id, p1, p2, p3, p4)
            st.success("✅ Notification preferences saved.")
            st.rerun()


# =========================================================
# COMPLAINT OVERVIEW
# =========================================================

st.markdown(
    '<div class="section-title">📊 Complaint Overview</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "📋 Total Complaints",
        total_complaints
    )

with col2:
    st.metric(
        "⏳ Pending",
        pending_count
    )

with col3:
    st.metric(
        "🔄 In Progress",
        progress_count
    )

with col4:
    st.metric(
        "✅ Resolved",
        resolved_count
    )

with col5:
    st.metric(
        "❌ Rejected",
        rejected_count
    )


# =========================================================
# RECENT COMPLAINTS
# =========================================================

st.markdown(
    '<div class="section-title">📝 My Recent Complaints</div>',
    unsafe_allow_html=True
)

if len(complaints) == 0:

    with st.container(border=True):

        st.markdown("### ✨ No complaints yet")

        st.write(
            "You haven't reported any campus issue yet."
        )

        st.info(
            "💡 Use the 'Report an Issue' button to submit your first complaint."
        )

else:

    # Only latest 2 complaints
    recent_complaints = complaints[:2]

    for complaint in recent_complaints:

        # =================================================
        # CORRECT DATABASE INDEXES
        # =================================================

        complaint_id = complaint[1]
        title = complaint[4]
        description = complaint[5]
        location = complaint[6]
        category = complaint[7]
        priority = complaint[8]

        # IMPORTANT
        status = complaint[11]
        created_at = complaint[12]

        with st.container(border=True):

            col1, col2 = st.columns([4, 1])

            # -------------------------------------------------
            # COMPLAINT INFORMATION
            # -------------------------------------------------

            with col1:

                st.markdown(
                    f"### {title}"
                )

                st.caption(
                    f"🆔 Complaint ID: {complaint_id}"
                )

                st.write(
                    f"📍 **Location:** {location or 'Not provided'}"
                )

                st.write(
                    f"🏷️ **Category:** {category or 'General'}"
                )

                st.write(
                    f"⚠️ **Priority:** {priority or 'Normal'}"
                )

                # IMPORTANT:
                # Created At = complaint[12]
                st.caption(
                    f"📅 Submitted: {created_at}"
                )

            # -------------------------------------------------
            # STATUS
            # -------------------------------------------------

            with col2:

                st.write("### Status")

                if status == "Pending":

                    st.markdown(
                        '<div class="status-pending">⏳ Pending</div>',
                        unsafe_allow_html=True
                    )

                elif status == "In Progress":

                    st.markdown(
                        '<div class="status-progress">🔄 In Progress</div>',
                        unsafe_allow_html=True
                    )

                elif status == "Resolved":

                    st.markdown(
                        '<div class="status-resolved">✅ Resolved</div>',
                        unsafe_allow_html=True
                    )

                elif status == "Rejected":

                    st.markdown(
                        '<div class="status-rejected">❌ Rejected</div>',
                        unsafe_allow_html=True
                    )

                else:

                    st.info(
                        status or "Pending"
                    )


            # -------------------------------------------------
            # STATUS DETAILS
            # -------------------------------------------------

            st.divider()

            st.markdown("### 📌 Complaint Status")

            if status == "Pending":

                st.warning(
                    "⏳ Your complaint has been submitted and is waiting for review."
                )

            elif status == "In Progress":

                st.info(
                    "🔄 Your complaint is currently being processed by the concerned department."
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
# PROFILE
# =========================================================

st.markdown(
    '<div class="section-title">👤 My Profile</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:

    with st.container(border=True):

        st.markdown(
            f"### 🎓 {student_name}"
        )

        st.write(
            f"🆔 **Student ID:** {student_id}"
        )

        st.write(
            f"📧 **Email:** {student_email or 'Not provided'}"
        )

        st.write(
            f"👤 **Role:** {student_role}"
        )

        st.success(
            "🟢 Account Status: Active"
        )


with col2:

    with st.container(border=True):

        st.markdown(
            "### 🛡️ Your Safety Matters"
        )

        st.write(
            "Campus Guardian AI gives students a simple "
            "and secure way to report campus problems."
        )

        st.write(
            "Your voice can help make the campus "
            "safer and better for everyone."
        )

        st.info(
            "💡 Report problems early so the right department can take action."
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