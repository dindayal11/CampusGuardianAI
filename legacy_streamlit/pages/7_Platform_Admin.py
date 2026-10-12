import streamlit as st

from database.database import (
    create_platform_admin,
    authenticate_platform_admin,
    get_pending_institutes,
    approve_institute,
    reject_institute,
    block_institute
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Platform Admin | Campus Guardian AI",
    page_icon="🛡️",
    layout="wide"
)


# ============================================================
# CREATE DEFAULT PLATFORM ADMIN
# ============================================================

create_platform_admin()


# ============================================================
# SESSION STATE
# ============================================================

if "platform_admin_logged_in" not in st.session_state:
    st.session_state.platform_admin_logged_in = False

if "platform_admin" not in st.session_state:
    st.session_state.platform_admin = None


# ============================================================
# LOGIN PAGE
# ============================================================

if not st.session_state.platform_admin_logged_in:

    st.title("🛡️ Campus Guardian AI")
    st.subheader("Platform Administrator Login")

    st.info(
        "Platform Admin manages institute registrations "
        "and platform-level access."
    )

    st.divider()

    email = st.text_input(
        "Admin Email",
        placeholder="Enter platform admin email"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter password"
    )

    if st.button("🔐 Login", use_container_width=True):

        if not email or not password:
            st.warning("Please enter email and password.")

        else:

            admin = authenticate_platform_admin(
                email,
                password
            )

            if admin:

                st.session_state.platform_admin_logged_in = True
                st.session_state.platform_admin = admin

                st.success("Login successful!")
                st.rerun()

            else:
                st.error("Invalid email or password.")

    st.divider()

    st.info(
        "Use the platform administrator credentials configured for your deployment."
    )

    st.stop()


# ============================================================
# ADMIN DASHBOARD
# ============================================================

admin = st.session_state.platform_admin

st.title("🛡️ Platform Admin Dashboard")

st.write(
    f"Welcome, **{admin[2]}**"
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("Platform Admin")

    st.write(f"👤 {admin[2]}")
    st.write(f"📧 {admin[3]}")

    if st.button(
        "🔐 Security & Audit",
        use_container_width=True
    ):

        st.switch_page("pages/19_Security_and_Audit.py")

    if st.button(
        "🩺 System Health",
        use_container_width=True
    ):

        st.switch_page("pages/20_System_Health.py")

    if st.button(
        "🔐 Change Password",
        use_container_width=True
    ):

        st.switch_page(
            "pages/21_Change_Password.py"
        )

    st.divider()

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state.platform_admin_logged_in = False
        st.session_state.platform_admin = None

        st.rerun()


# ============================================================
# PENDING INSTITUTES
# ============================================================

st.header("🏫 Institute Registration Requests")

pending_institutes = get_pending_institutes()


if not pending_institutes:

    st.success(
        "🎉 No pending institute registration requests."
    )

else:

    st.info(
        f"{len(pending_institutes)} institute(s) waiting for approval."
    )

    for institute in pending_institutes:

        institute_id = institute[0]
        institute_code = institute[1]
        name = institute[2]
        institute_type = institute[3]
        email = institute[4]
        phone = institute[5]
        address = institute[6]
        city = institute[7]
        state = institute[8]
        status = institute[9]
        created_at = institute[10]

        with st.container(border=True):

            st.subheader(f"🏫 {name}")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.write(f"**Institute Code:** {institute_code}")
                st.write(f"**Type:** {institute_type}")

            with col2:
                st.write(f"**Email:** {email}")
                st.write(f"**Phone:** {phone}")

            with col3:
                st.write(f"**City:** {city}")
                st.write(f"**State:** {state}")

            st.write(
                f"**Address:** {address}"
            )

            st.write(
                f"**Registration Date:** {created_at}"
            )

            st.divider()

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    "✅ Approve Institute",
                    key=f"approve_{institute_id}",
                    use_container_width=True
                ):

                    approve_institute(institute_id, admin[1], "Platform Admin")

                    st.success(
                        f"{name} has been approved."
                    )

                    st.rerun()

            with col2:

                if st.button(
                    "❌ Reject Institute",
                    key=f"reject_{institute_id}",
                    use_container_width=True
                ):

                    reject_institute(institute_id, admin[1], "Platform Admin")

                    st.warning(
                        f"{name} has been rejected."
                    )

                    st.rerun()


# ============================================================
# INFORMATION
# ============================================================

st.divider()

st.header("ℹ️ Platform Information")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Pending Institutes",
        len(pending_institutes)
    )

with col2:
    st.metric(
        "Platform Status",
        "🟢 Active"
    )

with col3:
    st.metric(
        "System",
        "Multi-Institute"
    )