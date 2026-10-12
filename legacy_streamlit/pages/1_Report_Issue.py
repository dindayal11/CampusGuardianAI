import streamlit as st
import os

from database.database import (
    add_complaint,
    get_complaints_for_duplicate_check,
    create_notification,
    get_institute_admins,
    get_campus_locations
)

from ai_engine.duplicate_detector import find_similar_complaints
from ai_engine.complaint_analyzer import analyze_complaint


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Report Issue | Campus Guardian AI",
    page_icon="🚨",
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

.block-container {
    max-width: 1400px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

header[data-testid="stHeader"] {
    background: transparent !important;
    box-shadow: none !important;
    border: none !important;
}

[data-testid="stToolbar"] {
    background: transparent !important;
}

h1, h2, h3, h4 {
    color: #f8fafc !important;
}

p {
    color: #cbd5e1;
}

.section-title {
    font-size: 22px;
    font-weight: 750;
    color: #f8fafc;
    margin-top: 25px;
    margin-bottom: 15px;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background:
        linear-gradient(
            145deg,
            rgba(15, 23, 42, 0.92),
            rgba(23, 37, 84, 0.72)
        );

    border: 1px solid rgba(59, 130, 246, 0.30);
    border-radius: 18px;

    box-shadow:
        0 8px 30px rgba(0, 0, 0, 0.25);
}

div.stButton > button {
    border-radius: 13px;
    min-height: 48px;

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

div.stButton > button:hover {
    background:
        linear-gradient(
            135deg,
            #172554,
            #312e81
        );

    border-color: #38bdf8;

    box-shadow:
        0 0 18px rgba(59, 130, 246, 0.30);
}

input,
textarea {
    background-color: #0f172a !important;
    color: #f8fafc !important;
}

[data-testid="stFileUploaderDropzone"] {
    background-color: rgba(15, 23, 42, 0.75);
    border: 1px dashed rgba(96, 165, 250, 0.5);
}

div[data-testid="stMetric"] {
    background:
        linear-gradient(
            145deg,
            rgba(15, 23, 42, 0.95),
            rgba(23, 37, 84, 0.80)
        );

    border: 1px solid rgba(59, 130, 246, 0.35);
    border-radius: 17px;

    padding: 18px;

    box-shadow:
        0 5px 25px rgba(0, 0, 0, 0.25);
}

div[data-testid="stMetricLabel"] {
    color: #94a3b8 !important;
}

div[data-testid="stMetricValue"] {
    color: #f8fafc !important;
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

    st.error("🔒 Student Login Required")

    st.info(
        "Please login through the Student Login page before reporting an issue."
    )

    st.stop()


# =========================================================
# STUDENT INFORMATION
# =========================================================

student = st.session_state.student_user

student_id = student[2]
student_name = student[3]
institute_id = student[1]

# =========================================================
# CAMPUS LOCATIONS
# =========================================================

campus_locations = get_campus_locations(
    institute_id
)

# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="section-title">🚨 Report an Issue</div>',
    unsafe_allow_html=True
)

st.write(
    f"Welcome **{student_name}**. Report any safety, infrastructure "
    "or emergency issue on your campus."
)

st.caption(
    f"🆔 Student ID: {student_id}"
)

st.divider()


# =========================================================
# COMPLAINT FORM
# =========================================================

with st.form("complaint_form"):

    st.markdown("### 📝 Issue Details")

    title = st.text_input(
        "Issue Title *",
        placeholder="Example: Broken street light near hostel"
    )

    description = st.text_area(
        "Describe the Issue *",
        placeholder="Explain the problem in detail...",
        height=150
    )

    col1, col2 = st.columns(2)

with col1:

    if campus_locations:

        location_options = [
            location["location_name"]
            for location in campus_locations
        ]

        location = st.selectbox(
            "Location *",
            options=location_options,
            index=None,
            placeholder="Select campus location"
        )

    else:

        location = None

        st.warning(
            "⚠️ No campus locations have been configured "
            "by your Institute Admin yet."
        )

with col2:

    st.info(
        "🤖 AI will automatically analyze the category, "
        "priority and risk level after submission."
    )

    uploaded_file = st.file_uploader(
        "📷 Upload Image (Optional)",
        type=["jpg", "jpeg", "png"]
    )

    anonymous = st.checkbox(
        "Submit this complaint anonymously"
    )

    st.divider()

    submit_button = st.form_submit_button(
        "🚨 Submit Complaint",
        use_container_width=True
    )


# =========================================================
# SUBMIT COMPLAINT
# =========================================================

if submit_button:

    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not title.strip():

        st.error("❌ Please enter an issue title.")

    elif not description.strip():

        st.error("❌ Please describe the issue.")

    elif not location:

        st.error("❌ Please select the issue location.")

    else:

        # =================================================
        # IMAGE UPLOAD
        # =================================================

        image_path = None

        if uploaded_file:

            if not os.path.exists("uploads"):
                os.makedirs("uploads")

            safe_filename = uploaded_file.name.replace(
                " ",
                "_"
            )

            image_path = os.path.join(
                "uploads",
                safe_filename
            )

            with open(image_path, "wb") as file:

                file.write(
                    uploaded_file.getbuffer()
                )


        # =================================================
        # ANONYMOUS VALUE
        # =================================================

        anonymous_value = 1 if anonymous else 0


        # =================================================
        # AI ANALYSIS
        # =================================================

        with st.spinner("🤖 AI is analyzing your complaint..."):

            ai_result = analyze_complaint(
                title,
                description
            )


        category = ai_result["category"]
        priority = ai_result["priority"]


        # =================================================
        # DUPLICATE DETECTION
        # =================================================

        with st.spinner("🔍 Checking for similar complaints..."):

            existing_complaints = get_complaints_for_duplicate_check(
                institute_id
            )

            duplicate_result = find_similar_complaints(
                title,
                description,
                existing_complaints
            )


        # =================================================
        # SMART PRIORITY UPGRADE
        # =================================================

        if duplicate_result["similar_count"] >= 5:

            if priority == "Low":

                priority = "Medium"

            elif priority == "Medium":

                priority = "High"

            elif priority == "High":

                priority = "Critical"


        # =================================================
        # SAVE COMPLAINT
        # =================================================

        complaint_id = add_complaint(
            title=title,
            description=description,
            location=location,
            category=category,
            priority=priority,
            anonymous=anonymous_value,
            image_path=image_path,
            institute_id=institute_id,
            student_id=student_id,
            department=ai_result["department"]
        )
        
        
        
        # =================================================
        # CREATE STUDENT SUBMISSION NOTIFICATION
        # =================================================

        create_notification(
            institute_id=institute_id,
            user_id=student_id,
            complaint_id=complaint_id,
            notification_type="Complaint Submitted",
            title="📝 Complaint Submitted",
            message=(
                f"Your complaint {complaint_id} has been submitted successfully "
                "and is waiting for review."
            )
        )


        # =================================================
        # CREATE ADMIN COMPLAINT NOTIFICATIONS
        # =================================================

        institute_admins = get_institute_admins(
            institute_id
        )

        for admin_user in institute_admins:

            admin_user_id = admin_user[2]

            # ---------------------------------------------
            # NEW COMPLAINT ALERT
            # ---------------------------------------------

            create_notification(
                institute_id=institute_id,
                user_id=admin_user_id,
                complaint_id=complaint_id,
                notification_type="New Complaint",
                title="🆕 New Complaint Received",
                message=(
                    f"New complaint {complaint_id} has been submitted "
                    f"at {location}. Priority: {priority}."
                )
            )

            # ---------------------------------------------
            # PRIORITY ALERT
            # ---------------------------------------------

            if priority == "Critical":

                create_notification(
                    institute_id=institute_id,
                    user_id=admin_user_id,
                    complaint_id=complaint_id,
                    notification_type="Critical Alert",
                    title="🚨 Critical Complaint Alert",
                    message=(
                        f"Critical complaint {complaint_id} requires "
                        "immediate administrative attention."
                    )
                )

            elif priority == "High":

                create_notification(
                    institute_id=institute_id,
                    user_id=admin_user_id,
                    complaint_id=complaint_id,
                    notification_type="Priority Alert",
                    title="⚠️ High Priority Complaint",
                    message=(
                        f"High priority complaint {complaint_id} "
                        "should be reviewed as soon as possible."
                    )
                )

            if duplicate_result["similar_count"] > 0:
                create_notification(
                    institute_id=institute_id,
                    user_id=admin_user_id,
                    complaint_id=complaint_id,
                    notification_type="Duplicate Alert",
                    title="🔍 Similar Complaint Detected",
                    message=(
                        f"Complaint {complaint_id} has "
                        f"{duplicate_result['similar_count']} similar complaint(s). "
                        "Please review the complaint details."
                    )
                )


        # =================================================
        # SUCCESS
        # =================================================

        st.success(
            "✅ Complaint submitted successfully!"
        )

        st.info(
            f"🆔 Your Complaint ID: **{complaint_id}**"
        )


        # =================================================
        # DUPLICATE ANALYSIS
        # =================================================

        st.markdown(
            '<div class="section-title">🔄 Duplicate Complaint Detection</div>',
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Similar Complaints Found",
                duplicate_result["similar_count"]
            )

        with col2:

            st.metric(
                "Issue Impact Level",
                duplicate_result["impact_level"]
            )


        if duplicate_result["is_duplicate"]:

            st.warning(
                f"""
⚠️ Possible Duplicate Complaint Detected!

Similarity Score:
{duplicate_result["similarity_score"]}%

This issue appears similar to an existing complaint.
"""
            )

        else:

            st.success(
                f"""
✅ No duplicate complaint detected.

Highest Similarity:
{duplicate_result["similarity_score"]}%
"""
            )


        # =================================================
        # SIMILAR COMPLAINTS
        # =================================================

        if duplicate_result["similar_complaints"]:

            st.markdown("### 🔎 Similar Existing Complaints")

            for complaint in duplicate_result["similar_complaints"]:

                with st.container(border=True):

                    st.write(
                        f"🆔 **Complaint ID:** "
                        f"{complaint['complaint_id']}"
                    )

                    st.write(
                        f"📝 **Title:** "
                        f"{complaint['title']}"
                    )

                    st.write(
                        f"📊 **Similarity:** "
                        f"{complaint['similarity']}%"
                    )


        # =================================================
        # AI ANALYSIS RESULT
        # =================================================

        st.markdown(
            '<div class="section-title">🤖 AI Complaint Analysis</div>',
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Detected Category",
                ai_result["category"]
            )

        with col2:

            st.metric(
                "Priority Level",
                priority
            )

        with col3:

            st.metric(
                "Risk Score",
                f'{ai_result["risk_score"]}/100'
            )


        st.info(
            f"🏢 **Assigned Department:** "
            f"{ai_result['department']}"
        )

        st.warning(
            f"💡 **Recommended Action:** "
            f"{ai_result['recommended_action']}"
        )

        st.balloons()