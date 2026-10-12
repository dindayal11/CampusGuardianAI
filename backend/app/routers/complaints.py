from fastapi.responses import FileResponse
from datetime import datetime, timezone, timedelta
import math
from pathlib import Path
from uuid import uuid4
from zoneinfo import ZoneInfo
import logging

from app.services.push import send_push_to_user

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Query,
)
from sqlalchemy.orm import Session

from app.core.dependencies import Principal, get_current_principal
from app.db import get_db
from app.models import (
    Complaint,
    ComplaintHistory,
    ComplaintWorkflow,
    User,
)
from app.schemas import (
    ComplaintCreate,
    ComplaintListOut,
    ComplaintOut,
    ComplaintStatusUpdate,
    ComplaintDetailOut,
    WorkflowOut,
    ComplaintHistoryOut,
    ComplaintFeedbackCreate,
)
from app.services.ai import (
    analyze_complaint_hybrid,
    find_similar_complaints,
)
from app.services.audit import log_audit, now_text
from app.routers.notifications import add_notification


router = APIRouter(prefix="/complaints", tags=["Complaints"])
logger = logging.getLogger(__name__)

UPLOAD_ROOT = Path(__file__).resolve().parents[2] / "storage" / "complaints"
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


# ---------------------------------------------------------
# SERIALIZATION
# ---------------------------------------------------------

def serialize(row: Complaint, reveal_student: bool) -> dict:
    return {
        "id": row.id,
        "complaint_id": row.complaint_id,
        "title": row.title,
        "description": row.description,
        "location": row.location,
        "category": row.category,
        "priority": row.priority,
        "anonymous": bool(row.anonymous),
        "status": row.status,
        "created_at": row.created_at,
        "department": row.department,
        "student_id": (
            row.student_id
            if reveal_student and not row.anonymous
            else None
        ),
        "image_path": (
    f"/complaints/{row.complaint_id}/attachment"
    if row.image_path
    else None
),
        "risk_score": {
            "Low": 25,
            "Medium": 50,
            "High": 75,
            "Critical": 95,
        }.get(row.priority or ""),
        "recommended_action": {
            "Low": "Monitor the issue and schedule maintenance if required.",
            "Medium": "Assign the responsible department and resolve the issue soon.",
            "High": (
                "Immediate inspection is recommended. "
                "Take preventive safety measures."
            ),
            "Critical": (
                "Immediate action required. Secure the area "
                "and notify responsible authorities."
            ),
        }.get(row.priority or ""),
    }


# ---------------------------------------------------------
# ACCESS CONTROL
# ---------------------------------------------------------

def scoped_complaint(
    db: Session,
    complaint_id: str,
    principal: Principal,
) -> Complaint:
    row = (
        db.query(Complaint)
        .filter(Complaint.complaint_id == complaint_id)
        .first()
    )

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found.",
        )

    if principal.role == "Student":
        if (
            row.institute_id != principal.institute_id
            or row.student_id != principal.subject
        ):
            raise HTTPException(
                status_code=404,
                detail="Complaint not found.",
            )

    elif principal.role == "Institute Admin":
        if row.institute_id != principal.institute_id:
            raise HTTPException(
                status_code=404,
                detail="Complaint not found.",
            )

    elif principal.role != "Platform Admin":
        raise HTTPException(
            status_code=403,
            detail="Unsupported role.",
        )

    return row


# ---------------------------------------------------------
# SLA AND WORKFLOW HELPERS
# ---------------------------------------------------------

def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None

    formats = (
        "%Y-%m-%d %H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S",
    )

    for fmt in formats:
        try:
            parsed = datetime.strptime(value, fmt)

            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)

            return parsed

        except ValueError:
            continue

    return None


def default_sla(priority: str | None) -> int:
    return {
        "Critical": 4,
        "High": 12,
        "Medium": 48,
        "Low": 72,
    }.get(priority or "", 48)



