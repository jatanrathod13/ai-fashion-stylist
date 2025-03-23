#!/usr/bin/env python3
"""
Direct test of the recommendation feature using OpenAI API.

This script bypasses the server entirely and uses the same approach as test_openai_direct.py
to demonstrate functionality without requiring authentication.
"""

import os
import json
import asyncio
import argparse
from typing import Dict, List, Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DirectRecommendationTester:
    """Class for testing recommendations directly with OpenAI API"""
    
    def __init__(self, model="gpt-4o-mini"):
        """Initialize the tester with the OpenAI model"""
        # Get API key from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        # Initialize the client
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
    
    async def generate_recommendation(
        self,
        occasion="casual weekend",
        season="summer",
        budget_min=100,
        budget_max=400,
        specific_requests="Comfortable yet stylish outfits"
    ) -> List[Dict]:
        """Generate fashion recommendations"""
        # Build the prompt
        prompt = self._build_recommendation_prompt(
            occasion=occasion,
            season=season,
            budget_min=budget_min,
            budget_max=budget_max,
            specific_requests=specific_requests
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
            print("API Response received")
            
            # Parse the response
            result = json.loads(content)
            
            # Extract recommendations
            if "recommendations" not in result:
                print("Warning: Response missing 'recommendations' key")
                return []
            
            recommendations = result.get("recommendations", [])
            print(f"Successfully processed {len(recommendations)} recommendations")
            
            # Print the first recommendation
            if recommendations:
                self._print_recommendation(recommendations[0])
            
            return recommendations
            
        except Exception as e:
            print(f"Error calling OpenAI API: {str(e)}")
            raise
    
    def _build_recommendation_prompt(
        self,
        occasion=None,
        season=None,
        budget_min=None,
        budget_max=None,
        specific_requests=None
    ) -> str:
        """Build a prompt for the OpenAI API"""
        prompt_parts = [
            "Generate 3 detailed outfit recommendations that match the following criteria:"
        ]
        
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
        
        # Add specific requests if provided
        if specific_requests:
            prompt_parts.append(f"Special requirements: {specific_requests}")
        
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
    
    def _print_recommendation(self, recommendation: Dict) -> None:
        """Print a recommendation in a readable format"""
        print("\n===== Recommendation =====")
        print(f"Description: {recommendation.get('description', 'N/A')}")
        
        # Print items
        items = recommendation.get('items', [])
        print(f"\nItems ({len(items)}):")
        for i, item in enumerate(items, 1):
            print(f"  {i}. {item.get('name', 'N/A')} ({item.get('category', 'N/A')})")
            print(f"     Color: {item.get('color', 'N/A')}")
            print(f"     Price: {item.get('price_range', 'N/A')}")
        
        # Print styling tips
        styling_tips = recommendation.get('styling_tips', [])
        if styling_tips:
            print("\nStyling Tips:")
            for i, tip in enumerate(styling_tips[:3], 1):
                print(f"  {i}. {tip}")
            if len(styling_tips) > 3:
                print(f"  ... plus {len(styling_tips) - 3} more tips")
        
        print("================================\n")


async def main(args):
    """Main function"""
    # Create the tester
    tester = DirectRecommendationTester(model=args.model)
    
    # Generate recommendations
    print(f"Generating fashion recommendations for {args.occasion} in {args.season}...")
    await tester.generate_recommendation(
        occasion=args.occasion,
        season=args.season,
        budget_min=args.budget_min,
        budget_max=args.budget_max,
        specific_requests=args.specific_requests
    )
    
    print("\nDirect test completed successfully!\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test fashion recommendations directly using OpenAI API")
    
    # Model option
    parser.add_argument("--model", default="gpt-4o-mini", help="OpenAI model to use (default: gpt-4o-mini)")
    
    # Recommendation options
    parser.add_argument("--occasion", default="casual weekend", help="Occasion for the outfit")
    parser.add_argument("--season", default="summer", help="Season for the outfit")
    parser.add_argument("--budget-min", type=float, default=100.0, help="Minimum budget in USD")
    parser.add_argument("--budget-max", type=float, default=400.0, help="Maximum budget in USD")
    parser.add_argument("--specific-requests", default="Comfortable yet stylish outfits", help="Specific requirements for the outfits")
    
    args = parser.parse_args()
    
    asyncio.run(main(args)) 