
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.dependencies import Principal, get_current_principal
from app.db import get_db
from app.models import Institute, PlatformAdmin, User, UserProfile
from app.services.audit import log_audit, now_text


router = APIRouter(prefix="/profile", tags=["Profile"])

UPLOAD_ROOT = Path(__file__).resolve().parents[2] / "storage" / "profile_photos"
MAX_UPLOAD_BYTES = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png"}

SIGNATURES = {
    ".jpg": b"\xff\xd8\xff",
    ".jpeg": b"\xff\xd8\xff",
    ".png": b"\x89PNG\r\n\x1a\n",
}


class ProfileUpdate(BaseModel):
    # Retained for backward compatibility with existing API clients.
    phone: str = Field(default="", max_length=50)
    department: str = Field(default="", max_length=160)
    designation: str = Field(default="", max_length=160)
    address: str = Field(default="", max_length=2000)
    emergency_contact: str = Field(default="", max_length=100)
    bio: str = Field(default="", max_length=4000)

class InstituteDetailsUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    phone: str = Field(default="", max_length=50)

def get_own_profile(
    db: Session,
    principal: Principal,
) -> UserProfile | None:
    if principal.institute_id is None:
        return None

    return (
        db.query(UserProfile)
        .filter(
            UserProfile.institute_id == principal.institute_id,
            UserProfile.user_id == principal.subject,
        )
        .first()
    )


def get_or_create_own_profile(
    db: Session,
    principal: Principal,
) -> UserProfile:
    if principal.institute_id is None:
        raise HTTPException(
            status_code=400,
            detail="Institute scope is required.",
        )

    row = get_own_profile(db, principal)

    if row is None:
        row = UserProfile(
            institute_id=principal.institute_id,
            user_id=principal.subject,
            updated_at=now_text(),
        )
        db.add(row)
        db.flush()

    return row


@router.get("")
def get_profile(
    principal: Principal = Depends(get_current_principal),
    db: Session = Depends(get_db),
):
    if principal.role == "Platform Admin":
        account = (
            db.query(PlatformAdmin)
            .filter(PlatformAdmin.admin_id == principal.subject)
            .first()
        )

        if account is None:
            raise HTTPException(status_code=404, detail="Account not found.")

        return {
            "account_type": "Platform Admin",
            "user": {
                "name": account.name,
                "user_id": account.admin_id,
                "email": account.email,
                "institute_name": None,
            },
            "profile": {"photo_url": None},
        }

    account = (
        db.query(User)
        .filter(
            User.user_id == principal.subject,
            User.institute_id == principal.institute_id,
        )
        .first()
    )

    if account is None:
        raise HTTPException(status_code=404, detail="Account not found.")

    institute = (
        db.query(Institute)
        .filter(Institute.id == account.institute_id)
        .first()
        if account.institute_id is not None
        else None
    )

    row = get_own_profile(db, principal)

    return {
        "account_type": principal.role,
        "user": {
            "name": account.name,
            "user_id": account.user_id,
            "email": account.email,
            "institute_name": institute.name if institute else None,
        },
        "profile": {
            "photo_url": "/profile/photo" if row and row.photo_path else None,
        },
    }


@router.post("/photo")
async def upload_profile_photo(
    file: UploadFile = File(...),
    principal: Principal = Depends(get_current_principal),
    db: Session = Depends(get_db),
):
    if principal.role not in {"Student", "Institute Admin"}:
        raise HTTPException(
            status_code=403,
            detail="Profile photo upload is not enabled for this account.",
        )

    if principal.institute_id is None:
        raise HTTPException(
            status_code=400,
            detail="Institute scope is required.",
        )

    account = (
        db.query(User)
        .filter(
            User.user_id == principal.subject,
            User.institute_id == principal.institute_id,
        )
        .first()
    )

    if account is None:
        raise HTTPException(status_code=404, detail="Account not found.")

    extension = Path(file.filename or "").suffix.lower()
    content_type = (file.content_type or "").lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only JPG and PNG profile photos are allowed.",
        )

    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file must be a JPG or PNG image.",
        )

    contents = await file.read(MAX_UPLOAD_BYTES + 1)
    await file.close()

    if not contents:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail="Profile photo must be 5 MB or smaller.",
        )

    expected_signature = SIGNATURES[extension]

    if not contents.startswith(expected_signature):
        raise HTTPException(
            status_code=400,
            detail="The file content does not match its image type.",
        )

    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid4().hex}{extension}"
    destination = UPLOAD_ROOT / filename

    row = get_or_create_own_profile(db, principal)
    old_photo_path = row.photo_path

    try:
        destination.write_bytes(contents)

        # Store only the generated filename, never a user-supplied path.
        row.photo_path = filename
        row.updated_at = now_text()

        log_audit(
            db,
            principal.institute_id,
            principal.subject,
            principal.role,
            "Profile Photo Updated",
            "User",
            principal.subject,
        )

        db.commit()

    except Exception:
        db.rollback()

        if destination.exists():
            destination.unlink()

        raise HTTPException(
            status_code=500,
            detail="Could not save the profile photo.",
        )

    # Remove the previous photo only after the database commit succeeds.
    if old_photo_path and old_photo_path != filename:
        old_name = Path(old_photo_path).name

        if old_name == old_photo_path:
            old_destination = UPLOAD_ROOT / old_name

            try:
                if old_destination.is_file():
                    old_destination.unlink()
            except OSError:
                # A cleanup failure must not undo the successful upload.
                pass

    return {
        "success": True,
        "message": "Profile photo updated successfully.",
        "photo_url": "/profile/photo",
    }


