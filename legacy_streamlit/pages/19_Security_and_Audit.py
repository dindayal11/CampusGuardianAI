import streamlit as st
import pandas as pd
from database.database import create_tables, get_audit_logs, get_audit_metrics

st.set_page_config(page_title="Security & Audit | Campus Guardian AI", page_icon="🔐", layout="wide")
create_tables()

st.markdown("""
<style>
.stApp{background:linear-gradient(135deg,#020617 0%,#071333 50%,#120b2e 100%);color:#f8fafc}
header[data-testid="stHeader"]{background:transparent!important}
section[data-testid="stSidebar"]{background:#020617}
h1,h2,h3{color:#f8fafc!important}
p{color:#cbd5e1}
</style>
""", unsafe_allow_html=True)

is_platform = bool(st.session_state.get("platform_admin_logged_in") and st.session_state.get("platform_admin"))
is_institute = bool(st.session_state.get("institute_admin_logged_in") and st.session_state.get("institute_admin"))

if not is_platform and not is_institute:
    st.error("🔒 Login Required")
    st.info("Please login as an Institute Admin or Platform Admin.")
    st.stop()

if is_platform:
    account = st.session_state.platform_admin
    actor_id = account[1]
    actor_role = "Platform Admin"
    institute_id = None
    scope_label = "All Institutes"
else:
    account = st.session_state.institute_admin
    actor_id = account[2]
    actor_role = "Institute Admin"
    institute_id = account[1]
    scope_label = f"Institute {institute_id}"

st.title("🔐 Security & Audit Center")
st.caption(f"Security events and audit trail • Scope: {scope_label}")

metrics = get_audit_metrics(institute_id)
c1,c2,c3,c4 = st.columns(4)
c1.metric("Total Audit Events", metrics["total"])
c2.metric("Last 24 Hours", metrics["last_24h"])
c3.metric("Failed/Blocked Logins", metrics["failed_logins"])
c4.metric("Unique Actors", metrics["unique_actors"])

st.divider()

logs = get_audit_logs(institute_id, 1000)
columns = ["ID","Institute","Actor","Role","Action","Entity","Entity ID","Details","Created At"]
df = pd.DataFrame(logs, columns=columns)

if not df.empty:
    f1,f2,f3 = st.columns(3)
    with f1:
        actions = sorted(df["Action"].dropna().unique().tolist())
        selected_action = st.selectbox("Filter by Action", ["All"] + actions)
    with f2:
        roles = sorted(df["Role"].dropna().unique().tolist())
        selected_role = st.selectbox("Filter by Role", ["All"] + roles)
    with f3:
        actors = sorted(df["Actor"].dropna().unique().tolist())
        selected_actor = st.selectbox("Filter by Actor", ["All"] + actors)

    filtered = df.copy()
    if selected_action != "All":
        filtered = filtered[filtered["Action"] == selected_action]
    if selected_role != "All":
        filtered = filtered[filtered["Role"] == selected_role]
    if selected_actor != "All":
        filtered = filtered[filtered["Actor"] == selected_actor]

    st.subheader("📋 Audit Trail")
    st.dataframe(filtered, use_container_width=True, hide_index=True)
    st.download_button(
        "⬇️ Export Audit Log (CSV)",
        filtered.to_csv(index=False).encode("utf-8"),
        "campus_guardian_audit_log.csv",
        "text/csv",
        use_container_width=True
    )
else:
    st.info("📭 No audit activity has been recorded yet.")

st.divider()
st.subheader("🛡️ Security Controls")
sc1,sc2 = st.columns(2)
with sc1:
    st.success("🔐 Passwords are stored using PBKDF2-HMAC-SHA256 with per-password salt.")
    st.success("🏫 Institute-scoped account and complaint operations are enforced in database queries.")
    st.success("📝 Login, password-change and important administrative actions are auditable.")
with sc2:
    st.info("🌐 Production deployment should use HTTPS and protected environment secrets.")
    st.info("💾 Keep the SQLite database on persistent storage until a managed database is introduced.")
    st.info("👁️ Institute Admins can see only their institute's audit events; Platform Admin can see all.")

with st.sidebar:
    st.markdown("## 🛡️ Campus Guardian AI")
    st.caption(actor_role)
    st.divider()
    if is_platform:
        if st.button("🛡️ Platform Dashboard", use_container_width=True):
            st.switch_page("pages/7_Platform_Admin.py")
        if st.button("🩺 System Health", use_container_width=True):
            st.switch_page("pages/20_System_Health.py")
    else:
        if st.button("🏫 Admin Dashboard", use_container_width=True):
            st.switch_page("pages/8_Institute_Admin.py")
    if st.button("🔐 Change Password", use_container_width=True):
        st.switch_page("pages/21_Change_Password.py")