def workflow_snapshot(
    wf: ComplaintWorkflow,
    status: str | None = None,
) -> tuple[bool, float | None]:
    # Resolved and rejected complaints no longer have an active SLA timer.
    if status in {"Resolved", "Rejected"}:
        return False, None

    due = parse_time(wf.due_at)

    if not due:
        return False, None

    remaining = (
        due - datetime.now(timezone.utc)
    ).total_seconds() / 3600

    return remaining < 0, round(remaining, 1)
    due = parse_time(wf.due_at)

    if not due:
        return False, None

    remaining = (
        due - datetime.now(timezone.utc)
    ).total_seconds() / 3600

    return remaining < 0, round(remaining, 1)


def sync_sla_escalation(
    db: Session,
    row: Complaint,
    wf: ComplaintWorkflow,
) -> bool:
    if row.status in {"Resolved", "Rejected"} or not wf.due_at:
        return False

    due = parse_time(wf.due_at)

    if not due or datetime.now(timezone.utc) <= due:
        return False

    overdue_hours = max(
        0,
        (
            datetime.now(timezone.utc) - due
        ).total_seconds() / 3600,
    )

    target = min(
        3,
        max(
            1,
            math.floor(
                overdue_hours / max(1, wf.sla_hours or 48)
            ) + 1,
        ),
    )

    if target <= (wf.escalation_level or 0):
        return False

    old_level = wf.escalation_level or 0
    wf.escalation_level = target
    wf.updated_at = now_text()

    db.add(
        ComplaintHistory(
            institute_id=row.institute_id,
            complaint_id=row.complaint_id,
            actor_user_id="SYSTEM",
            action="SLA Escalated",
            old_value=str(old_level),
            new_value=str(target),
            note=(
                "Complaint exceeded SLA by "
                f"{round(overdue_hours, 1)} hour(s)."
            ),
            created_at=now_text(),
        )
    )

    admins = (
        db.query(User)
        .filter(
            User.institute_id == row.institute_id,
            User.role == "Institute Admin",
            User.status == "Active",
        )
        .all()
    )

    for admin in admins:
        add_notification(
            db,
            institute_id=row.institute_id,
            user_id=admin.user_id,
            complaint_id=row.complaint_id,
            notification_type="SLA Escalation",
            title=f"SLA escalation: {row.priority or 'Complaint'}",
            message=(
                f"{row.complaint_id} is overdue and has reached "
                f"escalation level {target}."
            ),
        )

    return True


def workflow_for(
    db: Session,
    complaint_id: str,
) -> ComplaintWorkflow:
    wf = (
        db.query(ComplaintWorkflow)
        .filter(
            ComplaintWorkflow.complaint_id == complaint_id
        )
        .first()
    )

    if not wf:
        now = now_text()

        wf = ComplaintWorkflow(
            complaint_id=complaint_id,
            sla_hours=48,
            updated_at=now,
        )

        db.add(wf)
        db.flush()

    return wf


# ---------------------------------------------------------
# LIST COMPLAINTS
# ---------------------------------------------------------

@router.get("", response_model=ComplaintListOut)
def list_complaints(
    principal: Principal = Depends(get_current_principal),
    db: Session = Depends(get_db),
    status: str | None = Query(default=None),
    priority: str | None = Query(default=None),
    department: str | None = Query(default=None),
):
    query = db.query(Complaint)

    if principal.role == "Student":
        query = query.filter(
            Complaint.institute_id == principal.institute_id,
            Complaint.student_id == principal.subject,
        )
        reveal_student = False

    elif principal.role == "Institute Admin":
        query = query.filter(
            Complaint.institute_id == principal.institute_id,
        )
        reveal_student = True

    elif principal.role == "Platform Admin":
        reveal_student = True

    else:
        raise HTTPException(
            status_code=403,
            detail="Unsupported role.",
        )

    if status:
        query = query.filter(Complaint.status == status)

    if priority:
        query = query.filter(Complaint.priority == priority)

    if department:
        query = query.filter(Complaint.department == department)

    rows = query.order_by(Complaint.id.desc()).all()

    return {
        "items": [
            ComplaintOut(
                **serialize(row, reveal_student)
            )
            for row in rows
        ],
        "total": len(rows),
    }


