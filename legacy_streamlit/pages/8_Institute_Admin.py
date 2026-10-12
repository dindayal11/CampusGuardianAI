import streamlit as st

from database.database import (
    authenticate_user,
    get_connection,
    get_campus_map_settings,
    create_campus_map_settings,
    update_campus_map_settings,
    get_campus_locations,
    add_campus_location,
    update_campus_location,
    delete_campus_location
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Institute Admin | Campus Guardian AI",
    page_icon="🏫",
    layout="wide"
)


# ============================================================
# DARK GRADIENT UI
# ============================================================

st.markdown(
    """
    <style>

    /* =====================================================
       MAIN APP
       ===================================================== */

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


    /* =====================================================
       HEADER
       ===================================================== */

    header[data-testid="stHeader"] {

        background: transparent !important;
        box-shadow: none !important;
        border: none !important;
    }


    [data-testid="stToolbar"] {

        background: transparent !important;
    }


    /* =====================================================
       MAIN CONTAINER
       ===================================================== */

    .block-container {

        max-width: 1450px;

        padding-top: 2rem;
        padding-bottom: 3rem;
    }


    /* =====================================================
       SIDEBAR
       ===================================================== */

    section[data-testid="stSidebar"] {

        background:
            linear-gradient(
                180deg,
                #020617 0%,
                #06133b 55%,
                #0b0924 100%
            );

        border-right:
            1px solid rgba(59, 130, 246, 0.35);
    }


    section[data-testid="stSidebar"] * {

        color: #e2e8f0;
    }


    /* =====================================================
       HEADINGS
       ===================================================== */

    h1,
    h2,
    h3,
    h4 {

        color: #f8fafc !important;
    }


    p {

        color: #cbd5e1;
    }


    /* =====================================================
       CARDS
       ===================================================== */

    div[data-testid="stVerticalBlockBorderWrapper"] {

        background:
            linear-gradient(
                145deg,
                rgba(15, 23, 42, 0.88),
                rgba(15, 23, 42, 0.72)
            );

        border:
            1px solid rgba(59, 130, 246, 0.28);

        border-radius: 18px;

        box-shadow:
            0 8px 30px rgba(0, 0, 0, 0.25);

        padding: 5px;
    }


    /* =====================================================
       BUTTONS
       ===================================================== */

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

        border:
            1px solid rgba(59, 130, 246, 0.45);

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


    /* =====================================================
       INPUTS
       ===================================================== */

    input,
    textarea {

        background-color: #0f172a !important;

        color: #f8fafc !important;
    }


    /* =====================================================
       SELECTBOX
       ===================================================== */

    div[data-baseweb="select"] > div {

        background-color: #0f172a !important;

        color: #f8fafc !important;

        border-radius: 10px;
    }


    /* =====================================================
       INFO / SUCCESS BOX
       ===================================================== */

    div[data-testid="stAlert"] {

        border-radius: 14px;
    }


    /* =====================================================
       DIVIDER
       ===================================================== */

    hr {

        border-color:
            rgba(59, 130, 246, 0.22);
    }


    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "institute_admin_logged_in" not in st.session_state:

    st.session_state.institute_admin_logged_in = False


if "institute_admin" not in st.session_state:

    st.session_state.institute_admin = None


if "show_campus_locations" not in st.session_state:

    st.session_state.show_campus_locations = False


# ============================================================
# LOGIN PAGE
# ============================================================

if not st.session_state.institute_admin_logged_in:

    st.markdown(
        """
        <div style="
            font-size:34px;
            font-weight:800;
            color:#ffffff;
            margin-bottom:5px;
        ">
            🏫 Campus Guardian AI
        </div>

        <div style="
            font-size:16px;
            color:#94a3b8;
            margin-bottom:25px;
        ">
            Institute Admin Portal
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### 🔐 Administrator Login")

    st.info(
        "Login using the Administrator ID and password "
        "provided during institute registration."
    )

    st.divider()

    col1, col2 = st.columns([1, 1])

    with col1:

        user_id = st.text_input(
            "Administrator ID",
            placeholder="Example: INST-0001-ADMIN"
        )

    with col2:

        password = st.text_input(
            "Password",
            type="password"
        )

    if st.button(
        "🔐 Login",
        use_container_width=True
    ):

        if not user_id or not password:

            st.warning(
                "⚠️ Please enter Administrator ID and password."
            )

        else:

            result = authenticate_user(
                user_id,
                password
            )

            if not result["success"]:

                st.error(
                    result["message"]
                )

            else:

                user = result["user"]

                # users table:
                #
                # 0 = id
                # 1 = institute_id
                # 2 = user_id
                # 3 = name
                # 4 = email
                # 5 = password
                # 6 = role
                # 7 = status
                # 8 = created_at
                # 9 = last_login

                if user[6] != "Institute Admin":

                    st.error(
                        "❌ This account is not an Institute Admin account."
                    )

                else:

                    st.session_state.institute_admin_logged_in = True

                    st.session_state.institute_admin = user

                    st.success(
                        "✅ Login successful!"
                    )

                    st.rerun()

    st.divider()

    st.caption(
        "Use the Administrator ID received after institute registration."
    )

    st.stop()


# ============================================================
# ADMIN DATA
# ============================================================

admin = st.session_state.institute_admin


if (
    not isinstance(admin, (tuple, list))
    or len(admin) < 10
):

    st.error("🔒 Access Denied")

    st.info(
        "Please logout and login again."
    )

    st.stop()


admin_id = admin[2]

admin_name = admin[3]

admin_email = admin[4]

institute_id = admin[1]


# ============================================================
# LOAD INSTITUTE
# ============================================================

conn = get_connection()

cursor = conn.cursor()

cursor.execute(
    """
    SELECT *
    FROM institutes
    WHERE id = ?
    """,
    (institute_id,)
)

institute = cursor.fetchone()

conn.close()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "## 🛡️ Campus Guardian AI"
    )

    st.caption(
        "Institute Admin Portal"
    )

    st.divider()

    st.markdown(
        "### 👤 Administrator"
    )

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


    # --------------------------------------------------------
    # ADMIN DASHBOARD
    # --------------------------------------------------------

    if st.button(
        "📊 Admin Dashboard",
        use_container_width=True
    ):

        st.switch_page(
            "pages/8_Institute_Admin.py"
        )


    # --------------------------------------------------------
    # STUDENT MANAGEMENT
    # --------------------------------------------------------

    if st.button(
        "👨‍🎓 Student Management",
        use_container_width=True
    ):

        st.switch_page(
            "pages/9_Student_Management.py"
        )


    # --------------------------------------------------------
    # CAMPUS LOCATIONS
    # --------------------------------------------------------

    if st.button(
        "📍 Campus Locations",
        use_container_width=True
    ):

        st.session_state.show_campus_locations = True

        st.rerun()


    # --------------------------------------------------------
    # ANNOUNCEMENTS
    # --------------------------------------------------------

    if st.button(
        "📢 Announcements",
        use_container_width=True
    ):

        st.switch_page(
            "pages/16_Announcements.py"
        )


    st.divider()


    # --------------------------------------------------------
    # LOGOUT
    # --------------------------------------------------------

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state.institute_admin_logged_in = False

        st.session_state.institute_admin = None

        st.session_state.show_campus_locations = False

        st.rerun()


