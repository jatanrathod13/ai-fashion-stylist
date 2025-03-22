"""
Style profile router.

This module provides API endpoints for style profile management including
creation, retrieval, update, and deletion of style profiles.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.models.style_profile import StyleProfile
from app.schemas.style_profile import (
    StyleProfileCreate,
    StyleProfileResponse,
    StyleProfileUpdate
)

router = APIRouter(
    prefix="/style-profiles",
    tags=["style profiles"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=StyleProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_style_profile(
    profile_data: StyleProfileCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new style profile for the current user.
    """
    # Create new style profile
    db_profile = StyleProfile(
        **profile_data.model_dump(),
        user_id=current_user.id,
    )
    
    try:
        db.add(db_profile)
        await db.commit()
        await db.refresh(db_profile)
        return db_profile
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create style profile. Please try again.",
        )


@router.get("/", response_model=List[StyleProfileResponse])
async def read_style_profiles(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all style profiles for the current user.
    """
    result = await db.execute(
        select(StyleProfile).where(StyleProfile.user_id == current_user.id)
    )
    profiles = result.scalars().all()
    return profiles


@router.get("/{profile_id}", response_model=StyleProfileResponse)
async def read_style_profile(
    profile_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific style profile by ID.
    """
    result = await db.execute(
        select(StyleProfile).where(
            StyleProfile.id == profile_id,
            StyleProfile.user_id == current_user.id
        )
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Style profile not found",
        )
    
    return profile


@router.put("/{profile_id}", response_model=StyleProfileResponse)
async def update_style_profile(
    profile_id: int,
    profile_data: StyleProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a specific style profile.
    """
    result = await db.execute(
        select(StyleProfile).where(
            StyleProfile.id == profile_id,
            StyleProfile.user_id == current_user.id
        )
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Style profile not found",
        )
    
    # Update profile fields
    update_data = profile_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    try:
        await db.commit()
        await db.refresh(profile)
        return profile
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update style profile",
        )


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_style_profile(
    profile_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a specific style profile.
    """
    result = await db.execute(
        select(StyleProfile).where(
            StyleProfile.id == profile_id,
            StyleProfile.user_id == current_user.id
        )
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Style profile not found",
        )
    
    await db.delete(profile)
    await db.commit()
    return None 