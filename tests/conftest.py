"""
Create test database tables.

This module provides fixtures for setting up and tearing down test database tables.
"""

import pytest
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import alembic.config
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.util._concurrency_py3k import greenlet_spawn

from app.database import Base
from app.config import settings
from app.models.user import User
from app.models.style_profile import StyleProfile, FeedbackHistory
from app.models.recommendation import Recommendation
from app.models.outfit import Outfit
from app.models.outfit_component import OutfitComponent
from app.models.product import Product

# Test database URL
TEST_DATABASE_URL = settings.DATABASE_URL.replace(
    "ai_fashion_shopper",
    "ai_fashion_shopper_test"
)

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=True,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def test_db():
    """Create test database tables before a test and drop them after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        
        # Run Alembic migrations
        alembicArgs = [
            '--raiseerr',
            'upgrade', 'head',
        ]
        alembic.config.main(argv=alembicArgs)
    
    yield test_engine
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def async_session():
    """Get a TestingSessionLocal instance."""
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()
        await session.close()

# Override the get_db dependency
async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback() 