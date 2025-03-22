"""
Image router.

This module provides API endpoints for image management including
upload, analysis, and retrieval of user images.
"""

import os
import uuid
from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.models.image import Image, ClothingItem
from app.schemas.image import (
    ImageResponse,
    ImageAnalysisResponse,
    ClothingItemResponse
)
from app.services.vision_service import vision_service
from app.config import settings

router = APIRouter(
    prefix="/images",
    tags=["images"],
    responses={404: {"description": "Not found"}},
)


async def save_upload_file(upload_file: UploadFile, user_id: int) -> str:
    """Save an uploaded file to disk and return the path."""
    # Create upload directory if it doesn't exist
    upload_dir = os.path.join(settings.UPLOAD_DIR, str(user_id))
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate a unique filename
    file_extension = os.path.splitext(upload_file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save the file
    with open(file_path, "wb") as f:
        content = await upload_file.read()
        f.write(content)
    
    return file_path


@router.post("/upload", response_model=ImageResponse, status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a new image file.
    """
    # Check if file is an image
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image",
        )
    
    # Save the file
    file_path = await save_upload_file(file, current_user.id)
    
    # Get image dimensions
    try:
        width, height = vision_service.get_image_dimensions(file_path)
    except Exception as e:
        os.remove(file_path)  # Clean up the file
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image file: {str(e)}",
        )
    
    # Create database record
    image = Image(
        file_path=file_path,
        original_filename=file.filename,
        width=width,
        height=height,
        user_id=current_user.id,
    )
    
    try:
        db.add(image)
        await db.commit()
        await db.refresh(image)
        return image
    except IntegrityError:
        os.remove(file_path)  # Clean up the file
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not save image information. Please try again.",
        )


@router.post("/{image_id}/analyze", response_model=ImageAnalysisResponse)
async def analyze_image(
    image_id: int,
    analysis_type: str = "full",
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Analyze an uploaded image to extract clothing items and body attributes.
    """
    # Get the image
    result = await db.execute(
        select(Image).where(
            Image.id == image_id,
            Image.user_id == current_user.id
        )
    )
    image = result.scalar_one_or_none()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found",
        )
    
    try:
        # Run analysis using the Vision Service
        analysis = await vision_service.analyze_image(image.file_path, analysis_type)
        
        # Update image with analysis results
        image.is_analyzed = True
        image.analysis_results = analysis
        
        # If clothing items were extracted, create clothing item records
        if "clothing_items" in analysis and analysis["clothing_items"]:
            for item_data in analysis["clothing_items"]:
                clothing_item = ClothingItem(
                    image_id=image.id,
                    category=item_data.get("category", "unknown"),
                    color=item_data.get("color", ""),
                    pattern=item_data.get("pattern", ""),
                    brand=item_data.get("brand", ""),
                    style=item_data.get("style", ""),
                    description=item_data.get("description", ""),
                    position_data=item_data.get("position", {})
                )
                db.add(clothing_item)
        
        await db.commit()
        await db.refresh(image)
        
        # Return combined results
        return {
            "image": image,
            "analysis_results": analysis
        }
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image analysis failed: {str(e)}",
        )


@router.get("/", response_model=List[ImageResponse])
async def read_images(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all images uploaded by the current user.
    """
    result = await db.execute(
        select(Image).where(Image.user_id == current_user.id)
    )
    images = result.scalars().all()
    return images


@router.get("/{image_id}", response_model=ImageResponse)
async def read_image(
    image_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific image by ID.
    """
    result = await db.execute(
        select(Image).where(
            Image.id == image_id,
            Image.user_id == current_user.id
        )
    )
    image = result.scalar_one_or_none()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found",
        )
    
    return image


@router.get("/{image_id}/clothing-items", response_model=List[ClothingItemResponse])
async def read_clothing_items(
    image_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all clothing items extracted from a specific image.
    """
    # Verify the image belongs to the current user
    result = await db.execute(
        select(Image).where(
            Image.id == image_id,
            Image.user_id == current_user.id
        )
    )
    image = result.scalar_one_or_none()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found",
        )
    
    # Get clothing items
    result = await db.execute(
        select(ClothingItem).where(ClothingItem.image_id == image_id)
    )
    clothing_items = result.scalars().all()
    
    return clothing_items


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    image_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a specific image.
    """
    result = await db.execute(
        select(Image).where(
            Image.id == image_id,
            Image.user_id == current_user.id
        )
    )
    image = result.scalar_one_or_none()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found",
        )
    
    # Delete the file from disk
    if os.path.exists(image.file_path):
        os.remove(image.file_path)
    
    # Delete from database
    await db.delete(image)
    await db.commit()
    
    return None 