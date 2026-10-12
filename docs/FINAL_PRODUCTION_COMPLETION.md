# Campus Guardian AI — Final Production Integration Pass

This package is the consolidated production web application built from the real Campus Guardian AI project. The legacy Streamlit application is retained under `legacy_streamlit/` as the functional source/reference for parity checks.

## Included product layers

- Next.js 16 + React 19 web application
- FastAPI API
- SQLAlchemy + PostgreSQL-ready persistence
- SQLite development fallback
- Role-based access: Student, Institute Admin, Platform Admin
- Secure HTTP-only cookie sessions
- Argon2 password hashing with legacy PBKDF2 verification/upgrade support
- Institute registration and platform approval workflow
- Student management
- Department management
- Complaint reporting with JPG/JPEG/PNG evidence uploads
- Local complaint category/priority/risk analysis
- TF-IDF similarity and duplicate detection
- Department routing recommendations
- Complaint lifecycle: Pending → In Progress → Resolved/Rejected
- Priority-based SLA and escalation workflow
- Complaint history and audit trail
- Student feedback after resolution
- In-app notifications and notification preferences
- Institute announcements
- Campus locations and safety map
- Reports/CSV export and analytics
- Platform controls and system health
- Public SEO-oriented product pages
- Privacy, Terms, Contact, FAQ and feature pages
- robots.txt and sitemap
- Security headers and origin checks

## Important product rule

The original `campus_guardian_review` project remains the source of truth for existing business behavior. The production layer should not silently replace working legacy logic with invented behavior.

## Final verification performed in this environment

- Python backend compilation: PASS
- AI analyzer smoke tests: PASS
- FastAPI application import: PASS
- Expected production API routes: PASS
- Frontend dependency installation/build: NOT completed in this environment because the npm install did not finish within the execution window. Run `npm install` followed by `npm run build` locally or in CI before deployment.

## Before public launch

Configure real production environment variables, managed PostgreSQL, HTTPS, secure cookies, exact CORS origins, backups, domain/DNS, support contact, reviewed legal policies, rate limiting/WAF, and a successful frontend CI build.

Ad/AdSense eligibility is not guaranteed by the codebase and requires actual policy-compliant content, privacy disclosures, site quality, and Google's review.
