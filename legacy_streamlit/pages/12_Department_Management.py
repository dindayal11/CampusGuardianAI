import streamlit as st

from database.database import (
    create_department,
    get_departments_by_institute,
    update_department,
    update_department_status
)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Department Management | Campus Guardian AI",
    page_icon="🏢",
    layout="wide"
)


# =========================================================
# SESSION CHECK
# =========================================================

if "institute_admin_logged_in" not in st.session_state:
    st.session_state.institute_admin_logged_in = False

if "institute_admin" not in st.session_state:
    st.session_state.institute_admin = None


if not st.session_state.institute_admin_logged_in:
    st.error("🔒 Access Denied. Please login as Institute Admin.")
    st.stop()


admin = st.session_state.institute_admin


# Validate admin session
if not isinstance(admin, (tuple, list)) or len(admin) < 10:
    st.error("❌ Invalid admin session data.")
    st.info("Please logout and login again.")
    st.stop()


admin_id = admin[2]
admin_name = admin[3]
institute_id = admin[1]


# =========================================================
# HEADER
# =========================================================

st.title("🏢 Department Management")

st.write(
    f"Welcome, **{admin_name}**. "
    "Manage departments of your institute from here."
)

st.divider()


# =========================================================
# LOAD DEPARTMENTS
# =========================================================

departments = get_departments_by_institute(institute_id)


# =========================================================
# STATISTICS
# =========================================================

total_departments = len(departments)

active_departments = sum(
    1 for department in departments
    if department[4] == "Active"
)

inactive_departments = sum(
    1 for department in departments
    if department[4] == "Inactive"
)


col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "🏢 Total Departments",
        total_departments
    )

with col2:
    st.metric(
        "🟢 Active",
        active_departments
    )

with col3:
    st.metric(
        "🔴 Inactive",
        inactive_departments
    )


st.divider()


# =========================================================
# ADD DEPARTMENT
# =========================================================

st.subheader("➕ Add New Department")

with st.form("add_department_form"):

    department_name = st.text_input(
        "Department Name",
        placeholder="Example: Electrical"
    )

    description = st.text_area(
        "Description",
        placeholder="Example: Handles electrical and power related complaints."
    )

    add_button = st.form_submit_button(
        "➕ Add Department",
        use_container_width=True
    )


if add_button:

    if not department_name.strip():

        st.warning(
            "⚠️ Please enter a department name."
        )

    else:

        result = create_department(
            institute_id=institute_id,
            department_name=department_name,
            description=description
        )

        if result["success"]:

            st.success(
                f"✅ {result['message']}"
            )

            st.rerun()

        else:

            st.error(
                f"❌ {result['message']}"
            )


st.divider()


# =========================================================
# EXISTING DEPARTMENTS
# =========================================================

st.subheader("📋 Existing Departments")


if not departments:

    st.info(
        "No departments have been created yet."
    )

else:

    for department in departments:

        # Department tuple
        # 0 id
        # 1 institute_id
        # 2 department_name
        # 3 description
        # 4 status
        # 5 created_at
        # 6 updated_at

        department_id = department[0]
        department_name = department[2]
        description = department[3] or ""
        status = department[4]
        created_at = department[5] or ""

        if status == "Active":
            status_text = "🟢 Active"
        else:
            status_text = "🔴 Inactive"

        with st.expander(
            f"🏢 {department_name}  •  {status_text}"
        ):

            col1, col2 = st.columns(2)

            with col1:

                st.write(
                    f"**Department ID:** {department_id}"
                )

                st.write(
                    f"**Status:** {status_text}"
                )

            with col2:

                st.write(
                    f"**Created:** {created_at}"
                )

            st.divider()

            # =================================================
            # EDIT DEPARTMENT
            # =================================================

            st.write("### ✏️ Edit Department")

            with st.form(
                f"edit_department_form_{department_id}"
            ):

                new_name = st.text_input(
                    "Department Name",
                    value=department_name,
                    key=f"name_{department_id}"
                )

                new_description = st.text_area(
                    "Description",
                    value=description,
                    key=f"description_{department_id}"
                )

                update_button = st.form_submit_button(
                    "💾 Save Changes",
                    use_container_width=True
                )

            if update_button:

                result = update_department(
                    department_id=department_id,
                    department_name=new_name,
                    description=new_description,
                    institute_id=institute_id
                )

                if result["success"]:

                    st.success(
                        f"✅ {result['message']}"
                    )

                    st.rerun()

                else:

                    st.error(
                        f"❌ {result['message']}"
                    )


            # =================================================
            # STATUS MANAGEMENT
            # =================================================

            st.write("### ⚙️ Department Status")

            if status == "Active":

                if st.button(
                    "🔴 Deactivate Department",
                    key=f"deactivate_{department_id}",
                    use_container_width=True
                ):

                    result = update_department_status(
                        department_id=department_id,
                        status="Inactive",
                        institute_id=institute_id
                    )

                    if result["success"]:

                        st.success(
                            f"✅ {result['message']}"
                        )

                        st.rerun()

                    else:

                        st.error(
                            f"❌ {result['message']}"
                        )

            else:

                if st.button(
                    "🟢 Activate Department",
                    key=f"activate_{department_id}",
                    use_container_width=True
                ):

                    result = update_department_status(
                        department_id=department_id,
                        status="Active",
                        institute_id=institute_id
                    )

                    if result["success"]:

                        st.success(
                            f"✅ {result['message']}"
                        )

                        st.rerun()

                    else:

                        st.error(
                            f"❌ {result['message']}"
                        )


st.divider()


# =========================================================
# SECURITY INFORMATION
# =========================================================

st.info(
    "🔐 **Institute Isolation:** "
    "You can only view and manage departments belonging "
    "to your own institute."
)

st.caption(
    "Campus Guardian AI • Department Management"
)