"""
User schemas

This module provides Pydantic models for User-related request and response validation.
"""
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator

from app.schemas.base import BaseSchema, IDMixin, TimestampMixin


# Base User schema with common attributes
class UserBase(BaseSchema):
    """Base schema for User with common fields"""
    
    email: EmailStr
    username: str


# Schema for creating a new user
class UserCreate(UserBase):
    """Schema for creating a new user"""
    
    password: str = Field(..., min_length=8)
    password_confirm: str
    
    @validator('password_confirm')
    def passwords_match(cls, v, values):
        """Validate that passwords match"""
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v


# Schema for updating a user
class UserUpdate(BaseSchema):
    """Schema for updating a user"""
    
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None


# Schema for user login
class UserLogin(BaseSchema):
    """Schema for user login"""
    
    username: str
    password: str


# Schema for user response (returned to client)
class User(UserBase, IDMixin, TimestampMixin):
    """Schema for user response"""
    
    is_active: bool
    is_verified: bool


# Schema for token response
class Token(BaseSchema):
    """Schema for authentication token response"""
    
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # Seconds
    user: User


# Schema for token data (used internally)
class TokenData(BaseSchema):
    """Schema for token payload data"""
    
    username: Optional[str] = None
    user_id: Optional[int] = None
    scopes: List[str] = [] 