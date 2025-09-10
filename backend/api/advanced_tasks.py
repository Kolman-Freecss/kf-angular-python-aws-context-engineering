from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import List, Optional, Dict, Any
from datetime import datetime

from core.database import get_db
from core.auth import get_current_user
from models.user import User
from models.task import Task, TaskDependency, TaskTemplate, TaskStatus, TaskPriority, Category
from schemas.task import (
    TaskDependencyCreate, TaskDependencyResponse,
    TaskTemplateCreate, TaskTemplateUpdate, TaskTemplateResponse,
    CreateTaskFromTemplate, BulkTaskOperation, TaskSearchRequest,
    TaskWithSubtasks, TaskListResponse
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# Task Dependencies
@router.post("/dependencies", response_model=TaskDependencyResponse)
async def create_task_dependency(
    dependency: TaskDependencyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a task dependency"""
    try:
        # Verify both tasks belong to the user
        task = db.query(Task).filter(
            and_(Task.id == dependency.task_id, Task.user_id == current_user.id)
        ).first()
        depends_on_task = db.query(Task).filter(
            and_(Task.id == dependency.depends_on_task_id, Task.user_id == current_user.id)
        ).first()
        
        if not task or not depends_on_task:
            raise HTTPException(status_code=404, detail="One or both tasks not found")
        
        # Check for circular dependencies
        if dependency.task_id == dependency.depends_on_task_id:
            raise HTTPException(status_code=400, detail="Task cannot depend on itself")
        
        # Check if dependency already exists
        existing = db.query(TaskDependency).filter(
            and_(
                TaskDependency.task_id == dependency.task_id,
                TaskDependency.depends_on_task_id == dependency.depends_on_task_id
            )
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Dependency already exists")
        
        # Create dependency
        db_dependency = TaskDependency(**dependency.dict())
        db.add(db_dependency)
        db.commit()
        db.refresh(db_dependency)
        
        return db_dependency
        
    except Exception as e:
        logger.error(f"Error creating task dependency: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create dependency")


@router.get("/dependencies/{task_id}", response_model=List[TaskDependencyResponse])
async def get_task_dependencies(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dependencies for a task"""
    try:
        # Verify task belongs to user
        task = db.query(Task).filter(
            and_(Task.id == task_id, Task.user_id == current_user.id)
        ).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        dependencies = db.query(TaskDependency).filter(
            TaskDependency.task_id == task_id
        ).all()
        
        return dependencies
        
    except Exception as e:
        logger.error(f"Error getting task dependencies: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get dependencies")


@router.delete("/dependencies/{dependency_id}")
async def delete_task_dependency(
    dependency_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a task dependency"""
    try:
        dependency = db.query(TaskDependency).join(Task).filter(
            and_(
                TaskDependency.id == dependency_id,
                Task.user_id == current_user.id
            )
        ).first()
        
        if not dependency:
            raise HTTPException(status_code=404, detail="Dependency not found")
        
        db.delete(dependency)
        db.commit()
        
        return {"message": "Dependency deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting task dependency: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete dependency")


# Task Templates
@router.post("/templates", response_model=TaskTemplateResponse)
async def create_task_template(
    template: TaskTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a task template"""
    try:
        # Validate category if provided
        if template.category_id:
            category = db.query(Category).filter(
                and_(Category.id == template.category_id, Category.user_id == current_user.id)
            ).first()
            if not category:
                raise HTTPException(status_code=404, detail="Category not found")
        
        db_template = TaskTemplate(
            **template.dict(),
            user_id=current_user.id
        )
        db.add(db_template)
        db.commit()
        db.refresh(db_template)
        
        return db_template
        
    except Exception as e:
        logger.error(f"Error creating task template: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create template")


@router.get("/templates", response_model=List[TaskTemplateResponse])
async def get_task_templates(
    include_public: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get task templates"""
    try:
        query = db.query(TaskTemplate).filter(
            or_(
                TaskTemplate.user_id == current_user.id,
                and_(TaskTemplate.is_public == True, include_public)
            )
        )
        
        templates = query.all()
        return templates
        
    except Exception as e:
        logger.error(f"Error getting task templates: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get templates")


@router.get("/templates/{template_id}", response_model=TaskTemplateResponse)
async def get_task_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific task template"""
    try:
        template = db.query(TaskTemplate).filter(
            and_(
                TaskTemplate.id == template_id,
                or_(
                    TaskTemplate.user_id == current_user.id,
                    TaskTemplate.is_public == True
                )
            )
        ).first()
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return template
        
    except Exception as e:
        logger.error(f"Error getting task template: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get template")


@router.put("/templates/{template_id}", response_model=TaskTemplateResponse)
async def update_task_template(
    template_id: int,
    template_update: TaskTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a task template"""
    try:
        template = db.query(TaskTemplate).filter(
            and_(TaskTemplate.id == template_id, TaskTemplate.user_id == current_user.id)
        ).first()
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        update_data = template_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(template, field, value)
        
        db.commit()
        db.refresh(template)
        
        return template
        
    except Exception as e:
        logger.error(f"Error updating task template: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update template")


@router.delete("/templates/{template_id}")
async def delete_task_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a task template"""
    try:
        template = db.query(TaskTemplate).filter(
            and_(TaskTemplate.id == template_id, TaskTemplate.user_id == current_user.id)
        ).first()
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        db.delete(template)
        db.commit()
        
        return {"message": "Template deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting task template: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete template")


@router.post("/templates/{template_id}/create-task", response_model=TaskWithSubtasks)
async def create_task_from_template(
    template_id: int,
    task_data: CreateTaskFromTemplate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a task from a template"""
    try:
        template = db.query(TaskTemplate).filter(
            and_(TaskTemplate.id == template_id, TaskTemplate.user_id == current_user.id)
        ).first()
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Create task from template
        task_dict = {
            "title": task_data.title or template.name,
            "description": template.description,
            "category_id": task_data.category_id or template.category_id,
            "priority": task_data.priority or template.priority,
            "estimated_duration": template.estimated_duration,
            "tags": template.tags,
            "due_date": task_data.due_date,
            "is_template": False,
            "template_name": template.name
        }
        
        db_task = Task(**task_dict, user_id=current_user.id)
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        
        # Update template usage count
        template.usage_count += 1
        db.commit()
        
        return db_task
        
    except Exception as e:
        logger.error(f"Error creating task from template: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create task from template")


# Advanced Task Operations
@router.get("/tasks/{task_id}/with-subtasks", response_model=TaskWithSubtasks)
async def get_task_with_subtasks(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a task with its subtasks and dependencies"""
    try:
        task = db.query(Task).filter(
            and_(Task.id == task_id, Task.user_id == current_user.id)
        ).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Get subtasks
        subtasks = db.query(Task).filter(
            and_(Task.parent_task_id == task_id, Task.user_id == current_user.id)
        ).all()
        
        # Get dependencies
        dependencies = db.query(TaskDependency).filter(
            TaskDependency.task_id == task_id
        ).all()
        
        # Get dependents
        dependents = db.query(TaskDependency).filter(
            TaskDependency.depends_on_task_id == task_id
        ).all()
        
        return TaskWithSubtasks(
            **task.__dict__,
            subtasks=subtasks,
            dependencies=dependencies,
            dependents=dependents
        )
        
    except Exception as e:
        logger.error(f"Error getting task with subtasks: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get task with subtasks")


@router.post("/tasks/bulk-operation")
async def bulk_task_operation(
    operation: BulkTaskOperation,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Perform bulk operations on tasks"""
    try:
        # Verify all tasks belong to user
        tasks = db.query(Task).filter(
            and_(Task.id.in_(operation.task_ids), Task.user_id == current_user.id)
        ).all()
        
        if len(tasks) != len(operation.task_ids):
            raise HTTPException(status_code=404, detail="Some tasks not found")
        
        updated_count = 0
        
        if operation.operation == "delete":
            for task in tasks:
                db.delete(task)
            updated_count = len(tasks)
            
        elif operation.operation == "update_status":
            status = operation.data.get("status")
            if not status:
                raise HTTPException(status_code=400, detail="Status is required")
            
            for task in tasks:
                task.status = status
            updated_count = len(tasks)
            
        elif operation.operation == "update_priority":
            priority = operation.data.get("priority")
            if not priority:
                raise HTTPException(status_code=400, detail="Priority is required")
            
            for task in tasks:
                task.priority = priority
            updated_count = len(tasks)
            
        elif operation.operation == "assign_category":
            category_id = operation.data.get("category_id")
            if category_id:
                # Verify category belongs to user
                category = db.query(Category).filter(
                    and_(Category.id == category_id, Category.user_id == current_user.id)
                ).first()
                if not category:
                    raise HTTPException(status_code=404, detail="Category not found")
            
            for task in tasks:
                task.category_id = category_id
            updated_count = len(tasks)
            
        else:
            raise HTTPException(status_code=400, detail="Invalid operation")
        
        db.commit()
        
        return {
            "message": f"Bulk operation completed successfully",
            "operation": operation.operation,
            "updated_count": updated_count
        }
        
    except Exception as e:
        logger.error(f"Error in bulk task operation: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to perform bulk operation")


@router.post("/tasks/search", response_model=TaskListResponse)
async def search_tasks(
    search_request: TaskSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Advanced task search with multiple filters"""
    try:
        query = db.query(Task).filter(Task.user_id == current_user.id)
        
        # Text search
        if search_request.query:
            query = query.filter(
                or_(
                    Task.title.ilike(f"%{search_request.query}%"),
                    Task.description.ilike(f"%{search_request.query}%")
                )
            )
        
        # Status filter
        if search_request.status:
            query = query.filter(Task.status.in_(search_request.status))
        
        # Priority filter
        if search_request.priority:
            query = query.filter(Task.priority.in_(search_request.priority))
        
        # Category filter
        if search_request.category_ids:
            query = query.filter(Task.category_id.in_(search_request.category_ids))
        
        # Tags filter
        if search_request.tags:
            for tag in search_request.tags:
                query = query.filter(Task.tags.contains([tag]))
        
        # Date filters
        if search_request.due_date_from:
            query = query.filter(Task.due_date >= search_request.due_date_from)
        if search_request.due_date_to:
            query = query.filter(Task.due_date <= search_request.due_date_to)
        
        if search_request.created_from:
            query = query.filter(Task.created_at >= search_request.created_from)
        if search_request.created_to:
            query = query.filter(Task.created_at <= search_request.created_to)
        
        # Subtasks filter
        if search_request.has_subtasks is not None:
            if search_request.has_subtasks:
                query = query.filter(Task.parent_task_id.isnot(None))
            else:
                query = query.filter(Task.parent_task_id.is_(None))
        
        # Dependencies filter
        if search_request.has_dependencies is not None:
            if search_request.has_dependencies:
                query = query.join(TaskDependency, Task.id == TaskDependency.task_id)
            else:
                query = query.outerjoin(TaskDependency, Task.id == TaskDependency.task_id)
                query = query.filter(TaskDependency.id.is_(None))
        
        # Template filter
        if search_request.is_template is not None:
            query = query.filter(Task.is_template == search_request.is_template)
        
        # Get total count
        total = query.count()
        
        # Sorting
        if search_request.sort_by == "title":
            sort_column = Task.title
        elif search_request.sort_by == "priority":
            sort_column = Task.priority
        elif search_request.sort_by == "due_date":
            sort_column = Task.due_date
        elif search_request.sort_by == "status":
            sort_column = Task.status
        else:
            sort_column = Task.created_at
        
        if search_request.sort_order == "asc":
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))
        
        # Pagination
        offset = (search_request.page - 1) * search_request.size
        tasks = query.offset(offset).limit(search_request.size).all()
        
        return TaskListResponse(
            tasks=tasks,
            total=total,
            page=search_request.page,
            size=search_request.size
        )
        
    except Exception as e:
        logger.error(f"Error searching tasks: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search tasks")


@router.post("/tasks/{task_id}/archive")
async def archive_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Archive a task (soft delete)"""
    try:
        task = db.query(Task).filter(
            and_(Task.id == task_id, Task.user_id == current_user.id)
        ).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # For now, we'll just mark it as completed
        # In a real implementation, you might have an archived status or separate table
        task.status = TaskStatus.DONE
        task.updated_at = datetime.now()
        
        db.commit()
        
        return {"message": "Task archived successfully"}
        
    except Exception as e:
        logger.error(f"Error archiving task: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to archive task")


@router.post("/tasks/{task_id}/duplicate")
async def duplicate_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Duplicate a task"""
    try:
        original_task = db.query(Task).filter(
            and_(Task.id == task_id, Task.user_id == current_user.id)
        ).first()
        
        if not original_task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Create duplicate
        duplicate_data = {
            "title": f"{original_task.title} (Copy)",
            "description": original_task.description,
            "status": TaskStatus.TODO,
            "priority": original_task.priority,
            "category_id": original_task.category_id,
            "estimated_duration": original_task.estimated_duration,
            "tags": original_task.tags,
            "is_template": False
        }
        
        db_duplicate = Task(**duplicate_data, user_id=current_user.id)
        db.add(db_duplicate)
        db.commit()
        db.refresh(db_duplicate)
        
        return {"message": "Task duplicated successfully", "duplicate_id": db_duplicate.id}
        
    except Exception as e:
        logger.error(f"Error duplicating task: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to duplicate task")
