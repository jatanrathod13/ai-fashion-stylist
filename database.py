"""
Database connection module

This module manages the SQLAlchemy database engine and session.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for declarative models
Base = declarative_base()

# Dependency for getting a database session
def get_db():
    """Get a database session and ensure it's closed after use"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 