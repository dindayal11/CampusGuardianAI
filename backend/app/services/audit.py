from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models import AuditLog

def now_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S%z")

def log_audit(db: Session, institute_id: int | None, actor_user_id: str | None,
              actor_role: str | None, action: str, entity_type: str | None = None,
              entity_id: str | None = None, details: str | None = None) -> None:
    db.add(AuditLog(
        institute_id=institute_id,
        actor_user_id=actor_user_id,
        actor_role=actor_role,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        created_at=now_text(),
    ))
