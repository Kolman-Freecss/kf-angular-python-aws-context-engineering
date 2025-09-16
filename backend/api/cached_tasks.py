from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from core.cache import get_cache, CacheService
from models.task import Task, Category
from models.user import User
from schemas.task import TaskResponse, TaskCreate, TaskUpdate, TaskListResponse, CategoryResponse, CategoryCreate, CategoryUpdate
from api.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/tasks", response_model=TaskListResponse)
async def get_tasks_cached(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    cache: CacheService = Depends(get_cache),
    current_user: User = Depends(get_current_user)
):
    """Get tasks with caching for improved performance"""
    
    # Create cache key based on user and filters
    cache_key = f"tasks:user:{current_user.id}:page:{page}:per_page:{per_page}:status:{status}:priority:{priority}:category:{category_id}"
    
    # Try to get from cache first
    cached_result = cache.get(cache_key)
    if cached_result:
        logger.info(f"Cache hit for tasks: {cache_key}")
        return cached_result
    
    # If not in cache, query database
    logger.info(f"Cache miss for tasks: {cache_key}")
    query = db.query(Task).filter(Task.user_id == current_user.id)
    
    # Apply filters
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if category_id:
        query = query.filter(Task.category_id == category_id)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * per_page
    tasks = query.offset(offset).limit(per_page).all()
    
    # Convert to response format
    result = TaskListResponse(
        tasks=[TaskResponse.from_orm(task) for task in tasks],
        total=total,
        page=page,
        per_page=per_page
    )
    
    # Cache the result for 2 minutes
    cache.set(cache_key, result.dict(), ttl=120)
    
    return result

@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_cached(
    task_id: int,
    db: Session = Depends(get_db),
    cache: CacheService = Depends(get_cache),
    current_user: User = Depends(get_current_user)
):
    """Get single task with caching"""
    
    cache_key = f"task:user:{current_user.id}:id:{task_id}"
    
    # Try cache first
    cached_result = cache.get(cache_key)
    if cached_result:
        logger.info(f"Cache hit for task: {cache_key}")
        return cached_result
    
    # Query database
    logger.info(f"Cache miss for task: {cache_key}")
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    result = TaskResponse.from_orm(task)
    
    # Cache for 5 minutes
    cache.set(cache_key, result.dict(), ttl=300)
    
    return result

@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories_cached(
    db: Session = Depends(get_db),
    cache: CacheService = Depends(get_cache),
    current_user: User = Depends(get_current_user)
):
    """Get categories with caching"""
    
    cache_key = f"categories:user:{current_user.id}"
    
    # Try cache first
    cached_result = cache.get(cache_key)
    if cached_result:
        logger.info(f"Cache hit for categories: {cache_key}")
        return cached_result
    
    # Query database
    logger.info(f"Cache miss for categories: {cache_key}")
    categories = db.query(Category).filter(Category.user_id == current_user.id).all()
    
    result = [CategoryResponse.from_orm(category) for category in categories]
    
    # Cache for 10 minutes (categories change less frequently)
    cache.set(cache_key, [cat.dict() for cat in result], ttl=600)
    
    return result

@router.post("/tasks", response_model=TaskResponse)
async def create_task_cached(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    cache: CacheService = Depends(get_cache),
    current_user: User = Depends(get_current_user)
):
    """Create task and invalidate related cache"""
    
    # Create task
    task = Task(
        **task_data.dict(),
        user_id=current_user.id
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Invalidate task list cache for this user
    cache.delete_pattern(f"tasks:user:{current_user.id}:*")
    
    logger.info(f"Created task {task.id} and invalidated task list cache")
    
    return TaskResponse.from_orm(task)

@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task_cached(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    cache: CacheService = Depends(get_cache),
    current_user: User = Depends(get_current_user)
):
    """Update task and invalidate related cache"""
    
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update task
    for field, value in task_data.dict(exclude_unset=True).items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    
    # Invalidate caches
    cache.delete_pattern(f"tasks:user:{current_user.id}:*")
    cache.delete(f"task:user:{current_user.id}:id:{task_id}")
    
    logger.info(f"Updated task {task_id} and invalidated related caches")
    
    return TaskResponse.from_orm(task)

@router.delete("/tasks/{task_id}")
async def delete_task_cached(
    task_id: int,
    db: Session = Depends(get_db),
    cache: CacheService = Depends(get_cache),
    current_user: User = Depends(get_current_user)
):
    """Delete task and invalidate related cache"""
    
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    
    # Invalidate caches
    cache.delete_pattern(f"tasks:user:{current_user.id}:*")
    cache.delete(f"task:user:{current_user.id}:id:{task_id}")
    
    logger.info(f"Deleted task {task_id} and invalidated related caches")
    
    return {"message": "Task deleted successfully"}

@router.get("/tasks/analytics")
async def get_task_analytics_cached(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    cache: CacheService = Depends(get_cache),
    current_user: User = Depends(get_current_user)
):
    """Get task analytics with caching"""
    
    cache_key = f"analytics:user:{current_user.id}"
    
    # Try cache first
    cached_result = cache.get(cache_key)
    if cached_result:
        logger.info(f"Cache hit for analytics: {cache_key}")
        return cached_result
    
    # Calculate analytics
    logger.info(f"Cache miss for analytics: {cache_key}")
    
    # Get task counts by status
    total_tasks = db.query(Task).filter(Task.user_id == current_user.id).count()
    completed_tasks = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.status == 'done'
    ).count()
    pending_tasks = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.status == 'todo'
    ).count()
    in_progress_tasks = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.status == 'in_progress'
    ).count()
    
    # Calculate completion rate
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Get tasks by priority
    tasks_by_priority = {}
    for priority in ['low', 'medium', 'high', 'urgent']:
        count = db.query(Task).filter(
            Task.user_id == current_user.id,
            Task.priority == priority
        ).count()
        tasks_by_priority[priority] = count
    
    # Get tasks by category
    tasks_by_category = {}
    categories = db.query(Category).filter(Category.user_id == current_user.id).all()
    for category in categories:
        count = db.query(Task).filter(
            Task.user_id == current_user.id,
            Task.category_id == category.id
        ).count()
        tasks_by_category[category.name] = count
    
    result = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completion_rate': round(completion_rate, 2),
        'tasks_by_priority': tasks_by_priority,
        'tasks_by_category': tasks_by_category
    }
    
    # Cache for 5 minutes
    cache.set(cache_key, result, ttl=300)
    
    return result

@router.get("/cache/stats")
async def get_cache_stats(
    cache: CacheService = Depends(get_cache),
    current_user: User = Depends(get_current_user)
):
    """Get cache statistics (admin only)"""
    
    # In a real application, you'd check if user is admin
    stats = cache.get_stats()
    return {
        'cache_stats': stats,
        'user_id': current_user.id
    }

@router.delete("/cache/clear")
async def clear_user_cache(
    cache: CacheService = Depends(get_cache),
    current_user: User = Depends(get_current_user)
):
    """Clear cache for current user"""
    
    # Clear all cache entries for this user
    patterns = [
        f"tasks:user:{current_user.id}:*",
        f"task:user:{current_user.id}:*",
        f"categories:user:{current_user.id}",
        f"analytics:user:{current_user.id}"
    ]
    
    total_deleted = 0
    for pattern in patterns:
        deleted = cache.delete_pattern(pattern)
        total_deleted += deleted
    
    logger.info(f"Cleared {total_deleted} cache entries for user {current_user.id}")
    
    return {
        'message': f'Cleared {total_deleted} cache entries',
        'user_id': current_user.id
    }
