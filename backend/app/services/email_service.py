
import logging
import smtplib
import ssl
from email.message import EmailMessage

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def send_institute_status_email(
    recipient: str,
    institute_name: str,
    status: str,
) -> None:
    settings = get_settings()

    if status not in {"Approved", "Rejected", "Blocked"}:
        return

    required = (
        settings.smtp_host,
        settings.smtp_username,
        settings.smtp_password,
        settings.smtp_from_email,
    )

    if not all(required):
        raise RuntimeError(
            "SMTP is not configured. Set SMTP_HOST, SMTP_USERNAME, "
            "SMTP_PASSWORD and SMTP_FROM_EMAIL in the backend .env file."
        )

    if not recipient or not recipient.strip():
        raise ValueError("Institute email address is missing.")

    subjects = {
        "Approved": "Your Institute Registration Has Been Approved",
        "Rejected": "Update on Your Institute Registration",
        "Blocked": "Your Institute Account Has Been Blocked",
    }

    messages = {
        "Approved": (
            f"Congratulations! The registration for {institute_name} "
            "has been approved by the Campus Guardian AI platform team. "
            "You can now sign in using your institute administrator account."
        ),
        "Rejected": (
            f"The registration for {institute_name} has been rejected "
            "by the Campus Guardian AI platform team. Please contact "
            "platform support if you need further information."
        ),
        "Blocked": (
            f"The account for {institute_name} has been blocked by the "
            "Campus Guardian AI platform team. Please contact platform "
            "support for assistance."
        ),
    }

    message = EmailMessage()
    message["Subject"] = subjects[status]
    message["From"] = settings.smtp_from_email
    message["To"] = recipient.strip()
    message.set_content(
        f"Hello {institute_name},\n\n"
        f"{messages[status]}\n\n"
        "Regards,\nCampus Guardian AI Team"
    )

    context = ssl.create_default_context()

    if settings.smtp_port == 465:
        with smtplib.SMTP_SSL(
            settings.smtp_host,
            settings.smtp_port,
            context=context,
            timeout=15,
        ) as server:
            server.login(
                settings.smtp_username,
                settings.smtp_password,
            )
            server.send_message(message)
    else:
        with smtplib.SMTP(
            settings.smtp_host,
            settings.smtp_port,
            timeout=15,
        ) as server:
            if settings.smtp_use_tls:
                server.starttls(context=context)

            server.login(
                settings.smtp_username,
                settings.smtp_password,
            )
            server.send_message(message)

    logger.info(
        "Institute status email submitted to SMTP for institute status %s",
        status,
    )
