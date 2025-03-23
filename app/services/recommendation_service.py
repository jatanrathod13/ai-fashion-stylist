"""
Recommendation Service.

This module provides functionality for generating personalized fashion recommendations
based on user style profiles, preferences, and specific requirements.
"""

import os
import json
import logging
import re
import time
from typing import Dict, List, Optional, Any
import openai
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.style_profile import StyleProfile
from app.schemas.recommendation import BudgetRange, StylePreferences, OutfitCreate, OutfitComponentCreate, ProductCreate
from app.config import settings

# Initialize OpenAI client
client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

# Model to use for recommendations
MODEL = settings.OPENAI_TEXT_MODEL

# Set up logging
logger = logging.getLogger(__name__)

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
    try:
        # Verbose logging for debugging
        print(f"DEBUG: Starting recommendation generation for user {user_id}")
        
        # Get style profile if provided
        profile = None
        if profile_id:
            print(f"DEBUG: Looking up style profile {profile_id}")
            result = await db.execute(
                select(StyleProfile).where(
                    StyleProfile.id == profile_id,
                    StyleProfile.user_id == user_id
                )
            )
            profile = result.scalar_one_or_none()
            print(f"DEBUG: Profile found: {profile is not None}")
        
        # Build prompt with improved method
        prompt = _build_recommendation_prompt(
            profile=profile,
            occasion=occasion,
            season=season,
            budget=budget,
            preferences=preferences
        )
        
        print(f"DEBUG: Built prompt for OpenAI API. Length: {len(prompt)}")
        logger.info("Sending request to OpenAI API for user %d", user_id)
        
        # Check OpenAI API key
        if not settings.OPENAI_API_KEY:
            print("DEBUG: OPENAI_API_KEY is not set!")
            raise ValueError("OpenAI API key is not configured")
        
        print(f"DEBUG: Using OpenAI model: {MODEL}")
        
        # Call OpenAI API with improved response format handling
        print("DEBUG: Sending request to OpenAI API...")
        try:
            response = await client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are a fashion stylist AI assistant that provides detailed, personalized outfit recommendations. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            print("DEBUG: Received response from OpenAI API")
        except Exception as openai_error:
            print(f"DEBUG: OpenAI API error: {str(openai_error)}")
            raise
        
        # Get response content
        content = response.choices[0].message.content
        print(f"DEBUG: Response content length: {len(content)}")
        
        # Process the response using enhanced method
        result = process_openai_response(content, user_id, profile_id)
        print(f"DEBUG: Processed response. Number of recommendations: {len(result)}")
        return result
        
    except Exception as e:
        print(f"DEBUG: Error in generate_recommendations: {str(e)}")
        logger.error("Error generating recommendations: %s", str(e))
        # Save more detailed error information for debugging
        error_file = f"openai_error_{user_id}_{profile_id or 'none'}_{int(time.time())}.log"
        try:
            with open(error_file, "w") as f:
                f.write(f"Error: {str(e)}\n\n")
                if 'response' in locals():
                    f.write(f"Response: {response}\n\n")
                if 'content' in locals():
                    f.write(f"Content: {content}\n\n")
                f.write(f"Request details:\n")
                f.write(f"User: {user_id}\n")
                f.write(f"Profile: {profile_id}\n")
                f.write(f"Occasion: {occasion}\n")
                f.write(f"Season: {season}\n")
            logger.info("Error details saved to %s", error_file)
        except Exception as write_error:
            logger.error("Failed to write error details: %s", str(write_error))
        
        # Re-raise the exception to be handled by the API layer
        raise


