import streamlit as st

from database.database import (
    add_student,
    get_students_by_institute,
    update_student_status
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Student Management | Campus Guardian AI",
    page_icon="👥",
    layout="wide"
)


# ============================================================
# SESSION STATE CHECK
# ============================================================

if "institute_admin_logged_in" not in st.session_state:
    st.session_state.institute_admin_logged_in = False

if "institute_admin" not in st.session_state:
    st.session_state.institute_admin = None


# ============================================================
# SECURITY CHECK
# ============================================================

if not st.session_state.institute_admin_logged_in:

    st.error(
        "🔒 Access Denied. Please login as Institute Admin."
    )

    st.stop()


# ============================================================
# ADMIN DATA
# ============================================================

admin = st.session_state.institute_admin

admin_id = admin[2]
admin_name = admin[3]
institute_id = admin[1]


# ============================================================
# PAGE HEADER
# ============================================================

st.title("👥 Student Management")

st.write(
    "Create and manage student accounts belonging to your institute."
)

st.divider()


# ============================================================
# ADD STUDENT
# ============================================================

st.subheader("➕ Add New Student")

with st.form("add_student_form"):

    col1, col2 = st.columns(2)

    with col1:

        student_name = st.text_input(
            "Student Name *",
            placeholder="Enter student's full name"
        )

        student_email = st.text_input(
            "Student Email",
            placeholder="student@example.com"
        )

    with col2:

        student_password = st.text_input(
            "Password *",
            type="password",
            placeholder="Create login password"
        )

        confirm_password = st.text_input(
            "Confirm Password *",
            type="password",
            placeholder="Re-enter password"
        )

    st.caption(
        "Student ID will be generated automatically by the system."
    )

    submit_student = st.form_submit_button(
        "➕ Create Student Account",
        use_container_width=True
    )


# ============================================================
# CREATE STUDENT
# ============================================================

if submit_student:

    if not student_name.strip():

        st.warning(
            "Please enter student name."
        )

    elif not student_password:

        st.warning(
            "Please create a password."
        )

    elif len(student_password) < 8:

        st.warning(
            "Password must contain at least 8 characters."
        )

    elif student_password != confirm_password:

        st.error(
            "Passwords do not match."
        )

    else:

        result = add_student(
            institute_id=institute_id,
            name=student_name,
            email=student_email,
            password=student_password
        )

        if result["success"]:

            st.success(
                "✅ Student account created successfully!"
            )

            st.info(
                f"🆔 **Student ID:** {result['student_id']}"
            )

            st.warning(
                "Save this Student ID. The student will use it to login."
            )

            st.rerun()

        else:

            st.error(
                result["message"]
            )


st.divider()


# ============================================================
# STUDENT STATISTICS
# ============================================================

students = get_students_by_institute(
    institute_id
)

total_students = len(students)

active_students = sum(
    1 for student in students
    if student[6] == "Active"
)

blocked_students = sum(
    1 for student in students
    if student[6] == "Blocked"
)


st.subheader("📊 Student Overview")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Total Students",
        total_students
    )

with col2:

    st.metric(
        "Active Students",
        active_students
    )

with col3:

    st.metric(
        "Blocked Students",
        blocked_students
    )


st.divider()


# ============================================================
# STUDENT LIST
# ============================================================

st.subheader("👥 All Students")

if not students:

    st.info(
        "No students have been added to this institute yet."
    )

else:

    for student in students:

        # get_students_by_institute indexes:
        #
        # 0 = id
        # 1 = institute_id
        # 2 = user_id
        # 3 = name
        # 4 = email
        # 5 = role
        # 6 = status
        # 7 = created_at
        # 8 = last_login

        student_db_id = student[0]
        student_institute_id = student[1]
        student_id = student[2]
        student_name = student[3]
        student_email = student[4]
        student_role = student[5]
        student_status = student[6]
        created_at = student[7]
        last_login = student[8]

        with st.container(border=True):

            col1, col2, col3 = st.columns([3, 3, 1.5])

            # ------------------------------------------------
            # STUDENT INFORMATION
            # ------------------------------------------------

            with col1:

                st.write(
                    f"### 👤 {student_name}"
                )

                st.write(
                    f"🆔 **Student ID:** {student_id}"
                )

                if student_email:

                    st.write(
                        f"📧 {student_email}"
                    )

            # ------------------------------------------------
            # ACCOUNT INFORMATION
            # ------------------------------------------------

            with col2:

                st.write(
                    f"**Role:** {student_role}"
                )

                st.write(
                    f"**Created:** {created_at}"
                )

                if last_login:

                    st.write(
                        f"**Last Login:** {last_login}"
                    )

                else:

                    st.write(
                        "**Last Login:** Never"
                    )

            # ------------------------------------------------
            # STATUS
            # ------------------------------------------------

            with col3:

                if student_status == "Active":

                    st.success(
                        "🟢 Active"
                    )

                elif student_status == "Blocked":

                    st.error(
                        "🔴 Blocked"
                    )

                else:

                    st.warning(
                        student_status
                    )

                # --------------------------------------------
                # ACCOUNT ACTION
                # --------------------------------------------

                if student_status == "Active":

                    if st.button(
                        "🚫 Block",
                        key=f"block_{student_db_id}",
                        use_container_width=True
                    ):

                        success = update_student_status(
                            student_id,
                            "Blocked",
                            institute_id
                        )

                        if success:

                            st.success(
                                "Student blocked."
                            )

                            st.rerun()

                        else:

                            st.error(
                                "Unable to update student."
                            )

                elif student_status == "Blocked":

                    if st.button(
                        "✅ Activate",
                        key=f"activate_{student_db_id}",
                        use_container_width=True
                    ):

                        success = update_student_status(
                            student_id,
                            "Active",
                            institute_id
                        )

                        if success:

                            st.success(
                                "Student activated."
                            )

                            st.rerun()

                        else:

                            st.error(
                                "Unable to update student."
                            )


# ============================================================
# SECURITY INFORMATION
# ============================================================

st.divider()

st.subheader("🔐 Data Security")

st.success(
    "You can only manage students belonging to your own institute."
)

st.caption(
    f"Institute ID: {institute_id}"
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Campus Guardian AI • Student Management System"
)