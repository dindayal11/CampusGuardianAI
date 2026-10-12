# Campus Guardian AI — Production Complete

This package converts the current Campus Guardian AI Streamlit application into a web/API production architecture while preserving the legacy app as a functional reference.

## Stack
- Web: Next.js + TypeScript
- API: FastAPI + SQLAlchemy
- Database: PostgreSQL
- Local analysis: scikit-learn TF-IDF similarity + keyword category/priority
- Maps: Leaflet + OpenStreetMap
- Auth: HttpOnly cookie + JWT, Argon2 for new/updated passwords
- Legacy reference: `legacy_streamlit/`

## Main production features
- Public SEO-friendly website: Home, Features, Solutions, How it works, About, FAQ, Contact, Privacy, Terms, Institute Registration
- Student reporting and complaint tracking
- AI-style category/priority analysis and duplicate similarity
- Attachments with file validation and generated filenames
- Complaint workflow, SLA, assignee, escalation, history and feedback
- Notifications and announcements
- Student and department management
- Campus locations and interactive campus map
- Reports/CSV export and analytics
- Security/audit and system health
- Platform Admin institute approval
- PostgreSQL migration from existing SQLite
- Password migration from legacy PBKDF2 to Argon2 after successful login

## Local run
### 1. Start PostgreSQL
```bash
docker compose up -d db
```

### 2. Backend
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend
```bash
cd frontend
npm install
copy .env.local.example .env.local
npm run dev
```

Open `http://localhost:3000`.

## Existing SQLite data
Keep a backup of the original `campus_guardian.db`.
Dry run:
```bash
python -m scripts.migrate_sqlite_to_postgres --sqlite "C:\path\campus_guardian.db" --dry-run
```
Migration:
```bash
python -m scripts.migrate_sqlite_to_postgres --sqlite "C:\path\campus_guardian.db"
```

## Platform Admin
Create a production admin manually instead of using a hardcoded public password:
```bash
python -m scripts.create_platform_admin --admin-id platform-admin --name "Platform Admin" --email admin@example.com
```

## Before public launch
Set:
- `SECRET_KEY`
- `DATABASE_URL`
- `CORS_ORIGINS`
- `COOKIE_SECURE=true`
- `NEXT_PUBLIC_SITE_URL`
- `NEXT_PUBLIC_API_BASE_URL`
- `NEXT_PUBLIC_SUPPORT_EMAIL`

Use managed PostgreSQL, HTTPS, object storage for production attachments, monitoring/backups, and Redis-backed rate limiting as traffic grows.

See `docs/COMPLETION_REPORT.md`, `docs/FEATURE_PARITY.md`, `docs/PRE_LAUNCH_CHECKLIST.md`, `docs/DEPLOYMENT.md`, and `docs/SECURITY.md`.


## Phase 3 — Complaint Workflow

Phase 3 strengthens the production complaint lifecycle with: priority-based SLA defaults, guarded status transitions, overdue detection, automatic SLA escalation signals, admin escalation endpoint, workflow history, and student-facing SLA state.

### Default SLA
- Critical: 4 hours
- High: 12 hours
- Medium: 48 hours
- Low: 72 hours

The workflow keeps the original Campus Guardian AI complaint/status model intact while adding production-safe lifecycle controls.
