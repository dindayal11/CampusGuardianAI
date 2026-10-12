import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap, MarkerCluster

from database.database import (
    get_all_complaints,
    get_campus_map_settings,
    get_campus_locations
)
from ai_engine.location_risk_analyzer import (
    analyze_location_risk,
    detect_hotspots
)



# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Campus Safety Map | Campus Guardian AI",
    page_icon="🗺️",
    layout="wide"
)


# =========================================================
# ADMIN LOGIN CHECK
# =========================================================

if (
    "institute_admin" not in st.session_state
    or st.session_state.institute_admin is None
):

    st.error("🔒 Access Denied")

    st.info(
        "Please login through the Institute Admin Login page."
    )

    st.stop()


# =========================================================
# GET LOGGED-IN INSTITUTE
# =========================================================

admin = st.session_state.institute_admin


if not isinstance(admin, (tuple, list)):

    st.error("🔒 Invalid administrator session.")

    st.stop()


if len(admin) < 2:

    st.error("🔒 Invalid administrator data.")

    st.stop()


# Current project structure:
# admin[1] = institute_id

institute_id = admin[1]


# =========================================================
# PAGE HEADER
# =========================================================

st.title("🗺️ Campus Safety Intelligence Map")

st.write(
    "AI-powered visualization of safety complaints, "
    "risk zones and campus hotspots."
)

st.caption(
    f"🏫 Institute ID: {institute_id}"
)

st.divider()


# =========================================================
# GET ONLY THIS INSTITUTE'S COMPLAINTS
# =========================================================

complaints = get_all_complaints(
    institute_id
)


# =========================================================
# LOAD INSTITUTE CAMPUS MAP CONFIGURATION
# =========================================================

map_settings = get_campus_map_settings(
    institute_id
)

campus_locations_data = get_campus_locations(
    institute_id
)

if not map_settings:
    st.warning(
        "⚠️ Campus map has not been configured for this institute yet."
    )
    st.info(
        "Please configure your campus center and locations from Institute Settings."
    )
    st.stop()

CAMPUS_CENTER = {
    "latitude": map_settings["center_latitude"],
    "longitude": map_settings["center_longitude"]
}

CAMPUS_LOCATIONS = {}

for location in campus_locations_data:

    CAMPUS_LOCATIONS[
        location["location_name"]
    ] = {
        "latitude": location["latitude"],
        "longitude": location["longitude"]
    }

DEFAULT_ZOOM = map_settings["default_zoom"]


# =========================================================
# MAP DISPLAY SETTINGS
# =========================================================

HEATMAP_ENABLED = bool(
    map_settings["heatmap_enabled"]
)

COMPLAINT_MARKERS_ENABLED = bool(
    map_settings["complaint_markers_enabled"]
)

HOTSPOTS_ENABLED = bool(
    map_settings["hotspots_enabled"]
)

CAMPUS_LOCATIONS_ENABLED = bool(
    map_settings["campus_locations_enabled"]
)

# =========================================================
# NO COMPLAINTS NOTICE
# =========================================================

if not complaints:

    st.info(
        "📭 No complaints have been reported for your institute yet."
    )

    st.caption(
        "The campus map is still available. "
        "Risk and hotspot information will appear automatically "
        "when complaints are reported."
    )

# =========================================================
# ANALYZE LOCATION RISKS
# =========================================================

location_risks = analyze_location_risk(
    complaints
)

hotspots = detect_hotspots(
    location_risks
)


# =========================================================
# TOP METRICS
# =========================================================

total_locations = len(location_risks)

danger_zones = len([
    location
    for location, data in location_risks.items()
    if data["risk_level"] == "Danger"
])

high_risk_zones = len([
    location
    for location, data in location_risks.items()
    if data["risk_level"] == "High Risk"
])

safe_locations = len([
    location
    for location, data in location_risks.items()
    if data["risk_level"] == "Safe"
])


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "📍 Locations With Reports",
        total_locations
    )


with col2:

    st.metric(
        "🔴 Danger Zones",
        danger_zones
    )


with col3:

    st.metric(
        "🟠 High Risk Zones",
        high_risk_zones
    )


with col4:

    st.metric(
        "🟢 Safe Locations",
        safe_locations
    )


st.divider()


# =========================================================
# AI HOTSPOT ALERTS
# =========================================================

