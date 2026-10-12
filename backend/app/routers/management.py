from datetime import datetime, timezone, timedelta
import importlib
import logging
from app.services.email_service import send_institute_status_email
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, text
from sqlalchemy.orm import Session
from app.core.dependencies import Principal, get_current_principal, require_roles
from app.core.security import hash_password
from app.db import get_db, engine
from app.models import (
    Institute, User, Department, CampusLocation, CampusMapSettings,
    Complaint, ComplaintWorkflow, AuditLog, Notification, PlatformAdmin
)
from app.schemas import (
    InstituteRegistrationCreate, StudentCreate, StudentStatusUpdate,
    DepartmentCreate, DepartmentUpdate, CampusLocationCreate, CampusLocationUpdate,
    CampusMapSettingsUpdate, InstituteStatusUpdate, ComplaintStatusUpdate
)
from app.services.audit import log_audit, now_text
from app.services.ai import generate_recommendations

router = APIRouter(prefix="/management", tags=["Management"])

# ---------- Public institute registration ----------
def make_code(institute_id: int) -> str:
    return f"INST-{institute_id:04d}"

@router.post("/institutes/register")
def register_institute(payload: InstituteRegistrationCreate, db: Session = Depends(get_db)):
    if db.query(Institute).filter(func.lower(Institute.email) == payload.email.lower()).first():
        raise HTTPException(status_code=409, detail="An institute with this email already exists.")
    if db.query(User).filter(func.lower(User.email) == payload.admin_email.lower()).first():
        raise HTTPException(status_code=409, detail="The admin email is already registered.")
    institute = Institute(
        institute_code="PENDING", name=payload.name.strip(), institute_type=payload.institute_type.strip(),
        email=payload.email.lower(), phone=payload.phone.strip(), address=payload.address.strip(),
        city=payload.city.strip(), state=payload.state.strip(), status="Pending", created_at=now_text()
    )
    db.add(institute)
    db.flush()
    institute.institute_code = make_code(institute.id)
    admin = User(
        institute_id=institute.id, user_id=f"{institute.institute_code}-ADMIN", name=payload.admin_name.strip(),
        email=payload.admin_email.lower(), password=hash_password(payload.admin_password),
        role="Institute Admin", status="Pending", created_at=now_text()
    )
    db.add(admin)
    log_audit(db, institute.id, admin.user_id, "Institute Admin", "Institute Registered", "Institute", str(institute.id))
    db.commit()
    return {"success": True, "message": "Institute registration submitted for platform review.",
            "institute_code": institute.institute_code, "admin_user_id": admin.user_id}

# ---------- Students ----------
@router.get("/students")
def list_students(principal: Principal = Depends(require_roles("Institute Admin")), db: Session = Depends(get_db)):
    rows = db.query(User).filter(User.institute_id == principal.institute_id, User.role == "Student").order_by(User.id.desc()).all()
    return [{"id": x.id, "user_id": x.user_id, "name": x.name, "email": x.email, "status": x.status,
             "created_at": x.created_at, "last_login": x.last_login} for x in rows]

@router.post("/students")
def create_student(payload: StudentCreate, principal: Principal = Depends(require_roles("Institute Admin")), db: Session = Depends(get_db)):
    if payload.email and db.query(User).filter(func.lower(User.email) == payload.email.lower()).first():
        raise HTTPException(status_code=409, detail="This email is already registered.")
    row = User(
        institute_id=principal.institute_id, user_id="PENDING",
        name=payload.name.strip(), email=payload.email.lower() if payload.email else None,
        password=hash_password(payload.password), role="Student", status="Active", created_at=now_text()
    )
    db.add(row); db.flush()
    # Use database id for collision-resistant student IDs.
    institute = db.query(Institute).filter(Institute.id == principal.institute_id).first()
    row.user_id = f"{institute.institute_code}-STU-{row.id:04d}"
    log_audit(db, principal.institute_id, principal.subject, principal.role, "Student Created", "User", row.user_id)
    db.commit()
    return {"success": True, "student_id": row.user_id, "name": row.name, "status": row.status}

