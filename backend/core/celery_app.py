from celery import Celery
from core.config import settings

# Create Celery instance
celery_app = Celery(
    "taskflow",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        'core.tasks.email_tasks',
        'core.tasks.background_tasks'
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Periodic tasks configuration
celery_app.conf.beat_schedule = {
    'send-task-reminders': {
        'task': 'core.tasks.email_tasks.send_task_reminders',
        'schedule': 3600.0,  # Every hour
    },
    'send-due-date-alerts': {
        'task': 'core.tasks.email_tasks.send_due_date_alerts',
        'schedule': 1800.0,  # Every 30 minutes
    },
    'cleanup-old-notifications': {
        'task': 'core.tasks.background_tasks.cleanup_old_notifications',
        'schedule': 86400.0,  # Daily
    },
}
