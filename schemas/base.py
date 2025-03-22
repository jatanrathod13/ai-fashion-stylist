"""
Base Pydantic schemas

This module provides base Pydantic models for schema validation.
"""
from datetime import datetime
from typing import Optional, TypeVar, Generic, List
from pydantic import BaseModel, ConfigDict, Field
from pydantic.generics import GenericModel


class BaseSchema(BaseModel):
    """Base schema with common configuration"""
    
    model_config = ConfigDict(
        from_attributes=True,  # Allow ORM model conversion
        populate_by_name=True  # Allow conversion from snake_case to camelCase
    )


class TimestampMixin(BaseSchema):
    """Mixin for created_at and updated_at fields"""
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class IDMixin(BaseSchema):
    """Mixin for ID field"""
    
    id: int


# Generic type for item models
T = TypeVar('T')


class PaginatedResponse(GenericModel, Generic[T]):
    """Generic model for paginated responses"""
    
    items: List[T]
    total: int
    page: int = 1
    per_page: int = 10
    pages: int = Field(...)
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class ResponseModel(BaseSchema):
    """Standard response wrapper for API responses"""
    
    success: bool = True
    message: str = "Operation successful"


class ErrorResponse(ResponseModel):
    """Error response model"""
    
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[dict] = None 