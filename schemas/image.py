"""
Image schemas

This module provides Pydantic models for Image-related request and response validation.
"""
from typing import Optional, List, Dict, Any
from pydantic import Field

from app.schemas.base import BaseSchema, IDMixin, TimestampMixin


# ClothingItem schema
class ClothingItemBase(BaseSchema):
    """Base schema for ClothingItem with common fields"""
    
    item_type: str
    description: Optional[str] = None
    bbox_x: Optional[float] = None
    bbox_y: Optional[float] = None
    bbox_width: Optional[float] = None
    bbox_height: Optional[float] = None
    color: Optional[str] = None
    pattern: Optional[str] = None
    material: Optional[str] = None
    style: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None


class ClothingItemCreate(ClothingItemBase):
    """Schema for creating a new clothing item"""
    
    image_id: int


class ClothingItem(ClothingItemBase, IDMixin, TimestampMixin):
    """Schema for clothing item response"""
    
    image_id: int


# Image schema
class ImageBase(BaseSchema):
    """Base schema for Image with common fields"""
    
    filename: str
    file_path: str
    file_size: int
    mime_type: str
    width: Optional[int] = None
    height: Optional[int] = None
    is_analyzed: bool = False
    analysis_status: str = "pending"
    analysis_results: Optional[Dict[str, Any]] = None


class ImageCreate(BaseSchema):
    """Schema for creating a new image record

    This doesn't include the file itself as that's handled separately
    through multipart file upload.
    """
    
    filename: str
    file_path: str
    file_size: int
    mime_type: str
    width: Optional[int] = None
    height: Optional[int] = None


class Image(ImageBase, IDMixin, TimestampMixin):
    """Schema for image response"""
    
    user_id: int
    style_profile_id: Optional[int] = None


# Upload response
class UploadResponse(BaseSchema):
    """Schema for file upload response"""
    
    filename: str
    content_type: str
    file_size: int
    image_id: int
    image_url: str


# Image analysis request
class ImageAnalysisRequest(BaseSchema):
    """Schema for requesting image analysis"""
    
    image_id: int = Field(..., description="ID of the image to analyze")
    analysis_type: str = Field("full", description="Type of analysis to perform (full, clothing, body, etc.)")


# Image analysis response
class ImageAnalysisResponse(BaseSchema):
    """Schema for image analysis response"""
    
    image_id: int
    analysis_results: Dict[str, Any]
    clothing_items: List[ClothingItem] = []
    detected_attributes: Dict[str, Any] 