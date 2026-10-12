import streamlit as st
import re

from database.database import register_institute


# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Register Institute | Campus Guardian AI",
    page_icon="🏫",
    layout="wide"
)


# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown("""
<style>

.main-title {
    font-size: 42px;
    font-weight: 700;
    text-align: center;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    font-size: 18px;
    color: #666;
    margin-bottom: 30px;
}

.section-title {
    font-size: 24px;
    font-weight: 600;
    margin-top: 10px;
}

.info-card {
    padding: 18px;
    border-radius: 12px;
    background-color: #f5f7fa;
    border: 1px solid #e1e5ea;
    margin-bottom: 15px;
}

.success-card {
    padding: 20px;
    border-radius: 12px;
    background-color: #eefaf1;
    border: 1px solid #b7e4c7;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# HEADER
# ==========================================

st.markdown(
    '<div class="main-title">🏫 Register Your Institute</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Bring AI-powered complaint management and campus safety '
    'to your institute.'
    '</div>',
    unsafe_allow_html=True
)


# ==========================================
# INFORMATION CARD
# ==========================================

st.info(
    "🔐 Institute registration requires verification. "
    "Your administrator account will remain inactive until "
    "the platform administrator approves your institute."
)


st.divider()


# ==========================================
# INSTITUTE INFORMATION
# ==========================================

st.markdown(
    '<div class="section-title">🏫 Institute Information</div>',
    unsafe_allow_html=True
)

st.write(
    "Enter the official information of your institute."
)

col1, col2 = st.columns(2)

with col1:

    institute_name = st.text_input(
        "Institute Name *",
        placeholder="Example: JB Institute of Technology"
    )

    institute_type = st.selectbox(
        "Institute Type *",
        [
            "College",
            "University",
            "School",
            "Coaching Institute",
            "Training Institute",
            "Other"
        ]
    )

    email = st.text_input(
        "Official Institute Email *",
        placeholder="admin@institute.edu"
    )


with col2:

    phone = st.text_input(
        "Official Contact Number *",
        placeholder="10-digit mobile number"
    )

    address = st.text_area(
        "Institute Address *",
        placeholder="Enter complete institute address",
        height=120
    )


col3, col4 = st.columns(2)

with col3:

    city = st.text_input(
        "City *",
        placeholder="Example: Dehradun"
    )

with col4:

    state = st.selectbox(
        "State *",
        [
            "Andhra Pradesh",
            "Assam",
            "Bihar",
            "Chhattisgarh",
            "Delhi",
            "Goa",
            "Gujarat",
            "Haryana",
            "Himachal Pradesh",
            "Jharkhand",
            "Karnataka",
            "Kerala",
            "Madhya Pradesh",
            "Maharashtra",
            "Odisha",
            "Punjab",
            "Rajasthan",
            "Tamil Nadu",
            "Telangana",
            "Uttar Pradesh",
            "Uttarakhand",
            "West Bengal",
            "Other"
        ]
    )


st.divider()


# ==========================================
# ADMIN INFORMATION
# ==========================================

st.markdown(
    '<div class="section-title">👤 Administrator Information</div>',
    unsafe_allow_html=True
)

st.write(
    "This person will manage the institute's Campus Guardian AI account."
)

col1, col2 = st.columns(2)

with col1:

    admin_name = st.text_input(
        "Administrator Name *",
        placeholder="Example: Rahul Sharma"
    )

with col2:

    admin_email = st.text_input(
        "Administrator Email *",
        placeholder="administrator@example.com"
    )


# ==========================================
# PASSWORD
# ==========================================

st.markdown(
    '<div class="section-title">🔐 Create Administrator Password</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:

    admin_password = st.text_input(
        "Password *",
        type="password",
        placeholder="Create a strong password"
    )

with col2:

    confirm_password = st.text_input(
        "Confirm Password *",
        type="password",
        placeholder="Enter password again"
    )


st.caption(
    "Password should contain at least 8 characters, "
    "including letters and numbers."
)


st.divider()


# ==========================================
# TERMS
# ==========================================

terms = st.checkbox(
    "I confirm that the information provided is accurate "
    "and I agree to the Campus Guardian AI terms and policies."
)


st.divider()


# ==========================================
# REGISTER BUTTON
# ==========================================

register_button = st.button(
    "🚀 Register Institute",
    use_container_width=True,
    type="primary"
)


# ==========================================
# FORM VALIDATION
# ==========================================

if register_button:

    errors = []

    if not institute_name.strip():
        errors.append("Institute Name is required.")

    if not email.strip():
        errors.append("Official Institute Email is required.")

    if not phone.strip():
        errors.append("Contact Number is required.")

    if not address.strip():
        errors.append("Institute Address is required.")

    if not city.strip():
        errors.append("City is required.")

    if not admin_name.strip():
        errors.append("Administrator Name is required.")

    if not admin_email.strip():
        errors.append("Administrator Email is required.")

    if not admin_password:
        errors.append("Password is required.")

    if not confirm_password:
        errors.append("Please confirm your password.")

    # --------------------------------------
    # EMAIL VALIDATION
    # --------------------------------------

    email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    if email and not re.match(
        email_pattern,
        email.strip()
    ):
        errors.append(
            "Please enter a valid institute email."
        )

    if admin_email and not re.match(
        email_pattern,
        admin_email.strip()
    ):
        errors.append(
            "Please enter a valid administrator email."
        )

    # --------------------------------------
    # PHONE VALIDATION
    # --------------------------------------

    if phone and not phone.isdigit():
        errors.append(
            "Contact Number should contain only digits."
        )

    elif phone and len(phone) != 10:
        errors.append(
            "Contact Number must contain exactly 10 digits."
        )

    # --------------------------------------
    # PASSWORD VALIDATION
    # --------------------------------------

    if admin_password:

        if len(admin_password) < 8:

            errors.append(
                "Password must contain at least 8 characters."
            )

        if not any(
            char.isalpha()
            for char in admin_password
        ):

            errors.append(
                "Password must contain at least one letter."
            )

        if not any(
            char.isdigit()
            for char in admin_password
        ):

            errors.append(
                "Password must contain at least one number."
            )

    # --------------------------------------
    # PASSWORD MATCH
    # --------------------------------------

    if (
        admin_password
        and confirm_password
        and admin_password != confirm_password
    ):

        errors.append(
            "Passwords do not match."
        )

    # --------------------------------------
    # TERMS
    # --------------------------------------

    if not terms:

        errors.append(
            "Please accept the terms and policies."
        )


    # ======================================
    # SHOW ERRORS
    # ======================================

    if errors:

        st.error(
            "❌ Please correct the following:"
        )

        for error in errors:

            st.warning(
                f"• {error}"
            )


    # ======================================
    # REGISTER
    # ======================================

    else:

        result = register_institute(

            name=institute_name,

            institute_type=institute_type,

            email=email,

            phone=phone,

            address=address,

            city=city,

            state=state,

            admin_name=admin_name,

            admin_email=admin_email,

            admin_password=admin_password
        )


        if result["success"]:

            st.balloons()

            st.success(
                "🎉 Institute registration submitted successfully!"
            )

            st.markdown(
                '<div class="success-card">',
                unsafe_allow_html=True
            )

            st.subheader(
                "🏫 Registration Details"
            )

            st.write(
                f"**Institute Code:** "
                f"`{result['institute_code']}`"
            )

            st.write(
                f"**Administrator ID:** "
                f"`{result['admin_user_id']}`"
            )

            st.write(
                "**Registration Status:** ⏳ Pending Verification"
            )

            st.markdown(
                '</div>',
                unsafe_allow_html=True
            )

            st.info(
                "🔐 Your administrator account has been created "
                "but is currently locked. You will be able to "
                "login after the platform administrator approves "
                "your institute."
            )

            st.warning(
                "⚠️ Please save your Institute Code and "
                "Administrator ID safely."
            )


        else:

            st.error(
                f"❌ {result['message']}"
            )