@router.patch("/students/{student_id}/status")
def update_student_status(student_id: str, payload: StudentStatusUpdate,
                           principal: Principal = Depends(require_roles("Institute Admin")), db: Session = Depends(get_db)):
    row = db.query(User).filter(User.user_id == student_id, User.institute_id == principal.institute_id, User.role == "Student").first()
    if not row:
        raise HTTPException(status_code=404, detail="Student not found.")
    old = row.status; row.status = payload.status
    log_audit(db, principal.institute_id, principal.subject, principal.role, "Student Status Updated", "User", row.user_id, f"{old} -> {row.status}")
    db.commit()
    return {"success": True, "status": row.status}

# ---------- Departments ----------
@router.get("/departments")
def list_departments(principal: Principal = Depends(require_roles("Institute Admin", "Platform Admin")), db: Session = Depends(get_db)):
    q = db.query(Department).order_by(Department.id.desc())
    if principal.role != "Platform Admin":
        q = q.filter(Department.institute_id == principal.institute_id)
    rows = q.all()
    return [{"id": x.id, "institute_id": x.institute_id, "department_name": x.department_name,
             "description": x.description, "status": x.status, "created_at": x.created_at, "updated_at": x.updated_at} for x in rows]

@router.post("/departments")
def create_department(payload: DepartmentCreate, principal: Principal = Depends(require_roles("Institute Admin")), db: Session = Depends(get_db)):
    if db.query(Department).filter(Department.institute_id == principal.institute_id, func.lower(Department.department_name) == payload.department_name.lower()).first():
        raise HTTPException(status_code=409, detail="Department already exists.")
    row = Department(institute_id=principal.institute_id, department_name=payload.department_name.strip(),
                     description=payload.description.strip(), status="Active", created_at=now_text(), updated_at=now_text())
    db.add(row)
    log_audit(db, principal.institute_id, principal.subject, principal.role, "Department Created", "Department", payload.department_name.strip())
    db.commit()
    return {"success": True, "id": row.id}

