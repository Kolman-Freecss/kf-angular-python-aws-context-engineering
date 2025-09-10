from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func, desc, asc
from typing import List, Optional, Dict, Any
from models.task import Task, Category
from models.user import User
import logging

logger = logging.getLogger(__name__)

class QueryOptimizer:
    """Database query optimization utilities"""
    
    @staticmethod
    def get_tasks_optimized(
        db: Session,
        user_id: int,
        page: int = 1,
        per_page: int = 10,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category_id: Optional[int] = None,
        sort_by: str = 'created_at',
        sort_order: str = 'desc'
    ) -> Dict[str, Any]:
        """
        Optimized task query with proper joins and pagination
        """
        
        # Base query with eager loading to avoid N+1 queries
        query = db.query(Task).options(
            joinedload(Task.category)  # Eager load category to avoid N+1
        ).filter(Task.user_id == user_id)
        
        # Apply filters
        if status:
            query = query.filter(Task.status == status)
        if priority:
            query = query.filter(Task.priority == priority)
        if category_id:
            query = query.filter(Task.category_id == category_id)
        
        # Apply sorting
        sort_column = getattr(Task, sort_by, Task.created_at)
        if sort_order.lower() == 'desc':
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # Get total count efficiently
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        tasks = query.offset(offset).limit(per_page).all()
        
        return {
            'tasks': tasks,
            'total': total,
            'page': page,
            'per_page': per_page
        }
    
    @staticmethod
    def get_task_with_relations(
        db: Session,
        task_id: int,
        user_id: int
    ) -> Optional[Task]:
        """
        Get single task with all relations loaded efficiently
        """
        
        return db.query(Task).options(
            joinedload(Task.category),
            joinedload(Task.user)
        ).filter(
            Task.id == task_id,
            Task.user_id == user_id
        ).first()
    
    @staticmethod
    def get_categories_optimized(
        db: Session,
        user_id: int
    ) -> List[Category]:
        """
        Get categories with task counts efficiently
        """
        
        # Use subquery to get task counts
        task_counts = db.query(
            Task.category_id,
            func.count(Task.id).label('task_count')
        ).filter(Task.user_id == user_id).group_by(Task.category_id).subquery()
        
        # Join with categories
        categories = db.query(Category).outerjoin(
            task_counts,
            Category.id == task_counts.c.category_id
        ).filter(Category.user_id == user_id).all()
        
        return categories
    
    @staticmethod
    def get_task_analytics_optimized(
        db: Session,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Get task analytics with optimized queries
        """
        
        # Single query to get all status counts
        status_counts = db.query(
            Task.status,
            func.count(Task.id).label('count')
        ).filter(Task.user_id == user_id).group_by(Task.status).all()
        
        # Single query to get priority counts
        priority_counts = db.query(
            Task.priority,
            func.count(Task.id).label('count')
        ).filter(Task.user_id == user_id).group_by(Task.priority).all()
        
        # Single query to get category counts
        category_counts = db.query(
            Category.name,
            func.count(Task.id).label('count')
        ).join(Task, Category.id == Task.category_id).filter(
            Task.user_id == user_id
        ).group_by(Category.name).all()
        
        # Calculate totals
        total_tasks = sum(count.count for count in status_counts)
        completed_tasks = next(
            (count.count for count in status_counts if count.status == 'done'), 0
        )
        
        # Build result
        result = {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': next(
                (count.count for count in status_counts if count.status == 'todo'), 0
            ),
            'in_progress_tasks': next(
                (count.count for count in status_counts if count.status == 'in_progress'), 0
            ),
            'completion_rate': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2),
            'tasks_by_priority': {count.priority: count.count for count in priority_counts},
            'tasks_by_category': {count.name: count.count for count in category_counts}
        }
        
        return result
    
    @staticmethod
    def bulk_update_tasks(
        db: Session,
        user_id: int,
        task_ids: List[int],
        updates: Dict[str, Any]
    ) -> int:
        """
        Bulk update multiple tasks efficiently
        """
        
        updated_count = db.query(Task).filter(
            Task.id.in_(task_ids),
            Task.user_id == user_id
        ).update(updates, synchronize_session=False)
        
        db.commit()
        return updated_count
    
    @staticmethod
    def get_recent_tasks(
        db: Session,
        user_id: int,
        limit: int = 10
    ) -> List[Task]:
        """
        Get recent tasks with optimized query
        """
        
        return db.query(Task).options(
            joinedload(Task.category)
        ).filter(Task.user_id == user_id).order_by(
            desc(Task.updated_at)
        ).limit(limit).all()
    
    @staticmethod
    def search_tasks(
        db: Session,
        user_id: int,
        search_term: str,
        page: int = 1,
        per_page: int = 10
    ) -> Dict[str, Any]:
        """
        Full-text search for tasks
        """
        
        # Use ILIKE for case-insensitive search
        search_pattern = f"%{search_term}%"
        
        query = db.query(Task).options(
            joinedload(Task.category)
        ).filter(
            Task.user_id == user_id,
            (Task.title.ilike(search_pattern) | Task.description.ilike(search_pattern))
        ).order_by(desc(Task.created_at))
        
        total = query.count()
        
        offset = (page - 1) * per_page
        tasks = query.offset(offset).limit(per_page).all()
        
        return {
            'tasks': tasks,
            'total': total,
            'page': page,
            'per_page': per_page,
            'search_term': search_term
        }
    
    @staticmethod
    def get_user_dashboard_data(
        db: Session,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Get all dashboard data in optimized queries
        """
        
        # Get recent tasks
        recent_tasks = QueryOptimizer.get_recent_tasks(db, user_id, 5)
        
        # Get analytics
        analytics = QueryOptimizer.get_task_analytics_optimized(db, user_id)
        
        # Get categories with task counts
        categories = QueryOptimizer.get_categories_optimized(db, user_id)
        
        return {
            'recent_tasks': recent_tasks,
            'analytics': analytics,
            'categories': categories
        }
