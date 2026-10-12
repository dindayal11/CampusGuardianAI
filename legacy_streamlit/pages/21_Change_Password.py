import re

import streamlit as st

from database.database import (
    change_user_password,
    change_platform_admin_password,
    get_user_by_id
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Change Password | Campus Guardian AI",
    page_icon="🔐",
    layout="wide"
)


# ============================================================
# UI
# ============================================================

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

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background:
            linear-gradient(
                145deg,
                rgba(15, 23, 42, 0.92),
                rgba(23, 37, 84, 0.72)
            );
        border: 1px solid rgba(59, 130, 246, 0.30);
        border-radius: 18px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.25);
        padding: 8px;
    }

    input {
        background-color: #0f172a !important;
        color: #f8fafc !important;
    }

    div.stButton > button {
        min-height: 48px;
        border-radius: 13px;
        background: linear-gradient(135deg, #111827, #172554);
        color: #f8fafc;
        border: 1px solid rgba(59, 130, 246, 0.45);
        font-weight: 650;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HELPERS
# ============================================================

def password_is_strong(password):

    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."

    if not re.search(r"\d", password):
        return False, "Password must contain at least one number."

    if not re.search(r"[^A-Za-z0-9]", password):
        return False, "Password must contain at least one special character."

    return True, ""


def clear_user_sessions():
    st.session_state.student_logged_in = False
    st.session_state.student_user = None
    st.session_state.institute_admin_logged_in = False
    st.session_state.institute_admin = None
    st.session_state.platform_admin_logged_in = False
    st.session_state.platform_admin = None


# ============================================================
# DETECT LOGGED-IN ACCOUNT
# ============================================================

account_type = None
account = None

if st.session_state.get("student_logged_in") and st.session_state.get("student_user"):
    account_type = "Student"
    account = st.session_state.student_user

elif st.session_state.get("institute_admin_logged_in") and st.session_state.get("institute_admin"):
    account_type = "Institute Admin"
    account = st.session_state.institute_admin

elif st.session_state.get("platform_admin_logged_in") and st.session_state.get("platform_admin"):
    account_type = "Platform Admin"
    account = st.session_state.platform_admin


if account_type is None:
    st.error("🔒 Login Required")
    st.info("Please login before changing your password.")
    st.stop()


# ============================================================
# ACCOUNT DETAILS
# ============================================================

if account_type in ("Student", "Institute Admin"):
    user_id = account[2]
    user_name = account[3]
    user_email = account[4] or "Not provided"
else:
    user_id = account[1]
    user_name = account[2]
    user_email = account[3]


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🛡️ Campus Guardian AI")
    st.caption(f"{account_type} Portal")
    st.divider()

    st.markdown("### 👤 Logged in as")
    st.markdown(f"**{user_name}**")
    st.caption(user_id)

    st.divider()

    if account_type == "Student":
        if st.button("🏠 Dashboard", use_container_width=True):
            st.switch_page("pages/11_Student_Dashboard.py")

    elif account_type == "Institute Admin":
        if st.button("📊 Admin Dashboard", use_container_width=True):
            st.switch_page("pages/8_Institute_Admin.py")

    else:
        if st.button("🛡️ Platform Dashboard", use_container_width=True):
            st.switch_page("pages/7_Platform_Admin.py")

    st.divider()

    if st.button("🚪 Logout", use_container_width=True):
        clear_user_sessions()
        st.rerun()


# ============================================================
# PAGE
# ============================================================

st.title("🔐 Change Password")
st.write("Update your account password securely.")

st.divider()

with st.container(border=True):

    st.markdown("### 👤 Account")
    st.write(f"**Name:** {user_name}")
    st.write(f"**Account:** {user_id}")
    st.write(f"**Email:** {user_email}")
    st.write(f"**Role:** {account_type}")

st.markdown("### 🔑 New Password")

current_password = st.text_input(
    "Current Password",
    type="password",
    placeholder="Enter your current password"
)

new_password = st.text_input(
    "New Password",
    type="password",
    placeholder="Enter a new password"
)

confirm_password = st.text_input(
    "Confirm New Password",
    type="password",
    placeholder="Re-enter your new password"
)

st.caption(
    "Password must be at least 8 characters and include uppercase, lowercase, number and special character."
)

if st.button("🔐 Change Password", use_container_width=True):

    if not current_password or not new_password or not confirm_password:
        st.warning("Please fill all password fields.")
        st.stop()

    if new_password != confirm_password:
        st.error("New password and confirmation password do not match.")
        st.stop()

    strong, message = password_is_strong(new_password)

    if not strong:
        st.error(message)
        st.stop()

    if account_type in ("Student", "Institute Admin"):

        result = change_user_password(
            user_id,
            account[1],
            current_password,
            new_password
        )

    else:

        result = change_platform_admin_password(
            user_email,
            current_password,
            new_password
        )

    if not result["success"]:
        st.error(result["message"])
        st.stop()

    # Refresh the session account so the new DB state is available immediately.
    if account_type in ("Student", "Institute Admin"):
        refreshed_user = get_user_by_id(user_id)

        if account_type == "Student":
            st.session_state.student_user = refreshed_user
        else:
            st.session_state.institute_admin = refreshed_user

    else:
        from database.database import authenticate_platform_admin
        refreshed_admin = authenticate_platform_admin(
            user_email,
            new_password
        )
        st.session_state.platform_admin = refreshed_admin

    st.success("✅ Password changed successfully.")
    st.info("Your new password will be required the next time you log in.")
