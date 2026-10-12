from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.dependencies import Principal, require_roles
from app.db import get_db
from app.models import Complaint, Department, Institute, User, ComplaintWorkflow
from app.services.audit import now_text

router = APIRouter(prefix="/admin", tags=["Administration"])

@router.get("/overview")
def overview(principal: Principal = Depends(require_roles("Institute Admin","Platform Admin")), db: Session = Depends(get_db)):
    if principal.role == "Platform Admin":
        return {
            "scope":"platform",
            "institutes": db.query(func.count(Institute.id)).scalar() or 0,
            "users": db.query(func.count(User.id)).scalar() or 0,
            "students": db.query(func.count(User.id)).filter(User.role=="Student").scalar() or 0,
            "complaints": db.query(func.count(Complaint.id)).scalar() or 0,
            "pending": db.query(func.count(Complaint.id)).filter(Complaint.status=="Pending").scalar() or 0,
            "in_progress": db.query(func.count(Complaint.id)).filter(Complaint.status=="In Progress").scalar() or 0,
            "resolved": db.query(func.count(Complaint.id)).filter(Complaint.status=="Resolved").scalar() or 0,
            "rejected": db.query(func.count(Complaint.id)).filter(Complaint.status=="Rejected").scalar() or 0,
            "critical": db.query(func.count(Complaint.id)).filter(Complaint.priority=="Critical").scalar() or 0,
            "high": db.query(func.count(Complaint.id)).filter(Complaint.priority=="High").scalar() or 0,
        }
    q = db.query(Complaint).filter(Complaint.institute_id == principal.institute_id)
    overdue = db.query(ComplaintWorkflow).join(Complaint, ComplaintWorkflow.complaint_id == Complaint.complaint_id).filter(
        Complaint.institute_id == principal.institute_id,
        Complaint.status.notin_(["Resolved", "Rejected"]),
        ComplaintWorkflow.due_at != None,
        ComplaintWorkflow.due_at < now_text()
    ).count()
    return {
        "scope":"institute",
        "complaints": q.count(),
        "pending": q.filter(Complaint.status=="Pending").count(),
        "in_progress": q.filter(Complaint.status=="In Progress").count(),
        "resolved": q.filter(Complaint.status=="Resolved").count(),
        "rejected": q.filter(Complaint.status=="Rejected").count(),
        "critical": q.filter(Complaint.priority=="Critical").count(),
        "high": q.filter(Complaint.priority=="High").count(),
        "departments": db.query(func.count(Department.id)).filter(Department.institute_id==principal.institute_id).scalar() or 0,
        "students": db.query(func.count(User.id)).filter(User.institute_id==principal.institute_id, User.role=="Student").scalar() or 0,
        "overdue": overdue,
    }
