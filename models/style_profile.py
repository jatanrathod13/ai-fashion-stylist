"""
Style Profile model

This module defines the StyleProfile model which stores a user's
fashion attributes, preferences, and style information.
"""
from sqlalchemy import Column, String, Integer, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base, BaseModel

class StyleProfile(Base, BaseModel):
    """StyleProfile model storing user's fashion attributes and preferences"""
    
    __tablename__ = "style_profiles"
    
    # Relationship to user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="style_profiles")
    
    # Profile name and description
    name = Column(String, nullable=False, default="Default Profile")
    description = Column(String, nullable=True)
    
    # Physical attributes
    body_shape = Column(String, nullable=True)  # hourglass, pear, rectangle, etc.
    skin_tone = Column(String, nullable=True)   # warm, cool, neutral, etc.
    height = Column(Float, nullable=True)       # height in cm
    
    # Size information stored as JSON
    sizes = Column(JSON, nullable=True)         # {"tops": "M", "bottoms": "32", "shoes": "9", etc.}
    
    # Style preferences
    style_preferences = Column(JSON, nullable=True)  # ["casual", "bohemian", "minimalist", etc.]
    favorite_colors = Column(JSON, nullable=True)    # ["blue", "black", "teal", etc.]
    disliked_items = Column(JSON, nullable=True)     # ["crop tops", "skinny jeans", etc.]
    favorite_brands = Column(JSON, nullable=True)    # ["Zara", "H&M", etc.]
    
    # Style embedding for similarity search
    style_embedding = Column(JSON, nullable=True)    # Vector representation of style for similarity search
    
    # One-to-many relationship with FeedbackHistory
    feedback_history = relationship("FeedbackHistory", back_populates="style_profile", cascade="all, delete-orphan")
    
    def __repr__(self):
        """String representation of the style profile"""
        return f"<StyleProfile {self.name} - User {self.user_id}>"


class FeedbackHistory(Base, BaseModel):
    """Feedback history for recommendations to improve future suggestions"""
    
    __tablename__ = "feedback_history"
    
    # Relationship to style profile
    style_profile_id = Column(Integer, ForeignKey("style_profiles.id"), nullable=False)
    style_profile = relationship("StyleProfile", back_populates="feedback_history")
    
    # Relationship to recommendation if available
    recommendation_id = Column(Integer, ForeignKey("recommendations.id"), nullable=True)
    recommendation = relationship("Recommendation", back_populates="feedback")
    
    # Feedback details
    rating = Column(Integer, nullable=False)  # 1-5 scale
    comments = Column(String, nullable=True)
    
    # Item preferences from this feedback
    liked_items = Column(JSON, nullable=True)    # ["blue shirt", "black jeans", etc.]
    disliked_items = Column(JSON, nullable=True)  # ["red shoes", "striped top", etc.]
    
    def __repr__(self):
        """String representation of the feedback"""
        return f"<Feedback Rating:{self.rating} - Profile {self.style_profile_id}>" 