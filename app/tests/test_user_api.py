"""
User API tests.

This module contains tests for the user API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db, Base
from app.dependencies.auth import get_password_hash
from app.models.user import User

# Create a test database
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)


# Test client
client = TestClient(app)

# Test user data
test_user = {
    "email": "test@example.com",
    "full_name": "Test User",
    "password": "testpassword123"
}


# Setup and teardown
@pytest.fixture(scope="module")
async def setup_database():
    """Set up the test database."""
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Drop tables after tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="module")
async def create_test_user(setup_database):
    """Create a test user in the database."""
    async with TestingSessionLocal() as session:
        # Check if user already exists
        db_user = User(
            email=test_user["email"],
            full_name=test_user["full_name"],
            hashed_password=get_password_hash(test_user["password"]),
            is_active=True
        )
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
        
        yield db_user


# Override the get_db dependency
async def override_get_db():
    """Override the get_db dependency for testing."""
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.mark.asyncio
async def test_create_user(setup_database):
    """Test creating a new user."""
    response = client.post(
        "/api/users/",
        json={
            "email": "newuser@example.com",
            "full_name": "New User",
            "password": "newpassword123"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["full_name"] == "New User"
    assert "id" in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_create_user_duplicate_email(create_test_user):
    """Test creating a user with a duplicate email."""
    response = client.post(
        "/api/users/",
        json=test_user
    )
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login(create_test_user):
    """Test user login and token generation."""
    response = client.post(
        "/api/auth/token",
        data={
            "username": test_user["email"],
            "password": test_user["password"]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(create_test_user):
    """Test login with wrong password."""
    response = client.post(
        "/api/auth/token",
        data={
            "username": test_user["email"],
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me(create_test_user):
    """Test getting current user info."""
    # First login to get token
    login_response = client.post(
        "/api/auth/token",
        data={
            "username": test_user["email"],
            "password": test_user["password"]
        }
    )
    
    token = login_response.json()["access_token"]
    
    # Then get user info with token
    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user["email"]
    assert data["full_name"] == test_user["full_name"]


@pytest.mark.asyncio
async def test_update_user(create_test_user):
    """Test updating user info."""
    # First login to get token
    login_response = client.post(
        "/api/auth/token",
        data={
            "username": test_user["email"],
            "password": test_user["password"]
        }
    )
    
    token = login_response.json()["access_token"]
    
    # Update user
    response = client.put(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"full_name": "Updated Name"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Name"
    assert data["email"] == test_user["email"]


@pytest.mark.asyncio
async def test_delete_user(create_test_user):
    """Test deleting user."""
    # First login to get token
    login_response = client.post(
        "/api/auth/token",
        data={
            "username": test_user["email"],
            "password": test_user["password"]
        }
    )
    
    token = login_response.json()["access_token"]
    
    # Delete user
    response = client.delete(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 204 