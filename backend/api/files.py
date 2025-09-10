from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import os

from core.database import get_db
from models.user import User
from models.task import Task
from models.file import TaskFile
from schemas.file import TaskFileResponse, TaskFileListResponse, FileUploadResponse
from api.auth import get_current_user
from core.s3_service import s3_service

router = APIRouter()

# Allowed file types and size limits
ALLOWED_EXTENSIONS = {
    'image': ['jpg', 'jpeg', 'png', 'gif', 'webp'],
    'document': ['pdf', 'doc', 'docx', 'txt', 'rtf'],
    'spreadsheet': ['xls', 'xlsx', 'csv'],
    'presentation': ['ppt', 'pptx'],
    'archive': ['zip', 'rar', '7z', 'tar', 'gz']
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def validate_file(file: UploadFile) -> None:
    """Validate uploaded file"""
    # Check file size
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413, 
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Check file extension
    if file.filename:
        file_extension = file.filename.split('.')[-1].lower()
        all_allowed_extensions = []
        for extensions in ALLOWED_EXTENSIONS.values():
            all_allowed_extensions.extend(extensions)
        
        if file_extension not in all_allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type '{file_extension}' is not allowed. Allowed types: {', '.join(all_allowed_extensions)}"
            )


def get_file_category(content_type: str, filename: str) -> str:
    """Determine file category based on content type and extension"""
    file_extension = filename.split('.')[-1].lower() if filename else ''
    
    for category, extensions in ALLOWED_EXTENSIONS.items():
        if file_extension in extensions:
            return category
    
    # Fallback to content type
    if content_type.startswith('image/'):
        return 'image'
    elif content_type.startswith('text/'):
        return 'document'
    elif 'pdf' in content_type:
        return 'document'
    elif 'spreadsheet' in content_type or 'excel' in content_type:
        return 'spreadsheet'
    elif 'presentation' in content_type or 'powerpoint' in content_type:
        return 'presentation'
    else:
        return 'document'


@router.post("/tasks/{task_id}/files", response_model=FileUploadResponse)
async def upload_file_to_task(
    task_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a file to a specific task"""
    # Validate task exists and belongs to user
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Validate file
    validate_file(file)
    
    # Read file content
    file_content = await file.read()
    
    # Generate S3 key
    s3_key = s3_service.generate_file_key(current_user.id, task_id, file.filename)
    
    # Upload to S3
    s3_service.upload_file(file_content, s3_key, file.content_type)
    
    # Save file record to database
    db_file = TaskFile(
        filename=file.filename,
        original_filename=file.filename,
        file_size=len(file_content),
        content_type=file.content_type,
        s3_key=s3_key,
        s3_bucket=s3_service.bucket_name,
        task_id=task_id,
        user_id=current_user.id
    )
    
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    
    return FileUploadResponse(
        file_id=db_file.id,
        filename=db_file.filename,
        file_size=db_file.file_size,
        content_type=db_file.content_type,
        message="File uploaded successfully"
    )


@router.get("/tasks/{task_id}/files", response_model=TaskFileListResponse)
async def get_task_files(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all files for a specific task"""
    # Validate task exists and belongs to user
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Get files for the task
    files = db.query(TaskFile).filter(
        TaskFile.task_id == task_id,
        TaskFile.user_id == current_user.id
    ).all()
    
    return TaskFileListResponse(
        files=files,
        total=len(files)
    )


@router.get("/files/{file_id}/download")
async def download_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a download URL for a file"""
    # Get file record
    file_record = db.query(TaskFile).filter(
        TaskFile.id == file_id,
        TaskFile.user_id == current_user.id
    ).first()
    
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Generate presigned URL
    download_url = s3_service.generate_presigned_url(file_record.s3_key)
    
    return {
        "download_url": download_url,
        "filename": file_record.original_filename,
        "content_type": file_record.content_type,
        "file_size": file_record.file_size
    }


@router.delete("/files/{file_id}")
async def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a file"""
    # Get file record
    file_record = db.query(TaskFile).filter(
        TaskFile.id == file_id,
        TaskFile.user_id == current_user.id
    ).first()
    
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Delete from S3
    s3_service.delete_file(file_record.s3_key)
    
    # Delete from database
    db.delete(file_record)
    db.commit()
    
    return {"message": "File deleted successfully"}


@router.get("/files/{file_id}", response_model=TaskFileResponse)
async def get_file_info(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get file information"""
    file_record = db.query(TaskFile).filter(
        TaskFile.id == file_id,
        TaskFile.user_id == current_user.id
    ).first()
    
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    return file_record