# ---------------------------------------------------------
# CREATE COMPLAINT
# ---------------------------------------------------------

@router.post(
    "",
    response_model=ComplaintOut,
    status_code=201,
)
def create_complaint(
    payload: ComplaintCreate,
    principal: Principal = Depends(get_current_principal),
    db: Session = Depends(get_db),
):
    if principal.role != "Student":
        raise HTTPException(
            status_code=403,
            detail="Only students can submit complaints.",
        )
        
    
    # Daily complaint limit: maximum 5 per student, based on IST.
    ist = ZoneInfo("Asia/Kolkata")
    now_ist = datetime.now(ist)
    start_ist = now_ist.replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    end_ist = start_ist + timedelta(days=1)

    start_utc = start_ist.astimezone(timezone.utc)
    end_utc = end_ist.astimezone(timezone.utc)

    student_complaints = (
        db.query(Complaint.created_at)
        .filter(
            Complaint.institute_id == principal.institute_id,
            Complaint.student_id == principal.subject,
        )
        .all()
    )

    todays_count = 0

    for (created_at,) in student_complaints:
        parsed = parse_time(created_at)
        if parsed and start_utc <= parsed < end_utc:
            todays_count += 1

    if todays_count >= 5:
        raise HTTPException(
            status_code=429,
            detail=(
                "Daily complaint limit reached. "
                "You can submit a maximum of 5 complaints per day. "
                "Please try again tomorrow."
            ),
        )
    

    existing_rows = (
        db.query(Complaint)
        .filter(
            Complaint.institute_id == principal.institute_id
        )
        .order_by(Complaint.id.desc())
        .limit(500)
        .all()
    )

    existing = [
        {
            "complaint_id": item.complaint_id,
            "title": item.title,
            "description": item.description,
        }
        for item in existing_rows
    ]

    # AI analysis with local rule-based fallback.
    ai_result = analyze_complaint_hybrid(
        payload.title,
        payload.description,
    )

    category = ai_result["category"]
    priority = ai_result["priority"]

    # Detect similar complaints within the same institute.
    duplicate = find_similar_complaints(
        payload.title,
        payload.description,
        existing,
    )

    # Raise priority when many similar reports exist.
    if duplicate["similar_count"] >= 5:
        priority = {
            "Low": "Medium",
            "Medium": "High",
            "High": "Critical",
        }.get(priority, priority)

    row = Complaint(
        institute_id=principal.institute_id,
        student_id=principal.subject,
        title=payload.title.strip(),
        description=payload.description.strip(),
        location=payload.location.strip(),
        category=category,
        priority=priority,
        anonymous=int(payload.anonymous),
        status="Pending",
        created_at=now_text(),
        department=ai_result["department"],
    )

    # Collect permitted push notifications and send them only after commit.
    push_targets: list[tuple[str, str, str]] = []
    try:
        db.add(row)
        db.flush()

        # Use the database-generated ID to create a unique complaint ID.
        row.complaint_id = (
            f"CG-{datetime.now(timezone.utc).year}-{row.id:04d}"
        )
        db.flush()

        sla_hours = default_sla(priority)
        due_at = (
            datetime.now(timezone.utc)
            + timedelta(hours=sla_hours)
        )

        db.add(
            ComplaintWorkflow(
                complaint_id=row.complaint_id,
                sla_hours=sla_hours,
                due_at=due_at.strftime(
                    "%Y-%m-%d %H:%M:%S%z"
                ),
                updated_at=now_text(),
            )
        )

        student_notification = add_notification(
            db,
            institute_id=principal.institute_id,
            user_id=principal.subject,
            complaint_id=row.complaint_id,
            notification_type="Complaint Update",
            title="Complaint submitted",
            message="Your complaint was submitted successfully.",
        )
        if student_notification is not None:
            push_targets.append((
                principal.subject,
                "Complaint submitted",
                "Your complaint was submitted successfully.",
            ))

        if duplicate["is_duplicate"]:
            duplicate_notification = add_notification(
                db,
                institute_id=principal.institute_id,
                user_id=principal.subject,
                complaint_id=row.complaint_id,
                notification_type="Duplicate Alert",
                title="Similar complaint detected",
                message=(
                    "Your report is highly similar to an existing "
                    f"complaint ({duplicate['similarity_score']}%)."
                ),
            )
            if duplicate_notification is not None:
                push_targets.append((
                    principal.subject,
                    "Similar complaint detected",
                    "Your report is similar to an existing complaint.",
                ))

        admins = (
            db.query(User)
            .filter(
                User.institute_id == principal.institute_id,
                User.role == "Institute Admin",
                User.status == "Active",
            )
            .all()
        )

        for admin in admins:
            admin_notification = add_notification(
                db,
                institute_id=principal.institute_id,
                user_id=admin.user_id,
                complaint_id=row.complaint_id,
                notification_type="New Complaint",
                title=f"New {priority} complaint",
                message=row.title,
                priority=priority,
            )
            if admin_notification is not None:
                push_targets.append((
                    admin.user_id,
                    f"New {priority} complaint",
                    "A new complaint requires institute review.",
                ))

        db.add(
            ComplaintHistory(
                institute_id=principal.institute_id,
                complaint_id=row.complaint_id,
                actor_user_id=principal.subject,
                action="Created",
                note="Complaint submitted.",
                created_at=now_text(),
            )
        )

        log_audit(
            db,
            principal.institute_id,
            principal.subject,
            principal.role,
            "Complaint Created",
            "Complaint",
            row.complaint_id,
        )

        db.commit()
        db.refresh(row)

    except Exception:
        db.rollback()
        raise

    # Push is best-effort after commit; delivery failure must not undo the complaint.
    for user_id, title, body in push_targets:
        try:
            send_push_to_user(
                db=db,
                institute_id=principal.institute_id,
                user_id=user_id,
                title=title,
                body=body,
                url="/dashboard/complaints",
            )
        except Exception:
            logger.exception("Push delivery failed after complaint submission.")

    # Return AI analysis and safe duplicate metadata.
    # Do not return other students' complaint titles.
    response_data = serialize(row, False)
    response_data["ai_analysis"] = ai_result.get("ai_analysis")
    response_data["duplicate_analysis"] = {
        "is_duplicate": duplicate["is_duplicate"],
        "similarity_score": duplicate["similarity_score"],
        "similar_count": duplicate["similar_count"],
        "impact_level": duplicate["impact_level"],
    }

    return ComplaintOut(**response_data)


