# Feature parity map

| Existing workflow | Production route |
|---|---|
| Student login | `/login` |
| Institute registration | `/register` + `POST /api/v1/management/institutes/register` |
| Student dashboard | `/dashboard` |
| Report Issue | `/dashboard/report` |
| My Complaints / Complaint list | `/dashboard/complaints` |
| Track Complaint / Complaint details | `/dashboard/complaints/[complaint_id]` |
| Notifications | `/dashboard/notifications` |
| Announcements | `/dashboard/announcements` |
| Student Profile / Change Password | `/dashboard/profile` |
| Student Management | `/dashboard/students` |
| Department Management | `/dashboard/departments` |
| Safety Map / Campus Locations | `/dashboard/campus` |
| Reports & Exports | `/dashboard/reports` |
| Security & Audit | `/dashboard/audit` |
| System Health | `/dashboard/health` |
| Platform Admin | `/dashboard/platform` after the restricted `/platform-access` login |
| Institute Control Center | Aggregated in the Institute Admin dashboard + management APIs |
| Complaint Feedback | Complaint detail page after resolution |
| Local complaint analysis | `backend/app/services/ai.py` |
| Duplicate detection | `backend/app/services/ai.py` |
| SQLite → PostgreSQL migration | `backend/scripts/migrate_sqlite_to_postgres.py` |

This is a production conversion foundation, not a declaration that every
legacy Streamlit screen has pixel-identical behavior. The legacy application
is preserved for side-by-side functional verification before public launch.
