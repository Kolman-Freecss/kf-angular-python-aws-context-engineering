from celery import current_task
from sqlalchemy.orm import Session
from core.database import get_db
from core.ses_service import ses_service
from models.notification import Notification, NotificationStatus, NotificationType
from models.user import User
from models.task import Task
from schemas.notification import NotificationCreate
from typing import List, Dict, Any
import logging
from datetime import datetime, timedelta
from jinja2 import Template

logger = logging.getLogger(__name__)

# Email templates
EMAIL_TEMPLATES = {
    NotificationType.TASK_REMINDER: {
        'subject': 'Task Reminder: {{ task_title }}',
        'html': '''
        <html>
        <body>
            <h2>Task Reminder</h2>
            <p>Hello {{ user_name }},</p>
            <p>This is a reminder about your task: <strong>{{ task_title }}</strong></p>
            <p><strong>Description:</strong> {{ task_description }}</p>
            <p><strong>Priority:</strong> {{ task_priority }}</p>
            <p><strong>Due Date:</strong> {{ task_due_date }}</p>
            <p>Please complete this task as soon as possible.</p>
            <br>
            <p>Best regards,<br>TaskFlow Team</p>
        </body>
        </html>
        ''',
        'text': '''
        Task Reminder
        
        Hello {{ user_name }},
        
        This is a reminder about your task: {{ task_title }}
        
        Description: {{ task_description }}
        Priority: {{ task_priority }}
        Due Date: {{ task_due_date }}
        
        Please complete this task as soon as possible.
        
        Best regards,
        TaskFlow Team
        '''
    },
    NotificationType.DUE_DATE_ALERT: {
        'subject': 'URGENT: Task Due Soon - {{ task_title }}',
        'html': '''
        <html>
        <body>
            <h2 style="color: #e74c3c;">URGENT: Task Due Soon</h2>
            <p>Hello {{ user_name }},</p>
            <p>Your task <strong>{{ task_title }}</strong> is due soon!</p>
            <p><strong>Due Date:</strong> {{ task_due_date }}</p>
            <p><strong>Priority:</strong> {{ task_priority }}</p>
            <p style="color: #e74c3c;"><strong>Please complete this task immediately!</strong></p>
            <br>
            <p>Best regards,<br>TaskFlow Team</p>
        </body>
        </html>
        ''',
        'text': '''
        URGENT: Task Due Soon
        
        Hello {{ user_name }},
        
        Your task {{ task_title }} is due soon!
        
        Due Date: {{ task_due_date }}
        Priority: {{ task_priority }}
        
        Please complete this task immediately!
        
        Best regards,
        TaskFlow Team
        '''
    },
    NotificationType.TASK_COMPLETED: {
        'subject': 'Task Completed: {{ task_title }}',
        'html': '''
        <html>
        <body>
            <h2 style="color: #27ae60;">Task Completed!</h2>
            <p>Hello {{ user_name }},</p>
            <p>Congratulations! You have completed the task: <strong>{{ task_title }}</strong></p>
            <p><strong>Completed at:</strong> {{ completion_time }}</p>
            <p>Great job on staying productive!</p>
            <br>
            <p>Best regards,<br>TaskFlow Team</p>
        </body>
        </html>
        ''',
        'text': '''
        Task Completed!
        
        Hello {{ user_name }},
        
        Congratulations! You have completed the task: {{ task_title }}
        
        Completed at: {{ completion_time }}
        
        Great job on staying productive!
        
        Best regards,
        TaskFlow Team
        '''
    },
    NotificationType.WELCOME: {
        'subject': 'Welcome to TaskFlow!',
        'html': '''
        <html>
        <body>
            <h2>Welcome to TaskFlow!</h2>
            <p>Hello {{ user_name }},</p>
            <p>Welcome to TaskFlow! We're excited to help you stay organized and productive.</p>
            <p>Here are some tips to get started:</p>
            <ul>
                <li>Create your first task</li>
                <li>Set up categories to organize your work</li>
                <li>Use priorities to focus on what's important</li>
                <li>Set due dates to stay on track</li>
            </ul>
            <p>If you have any questions, feel free to reach out to our support team.</p>
            <br>
            <p>Best regards,<br>TaskFlow Team</p>
        </body>
        </html>
        ''',
        'text': '''
        Welcome to TaskFlow!
        
        Hello {{ user_name }},
        
        Welcome to TaskFlow! We're excited to help you stay organized and productive.
        
        Here are some tips to get started:
        - Create your first task
        - Set up categories to organize your work
        - Use priorities to focus on what's important
        - Set due dates to stay on track
        
        If you have any questions, feel free to reach out to our support team.
        
        Best regards,
        TaskFlow Team
        '''
    }
}


