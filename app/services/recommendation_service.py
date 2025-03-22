"""
Recommendation Service.

This module provides functionality for generating personalized fashion recommendations
based on user style profiles, preferences, and specific requirements.
"""

import os
import json
from typing import Dict, List, Optional
import openai
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.style_profile import StyleProfile
from app.schemas.recommendation import BudgetRange, StylePreferences
from app.config import settings

# Initialize OpenAI client
client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

# Model to use for recommendations
MODEL = "gpt-4o"


async def generate_recommendations(
    db: AsyncSession,
    user_id: int,
    profile_id: Optional[int] = None,
    occasion: Optional[str] = None,
    season: Optional[str] = None,
    budget: Optional[BudgetRange] = None,
    preferences: Optional[StylePreferences] = None,
) -> List[Dict]:
    """
    Generate personalized fashion recommendations.
    
    Args:
        db: Database session
        user_id: ID of the user
        profile_id: Optional ID of the style profile to use
        occasion: Optional occasion for the outfit
        season: Optional season for the outfit
        budget: Optional budget range
        preferences: Optional additional style preferences
        
    Returns:
        List of recommendation dictionaries
    """
    # Get style profile if provided
    profile = None
    if profile_id:
        result = await db.execute(
            select(StyleProfile).where(
                StyleProfile.id == profile_id,
                StyleProfile.user_id == user_id
            )
        )
        profile = result.scalar_one_or_none()
    
    # Build prompt
    prompt = _build_recommendation_prompt(
        profile=profile,
        occasion=occasion,
        season=season,
        budget=budget,
        preferences=preferences
    )
    
    # Call OpenAI API
    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a fashion stylist AI assistant that provides detailed, personalized outfit recommendations."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.7,
    )
    
    # Parse response
    content = response.choices[0].message.content
    result = json.loads(content)
    
    # Return recommendations
    return result.get("recommendations", [])


def _build_recommendation_prompt(
    profile: Optional[StyleProfile] = None,
    occasion: Optional[str] = None,
    season: Optional[str] = None,
    budget: Optional[BudgetRange] = None,
    preferences: Optional[StylePreferences] = None,
) -> str:
    """
    Build a detailed prompt for the recommendation engine.
    """
    prompt_parts = [
        "Generate 3 detailed outfit recommendations that match the following criteria:"
    ]
    
    # Add style profile information if available
    if profile:
        profile_details = []
        
        if profile.body_shape:
            profile_details.append(f"Body shape: {profile.body_shape}")
        if profile.skin_tone:
            profile_details.append(f"Skin tone: {profile.skin_tone}")
        if profile.height:
            profile_details.append(f"Height: {profile.height} cm")
        if profile.weight:
            profile_details.append(f"Weight: {profile.weight} kg")
        if profile.age:
            profile_details.append(f"Age: {profile.age}")
        if profile.gender:
            profile_details.append(f"Gender: {profile.gender}")
        if profile.style_preferences:
            profile_details.append(f"Style preferences: {', '.join(profile.style_preferences)}")
        if profile.favorite_colors:
            profile_details.append(f"Favorite colors: {', '.join(profile.favorite_colors)}")
        if profile.disliked_items:
            profile_details.append(f"Dislikes: {', '.join(profile.disliked_items)}")
        if profile.sizes:
            size_details = [f"{k}: {v}" for k, v in profile.sizes.items()]
            profile_details.append(f"Sizes: {', '.join(size_details)}")
        
        if profile_details:
            prompt_parts.append("Style Profile Details:")
            prompt_parts.extend([f"- {detail}" for detail in profile_details])
    
    # Add occasion if provided
    if occasion:
        prompt_parts.append(f"Occasion: {occasion}")
    
    # Add season if provided
    if season:
        prompt_parts.append(f"Season: {season}")
    
    # Add budget if provided
    if budget:
        budget_text = f"Budget: {budget.min_price} to {budget.max_price} {budget.currency}"
        prompt_parts.append(budget_text)
    
    # Add additional preferences if provided
    if preferences:
        pref_details = []
        
        if preferences.color_palette:
            pref_details.append(f"Color palette: {', '.join(preferences.color_palette)}")
        if preferences.styles:
            pref_details.append(f"Styles: {', '.join(preferences.styles)}")
        if preferences.brands:
            pref_details.append(f"Preferred brands: {', '.join(preferences.brands)}")
        if preferences.sustainable_only:
            pref_details.append("Only include sustainable/eco-friendly options")
        
        if pref_details:
            prompt_parts.append("Additional Preferences:")
            prompt_parts.extend([f"- {detail}" for detail in pref_details])
    
    # Add output format instructions
    prompt_parts.append("""
Please format each recommendation as a JSON object with the following structure:
{
  "recommendations": [
    {
      "description": "Brief overall description of the outfit",
      "items": [
        {
          "name": "Item name",
          "category": "Category (e.g., top, bottom, shoes, accessory)",
          "description": "Detailed description",
          "color": "Color",
          "brand": "Suggested brand (optional)",
          "price_range": "Estimated price range",
          "alternatives": ["Alternative 1", "Alternative 2"]
        }
        // More items...
      ],
      "styling_tips": ["Tip 1", "Tip 2", "Tip 3"],
      "reasoning": "Explanation of why this outfit works for the given profile and occasion"
    }
    // More recommendations...
  ]
}
""")
    
    return "\n\n".join(prompt_parts) 