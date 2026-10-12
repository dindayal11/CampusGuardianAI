import os
from pathlib import Path
import importlib
import streamlit as st

from database.database import (
    create_tables,
    get_connection,
    get_platform_overview,
    get_audit_metrics,
    hash_password,
    verify_password,
)

st.set_page_config(page_title="System Health | Campus Guardian AI", page_icon="🩺", layout="wide")
create_tables()

st.markdown("""
<style>
.stApp{background:linear-gradient(135deg,#020617 0%,#071333 50%,#120b2e 100%);color:#f8fafc}
header[data-testid="stHeader"]{background:transparent!important}
section[data-testid="stSidebar"]{background:#020617}
h1,h2,h3{color:#f8fafc!important}
p{color:#cbd5e1}
.health-pass{padding:12px 16px;border-radius:12px;border:1px solid rgba(34,197,94,.35);background:rgba(34,197,94,.10)}
.health-warn{padding:12px 16px;border-radius:12px;border:1px solid rgba(234,179,8,.35);background:rgba(234,179,8,.10)}
.health-fail{padding:12px 16px;border-radius:12px;border:1px solid rgba(239,68,68,.35);background:rgba(239,68,68,.10)}
</style>
""", unsafe_allow_html=True)

if not (st.session_state.get("platform_admin_logged_in") and st.session_state.get("platform_admin")):
    st.error("🔒 Platform Admin access required")
    st.info("System Health contains platform-wide operational information.")
    st.stop()

admin = st.session_state.platform_admin

st.title("🩺 System Health")
st.caption("Live platform health, database integrity and production-readiness checks")

checks = []

def add_check(name, status, detail):
    checks.append((name, status, detail))

# Database connection
try:
    conn = get_connection()
    conn.execute("SELECT 1")
    conn.close()
    add_check("Database connection", "PASS", "SQLite connection is responding.")
except Exception as exc:
    add_check("Database connection", "FAIL", str(exc))

# Required schema
required_tables = [
    "institutes", "users", "complaints", "departments", "notifications",
    "notification_preferences", "campus_map_settings", "campus_locations",
    "platform_admins", "audit_logs", "platform_settings"
]
try:
    conn = get_connection()
    existing = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    conn.close()
    missing = [t for t in required_tables if t not in existing]
    add_check("Required database tables", "PASS" if not missing else "FAIL", "All required tables exist." if not missing else "Missing: " + ", ".join(missing))
except Exception as exc:
    add_check("Schema check", "FAIL", str(exc))

# Foreign-key integrity
try:
    conn = get_connection()
    fk_errors = conn.execute("PRAGMA foreign_key_check").fetchall()
    conn.close()
    add_check("Database integrity", "PASS" if not fk_errors else "WARN", "No foreign-key integrity errors found." if not fk_errors else f"{len(fk_errors)} foreign-key issue(s) found.")
except Exception as exc:
    add_check("Database integrity", "FAIL", str(exc))

# Password hashing self-test
try:
    probe = "HealthCheck@123"
    stored = hash_password(probe)
    valid = verify_password(probe, stored) and not verify_password("Wrong@123", stored)
    add_check("Password hashing", "PASS" if valid else "FAIL", "PBKDF2-HMAC-SHA256 self-test passed." if valid else "Password verification self-test failed.")
except Exception as exc:
    add_check("Password hashing", "FAIL", str(exc))

# Notification engine
try:
    importlib.import_module("ai_engine.notification_engine")
    add_check("Notification engine", "PASS", "Notification engine module loaded successfully.")
except Exception as exc:
    add_check("Notification engine", "FAIL", str(exc))

# AI modules
try:
    for module in ["ai_engine.complaint_analyzer", "ai_engine.duplicate_detector", "ai_engine.location_risk_analyzer", "ai_engine.admin_intelligence"]:
        importlib.import_module(module)
    add_check("AI modules", "PASS", "Core AI modules loaded successfully.")
except Exception as exc:
    add_check("AI modules", "FAIL", str(exc))

# Upload storage
try:
    upload_dir = Path(__file__).resolve().parents[1] / "uploads"
    upload_dir.mkdir(exist_ok=True)
    probe_file = upload_dir / ".health_check"
    probe_file.write_text("ok", encoding="utf-8")
    probe_file.unlink(missing_ok=True)
    add_check("File storage", "PASS", f"Uploads directory is writable: {upload_dir}")
except Exception as exc:
    add_check("File storage", "FAIL", str(exc))

# Database file size / location
try:
    db_path = Path(__file__).resolve().parents[1] / "campus_guardian.db"
    size_mb = db_path.stat().st_size / (1024 * 1024) if db_path.exists() else 0
    add_check("Database file", "PASS" if db_path.exists() else "WARN", f"{db_path.name} • {size_mb:.2f} MB")
except Exception as exc:
    add_check("Database file", "FAIL", str(exc))

# Audit system
try:
    audit_metrics = get_audit_metrics()
    add_check("Audit system", "PASS", f"Audit storage is active with {audit_metrics['total']} recorded event(s).")
except Exception as exc:
    add_check("Audit system", "FAIL", str(exc))

# Render checks
st.subheader("🔎 Health Checks")
for name, status, detail in checks:
    icon = "🟢" if status == "PASS" else ("🟡" if status == "WARN" else "🔴")
    box = "health-pass" if status == "PASS" else ("health-warn" if status == "WARN" else "health-fail")
    st.markdown(f'<div class="{box}"><b>{icon} {name} — {status}</b><br><span>{detail}</span></div>', unsafe_allow_html=True)
    st.write("")

passed = sum(1 for _, s, _ in checks if s == "PASS")
warnings = sum(1 for _, s, _ in checks if s == "WARN")
failed = sum(1 for _, s, _ in checks if s == "FAIL")

st.divider()
c1,c2,c3 = st.columns(3)
c1.metric("Healthy Checks", passed)
c2.metric("Warnings", warnings)
c3.metric("Failed Checks", failed)

st.subheader("📊 Live Platform Snapshot")
overview = get_platform_overview()
a,b,c,d,e = st.columns(5)
a.metric("Institutes", overview["institutes"])
b.metric("Users", overview["students"] + overview["admins"])
c.metric("Complaints", overview["complaints"])
d.metric("Resolved", overview["resolved"])
e.metric("Critical", overview["critical"])

st.divider()
st.subheader("🚀 Production Readiness")
ready_items = [
    ("Authentication & password hashing", "Implemented"),
    ("Institute data isolation", "Implemented"),
    ("Audit logging", "Implemented"),
    ("System health checks", "Implemented"),
    ("HTTPS", "Required after deployment"),
    ("Persistent managed database", "Recommended for production scale"),
    ("Secrets management", "Required for production credentials"),
]
for label, state in ready_items:
    st.write(f"**{label}:** {state}")

with st.sidebar:
    st.markdown("## 🛡️ Campus Guardian AI")
    st.caption("Platform Admin")
    st.divider()
    if st.button("🛡️ Platform Dashboard", use_container_width=True):
        st.switch_page("pages/7_Platform_Admin.py")
    if st.button("🔐 Security & Audit", use_container_width=True):
        st.switch_page("pages/19_Security_and_Audit.py")
    if st.button("🔐 Change Password", use_container_width=True):
        st.switch_page("pages/21_Change_Password.py")
