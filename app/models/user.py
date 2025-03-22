"""
User model for the application

This module defines the User model with authentication and profile fields.
"""
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from app.models.base import Base, BaseModel

class User(Base, BaseModel):
    """User model with authentication and profile information"""
    
    __tablename__ = "users"
    
    # Basic user info
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # User status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Relationships
    style_profiles = relationship("StyleProfile", back_populates="user", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        """String representation of the user"""
        return f"<User {self.username}>" 