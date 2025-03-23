"""
Base models for database operations

This module defines the base SQLAlchemy models and provides common
functionality for all models.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base

# Create a single base class for all models
Base = declarative_base()

class BaseModel:
    """Base model with common fields and methods for all models"""
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @classmethod
    def create(cls, db, **kwargs):
        """Create a new record in the database"""
        db_obj = cls(**kwargs)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    @classmethod
    def get(cls, db, id):
        """Get a record by ID"""
        return db.query(cls).filter(cls.id == id).first()
    
    @classmethod
    def get_all(cls, db, skip=0, limit=100):
        """Get all records with pagination"""
        return db.query(cls).offset(skip).limit(limit).all()
    
    @classmethod
    def update(cls, db, id, **kwargs):
        """Update a record by ID"""
        db_obj = cls.get(db, id)
        if not db_obj:
            return None
        
        # Update the object with the provided values
        for key, value in kwargs.items():
            if hasattr(db_obj, key):
                setattr(db_obj, key, value)
        
        # Update the updated_at timestamp
        db_obj.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    @classmethod
    def delete(cls, db, id):
        """Delete a record by ID"""
        db_obj = cls.get(db, id)
        if not db_obj:
            return False
        
        db.delete(db_obj)
        db.commit()
        return True 