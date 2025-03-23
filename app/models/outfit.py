"""
Outfit model for storing outfit recommendations.
"""

from sqlalchemy import Column, String, Integer, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.models.base import Base, BaseModel

class Outfit(Base, BaseModel):
    """Outfit model representing a complete style recommendation"""
    
    __tablename__ = "outfits"
    
    # Relationship to recommendation
    recommendation_id = Column(Integer, ForeignKey("recommendations.id"), nullable=False)
    recommendation = relationship("Recommendation", back_populates="outfits")
    
    # Outfit details
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Components of this outfit
    components = relationship("OutfitComponent", back_populates="outfit", cascade="all, delete-orphan")
    
    # Styling tips specific to this outfit
    styling_tips = Column(JSON, nullable=True)  # Array of styling tip strings
    
    # Occasions this outfit is suitable for
    occasions = Column(JSON, nullable=True)  # ["casual", "work", "evening", etc.]
    
    # Color palette
    color_palette = Column(JSON, nullable=True)  # Array of color hex codes
    
    def __repr__(self):
        """String representation of the outfit"""
        return f"<Outfit {self.name} - Recommendation {self.recommendation_id}>" 