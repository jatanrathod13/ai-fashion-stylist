"""
Database connection module

This module manages the SQLAlchemy database engine and session.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app.config import settings

# Create async database engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)

# Create a base class for declarative models
Base = declarative_base()

# Dependency for getting a database session
async def get_db():
    """Get a database session and ensure it's closed after use"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close() 