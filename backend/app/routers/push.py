
import json
import logging
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.dependencies import Principal, get_current_principal
from app.db import get_db
from app.models import PushSubscription
from app.services.audit import now_text

router = APIRouter(prefix="/push", tags=["Browser Push"])
logger = logging.getLogger(__name__)


class PushSubscriptionKeys(BaseModel):
    p256dh: str = Field(min_length=1, max_length=500)
    auth: str = Field(min_length=1, max_length=500)


class PushSubscriptionPayload(BaseModel):
    endpoint: str = Field(min_length=1, max_length=4096)
    keys: PushSubscriptionKeys


def validate_endpoint(endpoint: str) -> None:
    parsed = urlparse(endpoint)
    if parsed.scheme != "https" or not parsed.hostname:
        raise HTTPException(status_code=422, detail="Invalid push endpoint.")


@router.get("/public-key")
def get_public_key():
    settings = get_settings()
    if not settings.vapid_public_key:
        raise HTTPException(
            status_code=503,
            detail="Browser push notifications are not configured.",
        )
    return {"publicKey": settings.vapid_public_key}


@router.post("/subscribe")
def subscribe(
    payload: PushSubscriptionPayload,
    principal: Principal = Depends(get_current_principal),
    db: Session = Depends(get_db),
):
    if principal.institute_id is None:
        raise HTTPException(
            status_code=400,
            detail="An institute is required for browser push notifications.",
        )

    validate_endpoint(payload.endpoint)

    row = (
        db.query(PushSubscription)
        .filter(PushSubscription.endpoint == payload.endpoint)
        .first()
    )

    now = now_text()

    if row is not None:
        # A browser endpoint can belong to only one currently authenticated account.
        row.institute_id = principal.institute_id
        row.user_id = principal.subject
        row.p256dh = payload.keys.p256dh
        row.auth = payload.keys.auth
        row.is_active = 1
        row.updated_at = now
    else:
        row = PushSubscription(
            institute_id=principal.institute_id,
            user_id=principal.subject,
            endpoint=payload.endpoint,
            p256dh=payload.keys.p256dh,
            auth=payload.keys.auth,
            is_active=1,
            created_at=now,
            updated_at=now,
        )
        db.add(row)

    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Could not save browser push subscription")
        raise HTTPException(
            status_code=500,
            detail="Could not save push subscription.",
        )

    return {"success": True}


@router.post("/unsubscribe")
def unsubscribe(
    payload: PushSubscriptionPayload,
    principal: Principal = Depends(get_current_principal),
    db: Session = Depends(get_db),
):
    if principal.institute_id is None:
        raise HTTPException(status_code=400, detail="An institute is required.")

    row = (
        db.query(PushSubscription)
        .filter(
            PushSubscription.endpoint == payload.endpoint,
            PushSubscription.institute_id == principal.institute_id,
            PushSubscription.user_id == principal.subject,
        )
        .first()
    )

    if row is not None:
        row.is_active = 0
        row.updated_at = now_text()
        db.commit()

    return {"success": True}
