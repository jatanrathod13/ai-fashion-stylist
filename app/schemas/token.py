"""
Token schemas

This module provides Pydantic models for authentication tokens.
"""
from typing import Optional, List
from pydantic import BaseModel

from app.schemas.base import BaseSchema


class Token(BaseSchema):
    """Schema for authentication token response"""
    
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseSchema):
    """Schema for token payload data"""
    
    username: Optional[str] = None
    user_id: Optional[int] = None
    scopes: List[str] = [] 