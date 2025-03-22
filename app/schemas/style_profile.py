"""
Style Profile schemas

This module provides Pydantic models for StyleProfile-related request and response validation.
"""
from typing import Optional, List, Dict, Any, Union
from pydantic import Field

from app.schemas.base import BaseSchema, IDMixin, TimestampMixin


# Base StyleProfile schema with common attributes
class StyleProfileBase(BaseSchema):
    """Base schema for StyleProfile with common fields"""
    
    name: str
    description: Optional[str] = None
    body_shape: Optional[str] = None
    skin_tone: Optional[str] = None
    height: Optional[float] = None
    sizes: Optional[Dict[str, str]] = None
    style_preferences: Optional[List[str]] = None
    favorite_colors: Optional[List[str]] = None
    disliked_items: Optional[List[str]] = None
    favorite_brands: Optional[List[str]] = None


# Schema for creating a new style profile
class StyleProfileCreate(StyleProfileBase):
    """Schema for creating a new style profile"""
    
    pass


# Schema for updating a style profile
class StyleProfileUpdate(BaseSchema):
    """Schema for updating a style profile"""
    
    name: Optional[str] = None
    description: Optional[str] = None
    body_shape: Optional[str] = None
    skin_tone: Optional[str] = None
    height: Optional[float] = None
    sizes: Optional[Dict[str, str]] = None
    style_preferences: Optional[List[str]] = None
    favorite_colors: Optional[List[str]] = None
    disliked_items: Optional[List[str]] = None
    favorite_brands: Optional[List[str]] = None


# Schema for style profile response (returned to client)
class StyleProfile(StyleProfileBase, IDMixin, TimestampMixin):
    """Schema for style profile response"""
    
    user_id: int


# Schema for style profile response (used in API responses)
class StyleProfileResponse(StyleProfile):
    """Schema for style profile API responses"""
    
    pass


# Base FeedbackHistory schema with common attributes
class FeedbackHistoryBase(BaseSchema):
    """Base schema for FeedbackHistory with common fields"""
    
    rating: int = Field(..., ge=1, le=5)
    comments: Optional[str] = None
    liked_items: Optional[List[str]] = None
    disliked_items: Optional[List[str]] = None


# Schema for creating feedback
class FeedbackHistoryCreate(FeedbackHistoryBase):
    """Schema for creating new feedback"""
    
    recommendation_id: Optional[int] = None


# Schema for feedback response
class FeedbackHistory(FeedbackHistoryBase, IDMixin, TimestampMixin):
    """Schema for feedback response"""
    
    style_profile_id: int
    recommendation_id: Optional[int] = None


# Schema for style analysis from image
class StyleAnalysisRequest(BaseSchema):
    """Schema for requesting style analysis from images"""
    
    image_ids: List[int]
    create_profile: bool = False
    update_profile_id: Optional[int] = None


# Schema for style analysis response
class StyleAnalysisResponse(BaseSchema):
    """Schema for style analysis response"""
    
    analysis_results: Dict[str, Any]
    detected_attributes: Dict[str, Any]
    style_profile_id: Optional[int] = None 