# ---------------------------------------------------------
# GET ONE COMPLAINT
# ---------------------------------------------------------

@router.get(
    "/{complaint_id}",
    response_model=ComplaintOut,
)
def get_complaint(
    complaint_id: str,
    principal: Principal = Depends(get_current_principal),
    db: Session = Depends(get_db),
):
    row = scoped_complaint(
        db,
        complaint_id,
        principal,
    )

    return ComplaintOut(
        **serialize(
            row,
            principal.role != "Student",
        )
    )


# ---------------------------------------------------------
# COMPLAINT DETAIL, HISTORY, WORKFLOW AND DUPLICATES
# ---------------------------------------------------------

@router.get(
    "/{complaint_id}/detail",
    response_model=ComplaintDetailOut,
)
def get_complaint_detail(
    complaint_id: str,
    principal: Principal = Depends(get_current_principal),
    db: Session = Depends(get_db),
):
    row = scoped_complaint(
        db,
        complaint_id,
        principal,
    )

    wf = workflow_for(db, complaint_id)
    sync_sla_escalation(db, row, wf)

    history = (
        db.query(ComplaintHistory)
        .filter(
            ComplaintHistory.complaint_id == complaint_id
        )
        .order_by(ComplaintHistory.id.asc())
        .all()
    )

    duplicate = None

    # Duplicate details are available only to institute administrators.
    if principal.role == "Institute Admin" and row.description:
        peers = (
            db.query(Complaint)
            .filter(
                Complaint.institute_id == row.institute_id,
                Complaint.id != row.id,
            )
            .order_by(Complaint.id.desc())
            .limit(500)
            .all()
        )

        duplicate = find_similar_complaints(
            row.title,
            row.description,
            [
                {
                    "complaint_id": peer.complaint_id,
                    "title": peer.title,
                    "description": peer.description,
                }
                for peer in peers
            ],
        )

    return ComplaintDetailOut(
        complaint=ComplaintOut(
            **serialize(
                row,
                principal.role != "Student",
            )
        ),
        workflow=WorkflowOut(
            assigned_to=wf.assigned_to,
            sla_hours=wf.sla_hours,
            due_at=wf.due_at,
            escalation_level=wf.escalation_level,
            resolution_notes=wf.resolution_notes,
            resolved_at=wf.resolved_at,
            feedback_rating=wf.feedback_rating,
            feedback_comment=wf.feedback_comment,
            feedback_at=wf.feedback_at,
            is_overdue=workflow_snapshot(wf, row.status)[0],
            remaining_hours=workflow_snapshot(wf, row.status)[1],
        ),
        history=[
            ComplaintHistoryOut(
                id=item.id,
                action=item.action,
                actor_user_id=item.actor_user_id,
                old_value=item.old_value,
                new_value=item.new_value,
                note=item.note,
                created_at=item.created_at,
            )
            for item in history
        ],
        duplicate=duplicate,
    )


