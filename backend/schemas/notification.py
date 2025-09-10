from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime
from models.notification import NotificationType, NotificationStatus


class NotificationBase(BaseModel):
    type: NotificationType
    title: str
    message: str
    metadata: Optional[Dict[str, Any]] = None


class NotificationCreate(NotificationBase):
    user_id: int


class NotificationUpdate(BaseModel):
    status: Optional[NotificationStatus] = None
    email_sent: Optional[bool] = None
    email_sent_at: Optional[datetime] = None


class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    status: NotificationStatus
    email_sent: bool
    email_sent_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class NotificationPreferenceBase(BaseModel):
    email_enabled: bool = True
    task_reminders: bool = True
    due_date_alerts: bool = True
    task_completed_notifications: bool = True
    welcome_emails: bool = True
    category_notifications: bool = False
    file_notifications: bool = False
    reminder_frequency: str = "daily"


class NotificationPreferenceCreate(NotificationPreferenceBase):
    user_id: int


class NotificationPreferenceUpdate(BaseModel):
    email_enabled: Optional[bool] = None
    task_reminders: Optional[bool] = None
    due_date_alerts: Optional[bool] = None
    task_completed_notifications: Optional[bool] = None
    welcome_emails: Optional[bool] = None
    category_notifications: Optional[bool] = None
    file_notifications: Optional[bool] = None
    reminder_frequency: Optional[str] = None


class NotificationPreferenceResponse(NotificationPreferenceBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class EmailTemplateBase(BaseModel):
    name: str
    subject: str
    html_content: str
    text_content: Optional[str] = None
    template_type: NotificationType
    is_active: bool = True


class EmailTemplateCreate(EmailTemplateBase):
    pass


class EmailTemplateUpdate(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None
    html_content: Optional[str] = None
    text_content: Optional[str] = None
    template_type: Optional[NotificationType] = None
    is_active: Optional[bool] = None


class EmailTemplateResponse(EmailTemplateBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class SendNotificationRequest(BaseModel):
    user_id: int
    type: NotificationType
    title: str
    message: str
    metadata: Optional[Dict[str, Any]] = None


class UnsubscribeRequest(BaseModel):
    email: EmailStr
    token: str