# ============================================================
# PAGE HEADER
# ============================================================

st.markdown(
    """
    <div style="
        font-size:34px;
        font-weight:800;
        color:#ffffff;
        margin-bottom:5px;
    ">
        🏫 Institute Admin
    </div>

    <div style="
        font-size:15px;
        color:#94a3b8;
        margin-bottom:25px;
    ">
        Manage your institute information and administration.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# INSTITUTE NOT FOUND
# ============================================================

if not institute:

    st.error(
        "❌ Institute information could not be found."
    )

    st.stop()


# ============================================================
# INSTITUTE DATA
# ============================================================

institute_code = institute[1]

institute_name = institute[2]

institute_type = institute[3]

institute_email = institute[4]

institute_phone = institute[5]

institute_address = institute[6]

institute_city = institute[7]

institute_state = institute[8]

institute_status = institute[9]


# ============================================================
# WELCOME
# ============================================================

st.markdown(
    f'<div style="background:#111827; padding:24px; border-radius:18px; margin-bottom:25px;">'
    f'<div style="font-size:24px; font-weight:700; color:white;">'
    f'👋 Welcome, {admin_name}'
    f'</div>'
    f'<div style="font-size:15px; color:#cbd5e1; margin-top:8px;">'
    f'You are managing <strong>{institute_name}</strong>.'
    f'</div>'
    f'</div>',
    unsafe_allow_html=True
)
# ============================================================
# INSTITUTE INFORMATION
# ============================================================

st.markdown(
    "### 🏫 Institute Information"
)

col1, col2, col3 = st.columns(3)


with col1:

    with st.container(border=True):

        st.markdown(
            "#### 🏫 Basic Information"
        )

        st.write(
            f"**Institute Name:** {institute_name}"
        )

        st.write(
            f"**Institute Code:** {institute_code}"
        )

        st.write(
            f"**Institute Type:** {institute_type}"
        )


with col2:

    with st.container(border=True):

        st.markdown(
            "#### 📧 Contact Information"
        )

        st.write(
            f"**Email:** {institute_email}"
        )

        st.write(
            f"**Phone:** {institute_phone}"
        )

        st.write(
            f"**City:** {institute_city}"
        )


with col3:

    with st.container(border=True):

        st.markdown(
            "#### 📌 Status"
        )

        if institute_status == "Active":

            st.success(
                f"🟢 {institute_status}"
            )

        elif institute_status == "Pending":

            st.warning(
                f"🟡 {institute_status}"
            )

        else:

            st.error(
                f"🔴 {institute_status}"
            )

        st.write(
            f"**State:** {institute_state}"
        )

        st.write(
            f"**Institute ID:** {institute_id}"
        )


st.divider()


# ============================================================
# ADDRESS
# ============================================================

st.markdown(
    "### 📍 Institute Address"
)

with st.container(border=True):

    st.markdown(
        f"""
        **{institute_address}**

        {institute_city}, {institute_state}
        """
    )


st.divider()


# ============================================================
# MANAGEMENT MODULES
# ============================================================

st.markdown(
    "### 🚀 Management Modules"
)

st.caption(
    "Access the main administrative tools from the options below."
)


col1, col2, col3 = st.columns(3)


# ============================================================
# STUDENT MANAGEMENT
# ============================================================

with col1:

    with st.container(border=True):

        st.markdown(
            "### 👨‍🎓 Student Management"
        )

        st.write(
            "Create and manage student accounts "
            "for your institute."
        )

        if st.button(
            "Open Student Management",
            key="open_student_management",
            use_container_width=True
        ):

            st.switch_page(
                "pages/9_Student_Management.py"
            )


# ============================================================
# ADMIN DASHBOARD
# ============================================================

with col2:

    with st.container(border=True):

        st.markdown(
            "### 📊 Admin Dashboard"
        )

        st.write(
            "View complaints, analytics, AI insights, "
            "locations and department performance."
        )

        if st.button(
            "Open Admin Dashboard",
            key="open_admin_dashboard",
            use_container_width=True
        ):

            st.switch_page(
                "pages/_Admin_Dashboard.py"
            )


# ============================================================
# CAMPUS LOCATIONS
# ============================================================

with col3:

    with st.container(border=True):

        st.markdown(
            "### 📍 Campus Locations"
        )

        st.write(
            "Configure campus locations and map settings "
            "for your institute."
        )

        if st.button(
            "⚙️ Manage Campus Locations",
            key="manage_campus_locations",
            use_container_width=True
        ):

            st.session_state.show_campus_locations = True

            st.rerun()


# ============================================================
# CAMPUS LOCATION MANAGEMENT
# ============================================================

if st.session_state.get(
    "show_campus_locations",
    False
):

    st.divider()

    st.markdown(
        "## 📍 Campus Location Management"
    )

    st.caption(
        "Create, edit and remove locations for your institute. "
        "These locations are used by Student Report Issue "
        "and Safety Map."
    )


    # ========================================================
    # LOAD CURRENT MAP SETTINGS
    # ========================================================

    map_settings = get_campus_map_settings(
        institute_id
    )

    campus_locations = get_campus_locations(
        institute_id
    )


    # ========================================================
    # MAP SETTINGS
    # ========================================================

    st.markdown(
        "### 🗺️ Map Settings"
    )

    with st.container(border=True):

        if map_settings:

            current_lat = float(
                map_settings["center_latitude"]
            )

            current_lng = float(
                map_settings["center_longitude"]
            )

            current_zoom = int(
                map_settings["default_zoom"]
            )

            current_heatmap = bool(
                map_settings["heatmap_enabled"]
            )

            current_markers = bool(
                map_settings["complaint_markers_enabled"]
            )

            current_hotspots = bool(
                map_settings["hotspots_enabled"]
            )

            current_locations_layer = bool(
                map_settings["campus_locations_enabled"]
            )

        else:

            current_lat = 0.0
            current_lng = 0.0
            current_zoom = 17

            current_heatmap = True
            current_markers = True
            current_hotspots = True
            current_locations_layer = True


        col1, col2 = st.columns(2)


        with col1:

            center_latitude = st.number_input(
                "Campus Center Latitude",
                value=current_lat,
                format="%.6f",
                key="campus_center_latitude"
            )


        with col2:

            center_longitude = st.number_input(
                "Campus Center Longitude",
                value=current_lng,
                format="%.6f",
                key="campus_center_longitude"
            )


        default_zoom = st.slider(
            "Default Map Zoom",
            min_value=10,
            max_value=21,
            value=current_zoom,
            key="campus_default_zoom"
        )


        st.markdown(
            "#### 🧩 Map Layers"
        )


        col1, col2, col3, col4 = st.columns(4)


        with col1:

            heatmap_enabled = st.checkbox(
                "🔥 Heatmap",
                value=current_heatmap,
                key="heatmap_enabled"
            )


        with col2:

            complaint_markers_enabled = st.checkbox(
                "📍 Complaint Markers",
                value=current_markers,
                key="complaint_markers_enabled"
            )


        with col3:

            hotspots_enabled = st.checkbox(
                "🚨 Hotspots",
                value=current_hotspots,
                key="hotspots_enabled"
            )


        with col4:

            campus_locations_enabled = st.checkbox(
                "🏫 Campus Locations",
                value=current_locations_layer,
                key="campus_locations_enabled"
            )


        if st.button(
            "💾 Save Map Settings",
            key="save_map_settings",
            use_container_width=True
        ):

            if not map_settings:

                create_campus_map_settings(
                    institute_id=institute_id,
                    center_latitude=center_latitude,
                    center_longitude=center_longitude,
                    default_zoom=default_zoom
                )


            update_campus_map_settings(
                institute_id=institute_id,
                center_latitude=center_latitude,
                center_longitude=center_longitude,
                default_zoom=default_zoom,
                heatmap_enabled=heatmap_enabled,
                complaint_markers_enabled=complaint_markers_enabled,
                hotspots_enabled=hotspots_enabled,
                campus_locations_enabled=campus_locations_enabled
            )

            st.success(
                "✅ Map settings saved successfully."
            )

            st.rerun()


    # ========================================================
    # ADD NEW LOCATION
    # ========================================================

    st.markdown(
        "### ➕ Add Campus Location"
    )

    with st.container(border=True):

        col1, col2 = st.columns(2)


        with col1:

            new_location_name = st.text_input(
                "Location Name",
                placeholder="Example: Main Gate",
                key="new_location_name"
            )


        with col2:

            new_location_type = st.selectbox(
                "Location Type",
                [
                    "General",
                    "Gate",
                    "Academic",
                    "Department",
                    "Library",
                    "Canteen",
                    "Hostel",
                    "Parking",
                    "Playground",
                    "Office",
                    "Laboratory",
                    "Other"
                ],
                key="new_location_type"
            )


        col1, col2 = st.columns(2)


        with col1:

            new_latitude = st.number_input(
                "Latitude",
                format="%.6f",
                value=0.0,
                key="new_location_latitude"
            )


        with col2:

            new_longitude = st.number_input(
                "Longitude",
                format="%.6f",
                value=0.0,
                key="new_location_longitude"
            )


        if st.button(
            "➕ Add Location",
            key="add_campus_location",
            use_container_width=True
        ):

            if not new_location_name.strip():

                st.warning(
                    "⚠️ Please enter a location name."
                )

            elif (
                new_latitude == 0
                or new_longitude == 0
            ):

                st.warning(
                    "⚠️ Please enter valid latitude and longitude."
                )

            else:

                try:

                    add_campus_location(
                        institute_id=institute_id,
                        location_name=new_location_name.strip(),
                        latitude=new_latitude,
                        longitude=new_longitude,
                        location_type=new_location_type
                    )

                    st.success(
                        f"✅ {new_location_name} added successfully."
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"❌ Could not add location: {e}"
                    )


    # ========================================================
    # EXISTING LOCATIONS
    # ========================================================

    st.markdown(
        "### 📋 Existing Campus Locations"
    )


    if not campus_locations:

        st.info(
            "ℹ️ No campus locations have been added yet."
        )

    else:

        location_types = [
            "General",
            "Gate",
            "Academic",
            "Department",
            "Library",
            "Canteen",
            "Hostel",
            "Parking",
            "Playground",
            "Office",
            "Laboratory",
            "Other"
        ]


        for location in campus_locations:

            location_id = location["id"]

            location_name = location["location_name"]

            latitude = location["latitude"]

            longitude = location["longitude"]

            location_type = location["location_type"]


            with st.container(border=True):

                col1, col2, col3 = st.columns(
                    [3, 2, 2]
                )


                with col1:

                    st.markdown(
                        f"### 📍 {location_name}"
                    )

                    st.caption(
                        f"Type: {location_type}"
                    )


                with col2:

                    st.write(
                        f"**Latitude:** {latitude:.6f}"
                    )

                    st.write(
                        f"**Longitude:** {longitude:.6f}"
                    )


                with col3:

                    if st.button(
                        "✏️ Edit",
                        key=f"edit_location_{location_id}",
                        use_container_width=True
                    ):

                        st.session_state[
                            f"editing_location_{location_id}"
                        ] = True

                        st.rerun()


                    if st.button(
                        "🗑️ Delete",
                        key=f"delete_location_{location_id}",
                        use_container_width=True
                    ):

                        delete_campus_location(
                            location_id,
                            institute_id
                        )

                        st.success(
                            f"✅ {location_name} removed successfully."
                        )

                        st.rerun()


                # ====================================================
                # EDIT LOCATION
                # ====================================================

                if st.session_state.get(
                    f"editing_location_{location_id}",
                    False
                ):

                    st.divider()

                    st.markdown(
                        "#### ✏️ Edit Location"
                    )


                    edit_col1, edit_col2 = st.columns(2)


                    with edit_col1:

                        edit_name = st.text_input(
                            "Location Name",
                            value=location_name,
                            key=f"edit_name_{location_id}"
                        )


                    with edit_col2:

                        if location_type in location_types:

                            type_index = location_types.index(
                                location_type
                            )

                        else:

                            type_index = 0


                        edit_type = st.selectbox(
                            "Location Type",
                            location_types,
                            index=type_index,
                            key=f"edit_type_{location_id}"
                        )


                    edit_col1, edit_col2 = st.columns(2)


                    with edit_col1:

                        edit_latitude = st.number_input(
                            "Latitude",
                            value=float(latitude),
                            format="%.6f",
                            key=f"edit_latitude_{location_id}"
                        )


                    with edit_col2:

                        edit_longitude = st.number_input(
                            "Longitude",
                            value=float(longitude),
                            format="%.6f",
                            key=f"edit_longitude_{location_id}"
                        )


                    save_col, cancel_col = st.columns(2)


                    with save_col:

                        if st.button(
                            "💾 Save Changes",
                            key=f"save_location_{location_id}",
                            use_container_width=True
                        ):

                            if not edit_name.strip():

                                st.warning(
                                    "⚠️ Location name cannot be empty."
                                )

                            elif (
                                edit_latitude == 0
                                or edit_longitude == 0
                            ):

                                st.warning(
                                    "⚠️ Please enter valid coordinates."
                                )

                            else:

                                try:

                                    update_campus_location(
                                        location_id=location_id,
                                        institute_id=institute_id,
                                        location_name=edit_name.strip(),
                                        latitude=edit_latitude,
                                        longitude=edit_longitude,
                                        location_type=edit_type
                                    )

                                    st.success(
                                        "✅ Location updated successfully."
                                    )

                                    st.session_state[
                                        f"editing_location_{location_id}"
                                    ] = False

                                    st.rerun()

                                except Exception as e:

                                    st.error(
                                        f"❌ Could not update location: {e}"
                                    )


                    with cancel_col:

                        if st.button(
                            "❌ Cancel",
                            key=f"cancel_location_{location_id}",
                            use_container_width=True
                        ):

                            st.session_state[
                                f"editing_location_{location_id}"
                            ] = False

                            st.rerun()


    # ========================================================
    # CLOSE LOCATION MANAGEMENT
    # ========================================================

    st.divider()

    if st.button(
        "⬆️ Close Campus Location Management",
        key="close_campus_locations",
        use_container_width=True
    ):

        st.session_state.show_campus_locations = False

        st.rerun()


st.divider()


# ============================================================
# DATA ISOLATION
# ============================================================

st.markdown(
    "### 🔐 Data Isolation"
)

with st.container(border=True):

    st.success(
        "🛡️ This Institute Admin account can access "
        "only the data and management functions belonging "
        "to its own institute."
    )

    st.caption(
        f"Current Institute ID: {institute_id}"
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🛡️ Campus Guardian AI • Institute Admin Portal"
)

st.caption(
    "Secure • AI-Powered • Institute-Specific"
)