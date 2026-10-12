import streamlit as st

from database.database import get_complaint_by_id
from ai_engine.notification_engine import generate_complaint_notification


st.set_page_config(
    page_title="User Dashboard | Campus Guardian AI",
    page_icon="👤",
    layout="wide"
)

st.title("👤 User Dashboard")

st.write(
    "Enter your Complaint ID to view your complaint information."
)

st.divider()

complaint_id = st.text_input(
    "Complaint ID",
    placeholder="Example: CG-2026-0001"
)


if complaint_id:

    complaint = get_complaint_by_id(
        complaint_id.strip()
    )

    if complaint is None:

        st.error(
            "❌ Complaint not found. Please check your Complaint ID."
        )

    else:

        st.success("✅ Complaint found!")

        # ----------------------------------
        # NOTIFICATIONS & ALERTS
        # ----------------------------------

        notifications = generate_complaint_notification(
            complaint
        )

        st.divider()

        st.subheader("🔔 Notifications & Alerts")

        for notification in notifications:

            if notification.startswith("🚨"):
                st.error(notification)

            elif notification.startswith("⚠️"):
                st.warning(notification)

            elif notification.startswith("❌"):
                st.error(notification)

            elif notification.startswith("✅"):
                st.success(notification)

            elif notification.startswith("🛠️"):
                st.info(notification)

            else:
                st.info(notification)

        # ----------------------------------
        # COMPLAINT SUMMARY
        # ----------------------------------

        st.divider()

        st.subheader("📊 Complaint Summary")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Status",
                complaint[9]
            )

        with col2:
            st.metric(
                "Priority",
                complaint[6]
            )

        with col3:
            st.metric(
                "Category",
                complaint[5]
            )

        with col4:
            st.metric(
                "Location",
                complaint[4]
            )

        # ----------------------------------
        # COMPLAINT INFORMATION
        # ----------------------------------

        st.divider()

        st.subheader("📋 Complaint Information")

        st.write(
            f"**Complaint ID:** {complaint[1]}"
        )

        st.write(
            f"**Title:** {complaint[2]}"
        )

        st.write(
            f"**Description:** {complaint[3]}"
        )

        st.write(
            f"**Submitted On:** {complaint[10]}"
        )

        if complaint[7] == 1:
            st.write("**Submission Type:** Anonymous")
        else:
            st.write("**Submission Type:** Identified")

        # ----------------------------------
        # CURRENT STATUS
        # ----------------------------------

        st.divider()

        st.subheader("📌 Current Status")

        status = complaint[9]

        if status == "Pending":

            st.warning(
                "🟡 Your complaint is waiting for review."
            )

        elif status == "In Progress":

            st.info(
                "🟠 Your complaint is currently being processed."
            )

        elif status == "Resolved":

            st.success(
                "🟢 Your complaint has been resolved."
            )

        elif status == "Rejected":

            st.error(
                "❌ Your complaint has been rejected by the administrator."
            )

        else:

            st.info(
                f"Current Status: {status}"
            )

        # ----------------------------------
        # COMPLAINT TRACKING
        # ----------------------------------

        st.divider()

        st.subheader("🔎 Complaint Tracking")

        st.info(
            "You can use the Track Complaint page "
            "to view the detailed progress of your complaint."
        )