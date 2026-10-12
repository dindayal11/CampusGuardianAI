import streamlit as st
from datetime import datetime


def require_role(role):
    if role == 'Student':
        if not st.session_state.get('student_logged_in') or not st.session_state.get('student_user'):
            st.error('🔒 Please login through Student Login.')
            st.stop()
        return st.session_state.student_user
    if role == 'Institute Admin':
        if not st.session_state.get('institute_admin_logged_in') or not st.session_state.get('institute_admin'):
            st.error('🔒 Please login through Institute Admin Login.')
            st.stop()
        return st.session_state.institute_admin
    if role == 'Platform Admin':
        if not st.session_state.get('platform_admin_logged_in') or not st.session_state.get('platform_admin'):
            st.error('🔒 Please login through Platform Admin.')
            st.stop()
        return st.session_state.platform_admin
    return None


def base_style():
    st.markdown('''<style>
    .stApp{background:radial-gradient(circle at 10% 10%,rgba(37,99,235,.16),transparent 30%),radial-gradient(circle at 90% 20%,rgba(124,58,237,.14),transparent 30%),linear-gradient(135deg,#020617,#071333 48%,#120b2e);color:#f8fafc}
    header[data-testid="stHeader"]{background:transparent!important}
    .block-container{max-width:1450px;padding-top:2rem;padding-bottom:3rem}
    section[data-testid="stSidebar"]{background:linear-gradient(180deg,#020617,#06133b,#0b0924);border-right:1px solid rgba(59,130,246,.35)}
    section[data-testid="stSidebar"] *{color:#e2e8f0}
    h1,h2,h3,h4{color:#f8fafc!important} p{color:#cbd5e1}
    div[data-testid="stMetric"]{background:linear-gradient(145deg,rgba(15,23,42,.96),rgba(23,37,84,.8));border:1px solid rgba(59,130,246,.32);border-radius:17px;padding:18px;min-height:105px}
    </style>''', unsafe_allow_html=True)


def fmt_dt(value):
    if not value: return '—'
    return str(value)
