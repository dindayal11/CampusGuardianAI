from pydantic import BaseModel, ConfigDict, EmailStr, Field

class LoginRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=1, max_length=200)

class PlatformLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=200)

class UserSummary(BaseModel):
    subject: str
    name: str
    role: str
    email: str | None = None
    institute_id: int | None = None
    institute_code: str | None = None

class AuthResponse(BaseModel):
    authenticated: bool = True
    user: UserSummary

class ComplaintCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: str = Field(min_length=5, max_length=5000)
    location: str = Field(min_length=1, max_length=255)
    anonymous: bool = False

class ComplaintStatusUpdate(BaseModel):
    status: str = Field(pattern=r"^(Pending|In Progress|Resolved|Rejected)$")
    department: str | None = Field(default=None, max_length=160)
    resolution_notes: str | None = Field(default=None, max_length=5000)
    assigned_to: str | None = Field(default=None, max_length=120)
    sla_hours: int | None = Field(default=None, ge=1, le=720)
    escalation_level: int | None = Field(default=None, ge=0, le=5)

class ComplaintOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    complaint_id: str | None
    title: str
    description: str
    location: str
    category: str | None
    priority: str | None
    anonymous: bool
    status: str
    created_at: str | None
    department: str | None
    student_id: str | None = None
    image_path: str | None = None
    risk_score: int | None = None
    recommended_action: str | None = None
    ai_analysis: dict | None = None
    duplicate_analysis: dict | None = None

class ComplaintListOut(BaseModel):
    items: list[ComplaintOut]
    total: int

class ComplaintHistoryOut(BaseModel):
    id: int
    action: str
    actor_user_id: str | None
    old_value: str | None
    new_value: str | None
    note: str | None
    created_at: str | None

class WorkflowOut(BaseModel):
    assigned_to: str | None = None
    sla_hours: int = 48
    due_at: str | None = None
    escalation_level: int = 0
    resolution_notes: str | None = None
    resolved_at: str | None = None
    feedback_rating: int | None = None
    feedback_comment: str | None = None
    feedback_at: str | None = None
    is_overdue: bool = False
    remaining_hours: float | None = None

class ComplaintDetailOut(BaseModel):
    complaint: ComplaintOut
    workflow: WorkflowOut
    history: list[ComplaintHistoryOut]
    duplicate: dict | None = None

class ComplaintFeedbackCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str = Field(default="", max_length=4000)

class AnnouncementCreate(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    message: str = Field(min_length=2, max_length=10000)
    audience: str = Field(default="All", pattern=r"^(All|Students|Institute Admins)$")
    priority: str = Field(default="Normal", pattern=r"^(Normal|High|Critical)$")
    expires_at: str | None = Field(default=None, max_length=40)

class AnnouncementOut(BaseModel):
    id: int
    title: str
    message: str
    audience: str
    priority: str
    created_at: str | None
    expires_at: str | None

class NotificationPreferenceUpdate(BaseModel):
    in_app_enabled: bool | None = None
    complaint_updates: bool | None = None
    priority_alerts: bool | None = None
    admin_alerts: bool | None = None

class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=200)
    new_password: str = Field(min_length=8, max_length=200)
    confirm_password: str = Field(min_length=8, max_length=200)

class InstituteRegistrationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    institute_type: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone: str = Field(min_length=7, max_length=50)
    address: str = Field(min_length=2, max_length=2000)
    city: str = Field(min_length=2, max_length=120)
    state: str = Field(min_length=2, max_length=120)
    admin_name: str = Field(min_length=2, max_length=255)
    admin_email: EmailStr
    admin_password: str = Field(min_length=8, max_length=200)

class StudentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    email: EmailStr | None = None
    password: str = Field(min_length=8, max_length=200)

class StudentStatusUpdate(BaseModel):
    status: str = Field(pattern=r"^(Active|Blocked|Suspended|Rejected)$")

class DepartmentCreate(BaseModel):
    department_name: str = Field(min_length=2, max_length=160)
    description: str = Field(default="", max_length=2000)

class DepartmentUpdate(BaseModel):
    department_name: str = Field(min_length=2, max_length=160)
    description: str = Field(default="", max_length=2000)
    status: str = Field(pattern=r"^(Active|Inactive)$")

class CampusLocationCreate(BaseModel):
    location_name: str = Field(min_length=2, max_length=255)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    location_type: str = Field(default="General", max_length=80)

class CampusLocationUpdate(CampusLocationCreate):
    is_active: bool = True

class CampusMapSettingsUpdate(BaseModel):
    center_latitude: float = Field(ge=-90, le=90)
    center_longitude: float = Field(ge=-180, le=180)
    default_zoom: int = Field(ge=1, le=22)
    heatmap_enabled: bool = True
    complaint_markers_enabled: bool = True
    hotspots_enabled: bool = True
    campus_locations_enabled: bool = True

class InstituteStatusUpdate(BaseModel):
    status: str = Field(pattern=r"^(Approved|Rejected|Blocked|Pending)$")
