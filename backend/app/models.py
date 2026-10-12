from sqlalchemy import Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

class Institute(Base):
    __tablename__ = "institutes"
    id: Mapped[int] = mapped_column(primary_key=True)
    institute_code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    institute_type: Mapped[str | None] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50))
    address: Mapped[str | None] = mapped_column(Text)
    city: Mapped[str | None] = mapped_column(String(120))
    state: Mapped[str | None] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(40), default="Pending", nullable=False)
    created_at: Mapped[str | None] = mapped_column(String(40))
    approved_at: Mapped[str | None] = mapped_column(String(40))

class User(Base):
    __tablename__ = "users"
    __table_args__ = (Index("ix_users_institute", "institute_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    institute_id: Mapped[int | None] = mapped_column(ForeignKey("institutes.id"))
    user_id: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(320))
    password: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="Active", nullable=False)
    created_at: Mapped[str | None] = mapped_column(String(40))
    last_login: Mapped[str | None] = mapped_column(String(40))

class PlatformAdmin(Base):
    __tablename__ = "platform_admins"
    id: Mapped[int] = mapped_column(primary_key=True)
    admin_id: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="Active", nullable=False)
    created_at: Mapped[str | None] = mapped_column(String(40))

class Complaint(Base):
    __tablename__ = "complaints"
    __table_args__ = (
        Index("ix_complaints_institute_status", "institute_id", "status"),
        Index("ix_complaints_institute_priority", "institute_id", "priority"),
        Index("ix_complaints_student", "institute_id", "student_id"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    complaint_id: Mapped[str | None] = mapped_column(String(80), unique=True)
    institute_id: Mapped[int | None] = mapped_column(ForeignKey("institutes.id"))
    student_id: Mapped[str | None] = mapped_column(String(120))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str | None] = mapped_column(String(120))
    priority: Mapped[str | None] = mapped_column(String(40))
    anonymous: Mapped[int] = mapped_column(Integer, default=0)
    image_path: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), default="Pending")
    created_at: Mapped[str | None] = mapped_column(String(40))
    department: Mapped[str | None] = mapped_column(String(120))

class Department(Base):
    __tablename__ = "departments"
    __table_args__ = (UniqueConstraint("institute_id","department_name",name="uq_department_name"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    institute_id: Mapped[int] = mapped_column(ForeignKey("institutes.id"), nullable=False)
    department_name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), default="Active")
    created_at: Mapped[str | None] = mapped_column(String(40))
    updated_at: Mapped[str | None] = mapped_column(String(40))

class ComplaintWorkflow(Base):
    __tablename__ = "complaint_workflow"
    id: Mapped[int] = mapped_column(primary_key=True)
    complaint_id: Mapped[str] = mapped_column(String(80), ForeignKey("complaints.complaint_id"), unique=True, nullable=False)
    assigned_to: Mapped[str | None] = mapped_column(String(120))
    sla_hours: Mapped[int] = mapped_column(Integer, default=48)
    due_at: Mapped[str | None] = mapped_column(String(40))
    escalation_level: Mapped[int] = mapped_column(Integer, default=0)
    resolution_notes: Mapped[str | None] = mapped_column(Text)
    resolved_at: Mapped[str | None] = mapped_column(String(40))
    feedback_rating: Mapped[int | None] = mapped_column(Integer)
    feedback_comment: Mapped[str | None] = mapped_column(Text)
    feedback_at: Mapped[str | None] = mapped_column(String(40))
    updated_at: Mapped[str | None] = mapped_column(String(40))

class ComplaintHistory(Base):
    __tablename__ = "complaint_history"
    id: Mapped[int] = mapped_column(primary_key=True)
    institute_id: Mapped[int | None] = mapped_column(ForeignKey("institutes.id"))
    complaint_id: Mapped[str] = mapped_column(String(80), ForeignKey("complaints.complaint_id"), nullable=False)
    actor_user_id: Mapped[str | None] = mapped_column(String(120))
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    old_value: Mapped[str | None] = mapped_column(Text)
    new_value: Mapped[str | None] = mapped_column(Text)
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[str | None] = mapped_column(String(40))

