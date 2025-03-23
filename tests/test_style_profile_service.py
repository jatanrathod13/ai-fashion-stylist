"""Test cases for StyleProfileService"""
import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.services.style_profile_service import StyleProfileService
from app.models.style_profile import StyleProfile

@pytest.fixture
def style_service():
    """Fixture for StyleProfileService"""
    return StyleProfileService()

@pytest.fixture
def mock_db():
    """Fixture for mocked database session"""
    db = Mock(spec=Session)
    return db

@pytest.fixture
def sample_analysis_results():
    """Fixture for sample analysis results"""
    return {
        "person_attributes": {
            "body_shape": "hourglass",
            "skin_tone": "medium"
        },
        "style_assessment": {
            "style_descriptors": ["casual", "modern"],
            "color_palette": ["blue", "black"]
        },
        "size_estimation": {
            "top": "M",
            "bottom": "28"
        }
    }

@pytest.fixture
def mock_profile():
    """Fixture for a mock StyleProfile"""
    profile = Mock(spec=StyleProfile)
    profile.id = 1
    profile.user_id = 1
    profile.name = "Test Profile"
    profile.body_shape = "hourglass"
    profile.skin_tone = "medium"
    profile.sizes = {"top": "M", "bottom": "28"}
    profile.style_preferences = ["casual", "modern"]
    profile.favorite_colors = ["blue", "black"]
    profile.style_embedding = [0.1, 0.2, 0.3]
    profile.disliked_items = []  # Initialize as empty list
    return profile

@pytest.mark.asyncio
async def test_create_profile_from_analysis(style_service, mock_db, sample_analysis_results):
    """Test creating a style profile from analysis results"""
    # Mock the generate_style_embedding method
    with patch.object(style_service, 'generate_style_embedding') as mock_generate:
        mock_generate.return_value = [0.1, 0.2, 0.3]  # Mock embedding
        
        # Create profile
        profile = await style_service.create_profile_from_analysis(
            mock_db,
            user_id=1,
            analysis_results=sample_analysis_results,
            profile_name="Test Profile"
        )
        
        # Verify profile creation
        assert profile is not None
        assert profile.user_id == 1
        assert profile.name == "Test Profile"
        assert profile.body_shape == "hourglass"
        assert profile.skin_tone == "medium"
        assert profile.sizes == {"top": "M", "bottom": "28"}
        assert set(profile.style_preferences) == {"casual", "modern"}
        assert set(profile.favorite_colors) == {"blue", "black"}
        assert profile.style_embedding == [0.1, 0.2, 0.3]
        
        # Verify database operations
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_update_profile_from_analysis(style_service, mock_db, sample_analysis_results, mock_profile):
    """Test updating an existing style profile"""
    # Mock database query
    mock_db.query.return_value.filter.return_value.first.return_value = mock_profile
    
    # Mock embedding generation
    with patch.object(style_service, 'generate_style_embedding') as mock_generate:
        mock_generate.return_value = [0.4, 0.5, 0.6]  # New embedding
        
        # Update profile
        updated_profile = await style_service.update_profile_from_analysis(
            mock_db,
            profile_id=1,
            analysis_results=sample_analysis_results
        )
        
        # Verify profile update
        assert updated_profile is not None
        assert updated_profile.id == 1
        assert updated_profile.body_shape == "hourglass"
        assert updated_profile.skin_tone == "medium"
        assert updated_profile.sizes == {"top": "M", "bottom": "28"}
        assert set(updated_profile.style_preferences) == {"casual", "modern"}
        assert set(updated_profile.favorite_colors) == {"blue", "black"}
        assert updated_profile.style_embedding == [0.4, 0.5, 0.6]
        
        # Verify database operations
        mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_merge_profiles(style_service, mock_db, mock_profile):
    """Test merging multiple style profiles"""
    # Create mock profiles
    profile1 = mock_profile
    profile2 = Mock(spec=StyleProfile)
    profile2.id = 2
    profile2.user_id = 1
    profile2.body_shape = "athletic"
    profile2.skin_tone = "light"
    profile2.sizes = {"top": "S", "pants": "30"}
    profile2.style_preferences = ["elegant", "formal"]
    profile2.favorite_colors = ["red", "white"]
    profile2.style_embedding = [0.7, 0.8, 0.9]
    profile2.disliked_items = []  # Initialize as empty list
    
    # Mock database queries
    mock_db.query.return_value.filter.return_value.all.return_value = [profile1, profile2]
    
    # Mock embedding generation
    with patch.object(style_service, 'generate_style_embedding') as mock_generate:
        mock_generate.return_value = [0.4, 0.5, 0.6]  # Merged embedding
        
        # Merge profiles
        merged_profile = await style_service.merge_profiles(
            mock_db,
            user_id=1,
            profile_ids=[1, 2],
            new_profile_name="Merged Profile"
        )
        
        # Verify merged profile
        assert merged_profile is not None
        assert merged_profile.name == "Merged Profile"
        assert set(merged_profile.style_preferences) == {"casual", "modern", "elegant", "formal"}
        assert set(merged_profile.favorite_colors) == {"blue", "black", "red", "white"}
        assert merged_profile.sizes == {"top": "S", "bottom": "28", "pants": "30"}
        assert merged_profile.style_embedding == [0.4, 0.5, 0.6]
        
        # Verify database operations
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_find_similar_profiles(style_service, mock_db, mock_profile):
    """Test finding similar style profiles"""
    # Create mock profiles
    similar_profile = Mock(spec=StyleProfile)
    similar_profile.id = 2
    similar_profile.style_embedding = [0.15, 0.25, 0.35]  # Similar to mock_profile
    
    dissimilar_profile = Mock(spec=StyleProfile)
    dissimilar_profile.id = 3
    dissimilar_profile.style_embedding = [0.9, 0.9, 0.9]  # Very different
    
    # Mock database query
    mock_db.query.return_value.all.return_value = [mock_profile, similar_profile, dissimilar_profile]
    
    # Find similar profiles
    similar_profiles = await style_service.find_similar_profiles(
        mock_db,
        embedding=[0.1, 0.2, 0.3],
        limit=2
    )
    
    # Verify results
    assert len(similar_profiles) == 2
    assert similar_profiles[0].id == mock_profile.id  # Most similar
    assert similar_profiles[1].id == similar_profile.id  # Second most similar

