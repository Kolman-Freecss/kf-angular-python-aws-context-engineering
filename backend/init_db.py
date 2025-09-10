#!/usr/bin/env python3
"""
Database initialization script
"""
import asyncio
from sqlalchemy import create_engine
from core.database import Base
from core.config import settings
from models import user

def init_db():
    """Initialize the database"""
    print("Initializing database...")
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
