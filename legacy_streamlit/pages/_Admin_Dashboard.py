import streamlit as st
import pandas as pd
import plotly.express as px

from ai_engine.admin_intelligence import analyze_admin_intelligence
from ai_engine.smart_recommendations import generate_recommendations
from ai_engine.location_risk_analyzer import analyze_location_risk

from database.database import (
    get_all_complaints,
    get_complaint_stats,
    update_complaint_status,
    update_complaint_department,
    get_departments_by_institute,
    get_complaint_by_id,
    get_user_by_id,
    create_notification,
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
    page_title="Admin Dashboard | Campus Guardian AI",
    page_icon="📊",
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

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# ADMIN LOGIN CHECK
# =========================================================

if (
    "institute_admin" not in st.session_state
    or st.session_state.institute_admin is None
):
    st.error("🔒 Access Denied")
    st.info("Please login through the Institute Admin Login page.")
    st.stop()

admin = st.session_state.institute_admin

# Validate the logged-in admin data
if not isinstance(admin, (tuple, list)) or len(admin) < 10:
    st.error("🔒 Access Denied")
    st.info("Please logout and login again.")
    st.stop()

admin_id = admin[2]
admin_name = admin[3]
institute_id = admin[1]


# =========================================================
# ADMIN NOTIFICATION STATE
# =========================================================

if "show_admin_notifications" not in st.session_state:
    st.session_state["show_admin_notifications"] = False

if "notification_focus_complaint_id" not in st.session_state:
    st.session_state["notification_focus_complaint_id"] = None

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## 🛡️ Campus Guardian AI")

    st.caption("Institute Admin Portal")

    st.divider()

    st.markdown("### 👤 Administrator")

    st.markdown(
        f"**{admin_name}**"
    )

    st.caption(
        f"Admin ID: {admin_id}"
    )

    st.caption(
        f"Institute ID: {institute_id}"
    )

    st.divider()

    # ==========================================
    # DASHBOARD
    # ==========================================

    if st.button(
        "📊 Dashboard",
        use_container_width=True,
        key="admin_dashboard_button"
    ):
        st.session_state["show_admin_notifications"] = False
        st.session_state["notification_focus_complaint_id"] = None
        st.rerun()

    # ==========================================
    # ADMIN NOTIFICATIONS
    # ==========================================

    admin_unread_count = get_unread_notification_count(
        admin_id,
        institute_id
    )

    admin_notification_label = (
        f"🔔 Notifications ({admin_unread_count})"
        if admin_unread_count > 0
        else "🔔 Notifications"
    )

    if st.button(
        admin_notification_label,
        use_container_width=True,
        key="admin_notifications_button"
    ):
        st.session_state["show_admin_notifications"] = True
        st.rerun()

    # ==========================================
    # STUDENT MANAGEMENT
    # ==========================================

    if st.button(
        "👨‍🎓 Student Management",
        use_container_width=True,
        key="admin_student_management_button"
    ):
        st.session_state["show_admin_notifications"] = False
        st.session_state["notification_focus_complaint_id"] = None

        st.switch_page(
            "pages/9_Student_Management.py"
        )

    # ==========================================
    # LOGOUT
    # ==========================================

    if st.button(
        "🚪 Logout",
        use_container_width=True,
        key="admin_logout_button"
    ):

        st.session_state.institute_admin = None
        st.session_state["show_admin_notifications"] = False
        st.session_state["notification_focus_complaint_id"] = None

        st.rerun()

# =========================================================
# PAGE HEADER
# =========================================================

st.markdown(
    """
    <div style="
        font-size:34px;
        font-weight:800;
        color:#ffffff;
        margin-bottom:4px;
    ">
        📊 Admin Dashboard
    </div>

    <div style="
        font-size:15px;
        color:#94a3b8;
        margin-bottom:25px;
    ">
        Monitor, analyze and manage your institute's campus complaints.
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# ADMIN NOTIFICATION CENTER
# =========================================================

if st.session_state["show_admin_notifications"]:

    st.markdown("### 🔔 Notifications & Alerts")

    unread_count = get_unread_notification_count(admin_id, institute_id)
    all_notifications = get_notifications(admin_id, institute_id)
    notification_types = sorted({n[4] for n in all_notifications if n[4]})

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("🔔 Unread", unread_count)
    with c2:
        if st.button("✓ Mark All Read", use_container_width=True, disabled=unread_count == 0, key="admin_mark_all_notifications_read"):
            mark_all_notifications_as_read(admin_id, institute_id)
            st.rerun()
    with c3:
        if st.button("🗑️ Clear Read", use_container_width=True, disabled=not any(n[7] for n in all_notifications), key="admin_clear_read_notifications"):
            clear_read_notifications(admin_id, institute_id)
            st.rerun()

    f1, f2 = st.columns(2)
    with f1:
        read_filter = st.selectbox("Show", ["All", "Unread", "Read"], key="admin_notification_read_filter")
    with f2:
        type_filter = st.selectbox("Type", ["All"] + notification_types, key="admin_notification_type_filter")

    if read_filter == "Unread":
        visible = get_notifications(admin_id, institute_id, unread_only=True, notification_type=type_filter)
    else:
        visible = get_notifications(admin_id, institute_id, notification_type=type_filter)
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
                    if complaint_id and st.button("📋 View Complaint", use_container_width=True, key=f"admin_view_notification_{notification_id}"):
                        st.session_state["notification_focus_complaint_id"] = complaint_id
                        if not is_read:
                            mark_notification_as_read(notification_id, admin_id, institute_id)
                        st.session_state["show_admin_notifications"] = False
                        st.rerun()
                with a2:
                    if not is_read:
                        if st.button("✓ Mark Read", use_container_width=True, key=f"admin_read_notification_{notification_id}"):
                            mark_notification_as_read(notification_id, admin_id, institute_id)
                            st.rerun()
                    else:
                        st.caption("✓ Read")
                with a3:
                    if st.button("🗑️ Delete", use_container_width=True, key=f"admin_delete_notification_{notification_id}"):
                        delete_notification(notification_id, admin_id, institute_id)
                        st.rerun()

    with st.expander("⚙️ Notification Preferences", expanded=False):
        pref = get_notification_preferences(admin_id, institute_id)
        p1 = st.checkbox("🔔 Enable in-app notifications", bool(pref["in_app_enabled"]), key="admin_pref_in_app")
        p2 = st.checkbox("📋 Complaint updates", bool(pref["complaint_updates"]), key="admin_pref_updates")
        p3 = st.checkbox("🚨 Priority / critical alerts", bool(pref["priority_alerts"]), key="admin_pref_priority")
        p4 = st.checkbox("🆕 New complaint/admin alerts", bool(pref["admin_alerts"]), key="admin_pref_admin_alerts")
        if st.button("💾 Save Preferences", use_container_width=True, key="admin_save_notification_preferences"):
            update_notification_preferences(admin_id, institute_id, p1, p2, p3, p4)
            st.success("✅ Notification preferences saved.")
            st.rerun()

    st.divider()

# =========================================================
# GET ONLY THIS INSTITUTE'S DATA
# =========================================================

complaints = get_all_complaints(
    institute_id
)

stats = get_complaint_stats(
    institute_id
)


# =========================================================
# IF NO DATA
# =========================================================

if not complaints:

    st.info(
        "📭 No complaints available for your institute yet."
    )

    st.stop()


# =========================================================
# DATAFRAME
# =========================================================
#
# Canonical complaint order:
#
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
# 13 Department
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
    "Created At",
    "Department"
]


df = pd.DataFrame(
    complaints,
    columns=columns
)


# =========================================================
# GLOBAL DASHBOARD TIME PERIOD
# =========================================================
# Every dashboard section below uses this filtered data.
# This means 7 Days = only last 7 days, 30 Days = only last
# 30 days, 90 Days = only last 90 days, All Time = everything.

df["Created Date"] = pd.to_datetime(
    df["Created At"],
    errors="coerce"
)

if df["Created Date"].notna().any():

    latest_dashboard_date = df["Created Date"].max()

    period_col1, period_col2 = st.columns([1, 3])

    with period_col1:

        dashboard_period = st.selectbox(
            "📅 Dashboard Time Period",
            [
                "Last 7 Days",
                "Last 30 Days",
                "Last 90 Days",
                "All Time"
            ],
            key="global_dashboard_period"
        )

    if dashboard_period == "Last 7 Days":

        dashboard_start_date = (
            latest_dashboard_date
            - pd.Timedelta(days=6)
        )

    elif dashboard_period == "Last 30 Days":

        dashboard_start_date = (
            latest_dashboard_date
            - pd.Timedelta(days=29)
        )

    elif dashboard_period == "Last 90 Days":

        dashboard_start_date = (
            latest_dashboard_date
            - pd.Timedelta(days=89)
        )

    else:

        dashboard_start_date = df["Created Date"].min()

    df = df[
        df["Created Date"].between(
            dashboard_start_date,
            latest_dashboard_date
        )
    ].copy()

else:

    dashboard_period = "All Time"

    st.warning(
        "⚠️ Complaint dates could not be parsed. "
        "Showing all available complaints."
    )


# Keep the AI/database-style complaint list synchronized with
# the selected dashboard period.
period_indices = df.index.tolist()

complaints = [
    complaints[index]
    for index in period_indices
]

# Reset DataFrame index after period filtering.
df.reset_index(drop=True, inplace=True)


# =========================================================
# AI ANALYSIS
# =========================================================

admin_data = analyze_admin_intelligence(
    complaints
)

location_risks = analyze_location_risk(
    complaints
)

recommendations = generate_recommendations(
    complaints,
    location_risks
)


# =========================================================
# FILTERED DASHBOARD STATISTICS
# =========================================================

total_complaints = len(df)

pending_complaints = int(
    (df["Status"] == "Pending").sum()
)

critical_complaints = int(
    (df["Priority"] == "Critical").sum()
)

resolved_complaints = int(
    (df["Status"] == "Resolved").sum()
)

# =========================================================
# AI ADMIN INTELLIGENCE
# =========================================================

st.markdown(
    "### 🤖 AI Admin Intelligence"
)

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "📋 Total Complaints",
        total_complaints
    )

with col2:

    st.metric(
        "⏳ Pending",
        pending_complaints
    )

with col3:

    st.metric(
        "🚨 Critical",
        critical_complaints
    )

with col4:

    st.metric(
        "✅ Resolved",
        resolved_complaints
    )


# =========================================================
# AI INSIGHTS
# =========================================================

st.markdown("### 🔍 AI Insights")

col1, col2 = st.columns(2)

with col1:

    st.info(
        f"📌 Most Reported Category: "
        f"**{admin_data['top_category']}**"
    )

with col2:

    st.warning(
        f"📍 Most Reported Location: "
        f"**{admin_data['top_location']}**"
    )


st.divider()


# =========================================================
# CRITICAL ALERTS
# =========================================================

critical_df = df[
    df["Priority"] == "Critical"
]


if not critical_df.empty:

    st.markdown("### 🚨 Critical Alerts")

    for _, complaint in critical_df.iterrows():

        st.error(
            f"""
🚨 CRITICAL ISSUE

**Title:** {complaint['Title']}

**Location:** {complaint['Location']}

**Complaint ID:** {complaint['Complaint ID']}

**Current Status:** {complaint['Status']}
"""
        )


# =========================================================
# UNIFIED PHASE 9 ANALYTICS
# =========================================================

with st.expander("📊 Charts & Graphs — Show / Hide", expanded=True):

    st.caption(
        f"Showing dashboard data for: **{dashboard_period}**"
    )

    # ---------------------------------------------------------
    # Complaint Trend
    # ---------------------------------------------------------

    trend_col1, trend_col2 = st.columns(2)

    with trend_col1:

        if not df.empty and df["Created Date"].notna().any():

            trend_df = df[
                df["Created Date"].notna()
            ].copy()

            trend_df["Date"] = trend_df[
                "Created Date"
            ].dt.date

            daily_trend = (
                trend_df
                .groupby("Date")
                .size()
                .reset_index(name="Complaints")
            )

            trend_chart = px.line(
                daily_trend,
                x="Date",
                y="Complaints",
                markers=True,
                title="Complaint Trend"
            )

            st.plotly_chart(
                trend_chart,
                use_container_width=True
            )

        else:

            st.info("📭 No dated complaints available.")

    with trend_col2:

        if not df.empty:

            status_summary = (
                df["Status"]
                .fillna("Unknown")
                .value_counts()
                .reset_index()
            )

            status_summary.columns = [
                "Status",
                "Complaints"
            ]

            status_chart = px.pie(
                status_summary,
                names="Status",
                values="Complaints",
                title="Complaint Status"
            )

            st.plotly_chart(
                status_chart,
                use_container_width=True
            )


    # ---------------------------------------------------------
    # Category + Priority
    # ---------------------------------------------------------

    category_col, priority_col = st.columns(2)

    with category_col:

        if not df.empty:

            category_summary = (
                df["Category"]
                .fillna("Uncategorized")
                .value_counts()
                .reset_index()
            )

            category_summary.columns = [
                "Category",
                "Complaints"
            ]

            category_chart = px.bar(
                category_summary,
                x="Category",
                y="Complaints",
                title="Complaints by Category"
            )

            st.plotly_chart(
                category_chart,
                use_container_width=True
            )

    with priority_col:

        if not df.empty:

            priority_summary = (
                df["Priority"]
                .fillna("Unknown")
                .value_counts()
                .reset_index()
            )

            priority_summary.columns = [
                "Priority",
                "Complaints"
            ]

            priority_chart = px.bar(
                priority_summary,
                x="Priority",
                y="Complaints",
                title="Complaints by Priority"
            )

            st.plotly_chart(
                priority_chart,
                use_container_width=True
            )


    # ---------------------------------------------------------
    # Location Risk Intelligence
    # ---------------------------------------------------------

    st.markdown("### 📍 Location Risk Intelligence")

    if not df.empty:

        risk_df = df.copy()

        priority_weights = {
            "Critical": 10,
            "High": 6,
            "Medium": 3,
            "Low": 1
        }

        risk_df["Priority Weight"] = (
            risk_df["Priority"]
            .map(priority_weights)
            .fillna(1)
        )

        if risk_df["Created Date"].notna().any():

            risk_df["Recent 7 Days"] = (
                risk_df["Created Date"]
                >= latest_dashboard_date - pd.Timedelta(days=6)
            ).astype(int)

            risk_df["Recent 30 Days"] = (
                risk_df["Created Date"]
                >= latest_dashboard_date - pd.Timedelta(days=29)
            ).astype(int)

        else:

            risk_df["Recent 7 Days"] = 0
            risk_df["Recent 30 Days"] = 0

        risk_df["Risk Contribution"] = (
            risk_df["Priority Weight"]
            + risk_df["Recent 7 Days"] * 3
            + risk_df["Recent 30 Days"]
        )

        location_summary = (
            risk_df
            .groupby("Location")
            .agg(
                Complaints=("Complaint ID", "count"),
                Critical=("Priority", lambda x: (x == "Critical").sum()),
                High=("Priority", lambda x: (x == "High").sum()),
                Active=("Status", lambda x: x.isin(
                    ["Pending", "In Progress"]
                ).sum()),
                Resolved=("Status", lambda x: (x == "Resolved").sum()),
                Risk_Score=("Risk Contribution", "sum")
            )
            .reset_index()
        )

        location_summary["Resolution Rate (%)"] = (
            location_summary["Resolved"]
            / location_summary["Complaints"]
            * 100
        ).round(1)

        def get_risk_level(score):

            if score >= 20:
                return "Critical"

            if score >= 10:
                return "High"

            if score >= 4:
                return "Medium"

            return "Low"

        location_summary["Risk Level"] = (
            location_summary["Risk_Score"]
            .apply(get_risk_level)
        )

        location_summary = location_summary.sort_values(
            ["Risk_Score", "Complaints"],
            ascending=False
        )

        location_chart = px.bar(
            location_summary.head(10),
            x="Location",
            y="Risk_Score",
            color="Risk Level",
            title="Top Risky Locations"
        )

        st.plotly_chart(
            location_chart,
            use_container_width=True
        )

        st.dataframe(
            location_summary[
                [
                    "Location",
                    "Complaints",
                    "Critical",
                    "High",
                    "Active",
                    "Resolved",
                    "Resolution Rate (%)",
                    "Risk_Score",
                    "Risk Level"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("📭 No location data available.")


    # ---------------------------------------------------------
    # Department Performance
    # ---------------------------------------------------------

    st.markdown("### 🏢 Department Performance")

    department_df = df[
        df["Department"].notna()
    ].copy()

    department_df = department_df[
        department_df["Department"]
        .astype(str)
        .str.strip() != ""
    ]

    if not department_df.empty:

        department_summary = (
            department_df
            .groupby("Department")
            .agg(
                Total=("Complaint ID", "count"),
                Pending=("Status", lambda x: (x == "Pending").sum()),
                In_Progress=("Status", lambda x: (
                    x == "In Progress"
                ).sum()),
                Resolved=("Status", lambda x: (
                    x == "Resolved"
                ).sum()),
                Rejected=("Status", lambda x: (
                    x == "Rejected"
                ).sum()),
                Critical=("Priority", lambda x: (
                    x == "Critical"
                ).sum())
            )
            .reset_index()
        )

        department_summary["Open Complaints"] = (
            department_summary["Pending"]
            + department_summary["In_Progress"]
        )

        department_summary["Resolution Rate (%)"] = (
            department_summary["Resolved"]
            / department_summary["Total"]
            * 100
        ).round(1)

        department_chart = px.bar(
            department_summary,
            x="Department",
            y="Open Complaints",
            color="Department",
            title="Open Complaints by Department"
        )

        st.plotly_chart(
            department_chart,
            use_container_width=True
        )

        st.dataframe(
            department_summary[
                [
                    "Department",
                    "Total",
                    "Pending",
                    "In_Progress",
                    "Resolved",
                    "Rejected",
                    "Critical",
                    "Open Complaints",
                    "Resolution Rate (%)"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "📭 No department-assigned complaints for this period."
        )


    # ---------------------------------------------------------
    # Operational Insights
    # ---------------------------------------------------------

    st.markdown("### 💡 Operational Insights")

    if not df.empty:

        insight_messages = []

        top_location = (
            df["Location"]
            .fillna("Unknown")
            .value_counts()
            .idxmax()
        )

        top_location_count = int(
            df["Location"]
            .fillna("Unknown")
            .value_counts()
            .max()
        )

        top_category = (
            df["Category"]
            .fillna("Uncategorized")
            .value_counts()
            .idxmax()
        )

        top_category_count = int(
            df["Category"]
            .fillna("Uncategorized")
            .value_counts()
            .max()
        )

        active_count = int(
            df["Status"]
            .isin(["Pending", "In Progress"])
            .sum()
        )

        resolved_count = int(
            (df["Status"] == "Resolved").sum()
        )

        total_count = len(df)

        resolution_rate = (
            round(
                resolved_count / total_count * 100,
                1
            )
            if total_count > 0
            else 0
        )

        critical_count = int(
            (df["Priority"] == "Critical").sum()
        )

        if critical_count > 0:

            insight_messages.append(
                f"🚨 **{critical_count} critical complaint(s)** "
                "require priority attention."
            )

        if active_count > 0:

            insight_messages.append(
                f"⏳ **{active_count} active complaint(s)** "
                "are pending or in progress."
            )

        insight_messages.append(
            f"📍 **{top_location}** has the highest complaint volume "
            f"with **{top_location_count} complaint(s)**."
        )

        insight_messages.append(
            f"🧩 **{top_category}** is the most reported category "
            f"with **{top_category_count} complaint(s)**."
        )

        if resolution_rate < 50:

            insight_messages.append(
                "⚠️ Resolution rate is below 50%. "
                "Administrative follow-up may be required."
            )

        elif resolution_rate >= 80:

            insight_messages.append(
                "✅ Resolution rate is above 80%, indicating strong "
                "complaint handling performance."
            )

        for insight in insight_messages:

            st.info(insight)

    else:

        st.info("📭 No complaints available for this period.")


st.divider()


# =========================================================
# COMPLAINT MANAGEMENT
# =========================================================
st.markdown("### 🔍 Complaint Management")

st.caption(
    f"Complaint Management is filtered to: **{dashboard_period}**"
)


col1, col2, col3 ,col4 = st.columns(4)


with col1:

    categories = sorted(
        df["Category"].dropna().unique().tolist()
    )

    selected_category = st.selectbox(
        "Filter by Category",
        ["All"] + categories
    )


with col2:

    priorities = sorted(
        df["Priority"].dropna().unique().tolist()
    )

    selected_priority = st.selectbox(
        "Filter by Priority",
        ["All"] + priorities
    )


with col3:

    statuses = sorted(
        df["Status"].dropna().unique().tolist()
    )

    selected_status = st.selectbox(
        "Filter by Status",
        ["All"] + statuses
    )
    
with col4:

    departments = get_departments_by_institute(institute_id)

    active_departments = [
        department
        for department in departments
        if department[4] == "Active"
    ]

    department_names = [
        department[2]
        for department in active_departments
    ]

    selected_department = st.selectbox(
        "Filter by Department",
        ["All"] + department_names
    )    


filtered_df = df.copy()


if selected_category != "All":

    filtered_df = filtered_df[
        filtered_df["Category"] == selected_category
    ]


if selected_priority != "All":

    filtered_df = filtered_df[
        filtered_df["Priority"] == selected_priority
    ]


if selected_status != "All":

    filtered_df = filtered_df[
        filtered_df["Status"] == selected_status
    ]

if selected_department != "All":

    filtered_df = filtered_df[
        filtered_df["Department"] == selected_department
    ]



# =========================================================
# COMPLAINT TABLE
# =========================================================

display_columns = [
    "Complaint ID",
    "Title",
    "Location",
    "Category",
    "Priority",
    "Department",
    "Status",
    "Created At"
]

table_event = st.dataframe(
    filtered_df[display_columns],
    use_container_width=True,
    hide_index=True,
    on_select="rerun",
    selection_mode="single-row",
    key="complaint_management_table"
)

selected_rows = table_event.selection.rows

if selected_rows:
    selected_row_index = selected_rows[0]

    selected_complaint_id = filtered_df.iloc[
        selected_row_index
    ]["Complaint ID"]

    selected_complaint = get_complaint_by_id(
        selected_complaint_id,
        institute_id
    )



# =========================================================
# SELECTED COMPLAINT DETAILS
# =========================================================

selected_rows = table_event.selection.rows

selected_complaint_id = None

if selected_rows:

    selected_row_index = selected_rows[0]

    selected_complaint_id = filtered_df.iloc[
        selected_row_index
    ]["Complaint ID"]

elif st.session_state.get("notification_focus_complaint_id"):

    selected_complaint_id = st.session_state[
        "notification_focus_complaint_id"
    ]


if selected_complaint_id:

    selected_complaint = get_complaint_by_id(
        selected_complaint_id,
        institute_id
    )

    if selected_complaint:

        st.divider()

        st.markdown(
            "### 📋 Complaint Details"
        )

        if st.session_state.get("notification_focus_complaint_id"):

            st.info(
                f"🔔 Opened from notification: **{selected_complaint_id}**"
            )

            if st.button(
                "✕ Close Notification Focus",
                key="close_notification_focus"
            ):
                st.session_state["notification_focus_complaint_id"] = None
                st.rerun()

        # -----------------------------------------
        # COMPLAINT DATA
        # -----------------------------------------

        complaint_db_id = selected_complaint[0]
        complaint_id = selected_complaint[1]
        complaint_institute_id = selected_complaint[2]
        student_id = selected_complaint[3]
        title = selected_complaint[4]
        description = selected_complaint[5]
        location = selected_complaint[6]
        category = selected_complaint[7]
        priority = selected_complaint[8]
        anonymous = selected_complaint[9]
        image_path = selected_complaint[10]
        status = selected_complaint[11]
        created_at = selected_complaint[12]


        # -----------------------------------------
        # COMPLAINT HEADER
        # -----------------------------------------

        st.markdown(
            f"#### 🆔 {complaint_id}"
        )

        st.caption(
            f"Submitted on: {created_at}"
        )


        # -----------------------------------------
        # STUDENT INFORMATION
        # -----------------------------------------

        st.markdown(
            "#### 👤 Complaint Submitted By"
        )

        if anonymous:

            st.info(
                "🕵️ This complaint was submitted anonymously."
            )

        else:

            student = None

            if student_id:

                student = get_user_by_id(
                    student_id
                )

            if student:

                student_name = student[3]
                student_email = student[4]

                info_col1, info_col2 = st.columns(2)

                with info_col1:

                    st.write(
                        f"**Name:** {student_name}"
                    )

                    st.write(
                        f"**Student ID:** {student_id}"
                    )

                with info_col2:

                    st.write(
                        f"**Email:** {student_email or 'Not provided'}"
                    )

                    st.write(
                        "**Role:** Student"
                    )

            else:

                st.write(
                    f"**Student ID:** {student_id or 'Not available'}"
                )


        # -----------------------------------------
        # COMPLAINT INFORMATION
        # -----------------------------------------

        st.markdown(
            "#### 📝 Complaint Information"
        )

        detail_col1, detail_col2 = st.columns(2)

        with detail_col1:

            st.write(
                f"**Title:** {title}"
            )

            st.write(
                f"**Location:** {location}"
            )

            st.write(
                f"**Category:** {category}"
            )

            complaint_department = (
                selected_complaint[13]
                if len(selected_complaint) > 13
                else "Not assigned"
            )

            st.write(
                f"**Department:** {complaint_department or 'Not assigned'}"
            )

        with detail_col2:

            st.write(
                f"**Priority:** {priority}"
            )

            st.write(
                f"**Status:** {status}"
            )

            st.write(
                f"**Submitted At:** {created_at}"
            )

            st.write(
                f"**Anonymous:** {'Yes' if anonymous else 'No'}"
            )


        # -----------------------------------------
        # FULL DESCRIPTION
        # -----------------------------------------

        st.markdown(
            "#### 📄 Description"
        )

        st.info(
            description or "No description provided."
        )


        # -----------------------------------------
        # IMAGE
        # -----------------------------------------

        if image_path:

            st.markdown(
                "#### 🖼️ Attached Image"
            )

            try:

                st.image(
                    image_path,
                    caption="Complaint Evidence",
                    width=500
                )

            except Exception:

                st.warning(
                    "⚠️ Attached image could not be displayed."
                )


        # -----------------------------------------
        # CLOSE / SELECTION INFO
        # -----------------------------------------

        st.caption(
            "💡 Click another complaint in the table to view its details."
        )

# =========================================================
# UPDATE COMPLAINT STATUS
# =========================================================

st.markdown("### ⚙️ Update Complaint Status")


complaint_ids = filtered_df[
    "Complaint ID"
].tolist()


if complaint_ids:

    selected_complaint = st.selectbox(
        "Select Complaint",
        complaint_ids
    )

    new_status = st.selectbox(
        "Update Status",
        [
            "Pending",
            "In Progress",
            "Resolved",
            "Rejected"
        ]
    )

if st.button(
    "🔄 Update Complaint Status",
    use_container_width=True
):

    # Get current complaint details
    complaint = get_complaint_by_id(
        selected_complaint,
        institute_id
    )

    if complaint:

        old_status = complaint[11]
        student_id = complaint[3]

        # Only create notification if status actually changes
        if old_status != new_status:

            update_complaint_status(
                selected_complaint,
                new_status,
                institute_id,
                admin_id,
                "Institute Admin"
            )

            # Status notification message
            if new_status == "In Progress":

                notification_title = "🔄 Complaint In Progress"

                notification_message = (
                    f"Your complaint {selected_complaint} "
                    "is now being processed by the concerned department."
                )

            elif new_status == "Resolved":

                notification_title = "✅ Complaint Resolved"

                notification_message = (
                    f"Your complaint {selected_complaint} "
                    "has been resolved successfully."
                )

            elif new_status == "Rejected":

                notification_title = "❌ Complaint Rejected"

                notification_message = (
                    f"Your complaint {selected_complaint} "
                    "has been rejected by the administrator."
                )

            else:

                notification_title = "ℹ️ Complaint Status Updated"

                notification_message = (
                    f"Your complaint {selected_complaint} "
                    f"status has been changed to {new_status}."
                )

            # Create notification for student
            if student_id:

                create_notification(
                    institute_id=institute_id,
                    user_id=student_id,
                    complaint_id=selected_complaint,
                    notification_type="Status Changed",
                    title=notification_title,
                    message=notification_message
                )

            st.success(
                f"✅ Complaint {selected_complaint} "
                f"status changed from {old_status} to {new_status}."
            )

        else:

            st.info(
                f"ℹ️ Complaint {selected_complaint} "
                f"is already {new_status}."
            )

    else:

        st.error(
            "❌ Complaint not found."
        )

    st.rerun()


# =========================================================
# UPDATE COMPLAINT DEPARTMENT
# =========================================================

st.markdown("### 🏢 Assign Complaint Department")

complaint_ids = filtered_df[
    "Complaint ID"
].tolist()

if complaint_ids:

    selected_department_complaint = st.selectbox(
        "Select Complaint for Department Assignment",
        complaint_ids,
        key="department_complaint"
    )

    active_departments = [
        department
        for department in get_departments_by_institute(institute_id)
        if department[4] == "Active"
    ]

    department_names = [
        department[2]
        for department in active_departments
    ]

    if department_names:

        selected_assign_department = st.selectbox(
            "Select Department",
            department_names,
            key="assign_department"
        )

        if st.button(
            "🏢 Assign Department",
            use_container_width=True
        ):

            update_complaint_department(
                selected_department_complaint,
                selected_assign_department,
                institute_id,
                admin_id,
                "Institute Admin"
            )

            st.success(
                f"✅ Complaint {selected_department_complaint} "
                f"assigned to {selected_assign_department}."
            )

            st.rerun()

    else:

        st.warning(
            "⚠️ No active departments available. "
            "Please create or activate a department first."
        )


# =========================================================
# SMART AI RECOMMENDATIONS
# =========================================================

st.divider()

st.markdown(
    "### 🤖 Smart AI Recommendations"
)


if recommendations:

    for recommendation in recommendations:

        if recommendation.startswith("🚨"):

            st.error(recommendation)

        elif recommendation.startswith("🔥"):

            st.warning(recommendation)

        elif recommendation.startswith("⚠️"):

            st.warning(recommendation)

        elif recommendation.startswith("⏳"):

            st.info(recommendation)

        else:

            st.success(recommendation)

else:

    st.success(
        "✅ No immediate action is required."
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🛡️ Campus Guardian AI • Institute Admin Portal"
)

st.caption(
    "Secure • AI-Powered • Institute-Specific"
)