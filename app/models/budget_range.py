"""
Budget range model.

This module provides the Pydantic model for budget range validation.
"""
from pydantic import BaseModel, Field


class BudgetRange(BaseModel):
    """Model for budget range validation."""
    
    min_amount: float = Field(..., ge=0)
    max_amount: float = Field(..., gt=0)

    def __init__(self, min: float, max: float, **data):
        """Initialize budget range with min and max values."""
        super().__init__(min_amount=min, max_amount=max, **data)

    class Config:
        """Pydantic model configuration."""
        from_attributes = True 