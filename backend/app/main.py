from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.core.config import get_settings
from app.db import Base, engine
from app.routers import (
    admin,
    announcements,
    auth,
    complaints,
    notifications,
    profile,
    public,
    management,
    push,
)
import app.models  # noqa: F401

settings = get_settings()
app = FastAPI(
    title="Campus Guardian AI API",
    version="1.2.0",
    description="Production API for Campus Guardian AI campus safety and complaint management.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-CSRF-Protection"],
)

@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if settings.environment == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

@app.middleware("http")
async def csrf_origin_guard(request: Request, call_next):
    # Cookie-authenticated state-changing browser requests must carry a known Origin.
    # API clients without an Origin remain allowed (useful for mobile/backend tooling).
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        origin = request.headers.get("origin")
        if origin and origin not in settings.cors_origin_list:
            from fastapi.responses import JSONResponse
            return JSONResponse(status_code=403, content={"detail": "Origin is not allowed."})
    return await call_next(request)

if settings.environment != "production":
    Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"status": "ok", "service": "campus-guardian-api", "version": app.version}

@app.get("/ready")
def ready():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "ready", "database": "ok"}

prefix = "/api/v1"
app.include_router(public.router, prefix=prefix)
app.include_router(auth.router, prefix=prefix)
app.include_router(complaints.router, prefix=prefix)
app.include_router(announcements.router, prefix=prefix)
app.include_router(notifications.router, prefix=prefix)
app.include_router(push.router, prefix=prefix)
app.include_router(profile.router, prefix=prefix)
app.include_router(admin.router, prefix=prefix)
app.include_router(management.router, prefix=prefix)
