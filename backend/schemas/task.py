from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from models.task import TaskStatus, TaskPriority


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None
    category_id: Optional[int] = None
    parent_task_id: Optional[int] = None
    estimated_duration: Optional[int] = None  # in minutes
    actual_duration: Optional[int] = None  # in minutes
    tags: Optional[List[str]] = None
    is_template: bool = False
    template_name: Optional[str] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    category_id: Optional[int] = None
    parent_task_id: Optional[int] = None
    estimated_duration: Optional[int] = None
    actual_duration: Optional[int] = None
    tags: Optional[List[str]] = None
    is_template: Optional[bool] = None
    template_name: Optional[str] = None


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class TaskPriorityUpdate(BaseModel):
    priority: TaskPriority


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    color: str = Field(default="#3498db", regex=r"^#[0-9A-Fa-f]{6}$")


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    color: Optional[str] = Field(None, regex=r"^#[0-9A-Fa-f]{6}$")


class CategoryResponse(CategoryBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class TaskResponse(TaskBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    category: Optional[CategoryResponse] = None

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]
    total: int
    page: int
    size: int


# Task Dependency Schemas
class TaskDependencyBase(BaseModel):
    task_id: int
    depends_on_task_id: int
    dependency_type: str = "finish_to_start"


class TaskDependencyCreate(TaskDependencyBase):
    pass


class TaskDependencyResponse(TaskDependencyBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Task Template Schemas
class TaskTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category_id: Optional[int] = None
    estimated_duration: Optional[int] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    tags: Optional[List[str]] = None
    template_data: Optional[Dict[str, Any]] = None
    is_public: bool = False


class TaskTemplateCreate(TaskTemplateBase):
    pass


class TaskTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category_id: Optional[int] = None
    estimated_duration: Optional[int] = None
    priority: Optional[TaskPriority] = None
    tags: Optional[List[str]] = None
    template_data: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None


class TaskTemplateResponse(TaskTemplateBase):
    id: int
    user_id: int
    usage_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Advanced Task Management Schemas
class TaskWithSubtasks(TaskResponse):
    subtasks: List[TaskResponse] = []
    dependencies: List[TaskDependencyResponse] = []
    dependents: List[TaskDependencyResponse] = []


class CreateTaskFromTemplate(BaseModel):
    template_id: int
    title: Optional[str] = None
    due_date: Optional[datetime] = None
    category_id: Optional[int] = None
    priority: Optional[TaskPriority] = None


class BulkTaskOperation(BaseModel):
    task_ids: List[int]
    operation: str  # "delete", "update_status", "update_priority", "assign_category"
    data: Optional[Dict[str, Any]] = None


class TaskSearchRequest(BaseModel):
    query: Optional[str] = None
    status: Optional[List[TaskStatus]] = None
    priority: Optional[List[TaskPriority]] = None
    category_ids: Optional[List[int]] = None
    tags: Optional[List[str]] = None
    due_date_from: Optional[datetime] = None
    due_date_to: Optional[datetime] = None
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None
    has_subtasks: Optional[bool] = None
    has_dependencies: Optional[bool] = None
    is_template: Optional[bool] = None
    page: int = 1
    size: int = 10
    sort_by: str = "created_at"
    sort_order: str = "desc"
