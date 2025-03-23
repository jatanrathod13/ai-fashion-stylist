#!/usr/bin/env python3
"""
Direct test of the recommendation service with the OpenAI API.

This script bypasses the authentication and API layer to test the core recommendation 
functionality using the OpenAI API directly.
"""

import os
import json
import asyncio
import argparse
import re
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables for API keys
load_dotenv()


class TestRecommendationService:
    """Class to test the recommendation service directly with OpenAI API"""
    
    def __init__(self, model: str = "gpt-4o-mini"):
        """Initialize the test service"""
        # Get API key from environment or .env file
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        # Initialize OpenAI client
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        
    async def generate_recommendations(
        self,
        profile: Optional[Dict] = None,
        occasion: Optional[str] = "casual weekend",
        season: Optional[str] = "summer",
        budget_min: float = 100.0,
        budget_max: float = 400.0,
        additional_preferences: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Generate fashion recommendations using OpenAI API directly
        
        Args:
            profile: Optional dict with style profile information
            occasion: Optional occasion for the outfit
            season: Optional season for the outfit
            budget_min: Minimum budget
            budget_max: Maximum budget
            additional_preferences: Optional additional style preferences
            
        Returns:
            List of recommendation dictionaries
        """
        # Build the prompt
        prompt = self._build_recommendation_prompt(
            profile=profile,
            occasion=occasion,
            season=season,
            budget_min=budget_min,
            budget_max=budget_max,
            additional_preferences=additional_preferences
        )
        
        print(f"Using model: {self.model}")
        print("Sending request to OpenAI API...")
        
        try:
            # Call OpenAI API with JSON response format
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a fashion stylist AI assistant that provides detailed, personalized outfit recommendations. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            # Get response content
            content = response.choices[0].message.content
            print("\nAPI Response received")
            
            try:
                # Extract JSON if it's wrapped in code blocks or has other text
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
                if json_match:
                    content = json_match.group(1)
                    print("Extracted JSON from code block")
                
                # Parse response
                result = json.loads(content)
                
                # Validate the response structure
                if "recommendations" not in result:
                    print("Warning: Response missing 'recommendations' key")
                    result = {"recommendations": []}
                
                # Return recommendations
                recommendations = result.get("recommendations", [])
                print(f"Successfully processed {len(recommendations)} recommendations")
                
                # Print a sample of the first recommendation
                if recommendations:
                    self._print_recommendation_sample(recommendations[0])
                
                return recommendations
                
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON from OpenAI response: {str(e)}")
                print("Raw response content saved to 'openai_error.txt'")
                
                # Save the problematic response for debugging
                with open("openai_error.txt", "w") as f:
                    f.write(content)
                
                # Return empty list as fallback
                return []
        except Exception as e:
            print(f"Error calling OpenAI API: {str(e)}")
            raise
    
    def _build_recommendation_prompt(
        self,
        profile: Optional[Dict] = None,
        occasion: Optional[str] = None,
        season: Optional[str] = None,
        budget_min: Optional[float] = None,
        budget_max: Optional[float] = None,
        additional_preferences: Optional[Dict] = None,
    ) -> str:
        """
        Build a detailed prompt for the recommendation engine.
        
        Args:
            profile: Optional dict with style profile information
            occasion: Optional occasion for the outfit
            season: Optional season for the outfit
            budget_min: Minimum budget
            budget_max: Maximum budget
            additional_preferences: Optional additional style preferences
            
        Returns:
            String prompt for the OpenAI API
        """
        prompt_parts = [
            "Generate 3 detailed outfit recommendations that match the following criteria:"
        ]
        
        # Add style profile information if available
        if profile:
            profile_details = []
            
            if profile.get("body_shape"):
                profile_details.append(f"Body shape: {profile['body_shape']}")
            if profile.get("skin_tone"):
                profile_details.append(f"Skin tone: {profile['skin_tone']}")
            if profile.get("height"):
                profile_details.append(f"Height: {profile['height']} cm")
            if profile.get("style_preferences"):
                profile_details.append(f"Style preferences: {', '.join(profile['style_preferences'])}")
            if profile.get("favorite_colors"):
                profile_details.append(f"Favorite colors: {', '.join(profile['favorite_colors'])}")
            if profile.get("disliked_items"):
                profile_details.append(f"Dislikes: {', '.join(profile['disliked_items'])}")
            
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
        if budget_min is not None and budget_max is not None:
            budget_text = f"Budget: {budget_min} to {budget_max} USD"
            prompt_parts.append(budget_text)
        
        # Add additional preferences if provided
        if additional_preferences:
            pref_details = []
            
            if additional_preferences.get("favorite_colors"):
                pref_details.append(f"Color palette: {', '.join(additional_preferences['favorite_colors'])}")
            if additional_preferences.get("preferred_styles"):
                pref_details.append(f"Styles: {', '.join(additional_preferences['preferred_styles'])}")
            if additional_preferences.get("favorite_brands"):
                pref_details.append(f"Preferred brands: {', '.join(additional_preferences['favorite_brands'])}")
            if additional_preferences.get("special_requirements"):
                pref_details.append(f"Special requirements: {additional_preferences['special_requirements']}")
            
            if pref_details:
                prompt_parts.append("Additional Preferences:")
                prompt_parts.extend([f"- {detail}" for detail in pref_details])
        
        # Add output format instructions
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
        
        full_prompt = "\n\n".join(prompt_parts)
        print(f"\nPrompt:\n{full_prompt}\n")
        return full_prompt
    
    def _print_recommendation_sample(self, recommendation: Dict) -> None:
        """Print a sample of a recommendation for display purposes"""
        print("\n===== Sample Recommendation =====")
        print(f"Description: {recommendation.get('description', 'N/A')}")
        
        # Print items
        items = recommendation.get('items', [])
        print(f"\nItems ({len(items)}):")
        for i, item in enumerate(items, 1):
            print(f"  {i}. {item.get('name', 'N/A')} ({item.get('category', 'N/A')})")
            print(f"     Color: {item.get('color', 'N/A')}")
            print(f"     Price: {item.get('price_range', 'N/A')}")
        
        # Print styling tips (first 2)
        styling_tips = recommendation.get('styling_tips', [])
        if styling_tips:
            print("\nStyling Tips:")
            for i, tip in enumerate(styling_tips[:2], 1):
                print(f"  {i}. {tip}")
            if len(styling_tips) > 2:
                print(f"  ... plus {len(styling_tips) - 2} more tips")
        
        print("================================\n")


async def main(args):
    """Main function"""
    # Create the test service
    test_service = TestRecommendationService(model=args.model)
    
    # Example profile (can be customized via command-line args)
    profile = {
        "body_shape": args.body_shape,
        "skin_tone": args.skin_tone, 
        "height": args.height,
        "style_preferences": args.style_preferences.split(",") if args.style_preferences else None,
        "favorite_colors": args.favorite_colors.split(",") if args.favorite_colors else None,
        "disliked_items": args.disliked_items.split(",") if args.disliked_items else None
    }
    
    # Additional preferences
    additional_preferences = {
        "special_requirements": args.special_requirements
    }
    
    # Generate recommendations
    print(f"Generating fashion recommendations for {args.occasion} in {args.season}...")
    await test_service.generate_recommendations(
        profile=profile,
        occasion=args.occasion,
        season=args.season,
        budget_min=args.budget_min,
        budget_max=args.budget_max,
        additional_preferences=additional_preferences
    )
    
    print("\nRecommendation test completed successfully!\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test OpenAI API for fashion recommendations")
    
    # Model
    parser.add_argument("--model", default="gpt-4o-mini", help="OpenAI model to use (default: gpt-4o-mini)")
    
    # Basic parameters
    parser.add_argument("--occasion", default="casual weekend", help="Occasion for the outfit")
    parser.add_argument("--season", default="summer", help="Season for the outfit")
    parser.add_argument("--budget", help="Budget range in format 'min-max' (e.g., '100-400')")
    parser.add_argument("--budget-min", type=float, default=100.0, help="Minimum budget in USD")
    parser.add_argument("--budget-max", type=float, default=400.0, help="Maximum budget in USD")
    
    # Style profile parameters
    parser.add_argument("--body-shape", default="Rectangle", help="Body shape")
    parser.add_argument("--skin-tone", default="Medium", help="Skin tone")
    parser.add_argument("--height", type=int, default=175, help="Height in cm")
    parser.add_argument("--style-preferences", default="casual,minimalist,classic", help="Comma-separated style preferences")
    parser.add_argument("--favorite-colors", default="blue,gray,white", help="Comma-separated favorite colors")
    parser.add_argument("--disliked-items", default="crop tops,skinny jeans", help="Comma-separated disliked items")
    
    # Additional preferences
    parser.add_argument("--special-requirements", default="Looking for comfortable yet stylish outfits", help="Special requirements or notes")
    
    args = parser.parse_args()
    
    # Process budget range if provided
    if args.budget:
        try:
            budget_parts = args.budget.split('-')
            if len(budget_parts) == 2:
                args.budget_min = float(budget_parts[0])
                args.budget_max = float(budget_parts[1])
        except ValueError:
            print(f"Warning: Could not parse budget range '{args.budget}'. Using defaults.")
    
    asyncio.run(main(args)) 