@router.patch("/departments/{department_id}")
def update_department(department_id: int, payload: DepartmentUpdate,
                       principal: Principal = Depends(require_roles("Institute Admin")), db: Session = Depends(get_db)):
    row = db.query(Department).filter(Department.id == department_id, Department.institute_id == principal.institute_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Department not found.")
    row.department_name, row.description, row.status, row.updated_at = (
        payload.department_name.strip(), payload.description.strip(), payload.status, now_text()
    )
    log_audit(db, principal.institute_id, principal.subject, principal.role, "Department Updated", "Department", str(row.id))
    db.commit()
    return {"success": True}

@router.delete("/departments/{department_id}")
def delete_department(department_id: int, principal: Principal = Depends(require_roles("Institute Admin")), db: Session = Depends(get_db)):
    row = db.query(Department).filter(Department.id == department_id, Department.institute_id == principal.institute_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Department not found.")
    db.delete(row)
    log_audit(db, principal.institute_id, principal.subject, principal.role, "Department Deleted", "Department", str(department_id))
    db.commit()
    return {"success": True}

# ---------- Campus map ----------
@router.get("/campus-map")
def get_campus_map(
    principal: Principal = Depends(
        require_roles("Institute Admin", "Student")
    ),
    db: Session = Depends(get_db),
):
    if principal.institute_id is None:
        raise HTTPException(
            status_code=400,
            detail="Institute scope is required.",
        )

    settings = (
        db.query(CampusMapSettings)
        .filter(
            CampusMapSettings.institute_id == principal.institute_id
        )
        .first()
    )

    locations = (
        db.query(CampusLocation)
        .filter(
            CampusLocation.institute_id == principal.institute_id,
            CampusLocation.is_active == 1,
        )
        .order_by(CampusLocation.location_name.asc())
        .all()
    )

    map_settings = {
        "center_latitude": settings.center_latitude if settings else None,
        "center_longitude": settings.center_longitude if settings else None,
        "default_zoom": settings.default_zoom if settings else 17,
        "heatmap_enabled": bool(settings.heatmap_enabled) if settings else False,
        "complaint_markers_enabled": (
            bool(settings.complaint_markers_enabled) if settings else False
        ),
        "hotspots_enabled": bool(settings.hotspots_enabled) if settings else False,
        "campus_locations_enabled": (
            bool(settings.campus_locations_enabled) if settings else True
        ),
    }

    location_data = [
        {
            "id": item.id,
            "location_name": item.location_name,
            "latitude": item.latitude,
            "longitude": item.longitude,
            "location_type": item.location_type,
        }
        for item in locations
    ]

    # Students receive only approved campus locations.
    # Complaint and risk data are never included in their response.
    if principal.role == "Student":
        return {
            "settings": {
                "center_latitude": map_settings["center_latitude"],
                "center_longitude": map_settings["center_longitude"],
                "default_zoom": map_settings["default_zoom"],
                "campus_locations_enabled": map_settings[
                    "campus_locations_enabled"
                ],
            },
            "locations": location_data,
            "complaints": [],
        }

    # Institute Admin retains campus safety visibility.
    complaints = (
        db.query(Complaint)
        .filter(Complaint.institute_id == principal.institute_id)
        .order_by(Complaint.id.desc())
        .limit(500)
        .all()
    )

    return {
        "settings": map_settings,
        "locations": location_data,
        "complaints": [
            {
                "complaint_id": item.complaint_id,
                "location": item.location,
                "category": item.category,
                "priority": item.priority,
                "status": item.status,
                "created_at": item.created_at,
            }
            for item in complaints
        ],
    }
@router.put("/campus-map/settings")
def update_map_settings(payload: CampusMapSettingsUpdate,
                        principal: Principal = Depends(require_roles("Institute Admin")), db: Session = Depends(get_db)):
    row = db.query(CampusMapSettings).filter(CampusMapSettings.institute_id == principal.institute_id).first()
    if not row:
        row = CampusMapSettings(institute_id=principal.institute_id, created_at=now_text())
        db.add(row)
    row.center_latitude, row.center_longitude, row.default_zoom = payload.center_latitude, payload.center_longitude, payload.default_zoom
    row.heatmap_enabled, row.complaint_markers_enabled, row.hotspots_enabled, row.campus_locations_enabled = (
        int(payload.heatmap_enabled), int(payload.complaint_markers_enabled), int(payload.hotspots_enabled), int(payload.campus_locations_enabled)
    )
    row.updated_at = now_text()
    log_audit(db, principal.institute_id, principal.subject, principal.role, "Campus Map Settings Updated", "CampusMapSettings", str(row.id))
    db.commit()
    return {"success": True}

@router.post("/campus-locations")
def add_location(payload: CampusLocationCreate, principal: Principal = Depends(require_roles("Institute Admin")), db: Session = Depends(get_db)):
    row = CampusLocation(
        institute_id=principal.institute_id, location_name=payload.location_name.strip(),
        latitude=payload.latitude, longitude=payload.longitude, location_type=payload.location_type.strip(),
        is_active=1, created_at=now_text(), updated_at=now_text()
    )
    db.add(row)
    log_audit(db, principal.institute_id, principal.subject, principal.role, "Campus Location Created", "CampusLocation", payload.location_name.strip())
    db.commit()
    return {"success": True, "id": row.id}

@router.patch("/campus-locations/{location_id}")
def edit_location(location_id: int, payload: CampusLocationUpdate,
                  principal: Principal = Depends(require_roles("Institute Admin")), db: Session = Depends(get_db)):
    row = db.query(CampusLocation).filter(CampusLocation.id == location_id, CampusLocation.institute_id == principal.institute_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Campus location not found.")
    row.location_name, row.latitude, row.longitude, row.location_type = (
        payload.location_name.strip(), payload.latitude, payload.longitude, payload.location_type.strip()
    )
    row.is_active, row.updated_at = int(payload.is_active), now_text()
    log_audit(db, principal.institute_id, principal.subject, principal.role, "Campus Location Updated", "CampusLocation", str(row.id))
    db.commit()
    return {"success": True}

@router.delete("/campus-locations/{location_id}")
def remove_location(location_id: int, principal: Principal = Depends(require_roles("Institute Admin")), db: Session = Depends(get_db)):
    row = db.query(CampusLocation).filter(CampusLocation.id == location_id, CampusLocation.institute_id == principal.institute_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Campus location not found.")
    row.is_active = 0; row.updated_at = now_text()
    log_audit(db, principal.institute_id, principal.subject, principal.role, "Campus Location Archived", "CampusLocation", str(row.id))
    db.commit()
    return {"success": True}

# ---------- Institute admin control center ----------
@router.get("/control-center")
def control_center(principal: Principal = Depends(require_roles("Institute Admin")), db: Session = Depends(get_db)):
    iid = principal.institute_id
    q = db.query(Complaint).filter(Complaint.institute_id == iid)
    return {
        "students": db.query(User).filter(User.institute_id == iid, User.role == "Student").count(),
        "admins": db.query(User).filter(User.institute_id == iid, User.role == "Institute Admin").count(),
        "departments": db.query(Department).filter(Department.institute_id == iid).count(),
        "complaints": q.count(),
        "resolved": q.filter(Complaint.status == "Resolved").count(),
        "critical": q.filter(Complaint.priority == "Critical").count(),
        "high": q.filter(Complaint.priority == "High").count(),
        "overdue": db.query(ComplaintWorkflow).join(Complaint, ComplaintWorkflow.complaint_id == Complaint.complaint_id).filter(
            Complaint.institute_id == iid,
            Complaint.status.notin_(["Resolved", "Rejected"]),
            ComplaintWorkflow.due_at != None,
            ComplaintWorkflow.due_at < now_text()
        ).count(),
    }

@router.put("/workflow/{complaint_id}")
def save_workflow(complaint_id: str, payload: ComplaintStatusUpdate,
                  principal: Principal = Depends(require_roles("Institute Admin")), db: Session = Depends(get_db)):
    row = db.query(Complaint).filter(Complaint.complaint_id == complaint_id, Complaint.institute_id == principal.institute_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Complaint not found.")
    wf = db.query(ComplaintWorkflow).filter(ComplaintWorkflow.complaint_id == complaint_id).first()
    if not wf:
        wf = ComplaintWorkflow(complaint_id=complaint_id, sla_hours=48)
        db.add(wf)
    if payload.assigned_to is not None: wf.assigned_to = payload.assigned_to.strip() or None
    if payload.sla_hours is not None: wf.sla_hours = payload.sla_hours
    if payload.escalation_level is not None: wf.escalation_level = payload.escalation_level
    if payload.resolution_notes is not None: wf.resolution_notes = payload.resolution_notes.strip() or None
    wf.due_at = (datetime.now(timezone.utc) + timedelta(hours=wf.sla_hours)).strftime("%Y-%m-%d %H:%M:%S%z")
    wf.updated_at = now_text()
    log_audit(db, principal.institute_id, principal.subject, principal.role, "Complaint Workflow Updated", "Complaint", complaint_id)
    db.commit()
    return {"success": True}

# ---------- Reports ----------
@router.get("/reports/complaints")
def complaint_report(principal: Principal = Depends(require_roles("Institute Admin", "Platform Admin")), db: Session = Depends(get_db)):
    q = db.query(Complaint)
    if principal.role != "Platform Admin":
        q = q.filter(Complaint.institute_id == principal.institute_id)
    rows = q.order_by(Complaint.id.desc()).all()
    return [{
        "complaint_id": x.complaint_id, "title": x.title, "location": x.location,
        "category": x.category, "priority": x.priority, "status": x.status,
        "department": x.department, "created_at": x.created_at,
        "student_id": x.student_id if principal.role == "Platform Admin" or not x.anonymous else None,
    } for x in rows]

# ---------- Analytics ----------
@router.get("/analytics")
def analytics(principal: Principal = Depends(require_roles("Institute Admin", "Platform Admin")),
              db: Session = Depends(get_db)):
    q = db.query(Complaint)
    if principal.role != "Platform Admin":
        q = q.filter(Complaint.institute_id == principal.institute_id)
    rows = q.order_by(Complaint.id.asc()).all()

    def counts(values):
        out = {}
        for value in values:
            key = value or "General"
            out[key] = out.get(key, 0) + 1
        return [{"label": k, "count": v} for k, v in sorted(out.items(), key=lambda x: (-x[1], x[0]))]

    monthly = {}
    for row in rows:
        stamp = (row.created_at or "")[:7]
        if stamp:
            monthly[stamp] = monthly.get(stamp, 0) + 1

    return {
        "total": len(rows),
        "by_status": counts([x.status for x in rows]),
        "by_priority": counts([x.priority for x in rows]),
        "by_category": counts([x.category for x in rows]),
        "by_department": counts([x.department for x in rows]),
        "monthly": [{"month": k, "count": monthly[k]} for k in sorted(monthly)],
    }

# ---------- AI operational intelligence ----------
@router.get("/intelligence")
def intelligence(principal: Principal = Depends(require_roles("Institute Admin", "Platform Admin")),
                 db: Session = Depends(get_db)):
    q = db.query(Complaint)
    if principal.role != "Platform Admin":
        q = q.filter(Complaint.institute_id == principal.institute_id)
    rows = q.order_by(Complaint.id.desc()).limit(5000).all()
    complaints = [{"complaint_id": x.complaint_id, "title": x.title, "description": x.description,
                   "location": x.location, "category": x.category, "priority": x.priority,
                   "status": x.status, "department": x.department} for x in rows]
    location_risks = {}
    for c in complaints:
        loc = (c.get("location") or "").strip()
        if not loc:
            continue
        d = location_risks.setdefault(loc, {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0, "pending": 0, "in_progress": 0, "resolved": 0, "rejected": 0})
        d["total"] += 1
        priority = c.get("priority")
        status = c.get("status")
        if priority in {"Critical", "High", "Medium", "Low"}: d[priority.lower()] += 1
        if status == "Pending": d["pending"] += 1
        elif status == "In Progress": d["in_progress"] += 1
        elif status == "Resolved": d["resolved"] += 1
        elif status == "Rejected": d["rejected"] += 1
    for d in location_risks.values():
        score = min(d["total"] * 5 + d["critical"] * 30 + d["high"] * 15 + d["pending"] * 5 + d["in_progress"] * 3, 100)
        d["risk_score"] = score
        d["safety_score"] = 100 - score
        d["risk_level"] = "Danger" if score >= 75 else "High Risk" if score >= 50 else "Moderate" if score >= 25 else "Safe"
    return {"recommendations": generate_recommendations(complaints, location_risks),
            "hotspots": [{"location": k, "risk_score": v["risk_score"], "risk_level": v["risk_level"], "total_complaints": v["total"]}
                         for k, v in sorted(location_risks.items(), key=lambda item: item[1]["risk_score"], reverse=True) if v["risk_score"] >= 50],
            "complaint_count": len(complaints)}

# ---------- Audit ----------
@router.get("/audit")
def audit_logs(principal: Principal = Depends(require_roles("Institute Admin", "Platform Admin")),
               db: Session = Depends(get_db), action: str | None = None, role: str | None = None):
    q = db.query(AuditLog).order_by(AuditLog.id.desc())
    if principal.role != "Platform Admin":
        q = q.filter(AuditLog.institute_id == principal.institute_id)
    if action: q = q.filter(AuditLog.action == action)
    if role: q = q.filter(AuditLog.actor_role == role)
    rows = q.limit(500).all()
    return [{"id": x.id, "institute_id": x.institute_id, "actor_user_id": x.actor_user_id,
             "actor_role": x.actor_role, "action": x.action, "entity_type": x.entity_type,
             "entity_id": x.entity_id, "details": x.details, "created_at": x.created_at} for x in rows]

@router.get("/audit/metrics")
def audit_metrics(principal: Principal = Depends(require_roles("Institute Admin", "Platform Admin")),
                  db: Session = Depends(get_db)):
    iid = None if principal.role == "Platform Admin" else principal.institute_id
    q = db.query(AuditLog)
    if iid is not None: q = q.filter(AuditLog.institute_id == iid)
    total = q.count()
    today_prefix = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    today = q.filter(AuditLog.created_at.like(f"{today_prefix}%")).count()
    last_24h_prefix = datetime.now(timezone.utc) - timedelta(hours=24)
    last_7d_prefix = datetime.now(timezone.utc) - timedelta(days=7)
    # Timestamp strings are stored as sortable ISO-like UTC text.
    last_24h = q.filter(AuditLog.created_at >= last_24h_prefix.strftime("%Y-%m-%d %H:%M:%S")).count()
    last_7d = q.filter(AuditLog.created_at >= last_7d_prefix.strftime("%Y-%m-%d %H:%M:%S")).count()
    failed = q.filter(
        (func.lower(AuditLog.action).like("%login%failed%")) |
        (func.lower(AuditLog.action).like("%failed%login%"))
    ).count()
    actors = q.with_entities(func.count(func.distinct(AuditLog.actor_user_id))).scalar() or 0
    return {"total": total, "today": today, "last_24h": last_24h, "last_7d": last_7d, "failed_logins": failed, "unique_actors": actors}

# ---------- System health ----------
@router.get("/system-health")
def system_health(principal: Principal = Depends(require_roles("Platform Admin")), db: Session = Depends(get_db)):
    checks = []
    def check(name, status, detail):
        checks.append({"name": name, "status": status, "detail": detail})
    try:
        db.execute(text("SELECT 1"))
        check("Database connection", "PASS", "PostgreSQL connection is responding.")
    except Exception as exc:
        check("Database connection", "FAIL", str(exc))
    try:
        required = {"institutes","users","platform_admins","complaints","departments","complaint_workflow","complaint_history","announcements","notifications","notification_preferences","campus_map_settings","campus_locations","user_profiles","audit_logs","platform_settings"}
        if db.bind.dialect.name == "postgresql":
            found = set(db.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'")).scalars().all())
        else:
            found = set(db.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).scalars().all())
        missing = sorted(required - found)
        check("Required database tables", "PASS" if not missing else "FAIL", "All expected tables are present." if not missing else f"Missing: {', '.join(missing)}")
    except Exception as exc:
        check("Schema check", "FAIL", str(exc))
    try:
        hash_password("HealthCheck@123")
        check("Password hashing", "PASS", "Argon2 hashing self-test completed.")
    except Exception as exc:
        check("Password hashing", "FAIL", str(exc))
    for module in ["app.services.ai", "app.services.audit"]:
        try:
            importlib.import_module(module)
            check(module, "PASS", "Module loaded successfully.")
        except Exception as exc:
            check(module, "FAIL", str(exc))
    return {"checks": checks, "healthy": all(x["status"] == "PASS" for x in checks)}

# ---------- Platform administration ----------
@router.get("/platform/institutes")
def platform_institutes(principal: Principal = Depends(require_roles("Platform Admin")), db: Session = Depends(get_db)):
    rows = db.query(Institute).order_by(Institute.id.desc()).all()
    return [{"id": x.id, "institute_code": x.institute_code, "name": x.name, "institute_type": x.institute_type,
             "email": x.email, "phone": x.phone, "city": x.city, "state": x.state, "address": x.address,
             "status": x.status, "created_at": x.created_at, "approved_at": x.approved_at} for x in rows]


@router.patch("/platform/institutes/{institute_id}/status")
def platform_institute_status(
    institute_id: int,
    payload: InstituteStatusUpdate,
    principal: Principal = Depends(require_roles("Platform Admin")),
    db: Session = Depends(get_db),
):
    row = db.query(Institute).filter(
        Institute.id == institute_id
    ).first()

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Institute not found.",
        )

    allowed_statuses = {"Pending", "Approved", "Rejected", "Blocked"}

    if payload.status not in allowed_statuses:
        raise HTTPException(
            status_code=422,
            detail="Invalid institute status.",
        )

    previous_status = row.status
    row.status = payload.status

    if payload.status == "Approved":
        row.approved_at = now_text()

    user_status = {
        "Approved": "Active",
        "Rejected": "Rejected",
        "Blocked": "Blocked",
        "Pending": "Pending",
    }[payload.status]

    db.query(User).filter(
        User.institute_id == institute_id,
        User.role == "Institute Admin",
    ).update(
        {"status": user_status},
        synchronize_session=False,
    )

    log_audit(
        db,
        None,
        principal.subject,
        principal.role,
        f"Institute {payload.status}",
        "Institute",
        str(institute_id),
    )

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not update institute status.",
        )

    # Email only when the status actually changes to a final decision.
    if (
        payload.status in {"Approved", "Rejected", "Blocked"}
        and previous_status != payload.status
    ):
        try:
            send_institute_status_email(
                recipient=row.email,
                institute_name=row.name,
                status=payload.status,
            )
        except Exception:
            logging.exception(
                "Institute status email failed for institute_id=%s",
                institute_id,
            )

    return {
        "success": True,
        "status": row.status,
        "message": "Institute status updated.",
    }

@router.get("/platform/overview")
def platform_overview(principal: Principal = Depends(require_roles("Platform Admin")), db: Session = Depends(get_db)):
    return {
        "pending_institutes": db.query(Institute).filter(Institute.status == "Pending").count(),
        "approved_institutes": db.query(Institute).filter(Institute.status == "Approved").count(),
        "blocked_institutes": db.query(Institute).filter(Institute.status == "Blocked").count(),
        "institutes": db.query(Institute).count(),
        "users": db.query(User).count(),
        "complaints": db.query(Complaint).count(),
        "resolved": db.query(Complaint).filter(Complaint.status == "Resolved").count(),
        "critical": db.query(Complaint).filter(Complaint.priority == "Critical").count(),
    }
