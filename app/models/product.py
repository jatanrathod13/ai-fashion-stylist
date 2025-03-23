"""
Product model for storing product recommendations.
"""

from sqlalchemy import Column, String, Integer, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base, BaseModel

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
    product_metadata = Column(JSON, nullable=True)  # Additional product details
    
    def __repr__(self):
        """String representation of the product"""
        return f"<Product {self.title} - Component {self.component_id}>" 