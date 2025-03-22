"""
Database initialization script.

This script creates all tables defined in SQLAlchemy models.
Run this script before starting the application for the first time.
"""

import asyncio
from sqlalchemy import text

from app.database import engine
from app.models.user import Base as UserBase
from app.models.style_profile import Base as StyleProfileBase
from app.models.recommendation import Base as RecommendationBase
from app.models.image import Base as ImageBase

async def init_db():
    """Initialize the database by creating all tables."""
    print("Creating database tables...")
    
    # Create tables for all models
    async with engine.begin() as conn:
        # Drop all tables if they exist (comment out in production)
        # await conn.run_sync(lambda sync_conn: UserBase.metadata.drop_all(sync_conn))
        # await conn.run_sync(lambda sync_conn: StyleProfileBase.metadata.drop_all(sync_conn))
        # await conn.run_sync(lambda sync_conn: RecommendationBase.metadata.drop_all(sync_conn))
        # await conn.run_sync(lambda sync_conn: ImageBase.metadata.drop_all(sync_conn))
        
        # Create all tables
        await conn.run_sync(lambda sync_conn: UserBase.metadata.create_all(sync_conn))
        await conn.run_sync(lambda sync_conn: StyleProfileBase.metadata.create_all(sync_conn))
        await conn.run_sync(lambda sync_conn: RecommendationBase.metadata.create_all(sync_conn))
        await conn.run_sync(lambda sync_conn: ImageBase.metadata.create_all(sync_conn))
        
        # Test database connection
        result = await conn.execute(text("SELECT 1"))
        print(f"Database connection test: {result.scalar() == 1}")
    
    print("Database initialization completed!")

if __name__ == "__main__":
    """Run the database initialization script."""
    asyncio.run(init_db()) 