if HOTSPOTS_ENABLED and hotspots:

    st.subheader(
        "🔥 AI Detected Safety Hotspots"
    )
    
    

    for hotspot in hotspots:

        st.warning(
            f"""
🚨 **HOTSPOT DETECTED**

📍 **Location:** {hotspot["location"]}

⚠️ **Risk Level:** {hotspot["risk_level"]}

📊 **Risk Score:** {hotspot["risk_score"]}/100

📝 **Total Complaints:** {hotspot["total_complaints"]}

🔴 **Critical:** {hotspot["critical_complaints"]}

🟠 **High:** {hotspot["high_complaints"]}

⏳ **Pending:** {hotspot["pending_complaints"]}

🔄 **In Progress:** {hotspot["in_progress_complaints"]}
"""
        )

elif HOTSPOTS_ENABLED:

    st.success(
        "✅ No major safety hotspots detected."
    )


st.divider()


# =========================================================
# MAP
# =========================================================

campus_map = folium.Map(

    location=[
        CAMPUS_CENTER["latitude"],
        CAMPUS_CENTER["longitude"]
    ],

    zoom_start=DEFAULT_ZOOM,

    control_scale=True
)


# =========================================================
# HEATMAP DATA
# =========================================================

heatmap_data = []


for location_name, risk_data in location_risks.items():

    if location_name not in CAMPUS_LOCATIONS:

        continue


    coordinates = CAMPUS_LOCATIONS[
        location_name
    ]


    latitude = coordinates["latitude"]

    longitude = coordinates["longitude"]

    weight = risk_data["risk_score"]


    heatmap_data.append(
        [
            latitude,
            longitude,
            weight
        ]
    )


# =========================================================
# ADD HEATMAP
# =========================================================

if HEATMAP_ENABLED and heatmap_data:

    HeatMap(

        heatmap_data,

        radius=35,

        blur=25,

        min_opacity=0.4

    ).add_to(campus_map)

# =========================================================
# CAMPUS LOCATION MARKERS
# =========================================================
# =========================================================
# CAMPUS LOCATION MARKERS
# =========================================================

if CAMPUS_LOCATIONS_ENABLED:

    for location_name, coordinates in CAMPUS_LOCATIONS.items():

        risk_data = location_risks.get(
            location_name
        )

        # -----------------------------------------------------
        # LOCATION HAS COMPLAINTS
        # -----------------------------------------------------

        if risk_data:

            risk_level = risk_data[
                "risk_level"
            ]

            # Marker color

            if risk_level == "Danger":

                marker_color = "red"

            elif risk_level == "High Risk":

                marker_color = "orange"

            elif risk_level == "Moderate":

                marker_color = "beige"

            else:

                marker_color = "green"


            popup_text = f"""
            <div style="width:250px">

            <h4>📍 {location_name}</h4>

            <b>Risk Level:</b>
            {risk_level}

            <br><br>

            <b>Risk Score:</b>
            {risk_data["risk_score"]}/100

            <br>

            <b>Safety Score:</b>
            {risk_data["safety_score"]}/100

            <br><br>

            <b>Total Complaints:</b>
            {risk_data["total"]}

            <br>

            <b>Critical:</b>
            {risk_data["critical"]}

            <br>

            <b>High:</b>
            {risk_data["high"]}

            <br>

            <b>Medium:</b>
            {risk_data["medium"]}

            <br>

            <b>Low:</b>
            {risk_data["low"]}

            <br><br>

            <b>Pending:</b>
            {risk_data["pending"]}

            <br>

            <b>In Progress:</b>
            {risk_data["in_progress"]}

            <br>

            <b>Resolved:</b>
            {risk_data["resolved"]}

            <br>

            <b>Rejected:</b>
            {risk_data["rejected"]}

            </div>
            """


        # -----------------------------------------------------
        # NO COMPLAINTS
        # -----------------------------------------------------

        else:

            marker_color = "blue"

            popup_text = f"""
            <div style="width:220px">

            <h4>📍 {location_name}</h4>

            <p>
            ✅ No complaints reported
            at this location.
            </p>

            </div>
            """


        # -----------------------------------------------------
        # ADD CAMPUS LOCATION MARKER
        # -----------------------------------------------------

        folium.Marker(

            location=[
                coordinates["latitude"],
                coordinates["longitude"]
            ],

            popup=folium.Popup(
                popup_text,
                max_width=320
            ),

            tooltip=location_name,

            icon=folium.Icon(
                color=marker_color,
                icon="info-sign"
            )

        ).add_to(campus_map)


