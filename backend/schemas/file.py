from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TaskFileBase(BaseModel):
    filename: str
    original_filename: str
    file_size: int
    content_type: str


class TaskFileResponse(TaskFileBase):
    id: int
    task_id: int
    user_id: int
    s3_key: str
    s3_bucket: str
    created_at: datetime

    class Config:
        from_attributes = True


class TaskFileListResponse(BaseModel):
    files: List[TaskFileResponse]
    total: int


class FileUploadResponse(BaseModel):
    file_id: int
    filename: str
    file_size: int
    content_type: str
    upload_url: Optional[str] = None
    message: str
