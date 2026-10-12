import streamlit as st
from database.database import create_tables

# Page Configuration
st.set_page_config(
    page_title="Campus Guardian AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

create_tables()

# Sidebar
with st.sidebar:
    st.image(
        "https://cdn-icons-png.flaticon.com/512/2919/2919592.png",
        width=100
    )

    st.title("Campus Guardian AI")

    st.markdown("---")

    st.write("🛡️ Intelligent Campus Safety Platform")

    st.markdown("---")

    st.caption("Version 1.0")


# Main Page
st.title("🛡️ Campus Guardian AI")

st.subheader(
    "Intelligent Campus Safety & Issue Management System"
)

st.markdown("""
Campus Guardian AI helps students report safety issues,
infrastructure problems and emergency situations.

Our AI system analyzes complaints and helps administrators
identify high-risk areas across the campus.
""")


# Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Reports",
        value="0"
    )

with col2:
    st.metric(
        label="Critical Issues",
        value="0"
    )

with col3:
    st.metric(
        label="Resolved Issues",
        value="0"
    )

with col4:
    st.metric(
        label="Campus Safety Score",
        value="100%"
    )


st.divider()


# Features Section
st.header("Platform Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("""
    🤖 AI Complaint Analysis

    Automatically detects category,
    priority and department.
    """)

with col2:
    st.warning("""
    🚨 Emergency Detection

    Identifies critical situations
    requiring immediate action.
    """)

with col3:
    st.success("""
    🗺️ Campus Safety Intelligence

    Detects risk zones and
    safety patterns.
    """)


st.divider()


# Call To Action
st.header("Quick Start")

st.write(
    "Use the navigation menu on the left to report an issue or explore campus safety insights."
)

st.button("🚨 Report an Issue", use_container_width=True)


# Footer
st.markdown("---")

st.caption(
    "© 2026 Campus Guardian AI | Built for Innovation & Safer Campuses"
)