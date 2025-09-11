from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from core.database import get_db
from api.auth import get_current_user
from models.user import User
from models.task import Task, TaskStatus, TaskPriority, Category
from models.notification import Notification
from schemas.analytics import (
    AnalyticsOverview, TaskTrends, CategoryAnalytics, 
    ProductivityMetrics, TimeAnalytics, ExportData
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/overview", response_model=AnalyticsOverview)
async def get_analytics_overview(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get analytics overview for the user
    """
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Total tasks
        total_tasks = db.query(Task).filter(Task.user_id == current_user.id).count()
        
        # Completed tasks
        completed_tasks = db.query(Task).filter(
            and_(Task.user_id == current_user.id, Task.status == TaskStatus.DONE)
        ).count()
        
        # Overdue tasks
        overdue_tasks = db.query(Task).filter(
            and_(
                Task.user_id == current_user.id,
                Task.status.in_([TaskStatus.TODO, TaskStatus.IN_PROGRESS]),
                Task.due_date < end_date
            )
        ).count()
        
        # Tasks created in period
        tasks_created = db.query(Task).filter(
            and_(
                Task.user_id == current_user.id,
                Task.created_at >= start_date
            )
        ).count()
        
        # Tasks completed in period
        tasks_completed_period = db.query(Task).filter(
            and_(
                Task.user_id == current_user.id,
                Task.status == TaskStatus.DONE,
                Task.updated_at >= start_date
            )
        ).count()
        
        # Calculate completion rate
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Calculate period completion rate
        period_completion_rate = (tasks_completed_period / tasks_created * 100) if tasks_created > 0 else 0
        
        # Priority distribution
        priority_stats = db.query(
            Task.priority, func.count(Task.id)
        ).filter(Task.user_id == current_user.id).group_by(Task.priority).all()
        
        priority_distribution = {priority.value: count for priority, count in priority_stats}
        
        # Status distribution
        status_stats = db.query(
            Task.status, func.count(Task.id)
        ).filter(Task.user_id == current_user.id).group_by(Task.status).all()
        
        status_distribution = {status.value: count for status, count in status_stats}
        
        return AnalyticsOverview(
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            overdue_tasks=overdue_tasks,
            completion_rate=round(completion_rate, 2),
            period_completion_rate=round(period_completion_rate, 2),
            tasks_created_period=tasks_created,
            tasks_completed_period=tasks_completed_period,
            priority_distribution=priority_distribution,
            status_distribution=status_distribution,
            period_days=days
        )
        
    except Exception as e:
        logger.error(f"Error getting analytics overview: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get analytics overview"
        )


@router.get("/trends", response_model=TaskTrends)
async def get_task_trends(
    days: int = Query(30, ge=1, le=365),
    granularity: str = Query("daily", pattern="^(daily|weekly|monthly)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get task trends over time
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Determine date truncation based on granularity
        if granularity == "daily":
            date_trunc = func.date_trunc('day', Task.created_at)
        elif granularity == "weekly":
            date_trunc = func.date_trunc('week', Task.created_at)
        else:  # monthly
            date_trunc = func.date_trunc('month', Task.created_at)
        
        # Tasks created over time
        created_trends = db.query(
            date_trunc.label('date'),
            func.count(Task.id).label('count')
        ).filter(
            and_(
                Task.user_id == current_user.id,
                Task.created_at >= start_date
            )
        ).group_by(date_trunc).order_by(date_trunc).all()
        
        # Tasks completed over time
        completed_trends = db.query(
            date_trunc.label('date'),
            func.count(Task.id).label('count')
        ).filter(
            and_(
                Task.user_id == current_user.id,
                Task.status == TaskStatus.DONE,
                Task.updated_at >= start_date
            )
        ).group_by(date_trunc).order_by(date_trunc).all()
        
        # Convert to dictionaries
        created_data = {str(trend.date.date()): trend.count for trend in created_trends}
        completed_data = {str(trend.date.date()): trend.count for trend in completed_trends}
        
        return TaskTrends(
            created_tasks=created_data,
            completed_tasks=completed_data,
            granularity=granularity,
            period_days=days
        )
        
    except Exception as e:
        logger.error(f"Error getting task trends: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get task trends"
        )


@router.get("/categories", response_model=List[CategoryAnalytics])
async def get_category_analytics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get analytics by category
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get categories with task counts
        category_stats = db.query(
            Category.id,
            Category.name,
            Category.color,
            func.count(Task.id).label('total_tasks'),
            func.count(func.case([(Task.status == TaskStatus.DONE, 1)])).label('completed_tasks'),
            func.count(func.case([(Task.status.in_([TaskStatus.TODO, TaskStatus.IN_PROGRESS]), 1)])).label('active_tasks')
        ).outerjoin(Task, and_(
            Task.category_id == Category.id,
            Task.user_id == current_user.id
        )).filter(Category.user_id == current_user.id).group_by(
            Category.id, Category.name, Category.color
        ).all()
        
        analytics = []
        for stat in category_stats:
            completion_rate = (stat.completed_tasks / stat.total_tasks * 100) if stat.total_tasks > 0 else 0
            
            analytics.append(CategoryAnalytics(
                category_id=stat.id,
                category_name=stat.name,
                category_color=stat.color,
                total_tasks=stat.total_tasks,
                completed_tasks=stat.completed_tasks,
                active_tasks=stat.active_tasks,
                completion_rate=round(completion_rate, 2)
            ))
        
        return analytics
        
    except Exception as e:
        logger.error(f"Error getting category analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get category analytics"
        )


@router.get("/productivity", response_model=ProductivityMetrics)
async def get_productivity_metrics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get productivity metrics
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Average completion time (for completed tasks)
        completed_tasks = db.query(Task).filter(
            and_(
                Task.user_id == current_user.id,
                Task.status == TaskStatus.DONE,
                Task.created_at >= start_date,
                Task.updated_at >= start_date
            )
        ).all()
        
        completion_times = []
        for task in completed_tasks:
            if task.created_at and task.updated_at:
                completion_time = (task.updated_at - task.created_at).total_seconds() / 3600  # hours
                completion_times.append(completion_time)
        
        avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
        
        # Most productive hours (based on task creation)
        hourly_stats = db.query(
            func.extract('hour', Task.created_at).label('hour'),
            func.count(Task.id).label('count')
        ).filter(
            and_(
                Task.user_id == current_user.id,
                Task.created_at >= start_date
            )
        ).group_by(func.extract('hour', Task.created_at)).all()
        
        hourly_productivity = {int(stat.hour): stat.count for stat in hourly_stats}
        
        # Most productive days (based on task completion)
        daily_stats = db.query(
            func.extract('dow', Task.updated_at).label('day_of_week'),
            func.count(Task.id).label('count')
        ).filter(
            and_(
                Task.user_id == current_user.id,
                Task.status == TaskStatus.DONE,
                Task.updated_at >= start_date
            )
        ).group_by(func.extract('dow', Task.updated_at)).all()
        
        daily_productivity = {int(stat.day_of_week): stat.count for stat in daily_stats}
        
        # Streak calculation (consecutive days with task completion)
        completed_dates = db.query(
            func.date(Task.updated_at).label('completion_date')
        ).filter(
            and_(
                Task.user_id == current_user.id,
                Task.status == TaskStatus.DONE,
                Task.updated_at >= start_date
            )
        ).distinct().order_by(func.date(Task.updated_at).desc()).all()
        
        current_streak = 0
        if completed_dates:
            current_date = end_date.date()
            for date_obj in completed_dates:
                if date_obj.completion_date == current_date:
                    current_streak += 1
                    current_date -= timedelta(days=1)
                else:
                    break
        
        return ProductivityMetrics(
            average_completion_time_hours=round(avg_completion_time, 2),
            hourly_productivity=hourly_productivity,
            daily_productivity=daily_productivity,
            current_streak_days=current_streak,
            period_days=days
        )
        
    except Exception as e:
        logger.error(f"Error getting productivity metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get productivity metrics"
        )


@router.get("/time", response_model=TimeAnalytics)
async def get_time_analytics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get time-based analytics
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Tasks by time of day
        time_stats = db.query(
            func.extract('hour', Task.created_at).label('hour'),
            func.count(Task.id).label('count')
        ).filter(
            and_(
                Task.user_id == current_user.id,
                Task.created_at >= start_date
            )
        ).group_by(func.extract('hour', Task.created_at)).all()
        
        tasks_by_hour = {int(stat.hour): stat.count for stat in time_stats}
        
        # Tasks by day of week
        dow_stats = db.query(
            func.extract('dow', Task.created_at).label('day_of_week'),
            func.count(Task.id).label('count')
        ).filter(
            and_(
                Task.user_id == current_user.id,
                Task.created_at >= start_date
            )
        ).group_by(func.extract('dow', Task.created_at)).all()
        
        tasks_by_day = {int(stat.day_of_week): stat.count for stat in dow_stats}
        
        # Overdue trends
        overdue_trends = db.query(
            func.date_trunc('day', Task.due_date).label('date'),
            func.count(Task.id).label('count')
        ).filter(
            and_(
                Task.user_id == current_user.id,
                Task.status.in_([TaskStatus.TODO, TaskStatus.IN_PROGRESS]),
                Task.due_date < end_date,
                Task.due_date >= start_date
            )
        ).group_by(func.date_trunc('day', Task.due_date)).order_by(func.date_trunc('day', Task.due_date)).all()
        
        overdue_data = {str(trend.date.date()): trend.count for trend in overdue_trends}
        
        return TimeAnalytics(
            tasks_by_hour=tasks_by_hour,
            tasks_by_day_of_week=tasks_by_day,
            overdue_trends=overdue_data,
            period_days=days
        )
        
    except Exception as e:
        logger.error(f"Error getting time analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get time analytics"
        )


@router.get("/export", response_model=ExportData)
async def export_analytics_data(
    format: str = Query("json", pattern="^(json|csv)$"),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export analytics data
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get all tasks in period
        tasks = db.query(Task).filter(
            and_(
                Task.user_id == current_user.id,
                Task.created_at >= start_date
            )
        ).all()
        
        # Get all notifications in period
        notifications = db.query(Notification).filter(
            and_(
                Notification.user_id == current_user.id,
                Notification.created_at >= start_date
            )
        ).all()
        
        # Prepare export data
        tasks_data = []
        for task in tasks:
            tasks_data.append({
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
        
        notifications_data = []
        for notification in notifications:
            notifications_data.append({
                'id': notification.id,
                'type': notification.type.value,
                'title': notification.title,
                'message': notification.message,
                'status': notification.status.value,
                'email_sent': notification.email_sent,
                'email_sent_at': notification.email_sent_at.isoformat() if notification.email_sent_at else None,
                'created_at': notification.created_at.isoformat() if notification.created_at else None
            })
        
        export_data = {
            'user_id': current_user.id,
            'export_date': end_date.isoformat(),
            'period_days': days,
            'tasks': tasks_data,
            'notifications': notifications_data,
            'summary': {
                'total_tasks': len(tasks_data),
                'total_notifications': len(notifications_data),
                'completed_tasks': len([t for t in tasks_data if t['status'] == 'done']),
                'overdue_tasks': len([t for t in tasks_data if t['due_date'] and datetime.fromisoformat(t['due_date'].replace('Z', '+00:00')) < end_date and t['status'] in ['todo', 'in_progress']])
            }
        }
        
        return ExportData(
            data=export_data,
            format=format,
            export_date=end_date,
            record_count=len(tasks_data) + len(notifications_data)
        )
        
    except Exception as e:
        logger.error(f"Error exporting analytics data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to export analytics data"
        )
