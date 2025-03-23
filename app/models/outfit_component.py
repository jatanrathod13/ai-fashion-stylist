"""
OutfitComponent model for storing individual pieces of an outfit.
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.models.base import Base, BaseModel

class OutfitComponent(Base, BaseModel):
    """OutfitComponent model representing individual pieces in an outfit"""
    
    __tablename__ = "outfit_components"
    
    # Relationship to outfit
    outfit_id = Column(Integer, ForeignKey("outfits.id"), nullable=False)
    outfit = relationship("Outfit", back_populates="components")
    
    # Component details
    type = Column(String, nullable=False)  # "top", "bottom", "shoes", "accessory", etc.
    description = Column(Text, nullable=False)
    
    # Product suggestions for this component
    products = relationship("Product", back_populates="component", cascade="all, delete-orphan")
    
    def __repr__(self):
        """String representation of the component"""
        return f"<Component {self.type} - Outfit {self.outfit_id}>" 