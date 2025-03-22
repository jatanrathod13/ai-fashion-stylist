"""
Models package

This package contains SQLAlchemy models for database entities.
"""
from app.models.base import Base, BaseModel
from app.models.user import User
from app.models.style_profile import StyleProfile, FeedbackHistory
from app.models.recommendation import Recommendation, Outfit, OutfitComponent, Product
from app.models.image import Image, ClothingItem

# For convenience when importing models
__all__ = [
    "Base",
    "BaseModel",
    "User",
    "StyleProfile",
    "FeedbackHistory",
    "Recommendation",
    "Outfit",
    "OutfitComponent",
    "Product",
    "Image",
    "ClothingItem"
] 