# ---------------------------------------------------------
# UPDATE COMPLAINT STATUS AND WORKFLOW
# ---------------------------------------------------------

@router.patch(
    "/{complaint_id}",
    response_model=ComplaintOut,
)
def update_complaint(
    complaint_id: str,
    payload: ComplaintStatusUpdate,
    principal: Principal = Depends(get_current_principal),
    db: Session = Depends(get_db),
):
    if principal.role not in {
        "Institute Admin",
        "Platform Admin",
    }:
        raise HTTPException(
            status_code=403,
            detail="Admin access required.",
        )

    row = scoped_complaint(
        db,
        complaint_id,
        principal,
    )

    old_status = row.status
    old_department = row.department

    allowed_transitions = {
        "Pending": {
            "Pending",
            "In Progress",
            "Rejected",
        },
        "In Progress": {
            "In Progress",
            "Resolved",
            "Rejected",
        },
        "Resolved": {"Resolved"},
        "Rejected": {"Rejected"},
    }

    if payload.status not in allowed_transitions.get(
        row.status,
        {payload.status},
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid status transition: "
                f"{row.status} -> {payload.status}."
            ),
        )

    row.status = payload.status

    if payload.department is not None:
        row.department = payload.department.strip() or None

    wf = workflow_for(db, complaint_id)

    if payload.assigned_to is not None:
        wf.assigned_to = payload.assigned_to.strip() or None

    if payload.sla_hours is not None:
        wf.sla_hours = payload.sla_hours

    if payload.escalation_level is not None:
        wf.escalation_level = payload.escalation_level

    if payload.resolution_notes is not None:
        wf.resolution_notes = (
            payload.resolution_notes.strip() or None
        )

    if payload.status == "Resolved":
        wf.resolved_at = now_text()
    elif old_status == "Resolved":
        wf.resolved_at = None

    if payload.sla_hours is not None or not wf.due_at:
        wf.due_at = (
            datetime.now(timezone.utc)
            + timedelta(hours=int(wf.sla_hours or 48))
        ).strftime("%Y-%m-%d %H:%M:%S%z")

    wf.updated_at = now_text()

    db.add(
        ComplaintHistory(
            institute_id=row.institute_id,
            complaint_id=complaint_id,
            actor_user_id=principal.subject,
            action="Status Updated",
            old_value=old_status,
            new_value=row.status,
            note=(
                f"Department: {old_department or '-'} -> "
                f"{row.department or '-'}; "
                f"Assignee: {wf.assigned_to or 'Unassigned'}"
            ),
            created_at=now_text(),
        )
    )

    student_notification = None
    if row.student_id:
        student_notification = add_notification(
            db,
            institute_id=row.institute_id,
            user_id=row.student_id,
            complaint_id=complaint_id,
            notification_type="Complaint Update",
            title=f"Complaint {row.status}",
            message=(
                f"Your complaint status is now {row.status}."
            ),
        )

    log_audit(
        db,
        row.institute_id,
        principal.subject,
        principal.role,
        "Complaint Updated",
        "Complaint",
        complaint_id,
    )

    db.commit()
    db.refresh(row)
    
    logger.info(
    "Complaint push check: student_id=%r, institute_id=%r, notification_created=%s",
    row.student_id,
    row.institute_id,
    student_notification is not None,
)

    if row.student_id and student_notification is not None:
        try:
            send_push_to_user(
                db=db,
                institute_id=row.institute_id,
                user_id=row.student_id,
                title=f"Complaint {row.status}",
                body=f"Your complaint status is now {row.status}.",
                url="/dashboard/complaints",
            )
        except Exception:
            logger.exception("Push delivery failed after complaint status update.")

    return ComplaintOut(
        **serialize(
            row,
            principal.role != "Student",
        )
    )


