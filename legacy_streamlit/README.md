# Campus Guardian AI

AI-assisted multi-institute campus safety, complaint management and communication platform built with **Python, Streamlit and SQLite**.

## Completed roadmap

### Phases 1–10
- Complaint reporting and tracking
- Student and institute authentication
- Multi-institute isolation
- AI complaint analysis and duplicate detection
- Department management and assignment
- Campus safety map and risk intelligence
- Admin analytics
- Complaint details and workflow
- Notification center and preferences

### Phases 11–20
- **Phase 11 — Communication:** institute announcements, audience targeting, priority broadcasts and notification delivery.
- **Phase 12 — Student Profile:** profile details, emergency contact, bio and password change.
- **Phase 13 — Institute Control:** institute overview, departments, campus locations and operational controls.
- **Phase 14 — Advanced Complaint Workflow:** SLA hours, due dates, escalation level, assignee, resolution notes, history and student feedback.
- **Phase 15 — Analytics & Reports:** operational KPIs, resolution rate, overdue complaints, department workload and status analysis.
- **Phase 16 — Platform Intelligence:** platform-wide institute/user/complaint snapshot and activity visibility.
- **Phase 17 — Security & Audit:** institute-scoped audit logs, security visibility and audit export.
- **Phase 18 — Data Export:** CSV complaint and audit reports.
- **Phase 19 — Professional UI/UX:** consistent dark-gradient responsive Streamlit UI across the new management pages.
- **Phase 20 — Production Readiness:** database/schema health checks, core-system checks and deployment guidance.

## New pages

- `13_Institute_Control_Center.py`
- `14_Student_Profile.py`
- `15_Reports_and_Exports.py`
- `16_Announcements.py`
- `17_Platform_Intelligence.py`
- `18_Complaint_Feedback.py`
- `19_Security_and_Audit.py`
- `20_System_Health.py`

## Database additions

The existing database is migrated safely with new tables for:

- complaint workflow / SLA
- complaint history
- announcements
- user profiles
- audit logs
- platform settings

Existing institutes, users, complaints, departments, campus locations and notifications are preserved.

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Important

The application is still intended for local/controlled deployment. Before public production deployment, add HTTPS, environment-based secrets, rate limiting, stronger session management and a managed database service.
