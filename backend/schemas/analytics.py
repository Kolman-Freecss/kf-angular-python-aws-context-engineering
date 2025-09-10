from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime


class AnalyticsOverview(BaseModel):
    total_tasks: int
    completed_tasks: int
    overdue_tasks: int
    completion_rate: float
    period_completion_rate: float
    tasks_created_period: int
    tasks_completed_period: int
    priority_distribution: Dict[str, int]
    status_distribution: Dict[str, int]
    period_days: int


class TaskTrends(BaseModel):
    created_tasks: Dict[str, int]
    completed_tasks: Dict[str, int]
    granularity: str
    period_days: int


class CategoryAnalytics(BaseModel):
    category_id: int
    category_name: str
    category_color: str
    total_tasks: int
    completed_tasks: int
    active_tasks: int
    completion_rate: float


class ProductivityMetrics(BaseModel):
    average_completion_time_hours: float
    hourly_productivity: Dict[int, int]
    daily_productivity: Dict[int, int]
    current_streak_days: int
    period_days: int


class TimeAnalytics(BaseModel):
    tasks_by_hour: Dict[int, int]
    tasks_by_day_of_week: Dict[int, int]
    overdue_trends: Dict[str, int]
    period_days: int


class ExportData(BaseModel):
    data: Dict[str, Any]
    format: str
    export_date: datetime
    record_count: int
