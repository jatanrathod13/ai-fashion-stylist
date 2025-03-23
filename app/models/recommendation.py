"""
Recommendation model

This module defines the Recommendation model for storing style recommendations.
"""
from sqlalchemy import Column, String, Integer, Float, JSON, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship

from app.models.base import Base, BaseModel

class Recommendation(Base, BaseModel):
    """Recommendation model for storing style recommendations"""
    
    __tablename__ = "recommendations"
    
    # Relationship to user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="recommendations")
    
    # Recommendation details
    title = Column(String, nullable=False)
    occasion = Column(String, nullable=True)
    season = Column(String, nullable=True)
    
    # Budget range
    budget_min = Column(Float, nullable=True)
    budget_max = Column(Float, nullable=True)
    
    # Status and metadata
    status = Column(String, nullable=False, default="pending")  # pending, processing, completed, failed
    description = Column(Text, nullable=True)
    styling_tips = Column(JSON, nullable=True)  # Array of strings
    fashion_trends = Column(JSON, nullable=True)  # Array of trend objects
    is_favorite = Column(Boolean, default=False)
    
    # Relationships
    outfits = relationship("Outfit", back_populates="recommendation", cascade="all, delete-orphan")
    feedback = relationship("FeedbackHistory", back_populates="recommendation", cascade="all, delete-orphan")
    
    def __repr__(self):
        """String representation of the recommendation"""
        return f"<Recommendation {self.title} - User {self.user_id}>" 