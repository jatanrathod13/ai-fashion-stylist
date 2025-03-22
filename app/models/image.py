"""
Image model

This module defines the Image model for storing user-uploaded images
and their analysis results.
"""
from sqlalchemy import Column, String, Integer, JSON, ForeignKey, Boolean, Text, Float
from sqlalchemy.orm import relationship

from app.models.base import Base, BaseModel

class Image(Base, BaseModel):
    """Image model for storing user-uploaded images"""
    
    __tablename__ = "images"
    
    # Relationship to user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User")
    
    # Image details
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    mime_type = Column(String, nullable=False)
    
    # Image dimensions
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    
    # Analysis status
    is_analyzed = Column(Boolean, default=False)
    analysis_status = Column(String, default="pending")  # pending, processing, completed, failed
    
    # Analysis results
    analysis_results = Column(JSON, nullable=True)
    
    # Relationship to style profile if this image was used to create/update one
    style_profile_id = Column(Integer, ForeignKey("style_profiles.id"), nullable=True)
    style_profile = relationship("StyleProfile")
    
    def __repr__(self):
        """String representation of the image"""
        return f"<Image {self.filename} - User {self.user_id}>"


class ClothingItem(Base, BaseModel):
    """ClothingItem model for storing detected clothing items in images"""
    
    __tablename__ = "clothing_items"
    
    # Relationship to image
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False)
    image = relationship("Image")
    
    # Item details
    item_type = Column(String, nullable=False)  # top, bottom, dress, etc.
    description = Column(Text, nullable=True)
    
    # Bounding box coordinates (normalized 0-1)
    bbox_x = Column(Float, nullable=True)
    bbox_y = Column(Float, nullable=True)
    bbox_width = Column(Float, nullable=True)
    bbox_height = Column(Float, nullable=True)
    
    # Item attributes
    color = Column(String, nullable=True)
    pattern = Column(String, nullable=True)
    material = Column(String, nullable=True)
    style = Column(String, nullable=True)
    
    # Additional attributes as JSON
    attributes = Column(JSON, nullable=True)
    
    def __repr__(self):
        """String representation of the clothing item"""
        return f"<ClothingItem {self.item_type} - Image {self.image_id}>" 