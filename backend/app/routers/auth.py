from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.core.dependencies import Principal, get_current_principal
from app.core.security import create_access_token, hash_password, verify_password
from app.db import get_db
from app.models import Institute, PlatformAdmin, User
from app.schemas import AuthResponse, ChangePasswordRequest, LoginRequest, PlatformLoginRequest
from app.services.audit import log_audit

router = APIRouter(prefix="/auth", tags=["Authentication"])
settings = get_settings()

def set_session(response: Response, token: str) -> None:
    response.set_cookie(
        settings.cookie_name, token, httponly=True, secure=settings.cookie_secure,
        samesite="lax", max_age=settings.access_token_expire_minutes*60, path="/"
    )

def user_payload(db: Session, account: User) -> dict:
    institute = db.query(Institute).filter(Institute.id == account.institute_id).first() if account.institute_id else None
    return {"subject": account.user_id, "name": account.name, "role": account.role,
            "email": account.email, "institute_id": account.institute_id,
            "institute_code": institute.institute_code if institute else None}

@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> AuthResponse:
    account = db.query(User).filter(User.user_id == payload.user_id.strip()).first()
    if not account:
        raise HTTPException(status_code=401, detail="Invalid User ID or Password.")
    valid, upgrade = verify_password(payload.password, account.password)
    if not valid:
        log_audit(db, account.institute_id, account.user_id, account.role, "Login Failed", "User", account.user_id)
        db.commit()
        raise HTTPException(status_code=401, detail="Invalid User ID or Password.")
    if account.status != "Active":
        raise HTTPException(status_code=403, detail="Your account is not active.")
    if upgrade:
        account.password = hash_password(payload.password)
    account.last_login = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S%z")
    log_audit(db, account.institute_id, account.user_id, account.role, "Login", "User", account.user_id)
    db.commit()
    token = create_access_token(account.user_id, account.role, account.institute_id, settings.access_token_expire_minutes)
    set_session(response, token)
    return AuthResponse(user=user_payload(db, account))

@router.post("/platform-login", response_model=AuthResponse)
def platform_login(payload: PlatformLoginRequest, response: Response, db: Session = Depends(get_db)) -> AuthResponse:
    account = db.query(PlatformAdmin).filter(PlatformAdmin.email == payload.email).first()
    if not account:
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    valid, upgrade = verify_password(payload.password, account.password)
    if not valid:
        log_audit(db, None, account.admin_id, "Platform Admin", "Login Failed", "PlatformAdmin", account.admin_id)
        db.commit()
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    if account.status != "Active":
        raise HTTPException(status_code=403, detail="Platform admin account is inactive.")
    if upgrade:
        account.password = hash_password(payload.password)
    log_audit(db, None, account.admin_id, "Platform Admin", "Login", "PlatformAdmin", account.admin_id)
    db.commit()
    token = create_access_token(account.admin_id, "Platform Admin", None, settings.access_token_expire_minutes)
    set_session(response, token)
    return AuthResponse(user={"subject": account.admin_id, "name": account.name, "role": "Platform Admin", "email": account.email})

@router.post("/logout")
def logout(response: Response) -> dict:
    response.delete_cookie(settings.cookie_name, path="/")
    return {"success": True}

@router.get("/me", response_model=AuthResponse)
def me(principal: Principal = Depends(get_current_principal), db: Session = Depends(get_db)) -> AuthResponse:
    if principal.role == "Platform Admin":
        account = db.query(PlatformAdmin).filter(PlatformAdmin.admin_id == principal.subject).first()
        return AuthResponse(user={"subject": account.admin_id,"name": account.name,"role":"Platform Admin","email":account.email})
    account = db.query(User).filter(User.user_id == principal.subject).first()
    return AuthResponse(user=user_payload(db, account))

@router.post("/change-password")
def change_password(payload: ChangePasswordRequest, principal: Principal = Depends(get_current_principal), db: Session = Depends(get_db)) -> dict:
    if payload.new_password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="New passwords do not match.")
    if payload.current_password == payload.new_password:
        raise HTTPException(status_code=400, detail="New password must be different from the current password.")
    if principal.role == "Platform Admin":
        account = db.query(PlatformAdmin).filter(PlatformAdmin.admin_id == principal.subject).first()
        institute_id = None
    else:
        account = db.query(User).filter(User.user_id == principal.subject, User.institute_id == principal.institute_id).first()
        institute_id = principal.institute_id
    if not account:
        raise HTTPException(status_code=404, detail="Account not found.")
    valid, _ = verify_password(payload.current_password, account.password)
    if not valid:
        raise HTTPException(status_code=400, detail="Current password is incorrect.")
    account.password = hash_password(payload.new_password)
    log_audit(db, institute_id, principal.subject, principal.role, "Password Changed", "Account", principal.subject)
    db.commit()
    return {"success": True, "message": "Password changed successfully."}
