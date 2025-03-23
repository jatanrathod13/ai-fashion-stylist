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
import logging
import openai

from app.database import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.models.style_profile import StyleProfile
from app.models.recommendation import Recommendation
from app.models.outfit import Outfit
from app.models.outfit_component import OutfitComponent
from app.models.product import Product
from app.schemas.recommendation import (
    RecommendationCreate,
    RecommendationResponse,
    RecommendationRequest,
    BudgetRange,
    OutfitCreate,
    OutfitComponentCreate,
    ProductCreate
)
from app.services.recommendation_service import generate_recommendations
from app.models.style_preferences import StylePreferences

router = APIRouter(
    prefix="/recommendations",
    tags=["recommendations"],
    responses={404: {"description": "Not found"}},
)

async def create_outfit_from_data(db: AsyncSession, outfit_data: OutfitCreate, recommendation_id: int) -> Outfit:
    """
    Create an outfit and its components from the provided data.
    
    Args:
        db: Database session
        outfit_data: Outfit creation data
        recommendation_id: ID of the parent recommendation
        
    Returns:
        Created Outfit instance
    """
    # Create outfit
    outfit = Outfit(
        recommendation_id=recommendation_id,
        name=outfit_data.name,
        description=outfit_data.description,
        styling_tips=outfit_data.styling_tips,
        occasions=outfit_data.occasions,
        color_palette=outfit_data.color_palette
    )
    db.add(outfit)
    await db.flush()  # Get outfit ID
    
    # Create components and products
    for component_data in outfit_data.components or []:
        component = OutfitComponent(
            outfit_id=outfit.id,
            type=component_data.type,
            description=component_data.description
        )
        db.add(component)
        await db.flush()  # Get component ID
        
        # Create products
        for product_data in component_data.products or []:
            product = Product(
                component_id=component.id,
                title=product_data.title,
                brand=product_data.brand,
                price=product_data.price,
                currency=product_data.currency,
                url=product_data.url,
                image_url=product_data.image_url,
                retailer=product_data.retailer,
                product_metadata=product_data.metadata
            )
            db.add(product)
    
    return outfit

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
    if request.style_profile_id:
        result = await db.execute(
            select(StyleProfile).where(
                StyleProfile.id == request.style_profile_id,
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
        # Create budget range object using the improved from_string method if it's a string format
        if isinstance(request.budget_min, str) and request.budget_max is None:
            budget = BudgetRange.from_string(request.budget_min)
        else:
            budget = BudgetRange(min=request.budget_min, max=request.budget_max)
        
        # Create preferences object from specific requests
        preferences = StylePreferences(special_requirements=request.specific_requests) if request.specific_requests else None
        
        recommendations = await generate_recommendations(
            db=db,
            user_id=current_user.id,
            profile_id=request.style_profile_id,
            occasion=request.occasion,
            season=request.season,
            budget=budget,
            preferences=preferences
        )
        
        # Save recommendations to database
        db_recommendations = []
        for rec_data in recommendations:
            # Create recommendation
            recommendation = Recommendation(
                user_id=current_user.id,
                title=request.title or f"{request.occasion} recommendations",
                occasion=request.occasion,
                season=request.season,
                budget_min=budget.min,
                budget_max=budget.max,
                status="completed",
                description=rec_data.get("description", ""),
                styling_tips=rec_data.get("styling_tips", []),
                fashion_trends=[]  # We'll add trend support later
            )
            db.add(recommendation)
            await db.flush()  # Get recommendation ID
            
            # Create outfits and their components
            for outfit_data in rec_data.get("outfits", []):
                # Make sure outfit_data is a dictionary before unpacking it
                if isinstance(outfit_data, dict):
                    await create_outfit_from_data(db, OutfitCreate(**outfit_data), recommendation.id)
                else:
                    # If outfit_data is already an OutfitCreate object, convert it to dict
                    outfit_dict = {
                        "name": outfit_data.name,
                        "description": outfit_data.description,
                        "styling_tips": outfit_data.styling_tips,
                        "occasions": outfit_data.occasions,
                        "color_palette": outfit_data.color_palette,
                        "components": outfit_data.components
                    }
                    await create_outfit_from_data(db, OutfitCreate(**outfit_dict), recommendation.id)
            
            db_recommendations.append(recommendation)
        
        await db.commit()
        
        # Refresh all recommendations to get their IDs and relationships
        for rec in db_recommendations:
            await db.refresh(rec)
            
            # Explicitly load the outfits relationship to avoid lazy loading issues
            result = await db.execute(
                select(Outfit).where(Outfit.recommendation_id == rec.id)
            )
            rec.outfits = result.scalars().all()
        
        return db_recommendations
    
    except openai.APIError as e:
        await db.rollback()
        logging.error(f"OpenAI API error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"OpenAI service unavailable: {str(e)}",
        )
    except openai.APIConnectionError as e:
        await db.rollback()
        logging.error(f"OpenAI API connection error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to connect to recommendation service",
        )
    except openai.APITimeoutError as e:
        await db.rollback()
        logging.error(f"OpenAI API timeout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Recommendation service timed out",
        )
    except Exception as e:
        await db.rollback()
        logging.error(f"Recommendation generation error: {str(e)}")
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
    
    # Explicitly load outfits for each recommendation
    for rec in recommendations:
        result = await db.execute(
            select(Outfit).where(Outfit.recommendation_id == rec.id)
        )
        rec.outfits = result.scalars().all()
    
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
    
    # Explicitly load outfits for the recommendation
    result = await db.execute(
        select(Outfit).where(Outfit.recommendation_id == recommendation.id)
    )
    recommendation.outfits = result.scalars().all()
    
    return recommendation


@router.put("/{recommendation_id}/favorite", response_model=RecommendationResponse)
async def toggle_favorite(
    recommendation_id: int,
    is_favorite: bool,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Toggle favorite status for a recommendation.
    """
    # Find the recommendation
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
    
    # Update favorite status
    recommendation.is_favorite = is_favorite
    db.add(recommendation)
    await db.commit()
    
    # Refresh to get updated data
    await db.refresh(recommendation)
    
    # Explicitly load outfits for the recommendation
    result = await db.execute(
        select(Outfit).where(Outfit.recommendation_id == recommendation.id)
    )
    recommendation.outfits = result.scalars().all()
    
    return recommendation


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