"""
Recommendation schemas

This module provides Pydantic models for Recommendation-related request and response validation.
"""
from typing import Optional, List, Dict, Any
from pydantic import Field, field_validator, validator, BaseModel, ValidationInfo

from app.schemas.base import BaseSchema, IDMixin, TimestampMixin


# Budget range schema
class BudgetRange(BaseSchema):
    """Schema for budget range specification"""
    
    min: float = Field(0.0, ge=0, description="Minimum budget amount")
    max: float = Field(1000.0, gt=0, description="Maximum budget amount")
    
    @field_validator('max')
    @classmethod
    def validate_range(cls, v: float, info) -> float:
        """Validate that max is greater than min"""
        if 'min' in info.data and v <= info.data['min']:
            raise ValueError('Maximum budget must be greater than minimum budget')
        return v
    
    @classmethod
    def from_string(cls, budget_string: str) -> "BudgetRange":
        """Create a BudgetRange from a string like '100-400'."""
        try:
            parts = budget_string.split("-")
            if len(parts) == 2:
                return cls(min=float(parts[0]), max=float(parts[1]))
        except (ValueError, IndexError):
            pass
        
        # Default range if parsing fails
        return cls()


# Style preferences schema
class StylePreferences(BaseSchema):
    """Schema for style preferences specification"""
    
    favorite_colors: Optional[List[str]] = None
    favorite_brands: Optional[List[str]] = None
    preferred_styles: Optional[List[str]] = None
    disliked_items: Optional[List[str]] = None
    special_requirements: Optional[str] = None


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


# Item schema from improved version
class RecommendationItem(BaseModel):
    """An individual item in a recommendation outfit."""
    name: str
    category: str
    description: Optional[str] = None
    color: Optional[str] = None
    brand: Optional[str] = None
    price_range: Optional[str] = None
    alternatives: Optional[List[str]] = None


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
    items: Optional[List[Dict[str, Any]]] = None
    description: Optional[str] = None
    styling_tips: Optional[List[str]] = None
    reasoning: Optional[str] = None
    is_favorite: bool = False


class RecommendationCreate(RecommendationBase):
    """Schema for creating a new recommendation"""
    
    outfits: Optional[List[OutfitCreate]] = None
    user_id: Optional[int] = None
    profile_id: Optional[int] = None
    
    @field_validator('budget_max')
    def validate_budget_range(cls, v: float, info: ValidationInfo) -> float:
        """Validate that budget_max is greater than budget_min"""
        budget_min = info.data.get('budget_min')
        if budget_min is not None and v is not None:
            if v <= budget_min:
                raise ValueError('Maximum budget must be greater than minimum budget')
        return v


class Recommendation(RecommendationBase, IDMixin, TimestampMixin):
    """Schema for recommendation response"""
    
    user_id: int
    outfits: List[Outfit] = []


# API response schema for Recommendation
class RecommendationResponse(Recommendation):
    """API response schema for recommendations"""
    
    class Config:
        from_attributes = True  # Updated from orm_mode


# Request schemas
class RecommendationRequest(BaseSchema):
    """Schema for requesting style recommendations"""
    
    title: str = Field("My Outfit Recommendation", description="Title for this recommendation request")
    occasion: Optional[str] = Field(None, description="Occasion for the outfit (casual, formal, work, etc.)")
    season: Optional[str] = Field(None, description="Season (spring, summer, fall, winter)")
    budget_min: float = Field(0.0, ge=0, description="Minimum budget")
    budget_max: Optional[float] = Field(1000.0, gt=0, description="Maximum budget")
    style_profile_id: Optional[int] = Field(None, description="Style profile ID to use for recommendations")
    specific_requests: Optional[str] = Field(None, description="Additional specific requests or preferences")
    
    @field_validator('budget_max')
    def validate_budget_range(cls, v: float, info: ValidationInfo) -> float:
        """Validate that budget_max is greater than budget_min"""
        budget_min = info.data.get('budget_min')
        if budget_min is not None and v is not None:
            if v <= budget_min:
                raise ValueError('Maximum budget must be greater than minimum budget')
        return v
    
    @classmethod
    def from_form_data(cls, form_data: Dict[str, Any]) -> "RecommendationRequest":
        """Create a RecommendationRequest from form data with budget range handling."""
        # Handle budget range if provided as a single string
        if "budget" in form_data and isinstance(form_data["budget"], str):
            try:
                parts = form_data["budget"].split("-")
                if len(parts) == 2:
                    form_data["budget_min"] = float(parts[0])
                    form_data["budget_max"] = float(parts[1])
                    form_data.pop("budget")
            except (ValueError, IndexError):
                pass
        
        # Create the request object
        return cls(**form_data)


# Long-running task schemas
class TaskStatus(BaseSchema):
    """Schema for task status response"""
    
    task_id: str
    status: str  # pending, processing, completed, failed
    progress: float = 0.0  # 0.0 to 1.0
    result_id: Optional[int] = None
    message: Optional[str] = None 