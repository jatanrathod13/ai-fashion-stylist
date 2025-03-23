"""
Style preferences model.

This module provides the Pydantic model for style preferences validation.
"""
from typing import Optional, List
from pydantic import BaseModel


class StylePreferences(BaseModel):
    """Model for style preferences validation."""
    
    favorite_colors: Optional[List[str]] = None
    favorite_brands: Optional[List[str]] = None
    preferred_styles: Optional[List[str]] = None
    disliked_items: Optional[List[str]] = None
    special_requirements: Optional[str] = None

    class Config:
        """Pydantic model configuration."""
        from_attributes = True 