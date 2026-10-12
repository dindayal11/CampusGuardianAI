# Final Run Guide

## Backend

```text
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env       # Windows
# cp .env.example .env       # macOS/Linux
uvicorn app.main:app --reload --port 8000
```

## Frontend

```text
cd frontend
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1` in `frontend/.env.local` for local development.

## Production

Use PostgreSQL, HTTPS, a strong random `SECRET_KEY`, `COOKIE_SECURE=true`, the real frontend URL in `CORS_ORIGINS`, and run Alembic migrations before starting the API.
