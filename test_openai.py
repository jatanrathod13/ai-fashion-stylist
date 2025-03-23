#!/usr/bin/env python3
"""
Direct test of OpenAI API with gpt-4o-mini model
"""

import os
import json
import asyncio
import argparse
import re
from typing import Dict, Any, List
from openai import AsyncOpenAI

async def test_openai_api(model: str = "gpt-4o-mini") -> None:
    """Test the OpenAI API with a simple recommendation prompt"""
    # Get API key from environment or .env file
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    # Initialize client
    client = AsyncOpenAI(api_key=api_key)
    
    # Define a sample fashion recommendation prompt
    prompt = """
    Generate 3 detailed outfit recommendations that match the following criteria:
    
    Occasion: casual weekend
    Season: summer
    Budget: 100 to 400 USD
    
    Additional Preferences:
    - Color palette: blue, white, beige
    - Style: minimalist, casual
    
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
          ],
          "styling_tips": ["Tip 1", "Tip 2", "Tip 3"],
          "reasoning": "Explanation of why this outfit works for the given profile and occasion"
        }
      ]
    }
    
    Your response must be valid JSON. Do not include any text before or after the JSON object.
    """
    
    print(f"Testing OpenAI API with model: {model}")
    print("Sending request...")
    
    try:
        # Call OpenAI API
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a fashion stylist AI assistant that provides detailed, personalized outfit recommendations. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        # Get response content
        content = response.choices[0].message.content
        print("\nAPI Response:")
        print(f"```json\n{content}\n```")
        
        # Try to parse as JSON
        try:
            # Extract JSON if it's wrapped in code blocks or has other text
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
            
            result = json.loads(content)
            recommendations = result.get("recommendations", [])
            print(f"\nSuccessfully parsed {len(recommendations)} recommendations")
            
            # Print a sample recommendation in a more readable format
            if recommendations:
                print("\nSample recommendation:")
                sample = recommendations[0]
                print(f"Description: {sample['description']}")
                print(f"Items: {len(sample['items'])} items included")
                print(f"Styling tips: {', '.join(sample['styling_tips'][:2])}...")
            
            return recommendations
        except json.JSONDecodeError as e:
            print(f"\nWarning: Response couldn't be parsed as JSON. Error: {str(e)}")
            print("Raw response content saved to 'openai_response.txt'")
            
            # Save the raw response to a file for debugging
            with open("openai_response.txt", "w") as f:
                f.write(content)
                
            return None
            
    except Exception as e:
        print(f"Error calling OpenAI API: {str(e)}")
        raise

async def main(model: str) -> None:
    """Main function"""
    await test_openai_api(model)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test OpenAI API with gpt-4o-mini model")
    parser.add_argument("--model", default="gpt-4o-mini", 
                        help="OpenAI model to test (default: gpt-4o-mini)")
    
    args = parser.parse_args()
    
    asyncio.run(main(args.model)) 