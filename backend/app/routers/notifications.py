from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import Principal, get_current_principal
from app.db import get_db
from app.models import Notification, NotificationPreference
from app.schemas import NotificationPreferenceUpdate
from app.services.audit import now_text

router = APIRouter(prefix="/notifications", tags=["Notifications"])


def add_notification(db: Session, *, institute_id: int | None, user_id: str, notification_type: str, title: str, message: str, complaint_id: str | None = None, priority: str | None = None) -> Notification | None:
    """Create an in-app notification only when the user's preference permits it."""
    if institute_id is None:
        return None
    pref = db.query(NotificationPreference).filter(
        NotificationPreference.institute_id == institute_id, NotificationPreference.user_id == user_id
    ).first()
    if pref is None:
        pref = NotificationPreference(
            institute_id=institute_id, user_id=user_id, in_app_enabled=1, complaint_updates=1,
            priority_alerts=1, admin_alerts=1, created_at=now_text(), updated_at=now_text()
        )
        db.add(pref); db.flush()
    if not pref.in_app_enabled:
        return None
    if notification_type in {"Complaint Update", "Duplicate Alert"} and not pref.complaint_updates:
        return None
    if notification_type in {"New Complaint", "SLA Escalation"} and not pref.priority_alerts:
        return None
    if notification_type in {"System Alert", "Admin Alert"} and not pref.admin_alerts:
        return None
    row = Notification(
        institute_id=institute_id, user_id=user_id, complaint_id=complaint_id,
        notification_type=notification_type, title=title, message=message, created_at=now_text()
    )
    db.add(row)
    return row

def preference_for(db: Session, principal: Principal) -> NotificationPreference:
    if principal.institute_id is None:
        raise HTTPException(status_code=400, detail="Notification preferences are not available for this account.")
    row = db.query(NotificationPreference).filter(
        NotificationPreference.institute_id == principal.institute_id,
        NotificationPreference.user_id == principal.subject,
    ).first()
    if not row:
        row = NotificationPreference(
            institute_id=principal.institute_id, user_id=principal.subject,
            in_app_enabled=1, complaint_updates=1, priority_alerts=1, admin_alerts=1,
            created_at=now_text(), updated_at=now_text(),
        )
        db.add(row); db.flush()
    return row

@router.get("")
def notifications(principal: Principal = Depends(get_current_principal), db: Session = Depends(get_db)):
    rows = db.query(Notification).filter(Notification.user_id == principal.subject).order_by(Notification.id.desc()).limit(100).all()
    unread = sum(1 for x in rows if not x.is_read)
    return {"items":[{"id":x.id,"complaint_id":x.complaint_id,"notification_type":x.notification_type,
             "title":x.title,"message":x.message,"is_read":bool(x.is_read),"created_at":x.created_at} for x in rows],
            "unread": unread}

@router.get("/preferences")
def get_preferences(principal: Principal = Depends(get_current_principal), db: Session = Depends(get_db)):
    row = preference_for(db, principal)
    db.commit()
    return {
        "in_app_enabled": bool(row.in_app_enabled),
        "complaint_updates": bool(row.complaint_updates),
        "priority_alerts": bool(row.priority_alerts),
        "admin_alerts": bool(row.admin_alerts),
    }

@router.patch("/preferences")
def update_preferences(payload: NotificationPreferenceUpdate, principal: Principal = Depends(get_current_principal), db: Session = Depends(get_db)):
    row = preference_for(db, principal)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, key, int(value))
    row.updated_at = now_text()
    db.commit()
    return {"success": True, "in_app_enabled": bool(row.in_app_enabled), "complaint_updates": bool(row.complaint_updates),
            "priority_alerts": bool(row.priority_alerts), "admin_alerts": bool(row.admin_alerts)}

@router.patch("/read-all")
def mark_all_read(principal: Principal = Depends(get_current_principal), db: Session = Depends(get_db)) -> dict:
    q = db.query(Notification).filter(Notification.user_id == principal.subject, Notification.is_read == 0)
    count = q.update({"is_read": 1}, synchronize_session=False)
    db.commit()
    return {"success": True, "updated": count}


@router.patch("/{notification_id}/read")
def mark_read(notification_id: int, principal: Principal = Depends(get_current_principal), db: Session = Depends(get_db)) -> dict:
    row = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == principal.subject).first()
    if not row:
        raise HTTPException(status_code=404, detail="Notification not found.")
    row.is_read = 1
    db.commit()
    return {"success": True}