class Announcement(Base):
    __tablename__ = "announcements"
    id: Mapped[int] = mapped_column(primary_key=True)
    institute_id: Mapped[int] = mapped_column(ForeignKey("institutes.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    audience: Mapped[str] = mapped_column(String(80), default="All")
    priority: Mapped[str] = mapped_column(String(40), default="Normal")
    created_by: Mapped[str | None] = mapped_column(String(120))
    expires_at: Mapped[str | None] = mapped_column(String(40))
    is_active: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[str | None] = mapped_column(String(40))

class AnnouncementRead(Base):
    __tablename__ = "announcement_reads"

    __table_args__ = (
        UniqueConstraint(
            "announcement_id",
            "user_id",
            name="uq_announcement_read_user",
        ),
        Index("ix_announcement_reads_user", "user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    announcement_id: Mapped[int] = mapped_column(
        ForeignKey("announcements.id", ondelete="CASCADE"),
        nullable=False,
    )
    institute_id: Mapped[int] = mapped_column(
        ForeignKey("institutes.id"),
        nullable=False,
    )
    user_id: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )
    read_at: Mapped[str | None] = mapped_column(String(40))

class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(primary_key=True)
    institute_id: Mapped[int | None] = mapped_column(ForeignKey("institutes.id"))
    user_id: Mapped[str | None] = mapped_column(String(120))
    complaint_id: Mapped[str | None] = mapped_column(String(80))
    notification_type: Mapped[str] = mapped_column(String(80), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[str | None] = mapped_column(String(40))

class NotificationPreference(Base):
    __tablename__ = "notification_preferences"
    __table_args__ = (UniqueConstraint("institute_id", "user_id", name="uq_notification_preferences_user"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    institute_id: Mapped[int] = mapped_column(ForeignKey("institutes.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(120), nullable=False)
    in_app_enabled: Mapped[int] = mapped_column(Integer, default=1)
    complaint_updates: Mapped[int] = mapped_column(Integer, default=1)
    priority_alerts: Mapped[int] = mapped_column(Integer, default=1)
    admin_alerts: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[str | None] = mapped_column(String(40))
    updated_at: Mapped[str | None] = mapped_column(String(40))

class CampusMapSettings(Base):
    __tablename__ = "campus_map_settings"
    id: Mapped[int] = mapped_column(primary_key=True)
    institute_id: Mapped[int] = mapped_column(ForeignKey("institutes.id"), unique=True, nullable=False)
    center_latitude: Mapped[float] = mapped_column(Float, nullable=False)
    center_longitude: Mapped[float] = mapped_column(Float, nullable=False)
    default_zoom: Mapped[int] = mapped_column(Integer, default=17)
    heatmap_enabled: Mapped[int] = mapped_column(Integer, default=1)
    complaint_markers_enabled: Mapped[int] = mapped_column(Integer, default=1)
    hotspots_enabled: Mapped[int] = mapped_column(Integer, default=1)
    campus_locations_enabled: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[str | None] = mapped_column(String(40))
    updated_at: Mapped[str | None] = mapped_column(String(40))

class CampusLocation(Base):
    __tablename__ = "campus_locations"
    id: Mapped[int] = mapped_column(primary_key=True)
    institute_id: Mapped[int] = mapped_column(ForeignKey("institutes.id"), nullable=False)
    location_name: Mapped[str] = mapped_column(String(255), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    location_type: Mapped[str] = mapped_column(String(80), default="General")
    is_active: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[str | None] = mapped_column(String(40))
    updated_at: Mapped[str | None] = mapped_column(String(40))

class UserProfile(Base):
    __tablename__ = "user_profiles"
    __table_args__ = (UniqueConstraint("institute_id", "user_id", name="uq_user_profiles_user"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    institute_id: Mapped[int] = mapped_column(ForeignKey("institutes.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(120), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50))
    department: Mapped[str | None] = mapped_column(String(160))
    designation: Mapped[str | None] = mapped_column(String(160))
    address: Mapped[str | None] = mapped_column(Text)
    emergency_contact: Mapped[str | None] = mapped_column(String(100))
    bio: Mapped[str | None] = mapped_column(Text)
    photo_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    updated_at: Mapped[str | None] = mapped_column(String(40))

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    institute_id: Mapped[int | None] = mapped_column(ForeignKey("institutes.id"))
    actor_user_id: Mapped[str | None] = mapped_column(String(120))
    actor_role: Mapped[str | None] = mapped_column(String(80))
    action: Mapped[str] = mapped_column(String(160), nullable=False)
    entity_type: Mapped[str | None] = mapped_column(String(80))
    entity_id: Mapped[str | None] = mapped_column(String(120))
    details: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[str | None] = mapped_column(String(40))

class PlatformSetting(Base):
    __tablename__ = "platform_settings"
    id: Mapped[int] = mapped_column(primary_key=True)
    platform_name: Mapped[str] = mapped_column(String(255), default="Campus Guardian AI")
    support_email: Mapped[str] = mapped_column(String(320), default="")
    maintenance_mode: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[str | None] = mapped_column(String(40))


class PushSubscription(Base):
    __tablename__ = "push_subscriptions"

    __table_args__ = (
        UniqueConstraint("endpoint", name="uq_push_subscriptions_endpoint"),
        Index("ix_push_subscriptions_user", "institute_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    institute_id: Mapped[int] = mapped_column(
        ForeignKey("institutes.id"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(String(120), nullable=False)
    endpoint: Mapped[str] = mapped_column(Text, nullable=False)
    p256dh: Mapped[str] = mapped_column(Text, nullable=False)
    auth: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[str | None] = mapped_column(String(40))
    updated_at: Mapped[str | None] = mapped_column(String(40))
