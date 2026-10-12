from dataclasses import dataclass
import jwt
from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.core.security import decode_access_token
from app.db import get_db

settings = get_settings()

@dataclass(frozen=True)
class Principal:
    subject: str
    role: str
    institute_id: int | None

def get_current_principal(
    access_token: str | None = Cookie(default=None, alias=settings.cookie_name),
    db: Session = Depends(get_db),
) -> Principal:
    if not access_token:
        raise HTTPException(status_code=401, detail="Authentication required.")
    try:
        payload = decode_access_token(access_token)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired session.")
    subject = payload.get("sub")
    role = payload.get("role")
    institute_id = payload.get("institute_id")
    if not subject or not role:
        raise HTTPException(status_code=401, detail="Invalid session.")
    if role == "Platform Admin":
        from app.models import PlatformAdmin
        account = db.query(PlatformAdmin).filter(PlatformAdmin.admin_id == subject).first()
    else:
        from app.models import User
        account = db.query(User).filter(User.user_id == subject).first()
    if not account or account.status != "Active":
        raise HTTPException(status_code=401, detail="Account is inactive or unavailable.")
    return Principal(subject, role, institute_id)

def require_roles(*roles: str):
    def dependency(principal: Principal = Depends(get_current_principal)) -> Principal:
        if principal.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions.")
        return principal
    return dependency
