from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from api.auth import get_current_user
from models.user import User
from models.notification import Notification, NotificationPreference, EmailTemplate, NotificationType, NotificationStatus
from schemas.notification import (
    NotificationResponse, NotificationCreate, NotificationUpdate,
    NotificationPreferenceResponse, NotificationPreferenceCreate, NotificationPreferenceUpdate,
    EmailTemplateResponse, EmailTemplateCreate, EmailTemplateUpdate,
    SendNotificationRequest, UnsubscribeRequest
)
from core.tasks.email_tasks import send_notification_email, send_welcome_email
from core.tasks.background_tasks import generate_analytics_report
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/send", response_model=dict)
async def send_notification(
    request: SendNotificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send a notification to a user
    """
    try:
        # Check if user has permission to send notifications
        if current_user.id != request.user_id and not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )

        # Create notification
        notification = Notification(
            user_id=request.user_id,
            type=request.type,
            title=request.title,
            message=request.message,
            metadata=request.metadata
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)

        # Send email asynchronously
        try:
            if hasattr(send_notification_email, 'delay'):
                send_notification_email.delay(notification.id)
            else:
                send_notification_email(notification.id)
        except Exception as e:
            logger.error(f"Failed to send notification email: {e}")

        return {
            "success": True,
            "message": "Notification sent successfully",
            "notification_id": notification.id
        }

    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send notification"
        )


@router.get("/preferences", response_model=NotificationPreferenceResponse)
async def get_notification_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's notification preferences
    """
    preferences = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == current_user.id
    ).first()

    if not preferences:
        # Create default preferences
        preferences = NotificationPreference(
            user_id=current_user.id
        )
        db.add(preferences)
        db.commit()
        db.refresh(preferences)

    return preferences


@router.put("/preferences", response_model=NotificationPreferenceResponse)
async def update_notification_preferences(
    preferences_update: NotificationPreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update user's notification preferences
    """
    preferences = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == current_user.id
    ).first()

    if not preferences:
        # Create new preferences
        preferences_data = preferences_update.dict(exclude_unset=True)
        preferences_data['user_id'] = current_user.id
        preferences = NotificationPreference(**preferences_data)
        db.add(preferences)
    else:
        # Update existing preferences
        update_data = preferences_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(preferences, field, value)

    db.commit()
    db.refresh(preferences)
    return preferences


@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[NotificationStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's notifications
    """
    query = db.query(Notification).filter(Notification.user_id == current_user.id)

    if status_filter:
        query = query.filter(Notification.status == status_filter)

    notifications = query.offset(skip).limit(limit).all()
    return notifications


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific notification
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    return notification


@router.put("/{notification_id}", response_model=NotificationResponse)
async def update_notification(
    notification_id: int,
    notification_update: NotificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a notification
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    update_data = notification_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(notification, field, value)

    db.commit()
    db.refresh(notification)
    return notification


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a notification
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    db.delete(notification)
    db.commit()

    return {"success": True, "message": "Notification deleted"}


@router.post("/unsubscribe")
async def unsubscribe_from_emails(
    request: UnsubscribeRequest,
    db: Session = Depends(get_db)
):
    """
    Unsubscribe from email notifications
    """
    try:
        # Find user by email
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Update notification preferences
        preferences = db.query(NotificationPreference).filter(
            NotificationPreference.user_id == user.id
        ).first()

        if preferences:
            preferences.email_enabled = False
            preferences.task_reminders = False
            preferences.due_date_alerts = False
            preferences.task_completed_notifications = False
            preferences.welcome_emails = False
            preferences.category_notifications = False
            preferences.file_notifications = False
        else:
            preferences = NotificationPreference(
                user_id=user.id,
                email_enabled=False,
                task_reminders=False,
                due_date_alerts=False,
                task_completed_notifications=False,
                welcome_emails=False,
                category_notifications=False,
                file_notifications=False
            )
            db.add(preferences)

        db.commit()

        return {
            "success": True,
            "message": "Successfully unsubscribed from email notifications"
        }

    except Exception as e:
        logger.error(f"Error unsubscribing user: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unsubscribe"
        )


@router.post("/welcome/{user_id}")
async def send_welcome_notification(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send welcome notification to a user
    """
    # Check if user has permission
    if current_user.id != user_id and not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Queue welcome email
    try:
        if hasattr(send_welcome_email, 'delay'):
            send_welcome_email.delay(user_id)
        else:
            send_welcome_email(user_id)
    except Exception as e:
        logger.error(f"Failed to send welcome email: {e}")

    return {
        "success": True,
        "message": "Welcome notification queued"
    }


@router.post("/analytics/{user_id}")
async def generate_user_analytics(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate analytics report for a user
    """
    # Check if user has permission
    if current_user.id != user_id and not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Queue analytics generation
    try:
        if hasattr(generate_analytics_report, 'delay'):
            generate_analytics_report.delay(user_id)
        else:
            generate_analytics_report(user_id)
    except Exception as e:
        logger.error(f"Failed to generate analytics report: {e}")

    return {
        "success": True,
        "message": "Analytics report generation queued"
    }


# Email template management endpoints
@router.get("/templates/", response_model=List[EmailTemplateResponse])
async def get_email_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all email templates
    """
    templates = db.query(EmailTemplate).filter(EmailTemplate.is_active == True).all()
    return templates


@router.get("/templates/{template_id}", response_model=EmailTemplateResponse)
async def get_email_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific email template
    """
    template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email template not found"
        )
    return template


@router.post("/templates/", response_model=EmailTemplateResponse)
async def create_email_template(
    template: EmailTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new email template
    """
    # Check if template name already exists
    existing_template = db.query(EmailTemplate).filter(
        EmailTemplate.name == template.name
    ).first()
    
    if existing_template:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Template name already exists"
        )

    new_template = EmailTemplate(**template.dict())
    db.add(new_template)
    db.commit()
    db.refresh(new_template)
    return new_template


@router.put("/templates/{template_id}", response_model=EmailTemplateResponse)
async def update_email_template(
    template_id: int,
    template_update: EmailTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an email template
    """
    template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email template not found"
        )

    update_data = template_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)

    db.commit()
    db.refresh(template)
    return template


@router.delete("/templates/{template_id}")
async def delete_email_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an email template
    """
    template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email template not found"
        )

    db.delete(template)
    db.commit()

    return {"success": True, "message": "Email template deleted"}
