import streamlit as st

from database.database import authenticate_user


# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Student Login | Campus Guardian AI",
    page_icon="🎓",
    layout="centered"
)


# ==========================================
# SESSION STATE
# ==========================================

if "student_logged_in" not in st.session_state:
    st.session_state.student_logged_in = False

if "student_user" not in st.session_state:
    st.session_state.student_user = None


# ==========================================
# ALREADY LOGGED IN
# ==========================================

if st.session_state.student_logged_in:

    student = st.session_state.student_user

    st.success("✅ You are already logged in.")

    st.write(f"👤 **Name:** {student[3]}")
    st.write(f"🆔 **Student ID:** {student[2]}")
    st.write(f"📧 **Email:** {student[4] or 'Not provided'}")

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state.student_logged_in = False
        st.session_state.student_user = None

        st.rerun()

    st.stop()


# ==========================================
# LOGIN UI
# ==========================================

st.title("🎓 Student Login")

st.write(
    "Login to access your Campus Guardian AI dashboard."
)

st.divider()


with st.form("student_login_form"):

    student_id = st.text_input(
        "Student ID",
        placeholder="Example: INST-0001-STU-0001"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password"
    )

    login_button = st.form_submit_button(
        "🔐 Login",
        use_container_width=True
    )


# ==========================================
# LOGIN PROCESS
# ==========================================

if login_button:

    if not student_id.strip():

        st.warning("Please enter your Student ID.")

    elif not password:

        st.warning("Please enter your password.")

    else:

        result = authenticate_user(
            student_id.strip(),
            password
        )

        if result["success"]:

            user = result["user"]

            # ----------------------------------
            # CHECK STUDENT ROLE
            # ----------------------------------

            if user[6] != "Student":

                st.error(
                    "❌ This login is only for students."
                )

            else:

                # ------------------------------
                # SAVE STUDENT SESSION
                # ------------------------------

                st.session_state.student_logged_in = True

                st.session_state.student_user = user

                st.success(
                    "✅ Login successful!"
                )

                st.rerun()

        else:

            st.error(
                f"❌ {result['message']}"
            )


# ==========================================
# INFORMATION
# ==========================================

st.divider()

st.info(
    """
    🔐 **Student Login**

    Use the Student ID and password provided
    by your Institute Admin.

    After login, you will be able to access
    your personal dashboard and complaints.
    """
)

st.caption(
    "Campus Guardian AI • Student Portal"
)