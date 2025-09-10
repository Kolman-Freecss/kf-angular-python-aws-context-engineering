from celery import current_task
from sqlalchemy.orm import Session
from core.database import get_db
from models.notification import Notification, NotificationStatus
from models.task import Task
from models.user import User
from typing import List, Dict, Any
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@current_task.task
def cleanup_old_notifications():
    """
    Clean up old notifications (older than 30 days)
    """
    db = next(get_db())
    try:
        cutoff_date = datetime.now() - timedelta(days=30)
        
        # Delete old notifications
        old_notifications = db.query(Notification).filter(
            Notification.created_at < cutoff_date
        ).all()
        
        deleted_count = len(old_notifications)
        for notification in old_notifications:
            db.delete(notification)
        
        db.commit()
        
        logger.info(f"Cleaned up {deleted_count} old notifications")
        return {
            'success': True, 
            'message': f'Cleaned up {deleted_count} old notifications',
            'deleted_count': deleted_count
        }

    except Exception as e:
        logger.error(f"Error cleaning up old notifications: {str(e)}")
        db.rollback()
        return {'success': False, 'error': str(e)}
    finally:
        db.close()


@current_task.task
def generate_analytics_report(user_id: int):
    """
    Generate analytics report for a user
    """
    db = next(get_db())
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User {user_id} not found")
            return {'success': False, 'error': 'User not found'}

        # Get task statistics
        total_tasks = db.query(Task).filter(Task.user_id == user_id).count()
        completed_tasks = db.query(Task).filter(
            Task.user_id == user_id,
            Task.status == 'done'
        ).count()
        
        overdue_tasks = db.query(Task).filter(
            Task.user_id == user_id,
            Task.status.in_(['todo', 'in_progress']),
            Task.due_date < datetime.now()
        ).count()

        # Calculate completion rate
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        # Get tasks by priority
        priority_stats = db.query(Task.priority, db.func.count(Task.id)).filter(
            Task.user_id == user_id
        ).group_by(Task.priority).all()

        # Get tasks by status
        status_stats = db.query(Task.status, db.func.count(Task.id)).filter(
            Task.user_id == user_id
        ).group_by(Task.status).all()

        # Get recent activity (last 7 days)
        recent_tasks = db.query(Task).filter(
            Task.user_id == user_id,
            Task.created_at >= datetime.now() - timedelta(days=7)
        ).count()

        analytics_data = {
            'user_id': user_id,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'overdue_tasks': overdue_tasks,
            'completion_rate': round(completion_rate, 2),
            'priority_distribution': dict(priority_stats),
            'status_distribution': dict(status_stats),
            'recent_activity': recent_tasks,
            'generated_at': datetime.now().isoformat()
        }

        logger.info(f"Analytics report generated for user {user_id}")
        return {
            'success': True,
            'message': 'Analytics report generated',
            'data': analytics_data
        }

    except Exception as e:
        logger.error(f"Error generating analytics report for user {user_id}: {str(e)}")
        db.rollback()
        return {'success': False, 'error': str(e)}
    finally:
        db.close()


@current_task.task
def process_file_upload(file_id: int):
    """
    Process uploaded file (resize images, generate thumbnails, etc.)
    """
    db = next(get_db())
    try:
        from models.file import TaskFile
        
        file_record = db.query(TaskFile).filter(TaskFile.id == file_id).first()
        if not file_record:
            logger.error(f"File {file_id} not found")
            return {'success': False, 'error': 'File not found'}

        # Here you would implement file processing logic
        # For example: image resizing, thumbnail generation, virus scanning, etc.
        
        # Update file status
        file_record.processed = True
        file_record.processed_at = datetime.now()
        db.commit()

        logger.info(f"File {file_id} processed successfully")
        return {
            'success': True,
            'message': 'File processed successfully',
            'file_id': file_id
        }

    except Exception as e:
        logger.error(f"Error processing file {file_id}: {str(e)}")
        db.rollback()
        return {'success': False, 'error': str(e)}
    finally:
        db.close()


@current_task.task
def send_task_completion_notification(task_id: int):
    """
    Send notification when a task is completed
    """
    db = next(get_db())
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            logger.error(f"Task {task_id} not found")
            return {'success': False, 'error': 'Task not found'}

        user = db.query(User).filter(User.id == task.user_id).first()
        if not user:
            logger.error(f"User {task.user_id} not found")
            return {'success': False, 'error': 'User not found'}

        # Check if user wants completion notifications
        if user.notification_preferences and not user.notification_preferences.task_completed_notifications:
            logger.info(f"Task completion notifications disabled for user {user.id}")
            return {'success': True, 'message': 'Task completion notifications disabled'}

        # Create notification
        notification = Notification(
            user_id=user.id,
            type='task_completed',
            title=f"Task Completed: {task.title}",
            message=f"Congratulations! You have completed the task: {task.title}",
            metadata={'task_id': task_id}
        )
        db.add(notification)
        db.commit()

        # Send email
        from core.tasks.email_tasks import send_notification_email
        send_notification_email.delay(notification.id)

        logger.info(f"Task completion notification sent for task {task_id}")
        return {'success': True, 'message': 'Task completion notification sent'}

    except Exception as e:
        logger.error(f"Error sending task completion notification for task {task_id}: {str(e)}")
        db.rollback()
        return {'success': False, 'error': str(e)}
    finally:
        db.close()


@current_task.task
def backup_user_data(user_id: int):
    """
    Create backup of user data
    """
    db = next(get_db())
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User {user_id} not found")
            return {'success': False, 'error': 'User not found'}

        # Get all user data
        user_data = {
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'updated_at': user.updated_at.isoformat() if user.updated_at else None
            },
            'tasks': [],
            'categories': [],
            'notifications': []
        }

        # Get tasks
        tasks = db.query(Task).filter(Task.user_id == user_id).all()
        for task in tasks:
            user_data['tasks'].append({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'status': task.status.value,
                'priority': task.priority.value,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'category_id': task.category_id,
                'created_at': task.created_at.isoformat() if task.created_at else None,
                'updated_at': task.updated_at.isoformat() if task.updated_at else None
            })

        # Get categories
        from models.task import Category
        categories = db.query(Category).filter(Category.user_id == user_id).all()
        for category in categories:
            user_data['categories'].append({
                'id': category.id,
                'name': category.name,
                'color': category.color,
                'created_at': category.created_at.isoformat() if category.created_at else None
            })

        # Get notifications
        notifications = db.query(Notification).filter(Notification.user_id == user_id).all()
        for notification in notifications:
            user_data['notifications'].append({
                'id': notification.id,
                'type': notification.type.value,
                'title': notification.title,
                'message': notification.message,
                'status': notification.status.value,
                'email_sent': notification.email_sent,
                'email_sent_at': notification.email_sent_at.isoformat() if notification.email_sent_at else None,
                'metadata': notification.metadata,
                'created_at': notification.created_at.isoformat() if notification.created_at else None,
                'updated_at': notification.updated_at.isoformat() if notification.updated_at else None
            })

        # Here you would typically save this data to S3 or another storage service
        # For now, we'll just log the backup
        logger.info(f"User data backup created for user {user_id}")
        
        return {
            'success': True,
            'message': 'User data backup created',
            'user_id': user_id,
            'backup_size': len(str(user_data))
        }

    except Exception as e:
        logger.error(f"Error creating backup for user {user_id}: {str(e)}")
        db.rollback()
        return {'success': False, 'error': str(e)}
    finally:
        db.close()
