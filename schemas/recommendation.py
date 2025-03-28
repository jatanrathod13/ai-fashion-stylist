"""
Recommendation schemas

This module provides Pydantic models for Recommendation-related request and response validation.
"""
from typing import Optional, List, Dict, Any
from pydantic import Field, field_validator

from app.schemas.base import BaseSchema, IDMixin, TimestampMixin


# Product schema
class ProductBase(BaseSchema):
    """Base schema for Product with common fields"""
    
    title: str
    brand: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = "USD"
    url: Optional[str] = None
    image_url: Optional[str] = None
    retailer: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ProductCreate(ProductBase):
    """Schema for creating a new product"""
    
    pass


class Product(ProductBase, IDMixin, TimestampMixin):
    """Schema for product response"""
    
    component_id: int


# OutfitComponent schema
class OutfitComponentBase(BaseSchema):
    """Base schema for OutfitComponent with common fields"""
    
    type: str
    description: str


class OutfitComponentCreate(OutfitComponentBase):
    """Schema for creating a new outfit component"""
    
    products: Optional[List[ProductCreate]] = None


class OutfitComponent(OutfitComponentBase, IDMixin, TimestampMixin):
    """Schema for outfit component response"""
    
    outfit_id: int
    products: List[Product] = []


# Outfit schema
class OutfitBase(BaseSchema):
    """Base schema for Outfit with common fields"""
    
    name: str
    description: Optional[str] = None
    styling_tips: Optional[List[str]] = None
    occasions: Optional[List[str]] = None
    color_palette: Optional[List[str]] = None


class OutfitCreate(OutfitBase):
    """Schema for creating a new outfit"""
    
    components: Optional[List[OutfitComponentCreate]] = None


class Outfit(OutfitBase, IDMixin, TimestampMixin):
    """Schema for outfit response"""
    
    recommendation_id: int
    components: List[OutfitComponent] = []


# Recommendation schema
class RecommendationBase(BaseSchema):
    """Base schema for Recommendation with common fields"""
    
    title: str
    occasion: Optional[str] = None
    season: Optional[str] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    status: str = "pending"
    fashion_trends: Optional[List[Dict[str, Any]]] = None


class RecommendationCreate(RecommendationBase):
    """Schema for creating a new recommendation"""
    
    outfits: Optional[List[OutfitCreate]] = None
    
    @field_validator('budget_max')
    def validate_budget_range(cls, v, values):
        """Validate that budget_max is greater than budget_min"""
        if 'budget_min' in values and v is not None and values['budget_min'] is not None:
            if v <= values['budget_min']:
                raise ValueError('Maximum budget must be greater than minimum budget')
        return v


class Recommendation(RecommendationBase, IDMixin, TimestampMixin):
    """Schema for recommendation response"""
    
    user_id: int
    outfits: List[Outfit] = []


# Request schemas
class RecommendationRequest(BaseSchema):
    """Schema for requesting style recommendations"""
    
    title: str = Field(..., description="Title for this recommendation request")
    occasion: str = Field(..., description="Occasion for the outfit (casual, formal, work, etc.)")
    season: Optional[str] = Field(None, description="Season (spring, summer, fall, winter)")
    budget_min: float = Field(..., ge=0, description="Minimum budget")
    budget_max: float = Field(..., gt=0, description="Maximum budget")
    style_profile_id: int = Field(..., description="Style profile ID to use for recommendations")
    specific_requests: Optional[str] = Field(None, description="Additional specific requests or preferences")


# Long-running task schemas
class TaskStatus(BaseSchema):
    """Schema for task status response"""
    
    task_id: str
    status: str  # pending, processing, completed, failed
    progress: float = 0.0  # 0.0 to 1.0
    result_id: Optional[int] = None
    message: Optional[str] = None 