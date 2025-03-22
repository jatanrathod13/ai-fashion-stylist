"""
Recommendation model

This module defines the Recommendation model and related models for 
storing style recommendations and product data.
"""
from sqlalchemy import Column, String, Integer, Float, JSON, ForeignKey, Text
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
    
    # Status of the recommendation
    status = Column(String, nullable=False, default="pending")  # pending, processing, completed, failed
    
    # Outfits in this recommendation
    outfits = relationship("Outfit", back_populates="recommendation", cascade="all, delete-orphan")
    
    # Fashion trends associated with this recommendation
    fashion_trends = Column(JSON, nullable=True)  # Array of trend objects
    
    # Feedback for this recommendation
    feedback = relationship("FeedbackHistory", back_populates="recommendation")
    
    def __repr__(self):
        """String representation of the recommendation"""
        return f"<Recommendation {self.title} - User {self.user_id}>"


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


class Product(Base, BaseModel):
    """Product model representing e-commerce product suggestions"""
    
    __tablename__ = "products"
    
    # Relationship to outfit component
    component_id = Column(Integer, ForeignKey("outfit_components.id"), nullable=False)
    component = relationship("OutfitComponent", back_populates="products")
    
    # Product details
    title = Column(String, nullable=False)
    brand = Column(String, nullable=True)
    price = Column(Float, nullable=True)
    currency = Column(String, nullable=True, default="USD")
    
    # Product URLs
    url = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    
    # Retailer information
    retailer = Column(String, nullable=True)
    
    # Product metadata
    metadata = Column(JSON, nullable=True)  # Additional product details
    
    def __repr__(self):
        """String representation of the product"""
        return f"<Product {self.title} - Component {self.component_id}>" 