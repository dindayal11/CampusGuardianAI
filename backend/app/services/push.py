
import json
import requests
import logging
from urllib.parse import urlparse

from pywebpush import WebPushException, webpush
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import PushSubscription
from app.services.audit import now_text

logger = logging.getLogger(__name__)


def send_push_to_user(
    db: Session,
    institute_id: int,
    user_id: str,
    title: str,
    body: str,
    url: str = "/dashboard/notifications",
) -> int:
    """Send browser push notifications to a user's active subscriptions.

    Call after the related business transaction has committed.
    Returns the number of successful push submissions.
    """
    settings = get_settings()

    if not settings.vapid_public_key or not settings.vapid_private_key:
        logger.warning("Browser push is not configured; skipping delivery.")
        return 0

    subscriptions = (
        db.query(PushSubscription)
        .filter(
            PushSubscription.institute_id == institute_id,
            PushSubscription.user_id == user_id,
            PushSubscription.is_active == 1,
        )
        .all()
    )

    if not subscriptions:
        logger.info("No active push subscriptions for recipient.")
        return 0

    safe_url = (
        url
        if isinstance(url, str)
        and url.startswith("/")
        and not url.startswith("//")
        else "/dashboard/notifications"
    )

    payload = json.dumps(
        {
            "title": title[:120],
            "body": body[:240],
            "url": safe_url,
        }
    )

    sent = 0
    expired_found = False

    for subscription in subscriptions:
        try:
            endpoint_host = (
                urlparse(subscription.endpoint).hostname or ""
            ).lower()

            push_headers = {}

            # Conditional WNS headers; other push services use defaults.
            if endpoint_host.endswith(".notify.windows.com"):
                push_headers = {
                    "X-WNS-Type": "wns/raw",
                    "Content-Type": "application/octet-stream",
                }

            webpush(
                subscription_info={
                    "endpoint": subscription.endpoint,
                    "keys": {
                        "p256dh": subscription.p256dh,
                        "auth": subscription.auth,
                    },
                },
                data=payload,
                vapid_private_key=settings.vapid_private_key,
                vapid_claims={
                    "sub": settings.vapid_claims_email,
                },
                headers=push_headers,
                timeout=10,
            )

            sent += 1
            
        
        
        except requests.exceptions.Timeout:
            logger.warning(
                "Browser push timed out; complaint operation "
                "should remain successful."
            )
            continue    

        except WebPushException as exc:
            response = getattr(exc, "response", None)
            status_code = getattr(response, "status_code", None)
            response_text = getattr(response, "text", "") or ""
            response_reason = getattr(response, "reason", "") or ""

            # Never log endpoint URLs, subscription keys, or VAPID secrets.
            logger.warning(
                "Browser push failed: status=%s reason=%s body=%r exception=%r",
                status_code or "unknown",
                response_reason[:200],
                response_text[:500],
                str(exc)[:500],
            )

            if status_code in (404, 410):
                subscription.is_active = 0
                subscription.updated_at = now_text()
                expired_found = True

        except Exception:
            logger.exception("Unexpected browser push delivery failure.")

    if expired_found:
        try:
            db.commit()
        except Exception:
            db.rollback()
            logger.exception(
                "Could not save expired push subscription updates."
            )

    return sent
