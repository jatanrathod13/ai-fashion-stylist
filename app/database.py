"""
Database connection module

This module manages the SQLAlchemy database engine and session.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Import the shared Base from models
from app.models.base import Base

from app.config import settings

# Import all models to register them with SQLAlchemy's metadata
from app.models.user import User
from app.models.style_profile import StyleProfile, FeedbackHistory
from app.models.recommendation import Recommendation
from app.models.outfit import Outfit
from app.models.outfit_component import OutfitComponent
from app.models.product import Product

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

# Dependency for getting a database session
async def get_db():
    """Get a database session and ensure it's closed after use"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close() 