import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.main import app
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.style_profile import StyleProfile
from tests.conftest import override_get_db
from app.database import get_db

# Test data
TEST_USER = {
    "id": 1,
    "email": "test@example.com",
    "username": "testuser",
    "hashed_password": "hashed_password",
    "is_active": True,
    "is_verified": False
}

TEST_PROFILE = {
    "id": 1,
    "user_id": 1,
    "name": "Default Profile",
    "description": "Test profile for recommendations",
    "body_shape": "hourglass",
    "skin_tone": "warm",
    "height": 165.0,
    "sizes": {"tops": "M", "bottoms": "28", "shoes": "7.5"},
    "style_preferences": ["casual", "modern"],
    "favorite_colors": ["blue", "black"],
    "disliked_items": ["crop tops"],
    "favorite_brands": ["Zara", "H&M"]
}

# Override dependencies
async def override_get_current_user():
    return User(**TEST_USER)

app.dependency_overrides[get_current_user] = override_get_current_user
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
async def setup_test_data(async_session: AsyncSession):
    """Setup test data before each test."""
    # Clear existing data
    await async_session.execute(text('DELETE FROM recommendations'))
    await async_session.execute(text('DELETE FROM style_profiles'))
    await async_session.execute(text('DELETE FROM users'))
    
    # Create test user
    user = User(**TEST_USER)
    async_session.add(user)
    await async_session.commit()
    
    # Create test style profile
    profile = StyleProfile(**TEST_PROFILE)
    async_session.add(profile)
    await async_session.commit()

@pytest.mark.asyncio
async def test_create_recommendations():
    response = client.post(
        "/api/recommendations/generate",
        json={
            "season": "summer",
            "budget_min": 50,
            "budget_max": 200,
            "style_profile_id": TEST_PROFILE["id"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["season"] == "summer"
    assert data["budget_min"] == 50
    assert data["budget_max"] == 200

@pytest.mark.asyncio
async def test_create_recommendations_invalid_profile():
    response = client.post(
        "/api/recommendations/generate",
        json={
            "season": "summer",
            "budget_min": 50,
            "budget_max": 200,
            "style_profile_id": 999  # Non-existent profile
        }
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_create_recommendations_invalid_budget():
    response = client.post(
        "/api/recommendations/generate",
        json={
            "season": "summer",
            "budget_min": 200,  # Invalid: min > max
            "budget_max": 50,
            "style_profile_id": TEST_PROFILE["id"]
        }
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_get_recommendations():
    # First create a recommendation
    create_response = client.post(
        "/api/recommendations/generate",
        json={
            "season": "summer",
            "budget_min": 50,
            "budget_max": 200,
            "style_profile_id": TEST_PROFILE["id"]
        }
    )
    assert create_response.status_code == 200
    
    # Then get all recommendations
    response = client.get("/api/recommendations/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

@pytest.mark.asyncio
async def test_get_recommendation_by_id():
    # First create a recommendation
    create_response = client.post(
        "/api/recommendations/generate",
        json={
            "season": "summer",
            "budget_min": 50,
            "budget_max": 200,
            "style_profile_id": TEST_PROFILE["id"]
        }
    )
    assert create_response.status_code == 200
    recommendation_id = create_response.json()["id"]
    
    # Then get it by ID
    response = client.get(f"/api/recommendations/{recommendation_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == recommendation_id

@pytest.mark.asyncio
async def test_toggle_favorite():
    # First create a recommendation
    create_response = client.post(
        "/api/recommendations/generate",
        json={
            "season": "summer",
            "budget_min": 50,
            "budget_max": 200,
            "style_profile_id": TEST_PROFILE["id"]
        }
    )
    assert create_response.status_code == 200
    recommendation_id = create_response.json()["id"]
    
    # Toggle favorite
    response = client.post(f"/api/recommendations/{recommendation_id}/toggle-favorite")
    assert response.status_code == 200
    data = response.json()
    assert data["is_favorite"] is True
    
    # Toggle again
    response = client.post(f"/api/recommendations/{recommendation_id}/toggle-favorite")
    assert response.status_code == 200
    data = response.json()
    assert data["is_favorite"] is False