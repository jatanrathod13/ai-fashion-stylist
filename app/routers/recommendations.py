"""
Recommendations router.

This module provides API endpoints for generating, retrieving, and
managing style recommendations.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.models.style_profile import StyleProfile
from app.models.recommendation import Recommendation
from app.schemas.recommendation import (
    RecommendationCreate,
    RecommendationResponse,
    RecommendationRequest
)
from app.services.recommendation_service import generate_recommendations

router = APIRouter(
    prefix="/recommendations",
    tags=["recommendations"],
    responses={404: {"description": "Not found"}},
)


@router.post("/generate", response_model=List[RecommendationResponse])
async def create_recommendations(
    request: RecommendationRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate new style recommendations based on the provided criteria.
    """
    # Validate that the profile belongs to the user
    if request.profile_id:
        result = await db.execute(
            select(StyleProfile).where(
                StyleProfile.id == request.profile_id,
                StyleProfile.user_id == current_user.id
            )
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Style profile not found",
            )
    
    # Generate recommendations
    try:
        recommendations = await generate_recommendations(
            db=db,
            user_id=current_user.id,
            profile_id=request.profile_id,
            occasion=request.occasion,
            season=request.season,
            budget=request.budget,
            preferences=request.preferences
        )
        
        # Save recommendations to database
        db_recommendations = []
        for rec_data in recommendations:
            recommendation = Recommendation(
                user_id=current_user.id,
                profile_id=request.profile_id,
                occasion=request.occasion,
                season=request.season,
                budget_min=request.budget.min_price if request.budget else None,
                budget_max=request.budget.max_price if request.budget else None,
                items=rec_data.get("items", []),
                description=rec_data.get("description", ""),
                styling_tips=rec_data.get("styling_tips", []),
                reasoning=rec_data.get("reasoning", "")
            )
            db.add(recommendation)
            db_recommendations.append(recommendation)
        
        await db.commit()
        
        # Refresh all recommendations to get their IDs
        for rec in db_recommendations:
            await db.refresh(rec)
        
        return db_recommendations
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}",
        )


@router.get("/", response_model=List[RecommendationResponse])
async def read_recommendations(
    profile_id: Optional[int] = None,
    occasion: Optional[str] = None,
    season: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all recommendations for the current user with optional filters.
    """
    query = select(Recommendation).where(Recommendation.user_id == current_user.id)
    
    # Apply filters if provided
    if profile_id:
        query = query.where(Recommendation.profile_id == profile_id)
    if occasion:
        query = query.where(Recommendation.occasion == occasion)
    if season:
        query = query.where(Recommendation.season == season)
    
    result = await db.execute(query)
    recommendations = result.scalars().all()
    return recommendations


@router.get("/{recommendation_id}", response_model=RecommendationResponse)
async def read_recommendation(
    recommendation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific recommendation by ID.
    """
    result = await db.execute(
        select(Recommendation).where(
            Recommendation.id == recommendation_id,
            Recommendation.user_id == current_user.id
        )
    )
    recommendation = result.scalar_one_or_none()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found",
        )
    
    return recommendation


@router.put("/{recommendation_id}/favorite", response_model=RecommendationResponse)
async def toggle_favorite(
    recommendation_id: int,
    is_favorite: bool,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Mark or unmark a recommendation as favorite.
    """
    result = await db.execute(
        select(Recommendation).where(
            Recommendation.id == recommendation_id,
            Recommendation.user_id == current_user.id
        )
    )
    recommendation = result.scalar_one_or_none()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found",
        )
    
    recommendation.is_favorite = is_favorite
    
    try:
        await db.commit()
        await db.refresh(recommendation)
        return recommendation
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update recommendation",
        )


@router.delete("/{recommendation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recommendation(
    recommendation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a specific recommendation.
    """
    result = await db.execute(
        select(Recommendation).where(
            Recommendation.id == recommendation_id,
            Recommendation.user_id == current_user.id
        )
    )
    recommendation = result.scalar_one_or_none()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found",
        )
    
    await db.delete(recommendation)
    await db.commit()
    
    return None 