@current_task.task(bind=True)
def send_notification_email(self, notification_id: int):
    """
    Send a notification email
    """
    db = next(get_db())
    try:
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            logger.error(f"Notification {notification_id} not found")
            return {'success': False, 'error': 'Notification not found'}

        user = db.query(User).filter(User.id == notification.user_id).first()
        if not user:
            logger.error(f"User {notification.user_id} not found")
            return {'success': False, 'error': 'User not found'}

        # Check if user has email notifications enabled
        if user.notification_preferences and not user.notification_preferences.email_enabled:
            logger.info(f"Email notifications disabled for user {user.id}")
            notification.status = NotificationStatus.SENT
            notification.email_sent = False
            db.commit()
            return {'success': True, 'message': 'Email notifications disabled'}

        # Get email template
        template_data = EMAIL_TEMPLATES.get(notification.type)
        if not template_data:
            logger.error(f"No template found for notification type {notification.type}")
            return {'success': False, 'error': 'No template found'}

        # Prepare template data
        template_context = {
            'user_name': user.full_name,
            'user_email': user.email,
        }

        # Add task-specific data if available
        if notification.metadata and 'task_id' in notification.metadata:
            task = db.query(Task).filter(Task.id == notification.metadata['task_id']).first()
            if task:
                template_context.update({
                    'task_title': task.title,
                    'task_description': task.description or 'No description',
                    'task_priority': task.priority.value.title(),
                    'task_due_date': task.due_date.strftime('%Y-%m-%d %H:%M') if task.due_date else 'No due date',
                    'completion_time': datetime.now().strftime('%Y-%m-%d %H:%M')
                })

        # Render templates
        subject_template = Template(template_data['subject'])
        html_template = Template(template_data['html'])
        text_template = Template(template_data['text'])

        subject = subject_template.render(**template_context)
        html_content = html_template.render(**template_context)
        text_content = text_template.render(**template_context)

        # Send email
        result = ses_service.send_email(
            to_email=user.email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )

        if result['success']:
            notification.status = NotificationStatus.SENT
            notification.email_sent = True
            notification.email_sent_at = datetime.now()
            logger.info(f"Email sent successfully for notification {notification_id}")
        else:
            notification.status = NotificationStatus.FAILED
            logger.error(f"Failed to send email for notification {notification_id}: {result.get('error_message')}")

        db.commit()
        return result

    except Exception as e:
        logger.error(f"Error sending notification email {notification_id}: {str(e)}")
        db.rollback()
        return {'success': False, 'error': str(e)}
    finally:
        db.close()