def transform_openai_recommendation(rec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform an OpenAI recommendation into our database schema format.
    
    Args:
        rec: Raw recommendation from OpenAI
        
    Returns:
        Transformed recommendation matching our schema
    """
    # Create outfits from items
    outfits = []
    if "items" in rec and isinstance(rec["items"], list):
        # Group items by category into a single outfit
        outfit_components = []
        for item in rec["items"]:
            if not isinstance(item, dict):
                continue
                
            # Create product
            product_data = {
                "title": item.get("name", ""),
                "brand": item.get("brand"),
                "price": None,  # We'll need to parse price_range to get an actual value
                "currency": "USD",
                "metadata": {
                    "color": item.get("color"),
                    "alternatives": item.get("alternatives", [])
                }
            }
            
            # Create outfit component data as a dictionary
            component_data = {
                "type": item.get("category", "unknown"),
                "description": item.get("description", ""),
                "products": [product_data]
            }
            
            outfit_components.append(component_data)
        
        # Create outfit data as a dictionary
        if outfit_components:
            outfit_data = {
                "name": rec.get("description", "Recommended Outfit"),
                "description": rec.get("description"),
                "styling_tips": rec.get("styling_tips", []),
                "components": outfit_components
            }
            outfits.append(outfit_data)
    
    # Return transformed recommendation
    return {
        "description": rec.get("description", ""),
        "outfits": outfits,
        "styling_tips": rec.get("styling_tips", []),
        "reasoning": rec.get("reasoning", "")
    }

def process_openai_response(content: str, user_id: int, profile_id: Optional[int] = None) -> List[Dict]:
    """
    Process the OpenAI API response, extracting and validating the recommendations.
    
    Args:
        content: The response content from OpenAI
        user_id: User ID for logging purposes
        profile_id: Profile ID for logging purposes
        
    Returns:
        List of recommendation dictionaries
    """
    try:
        # Extract JSON if it's wrapped in code blocks or has other text
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
        if json_match:
            content = json_match.group(1)
            logger.info("Extracted JSON from code block")
        
        # Parse response
        result = json.loads(content)
        
        # Validate the response structure
        if "recommendations" not in result:
            logger.warning("OpenAI response missing 'recommendations' key for user %d", user_id)
            return []
        
        # Get recommendations and validate their structure
        recommendations = result.get("recommendations", [])
        valid_recommendations = []
        
        for i, rec in enumerate(recommendations):
            # Validate recommendation structure
            if not isinstance(rec, dict):
                logger.warning("Recommendation %d is not a dictionary for user %d", i, user_id)
                continue
                
            if "items" not in rec or not isinstance(rec["items"], list):
                logger.warning("Recommendation %d missing valid 'items' for user %d", i, user_id)
                continue
                
            # Transform recommendation to match our schema
            try:
                transformed_rec = transform_openai_recommendation(rec)
                valid_recommendations.append(transformed_rec)
            except Exception as e:
                logger.error("Error transforming recommendation %d for user %d: %s", 
                           i, user_id, str(e))
                continue
        
        logger.info("Successfully processed %d recommendations for user %d", 
                    len(valid_recommendations), user_id)
        
        return valid_recommendations
        
    except json.JSONDecodeError as e:
        logger.error("Error parsing JSON from OpenAI response for user %d: %s", 
                     user_id, str(e))
        
        # Save the problematic response for debugging
        error_file = f"openai_error_{user_id}_{profile_id or 'none'}_{int(time.time())}.txt"
        with open(error_file, "w") as f:
            f.write(content)
        logger.info("Saved problematic response to %s", error_file)
        
        # Return empty list as fallback
        return []


def _build_recommendation_prompt(
    profile: Optional[StyleProfile] = None,
    occasion: Optional[str] = None,
    season: Optional[str] = None,
    budget: Optional[BudgetRange] = None,
    preferences: Optional[StylePreferences] = None,
) -> str:
    """
    Build a detailed prompt for the recommendation engine with improved formatting.
    
    Args:
        profile: Optional style profile
        occasion: Optional occasion for the outfit
        season: Optional season for the outfit
        budget: Optional budget range
        preferences: Optional additional style preferences
        
    Returns:
        Formatted prompt string
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
        budget_text = f"Budget: {budget.min} to {budget.max} USD"
        prompt_parts.append(budget_text)
    
    # Add additional preferences if provided
    if preferences:
        pref_details = []
        
        if preferences.favorite_colors:
            pref_details.append(f"Color palette: {', '.join(preferences.favorite_colors)}")
        if preferences.preferred_styles:
            pref_details.append(f"Styles: {', '.join(preferences.preferred_styles)}")
        if preferences.favorite_brands:
            pref_details.append(f"Preferred brands: {', '.join(preferences.favorite_brands)}")
        if preferences.special_requirements:
            pref_details.append(f"Special requirements: {preferences.special_requirements}")
        if preferences.disliked_items:
            pref_details.append(f"Disliked items: {', '.join(preferences.disliked_items)}")
        
        if pref_details:
            prompt_parts.append("Additional Preferences:")
            prompt_parts.extend([f"- {detail}" for detail in pref_details])
    
    # Add output format instructions with clear JSON structure
    prompt_parts.append("""
Return your response as valid JSON following this exact structure:
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

Your response must be valid JSON. Do not include any text before or after the JSON object.
""")
    
    return "\n\n".join(prompt_parts) 