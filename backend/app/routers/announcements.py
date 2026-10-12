import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.dependencies import (
    Principal,
    get_current_principal,
    require_roles,
)
from app.db import get_db
from app.models import Announcement, AnnouncementRead, Notification, User
from app.schemas import AnnouncementCreate, AnnouncementOut
from app.services.audit import log_audit, now_text
from app.services.push import send_push_to_user
from app.routers.notifications import add_notification

router = APIRouter(prefix="/announcements", tags=["Announcements"])
logger = logging.getLogger(__name__)


def visible_announcements_query(principal: Principal, db: Session):
    query = db.query(Announcement).filter(
        Announcement.is_active == 1
    )

    if principal.institute_id is None:
        return query

    query = query.filter(
        Announcement.institute_id == principal.institute_id
    )

    # Students see announcements intended for everyone or students.
    if principal.role == "Student":
        query = query.filter(
            Announcement.audience.in_(["All", "Students"])
        )

    # Institute admins can see all announcements for their institute,
    # regardless of the selected audience.
    return query



@router.get("", response_model=list[AnnouncementOut])
def list_announcements(
    principal: Principal = Depends(get_current_principal),
    db: Session = Depends(get_db),
):
    rows = (
        visible_announcements_query(principal, db)
        .order_by(Announcement.id.desc())
        .limit(100)
        .all()
    )

    return [
        AnnouncementOut(
            id=x.id,
            title=x.title,
            message=x.message,
            audience=x.audience,
            priority=x.priority,
            created_at=x.created_at,
            expires_at=x.expires_at,
        )
        for x in rows
    ]


@router.get("/unread-count")
def announcement_unread_count(
    principal: Principal = Depends(get_current_principal),
    db: Session = Depends(get_db),
):
    if principal.role != "Student" or principal.institute_id is None:
        return {"unread": 0}

    read_exists = (
        db.query(AnnouncementRead.id)
        .filter(
            AnnouncementRead.announcement_id == Announcement.id,
            AnnouncementRead.institute_id == principal.institute_id,
            AnnouncementRead.user_id == principal.subject,
        )
        .exists()
    )

    count = (
        db.query(func.count(Announcement.id))
        .filter(
            Announcement.institute_id == principal.institute_id,
            Announcement.is_active == 1,
            (Announcement.audience == "All")
            | (Announcement.audience == "Students"),
            ~read_exists,
        )
        .scalar()
    )

    return {"unread": int(count or 0)}



@router.post("/{announcement_id}/read")
def mark_announcement_as_read(
    announcement_id: int,
    principal: Principal = Depends(get_current_principal),
    db: Session = Depends(get_db),
):
    # Only students can mark student-visible announcements as read.
    if principal.role != "Student" or principal.institute_id is None:
        raise HTTPException(
            status_code=403,
            detail="Only students can mark announcements as read.",
        )

    # Ensure the announcement belongs to the student's institute,
    # is active, and is intended for students or everyone.
    announcement = (
        db.query(Announcement)
        .filter(
            Announcement.id == announcement_id,
            Announcement.institute_id == principal.institute_id,
            Announcement.is_active == 1,
            Announcement.audience.in_(["All", "Students"]),
        )
        .first()
    )

    if announcement is None:
        raise HTTPException(
            status_code=404,
            detail="Announcement not found.",
        )

    # The unique constraint prevents duplicate read records.
    existing_read = (
        db.query(AnnouncementRead)
        .filter(
            AnnouncementRead.announcement_id == announcement_id,
            AnnouncementRead.user_id == principal.subject,
        )
        .first()
    )

    if existing_read is not None:
        return {"success": True, "already_read": True}

    read_record = AnnouncementRead(
        announcement_id=announcement_id,
        institute_id=principal.institute_id,
        user_id=principal.subject,
        read_at=now_text(),
    )

    try:
        db.add(read_record)
        db.commit()
    except Exception:
        db.rollback()

        # Handle a simultaneous duplicate request safely.
        existing_read = (
            db.query(AnnouncementRead)
            .filter(
                AnnouncementRead.announcement_id == announcement_id,
                AnnouncementRead.user_id == principal.subject,
            )
            .first()
        )

        if existing_read is not None:
            return {"success": True, "already_read": True}

        logger.exception("Failed to mark announcement as read.")
        raise HTTPException(
            status_code=500,
            detail="Could not mark announcement as read.",
        )

    return {"success": True, "already_read": False}



@router.post("", response_model=AnnouncementOut, status_code=201)
def create_announcement(
    payload: AnnouncementCreate,
    principal: Principal = Depends(require_roles("Institute Admin")),
    db: Session = Depends(get_db),
):
    if principal.institute_id is None:
        raise HTTPException(
            status_code=400,
            detail="An institute is required to publish announcements.",
        )

    now = now_text()
    row = Announcement(
        institute_id=principal.institute_id,
        title=payload.title.strip(),
        message=payload.message.strip(),
        audience=payload.audience,
        priority=payload.priority,
        created_by=principal.subject,
        expires_at=payload.expires_at,
        is_active=1,
        created_at=now,
    )

    try:
        db.add(row)
        db.flush()

        query = db.query(User).filter(
            User.institute_id == principal.institute_id,
            User.status == "Active",
        )

        if payload.audience == "Students":
            query = query.filter(User.role == "Student")
        elif payload.audience == "Institute Admins":
            query = query.filter(User.role == "Institute Admin")

        recipient_ids = [user.user_id for user in query.all()]

        # Preserve existing in-app notifications.
        for user_id in recipient_ids:
            add_notification(
                db,
                institute_id=principal.institute_id,
                user_id=user_id,
                notification_type="System Alert",
                title=row.title,
                message=row.message,
            )

        log_audit(
            db,
            principal.institute_id,
            principal.subject,
            principal.role,
            "Announcement Published",
            "Announcement",
            str(row.id),
        )

        # Commit the announcement and in-app notifications first.
        db.commit()
        db.refresh(row)

    except Exception:
        db.rollback()
        logger.exception("Failed to publish announcement.")
        raise HTTPException(
            status_code=500,
            detail="Could not publish the announcement.",
        )

    # Push delivery is best-effort and must not undo a published announcement.
    for user_id in recipient_ids:
        try:
            send_push_to_user(
                db=db,
                institute_id=principal.institute_id,
                user_id=user_id,
                title="New institute announcement",
                body="A new announcement is available. Open Campus Guardian AI to view it.",
                url="/dashboard/announcements",
            )
        except Exception:
            db.rollback()
            logger.exception(
                "Push delivery failed for an announcement recipient."
            )

    return AnnouncementOut(
        id=row.id,
        title=row.title,
        message=row.message,
        audience=row.audience,
        priority=row.priority,
        created_at=row.created_at,
        expires_at=row.expires_at,
    )


@router.delete("/{announcement_id}")
def delete_announcement(
    announcement_id: int,
    principal: Principal = Depends(require_roles("Institute Admin")),
    db: Session = Depends(get_db),
):
    row = (
        db.query(Announcement)
        .filter(
            Announcement.id == announcement_id,
            Announcement.institute_id == principal.institute_id,
        )
        .first()
    )

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Announcement not found.",
        )

    db.query(Notification).filter(
        Notification.institute_id == principal.institute_id,
        Notification.notification_type == "System Alert",
        Notification.title == row.title,
        Notification.message == row.message,
    ).delete(synchronize_session=False)

    db.delete(row)

    log_audit(
        db,
        principal.institute_id,
        principal.subject,
        principal.role,
        "Announcement Deleted",
        "Announcement",
        str(announcement_id),
    )

    db.commit()
    return {"success": True}