@current_task.task
def send_task_reminders():
    """
    Send reminders for tasks that need attention
    """
    db = next(get_db())
    try:
        # Find users who want task reminders
        users_with_reminders = db.query(User).join(User.notification_preferences).filter(
            User.notification_preferences.has(task_reminders=True)
        ).all()

        for user in users_with_reminders:
            # Find tasks that need reminders (created more than 24 hours ago, still TODO)
            reminder_tasks = db.query(Task).filter(
                Task.user_id == user.id,
                Task.status == 'todo',
                Task.created_at < datetime.now() - timedelta(hours=24)
            ).all()

            for task in reminder_tasks:
                # Check if we already sent a reminder recently
                recent_reminder = db.query(Notification).filter(
                    Notification.user_id == user.id,
                    Notification.type == NotificationType.TASK_REMINDER,
                    Notification.metadata.contains({'task_id': task.id}),
                    Notification.created_at > datetime.now() - timedelta(hours=24)
                ).first()

                if not recent_reminder:
                    # Create notification
                    notification = Notification(
                        user_id=user.id,
                        type=NotificationType.TASK_REMINDER,
                        title=f"Task Reminder: {task.title}",
                        message=f"This is a reminder about your task: {task.title}",
                        metadata={'task_id': task.id}
                    )
                    db.add(notification)
                    db.commit()

                    # Send email
                    send_notification_email.delay(notification.id)

        logger.info("Task reminders processed successfully")
        return {'success': True, 'message': 'Task reminders processed'}

    except Exception as e:
        logger.error(f"Error processing task reminders: {str(e)}")
        db.rollback()
        return {'success': False, 'error': str(e)}
    finally:
        db.close()


@current_task.task
def send_due_date_alerts():
    """
    Send alerts for tasks that are due soon
    """
    db = next(get_db())
    try:
        # Find users who want due date alerts
        users_with_alerts = db.query(User).join(User.notification_preferences).filter(
            User.notification_preferences.has(due_date_alerts=True)
        ).all()

        for user in users_with_alerts:
            # Find tasks due in the next 2 hours
            due_soon_tasks = db.query(Task).filter(
                Task.user_id == user.id,
                Task.status.in_(['todo', 'in_progress']),
                Task.due_date.isnot(None),
                Task.due_date <= datetime.now() + timedelta(hours=2),
                Task.due_date > datetime.now()
            ).all()

            for task in due_soon_tasks:
                # Check if we already sent an alert recently
                recent_alert = db.query(Notification).filter(
                    Notification.user_id == user.id,
                    Notification.type == NotificationType.DUE_DATE_ALERT,
                    Notification.metadata.contains({'task_id': task.id}),
                    Notification.created_at > datetime.now() - timedelta(hours=1)
                ).first()

                if not recent_alert:
                    # Create notification
                    notification = Notification(
                        user_id=user.id,
                        type=NotificationType.DUE_DATE_ALERT,
                        title=f"URGENT: Task Due Soon - {task.title}",
                        message=f"Your task '{task.title}' is due soon!",
                        metadata={'task_id': task.id}
                    )
                    db.add(notification)
                    db.commit()

                    # Send email
                    send_notification_email.delay(notification.id)

        logger.info("Due date alerts processed successfully")
        return {'success': True, 'message': 'Due date alerts processed'}

    except Exception as e:
        logger.error(f"Error processing due date alerts: {str(e)}")
        db.rollback()
        return {'success': False, 'error': str(e)}
    finally:
        db.close()


@current_task.task
def send_welcome_email(user_id: int):
    """
    Send welcome email to new user
    """
    db = next(get_db())
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User {user_id} not found")
            return {'success': False, 'error': 'User not found'}

        # Check if user wants welcome emails
        if user.notification_preferences and not user.notification_preferences.welcome_emails:
            logger.info(f"Welcome emails disabled for user {user_id}")
            return {'success': True, 'message': 'Welcome emails disabled'}

        # Create notification
        notification = Notification(
            user_id=user.id,
            type=NotificationType.WELCOME,
            title="Welcome to TaskFlow!",
            message="Welcome to TaskFlow! We're excited to help you stay organized and productive.",
            metadata={'user_id': user_id}
        )
        db.add(notification)
        db.commit()

        # Send email
        send_notification_email.delay(notification.id)

        logger.info(f"Welcome email queued for user {user_id}")
        return {'success': True, 'message': 'Welcome email queued'}

    except Exception as e:
        logger.error(f"Error sending welcome email to user {user_id}: {str(e)}")
        db.rollback()
        return {'success': False, 'error': str(e)}
    finally:
        db.close()
