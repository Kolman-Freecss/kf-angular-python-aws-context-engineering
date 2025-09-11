from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "TaskFlow API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    TESTING: bool = False
    
    # Database settings
    DATABASE_URL: str = "postgresql://user:pass@db:5432/mydb"
    
    # JWT settings
    JWT_SECRET: str = "your-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://frontend:80"]
    
    # AWS settings
    AWS_ENDPOINT: str = "http://localstack:4566"
    AWS_ACCESS_KEY_ID: str = "test"
    AWS_SECRET_ACCESS_KEY: str = "test"
    AWS_DEFAULT_REGION: str = "us-east-1"
    
    # S3 settings
    S3_BUCKET_NAME: str = "taskflow-files"
    
    # Email settings
    SES_FROM_EMAIL: str = "noreply@taskflow.com"
    SES_REGION: str = "us-east-1"
    
    # Celery settings
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"
    
    # Redis settings
    REDIS_URL: str = "redis://redis:6379/0"
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