@pytest.mark.asyncio
async def test_generate_style_embedding(style_service):
    """Test generating style embedding"""
    # Create a mock profile
    profile = {
        "person_attributes": {"body_shape": "athletic"},
        "style_assessment": {"style_descriptors": ["casual"]}
    }
    
    # Mock OpenAI client response
    mock_embedding = [0.1, 0.2, 0.3]
    mock_response = Mock()
    mock_response.data = [Mock(embedding=mock_embedding)]
    
    with patch.object(style_service.client.embeddings, 'create') as mock_create:
        mock_create.return_value = mock_response
        
        # Generate embedding
        embedding = await style_service.generate_style_embedding(profile)
        
        # Verify embedding generation
        assert embedding == mock_embedding
        mock_create.assert_called_once()

@pytest.mark.asyncio
async def test_error_handling(style_service, mock_db, sample_analysis_results):
    """Test error handling in profile creation"""
    # Mock database error
    mock_db.commit.side_effect = Exception("Database error")
    
    with pytest.raises(HTTPException) as exc_info:
        await style_service.create_profile_from_analysis(
            mock_db,
            user_id=1,
            analysis_results=sample_analysis_results
        )
    
    assert "Database error" in str(exc_info.value.detail)
    mock_db.rollback.assert_called_once()

@pytest.mark.asyncio
async def test_update_profile_not_found(style_service, mock_db):
    """Test updating a non-existent profile"""
    # Mock database query to return None
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    with pytest.raises(HTTPException) as exc_info:
        await style_service.update_profile_from_analysis(
            mock_db,
            profile_id=999,
            analysis_results={}
        )
    
    assert exc_info.value.status_code == 404
    assert "Style profile not found" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_merge_profiles_not_found(style_service, mock_db):
    """Test merging when some profiles don't exist"""
    # Mock database query to return fewer profiles than requested
    mock_db.query.return_value.filter.return_value.all.return_value = []
    
    with pytest.raises(HTTPException) as exc_info:
        await style_service.merge_profiles(
            mock_db,
            user_id=1,
            profile_ids=[1, 2],
            new_profile_name="Merged Profile"
        )
    
    assert exc_info.value.status_code == 404
    assert "One or more profiles not found" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_find_similar_profiles_empty(style_service, mock_db):
    """Test finding similar profiles when no profiles exist"""
    # Mock database query to return empty list
    mock_db.query.return_value.all.return_value = []
    
    similar_profiles = await style_service.find_similar_profiles(
        mock_db,
        embedding=[0.1, 0.2, 0.3],
        limit=5
    )
    
    assert similar_profiles == []

@pytest.mark.asyncio
async def test_generate_style_embedding_error(style_service):
    """Test error handling in embedding generation"""
    # Mock OpenAI client to raise an error
    with patch.object(style_service.client.embeddings, 'create') as mock_create:
        mock_create.side_effect = Exception("API Error")
        
        with pytest.raises(HTTPException) as exc_info:
            await style_service.generate_style_embedding({})
        
        assert exc_info.value.status_code == 500
        assert "Failed to generate style embedding" in str(exc_info.value.detail) 