# ---------------------------------------------------------
# MANUAL SLA ESCALATION
# ---------------------------------------------------------

@router.post("/{complaint_id}/escalate")
def escalate_complaint(
    complaint_id: str,
    principal: Principal = Depends(get_current_principal),
    db: Session = Depends(get_db),
):
    if principal.role not in {
        "Institute Admin",
        "Platform Admin",
    }:
        raise HTTPException(
            status_code=403,
            detail="Admin access required.",
        )

    row = scoped_complaint(
        db,
        complaint_id,
        principal,
    )

    wf = workflow_for(db, complaint_id)
    changed = sync_sla_escalation(db, row, wf)

    if (
        not changed
        and row.status not in {"Resolved", "Rejected"}
    ):
        old_level = wf.escalation_level or 0
        wf.escalation_level = min(3, old_level + 1)
        wf.updated_at = now_text()

        db.add(
            ComplaintHistory(
                institute_id=row.institute_id,
                complaint_id=complaint_id,
                actor_user_id=principal.subject,
                action="Manual Escalation",
                old_value=str(old_level),
                new_value=str(wf.escalation_level),
                note="Escalated manually by administrator.",
                created_at=now_text(),
            )
        )

        changed = True

    if changed:
        log_audit(
            db,
            row.institute_id,
            principal.subject,
            principal.role,
            "Complaint Escalated",
            "Complaint",
            complaint_id,
        )
        db.commit()

    return {
        "success": True,
        "escalated": changed,
        "escalation_level": wf.escalation_level,
    }


# ---------------------------------------------------------
# STUDENT FEEDBACK
# ---------------------------------------------------------

@router.post("/{complaint_id}/feedback")
def feedback(
    complaint_id: str,
    payload: ComplaintFeedbackCreate,
    principal: Principal = Depends(get_current_principal),
    db: Session = Depends(get_db),
):
    if principal.role != "Student":
        raise HTTPException(
            status_code=403,
            detail="Only students can submit feedback.",
        )

    row = scoped_complaint(
        db,
        complaint_id,
        principal,
    )

    if row.status != "Resolved":
        raise HTTPException(
            status_code=400,
            detail="Feedback is available after resolution.",
        )

    wf = workflow_for(db, complaint_id)

    if wf.feedback_rating is not None:
        raise HTTPException(
            status_code=409,
            detail="Feedback has already been submitted.",
        )

    now = now_text()

    (
        wf.feedback_rating,
        wf.feedback_comment,
        wf.feedback_at,
        wf.updated_at,
    ) = (
        payload.rating,
        payload.comment.strip(),
        now,
        now,
    )

    log_audit(
        db,
        principal.institute_id,
        principal.subject,
        principal.role,
        "Complaint Feedback Submitted",
        "Complaint",
        complaint_id,
    )

    db.commit()

    return {
        "success": True,
        "message": "Thank you for your feedback.",
    }



# ---------------------------------------------------------
# IMAGE ATTACHMENT UPLOAD AND SECURE VIEWING
# ---------------------------------------------------------

