"""
Schemas package

This package contains Pydantic models for request and response validation.
"""
from app.schemas.base import (
    BaseSchema, 
    IDMixin, 
    TimestampMixin, 
    PaginatedResponse, 
    ResponseModel, 
    ErrorResponse
)
from app.schemas.user import (
    UserBase, 
    UserCreate, 
    UserUpdate, 
    User, 
    UserLogin, 
    Token, 
    TokenData
)
from app.schemas.style_profile import (
    StyleProfileBase, 
    StyleProfileCreate, 
    StyleProfileUpdate, 
    StyleProfile,
    FeedbackHistoryBase,
    FeedbackHistoryCreate,
    FeedbackHistory,
    StyleAnalysisRequest,
    StyleAnalysisResponse
)
from app.schemas.recommendation import (
    ProductBase,
    ProductCreate,
    Product,
    OutfitComponentBase,
    OutfitComponentCreate,
    OutfitComponent,
    OutfitBase,
    OutfitCreate,
    Outfit,
    RecommendationBase,
    RecommendationCreate,
    Recommendation,
    RecommendationRequest,
    TaskStatus
)
from app.schemas.image import (
    ClothingItemBase,
    ClothingItemCreate,
    ClothingItem,
    ImageBase,
    ImageCreate,
    Image,
    UploadResponse,
    ImageAnalysisRequest,
    ImageAnalysisResponse
)

# For convenience when importing schemas
__all__ = [
    # Base
    "BaseSchema", "IDMixin", "TimestampMixin", "PaginatedResponse", "ResponseModel", "ErrorResponse",
    
    # User
    "UserBase", "UserCreate", "UserUpdate", "User", "UserLogin", "Token", "TokenData",
    
    # Style Profile
    "StyleProfileBase", "StyleProfileCreate", "StyleProfileUpdate", "StyleProfile",
    "FeedbackHistoryBase", "FeedbackHistoryCreate", "FeedbackHistory",
    "StyleAnalysisRequest", "StyleAnalysisResponse",
    
    # Recommendation
    "ProductBase", "ProductCreate", "Product",
    "OutfitComponentBase", "OutfitComponentCreate", "OutfitComponent",
    "OutfitBase", "OutfitCreate", "Outfit",
    "RecommendationBase", "RecommendationCreate", "Recommendation",
    "RecommendationRequest", "TaskStatus",
    
    # Image
    "ClothingItemBase", "ClothingItemCreate", "ClothingItem",
    "ImageBase", "ImageCreate", "Image",
    "UploadResponse", "ImageAnalysisRequest", "ImageAnalysisResponse"
] 