@router.get("/photo")
def get_profile_photo(
    principal: Principal = Depends(get_current_principal),
    db: Session = Depends(get_db),
):
    if principal.role not in {"Student", "Institute Admin"}:
        raise HTTPException(
            status_code=403,
            detail="Profile photo access is not enabled for this account.",
        )

    row = get_own_profile(db, principal)

    if row is None or not row.photo_path:
        raise HTTPException(status_code=404, detail="No profile photo found.")

    # Accept only the generated filename; never resolve arbitrary paths.
    filename = row.photo_path

    if Path(filename).name != filename:
        raise HTTPException(status_code=404, detail="Profile photo not found.")

    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=404, detail="Profile photo not found.")

    photo_path = (UPLOAD_ROOT / filename).resolve()

    if photo_path.parent != UPLOAD_ROOT.resolve() or not photo_path.is_file():
        raise HTTPException(status_code=404, detail="Profile photo not found.")

    media_type = "image/png" if extension == ".png" else "image/jpeg"

    return FileResponse(
        path=photo_path,
        media_type=media_type,
        headers={
            "Cache-Control": "private, no-store",
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.put("")
def update_profile(
    payload: ProfileUpdate,
    principal: Principal = Depends(get_current_principal),
    db: Session = Depends(get_db),
):
    # Keep the existing endpoint for compatibility with older clients.
    if principal.role == "Platform Admin":
        raise HTTPException(
            status_code=403,
            detail="Platform Admin profile editing is not enabled.",
        )

    account = (
        db.query(User)
        .filter(
            User.user_id == principal.subject,
            User.institute_id == principal.institute_id,
        )
        .first()
    )

    if account is None:
        raise HTTPException(status_code=404, detail="Account not found.")

    row = get_or_create_own_profile(db, principal)

    row.phone = payload.phone.strip()
    row.department = payload.department.strip()
    row.designation = payload.designation.strip()
    row.address = payload.address.strip()
    row.emergency_contact = payload.emergency_contact.strip()
    row.bio = payload.bio.strip()
    row.updated_at = now_text()

    log_audit(
        db,
        principal.institute_id,
        principal.subject,
        principal.role,
        "Profile Updated",
        "User",
        principal.subject,
    )

    db.commit()

    return {"success": True}

@router.get("/institute")
def get_institute_details(
    principal: Principal = Depends(get_current_principal),
    db: Session = Depends(get_db),
):
    if principal.role != "Institute Admin":
        raise HTTPException(
            status_code=403,
            detail="Only Institute Admin can access institute details.",
        )

    if principal.institute_id is None:
        raise HTTPException(
            status_code=400,
            detail="Institute scope is required.",
        )

    institute = (
        db.query(Institute)
        .filter(Institute.id == principal.institute_id)
        .first()
    )

    if institute is None:
        raise HTTPException(status_code=404, detail="Institute not found.")

    return {
        "name": institute.name,
        "phone": institute.phone or "",
        "registration_date": institute.created_at,
    }


@router.put("/institute")
def update_institute_details(
    payload: InstituteDetailsUpdate,
    principal: Principal = Depends(get_current_principal),
    db: Session = Depends(get_db),
):
    if principal.role != "Institute Admin":
        raise HTTPException(
            status_code=403,
            detail="Only Institute Admin can update institute details.",
        )

    if principal.institute_id is None:
        raise HTTPException(
            status_code=400,
            detail="Institute scope is required.",
        )

    name = payload.name.strip()
    phone = payload.phone.strip()

    if not name:
        raise HTTPException(
            status_code=422,
            detail="Institute name cannot be empty.",
        )

    institute = (
        db.query(Institute)
        .filter(Institute.id == principal.institute_id)
        .first()
    )

    if institute is None:
        raise HTTPException(status_code=404, detail="Institute not found.")

    old_name = institute.name
    old_phone = institute.phone or ""

    try:
        institute.name = name
        institute.phone = phone or None

        log_audit(
            db,
            principal.institute_id,
            principal.subject,
            principal.role,
            "Institute Details Updated",
            "Institute",
            str(principal.institute_id),
        )

        db.commit()
        db.refresh(institute)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not save institute details.",
        )

    return {
        "success": True,
        "message": "Institute details updated successfully.",
        "name": institute.name,
        "phone": institute.phone or "",
        "registration_date": institute.created_at,
    }