@router.post(
    "/{complaint_id}/attachment",
    response_model=ComplaintOut,
)
async def upload_attachment(
    complaint_id: str,
    file: UploadFile = File(...),
    principal: Principal = Depends(get_current_principal),
    db: Session = Depends(get_db),
):
    # Only students and institute administrators may upload images.
    if principal.role not in {"Student", "Institute Admin"}:
        raise HTTPException(
            status_code=403,
            detail="Attachment upload is not available for this role.",
        )

    # Enforce complaint ownership and institute-level access.
    row = scoped_complaint(db, complaint_id, principal)

    suffix = Path(file.filename or "").suffix.lower()

    if suffix not in ALLOWED_EXTENSIONS:
        await file.close()
        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG and PNG images are allowed.",
        )

    if file.content_type not in {"image/jpeg", "image/png"}:
        await file.close()
        raise HTTPException(
            status_code=400,
            detail="The uploaded content type must be JPEG or PNG.",
        )

    try:
        data = await file.read()
    finally:
        await file.close()

    if not data:
        raise HTTPException(
            status_code=400,
            detail="Image file is empty.",
        )

    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=400,
            detail="Image is too large. Maximum size is 5 MB.",
        )

    # Verify the file signature, not just its extension.
    if suffix in {".jpg", ".jpeg"} and not data.startswith(b"\xff\xd8\xff"):
        raise HTTPException(
            status_code=400,
            detail="The file content does not match a JPEG image.",
        )

    if suffix == ".png" and data[:8] != b"\x89PNG\r\n\x1a\n":
        raise HTTPException(
            status_code=400,
            detail="The file content does not match a PNG image.",
        )

    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)

    safe_name = f"{uuid4().hex}{suffix}"
    target = UPLOAD_ROOT / safe_name

    try:
        target.write_bytes(data)

        # Store a relative path in the database, not an absolute path.
        row.image_path = str(
            target.relative_to(UPLOAD_ROOT.parent.parent)
        )

        log_audit(
            db,
            row.institute_id,
            principal.subject,
            principal.role,
            "Complaint Attachment Uploaded",
            "Complaint",
            complaint_id,
        )

        db.commit()
        db.refresh(row)

    except Exception:
        db.rollback()

        try:
            if target.exists():
                target.unlink()
        except OSError:
            pass

        raise

    return ComplaintOut(
        **serialize(
            row,
            principal.role != "Student",
        )
    )


# ---------------------------------------------------------
# SECURE COMPLAINT PHOTO VIEWING
# ---------------------------------------------------------

@router.get(
    "/{complaint_id}/attachment",
    response_class=FileResponse,
)
def get_complaint_attachment(
    complaint_id: str,
    principal: Principal = Depends(get_current_principal),
    db: Session = Depends(get_db),
):
    # Platform Admin is explicitly denied access to complaint photos.
    if principal.role == "Platform Admin":
        raise HTTPException(
            status_code=403,
            detail="Complaint photos are not available for this role.",
        )

    if principal.role not in {"Student", "Institute Admin"}:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to view complaint photos.",
        )

    # Students can access their own complaints.
    # Institute Admins are restricted to their own institute.
    row = scoped_complaint(db, complaint_id, principal)

    if not row.image_path:
        raise HTTPException(
            status_code=404,
            detail="No photo is attached to this complaint.",
        )

    # Extract only the stored filename and safely resolve its location.
    stored_name = Path(row.image_path).name
    suffix = Path(stored_name).suffix.lower()

    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=404,
            detail="Complaint photo was not found.",
        )

    safe_root = UPLOAD_ROOT.resolve()
    target = (safe_root / stored_name).resolve()

    if target.parent != safe_root or not target.is_file():
        raise HTTPException(
            status_code=404,
            detail="Complaint photo was not found.",
        )

    media_type = (
        "image/png"
        if suffix == ".png"
        else "image/jpeg"
    )

    return FileResponse(
        path=str(target),
        media_type=media_type,
        content_disposition_type="inline",
        headers={
            "X-Content-Type-Options": "nosniff",
            "Cache-Control": "private, no-store",
        },
    )
