from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base
import enum


class NotificationType(str, enum.Enum):
    TASK_REMINDER = "task_reminder"
    DUE_DATE_ALERT = "due_date_alert"
    TASK_COMPLETED = "task_completed"
    WELCOME = "welcome"
    CATEGORY_CREATED = "category_created"
    FILE_UPLOADED = "file_uploaded"


class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    BOUNCED = "bounced"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING, nullable=False)
    email_sent = Column(Boolean, default=False)
    email_sent_at = Column(DateTime(timezone=True), nullable=True)
    metadata = Column(JSON, nullable=True)  # Store additional data like task_id, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="notifications")


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    email_enabled = Column(Boolean, default=True, nullable=False)
    task_reminders = Column(Boolean, default=True, nullable=False)
    due_date_alerts = Column(Boolean, default=True, nullable=False)
    task_completed_notifications = Column(Boolean, default=True, nullable=False)
    welcome_emails = Column(Boolean, default=True, nullable=False)
    category_notifications = Column(Boolean, default=False, nullable=False)
    file_notifications = Column(Boolean, default=False, nullable=False)
    reminder_frequency = Column(String(20), default="daily", nullable=False)  # daily, weekly, never
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="notification_preferences")


class EmailTemplate(Base):
    __tablename__ = "email_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    subject = Column(String(255), nullable=False)
    html_content = Column(Text, nullable=False)
    text_content = Column(Text, nullable=True)
    template_type = Column(Enum(NotificationType), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
