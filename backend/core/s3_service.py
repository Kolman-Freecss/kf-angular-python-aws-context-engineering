import boto3
import uuid
import os
from typing import Optional
from fastapi import HTTPException
from core.config import settings
import logging

logger = logging.getLogger(__name__)


class S3Service:
    def __init__(self):
        self.s3_client = None
        self.bucket_name = "taskflow-files"
        self._initialized = False
        
    def _initialize(self):
        """Lazy initialization of S3 client"""
        if self._initialized:
            return
            
        try:
            self.s3_client = boto3.client(
                's3',
                endpoint_url=settings.AWS_ENDPOINT,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_DEFAULT_REGION
            )
            self._ensure_bucket_exists()
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize S3 service: {e}")
            if not (settings.TESTING or os.getenv("TESTING") == "true"):
                raise HTTPException(status_code=500, detail="Failed to initialize file storage")

    def _ensure_bucket_exists(self):
        """Ensure the S3 bucket exists, create if it doesn't"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Bucket {self.bucket_name} already exists")
        except self.s3_client.exceptions.NoSuchBucket:
            try:
                self.s3_client.create_bucket(Bucket=self.bucket_name)
                logger.info(f"Created bucket {self.bucket_name}")
            except Exception as e:
                logger.error(f"Failed to create bucket {self.bucket_name}: {e}")
                # Don't raise exception during testing
                if not (settings.TESTING or os.getenv("TESTING") == "true"):
                    raise HTTPException(status_code=500, detail="Failed to initialize file storage")
        except Exception as e:
            logger.error(f"Error checking bucket {self.bucket_name}: {e}")
            # Don't raise exception during testing
            if not (settings.TESTING or os.getenv("TESTING") == "true"):
                raise HTTPException(status_code=500, detail="Failed to access file storage")

    def generate_file_key(self, user_id: int, task_id: int, filename: str) -> str:
        """Generate a unique S3 key for the file"""
        file_extension = filename.split('.')[-1] if '.' in filename else ''
        unique_filename = f"{uuid.uuid4()}.{file_extension}" if file_extension else str(uuid.uuid4())
        return f"users/{user_id}/tasks/{task_id}/{unique_filename}"

    def upload_file(self, file_content: bytes, s3_key: str, content_type: str) -> bool:
        """Upload file to S3"""
        self._initialize()
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type
            )
            logger.info(f"Successfully uploaded file to S3: {s3_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload file to S3: {e}")
            raise HTTPException(status_code=500, detail="Failed to upload file")

    def delete_file(self, s3_key: str) -> bool:
        """Delete file from S3"""
        self._initialize()
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            logger.info(f"Successfully deleted file from S3: {s3_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete file from S3: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete file")

    def generate_presigned_url(self, s3_key: str, expiration: int = 3600) -> str:
        """Generate a presigned URL for file download"""
        self._initialize()
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return url
        except Exception as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            raise HTTPException(status_code=500, detail="Failed to generate download URL")

    def get_file_info(self, s3_key: str) -> Optional[dict]:
        """Get file information from S3"""
        self._initialize()
        try:
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return {
                'size': response['ContentLength'],
                'content_type': response['ContentType'],
                'last_modified': response['LastModified']
            }
        except self.s3_client.exceptions.NoSuchKey:
            return None
        except Exception as e:
            logger.error(f"Failed to get file info: {e}")
            raise HTTPException(status_code=500, detail="Failed to get file information")


# Global S3 service instance
s3_service = S3Service()