# =========================================================
# COMPLAINT MARKERS
# =========================================================

if COMPLAINT_MARKERS_ENABLED:

    complaint_cluster = MarkerCluster(
        name="Complaint Markers"
    ).add_to(campus_map)

    for complaint in complaints:
        # -------------------------------------------------
        # CURRENT COMPLAINT DATA STRUCTURE
        # -------------------------------------------------

        complaint_id = complaint[1]
        title = complaint[4]
        description = complaint[5]
        location_name = complaint[6]
        priority = complaint[8]
        status = complaint[11]
        created_at = complaint[12]
        department = complaint[13]


        # -------------------------------------------------
        # CHECK LOCATION
        # -------------------------------------------------

        if location_name not in CAMPUS_LOCATIONS:

            continue


        coordinates = CAMPUS_LOCATIONS[
            location_name
        ]


        # -------------------------------------------------
        # MARKER COLOR
        # -------------------------------------------------

        if priority == "Critical":

            marker_color = "red"

        elif priority == "High":

            marker_color = "orange"

        elif priority == "Medium":

            marker_color = "beige"

        else:

            marker_color = "green"


        # -------------------------------------------------
        # COMPLAINT POPUP
        # -------------------------------------------------

        popup_text = f"""
        <div style="width:300px">

            <h4>🚨 Complaint Details</h4>

            <b>Complaint ID:</b>
            {complaint_id}

            <br><br>

            <b>Title:</b>
            {title}

            <br><br>

            <b>Location:</b>
            {location_name}

            <br><br>

            <b>Priority:</b>
            {priority}

            <br><br>

            <b>Status:</b>
            {status}

            <br><br>

            <b>Department:</b>
            {department or "Not Assigned"}

            <br><br>

            <b>Created:</b>
            {created_at}

            <br><br>

            <b>Description:</b>
            <br>
            {description}

        </div>
        """


        # -------------------------------------------------
        # ADD COMPLAINT MARKER
        # -------------------------------------------------

        folium.Marker(

            location=[
                coordinates["latitude"],
                coordinates["longitude"]
            ],

            popup=folium.Popup(
                popup_text,
                max_width=350
            ),

            tooltip=f"{priority} | {title}",

            icon=folium.Icon(
                color=marker_color,
                icon="warning-sign"
            )

        ).add_to(complaint_cluster)

# =========================================================
# DISPLAY MAP
# =========================================================

st_folium(

    campus_map,

    width=1400,

    height=600

)


# =========================================================
# LOCATION RISK ANALYSIS
# =========================================================

st.divider()

st.header(
    "📊 Location Risk Analysis"
)


if location_risks:

    sorted_locations = sorted(

        location_risks.items(),

        key=lambda x:
        x[1]["risk_score"],

        reverse=True

    )


    for location, data in sorted_locations:

        with st.expander(
            f"📍 {location} — {data['risk_level']}"
        ):

            col1, col2, col3, col4 = st.columns(4)


            with col1:

                st.metric(
                    "Total Complaints",
                    data["total"]
                )


            with col2:

                st.metric(
                    "Critical",
                    data["critical"]
                )


            with col3:

                st.metric(
                    "Risk Score",
                    f"{data['risk_score']}/100"
                )


            with col4:

                st.metric(
                    "Safety Score",
                    f"{data['safety_score']}/100"
                )


            st.divider()


            col1, col2, col3, col4 = st.columns(4)


            with col1:

                st.metric(
                    "High",
                    data["high"]
                )


            with col2:

                st.metric(
                    "Medium",
                    data["medium"]
                )


            with col3:

                st.metric(
                    "Pending",
                    data["pending"]
                )


            with col4:

                st.metric(
                    "Resolved",
                    data["resolved"]
                )


else:

    st.info(
        "No location data available yet."
    )


# =========================================================
# RISK LEGEND
# =========================================================

st.divider()

st.subheader(
    "🎯 Risk Level Guide"
)

st.write(
    """
🟢 **Safe** — Low complaint activity

🟡 **Moderate** — Some issues reported

🟠 **High Risk** — Frequent or serious complaints

🔴 **Danger** — Critical attention required
"""
)