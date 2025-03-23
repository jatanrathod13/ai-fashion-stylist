#!/usr/bin/env python3
"""
Test script for the recommendation endpoint with gpt-4o-mini model.
"""

import asyncio
import json
import httpx
import argparse
import time
import sys
from typing import Dict, Any, Optional

# Default values
DEFAULT_API_URL = "http://localhost:8000"
DEFAULT_EMAIL = "testuser123@example.com"  # Just for display
DEFAULT_USERNAME = "testuser123"
DEFAULT_PASSWORD = "testpassword123"
DEFAULT_PROFILE_ID = 4

async def login(client: httpx.AsyncClient, email: str, password: str) -> str:
    """Login and get access token"""
    print(f"🔐 Attempting to login as {email}...")
    login_data = {
        "username": DEFAULT_USERNAME,  # API expects actual username, not email
        "password": password,
        "grant_type": "password"
    }
    
    try:
        response = await client.post(
            f"{client.base_url}/api/auth/token",
            data=login_data,  # Using form data instead of JSON
            timeout=30.0
        )
        
        response.raise_for_status()
        data = response.json()
        print("✅ Login successful!")
        return data["access_token"]
    except httpx.HTTPStatusError as e:
        print(f"❌ Login failed with status code: {e.response.status_code}")
        print(f"Response: {e.response.text}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Login failed with error: {str(e)}")
        sys.exit(1)

async def get_profile(client: httpx.AsyncClient, profile_id: int) -> Dict[str, Any]:
    """Get style profile by ID"""
    print(f"📋 Getting profile {profile_id}...")
    
    try:
        response = await client.get(
            f"{client.base_url}/api/style-profiles/{profile_id}",
            timeout=30.0
        )
        
        response.raise_for_status()
        profile = response.json()
        print(f"✅ Successfully retrieved profile: {profile['name']}")
        return profile
    except httpx.HTTPStatusError as e:
        print(f"❌ Failed to get profile with status code: {e.response.status_code}")
        print(f"Response: {e.response.text}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to get profile with error: {str(e)}")
        sys.exit(1)

async def generate_recommendation(
    client: httpx.AsyncClient, 
    profile_id: int,
    title: str = "Summer Vacation",
    occasion: str = "vacation",
    season: str = "summer",
    budget_min: float = 100.0,
    budget_max: float = 500.0,
    specific_requests: str = "Looking for comfortable but stylish outfits for a beach vacation"
) -> Dict[str, Any]:
    """Generate a fashion recommendation"""
    
    request_data = {
        "title": title,
        "occasion": occasion,
        "season": season,
        "budget_min": budget_min,
        "budget_max": budget_max,
        "style_profile_id": profile_id,
        "specific_requests": specific_requests
    }
    
    print("\n📤 Sending recommendation request with data:")
    print(json.dumps(request_data, indent=2))
    print("\n⏳ Generating recommendation (this may take up to 60 seconds)...")
    
    start_time = time.time()
    
    try:
        response = await client.post(
            f"{client.base_url}/api/recommendations/generate",
            json=request_data,
            timeout=120.0  # Increase timeout for model generation
        )
        
        response.raise_for_status()
        
        elapsed_time = time.time() - start_time
        recommendations = response.json()
        
        print(f"✅ Successfully generated recommendations in {elapsed_time:.2f} seconds!")
        return recommendations
    except httpx.HTTPStatusError as e:
        print(f"❌ Failed to generate recommendation with status code: {e.response.status_code}")
        print(f"Response: {e.response.text}")
        sys.exit(1)
    except httpx.ReadTimeout:
        print("❌ Request timed out - the server took too long to respond.")
        print("This might be due to high server load or the model taking too long to generate.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to generate recommendation with error: {str(e)}")
        sys.exit(1)

def print_recommendation_details(recommendations: list) -> None:
    """Print details of generated recommendations in a readable format"""
    if not recommendations:
        print("No recommendations were generated.")
        return
    
    print(f"\n🎨 Received {len(recommendations)} recommendations:\n")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"📱 Recommendation {i}:")
        print(f"  Description: {rec.get('description', 'N/A')}")
        
        # Print items
        items = rec.get('items', [])
        print(f"  Items ({len(items)}):")
        for item in items:
            print(f"    - {item.get('name', 'N/A')} ({item.get('category', 'N/A')})")
            print(f"      {item.get('description', 'N/A')}")
            print(f"      Color: {item.get('color', 'N/A')}, Price: {item.get('price_range', 'N/A')}")
        
        # Print styling tips
        styling_tips = rec.get('styling_tips', [])
        if styling_tips:
            print(f"  Styling Tips:")
            for tip in styling_tips[:3]:  # Show first 3 tips
                print(f"    - {tip}")
            if len(styling_tips) > 3:
                print(f"    - ... plus {len(styling_tips) - 3} more tips")
        
        print()  # Add a blank line between recommendations

async def main(api_url: str, email: str, password: str, username: str, profile_id: int) -> None:
    """Main function to test the recommendation endpoint"""
    
    print(f"🚀 Starting test with API URL: {api_url}")
    
    # Check if the server is running
    try:
        async with httpx.AsyncClient() as check_client:
            response = await check_client.get(f"{api_url}/api/health", timeout=5.0)
            if response.status_code != 200:
                print(f"⚠️ Server health check returned status {response.status_code}")
    except Exception as e:
        print(f"⚠️ Server might not be running or accessible: {str(e)}")
        print("⚠️ Continuing anyway, but test might fail if server is not available")
    
    async with httpx.AsyncClient(base_url=api_url, timeout=60.0) as client:
        # Login
        token = await login(client, email, password)
        
        # Set auth header for subsequent requests
        client.headers["Authorization"] = f"Bearer {token}"
        
        # Get profile
        profile = await get_profile(client, profile_id)
        
        # Generate recommendation
        print("\n🧠 Generating recommendation with gpt-4o-mini model...")
        recommendations = await generate_recommendation(client, profile_id)
        
        # Print nicely formatted recommendation details
        print_recommendation_details(recommendations)
        
        print("\n✅ Test completed successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the recommendation endpoint with gpt-4o-mini model")
    parser.add_argument("--api-url", default=DEFAULT_API_URL, help="API base URL")
    parser.add_argument("--email", default=DEFAULT_EMAIL, help="User email for login")
    parser.add_argument("--username", default=DEFAULT_USERNAME, help="Username for login")
    parser.add_argument("--password", default=DEFAULT_PASSWORD, help="User password")
    parser.add_argument("--profile-id", type=int, default=DEFAULT_PROFILE_ID, help="Style profile ID")
    
    args = parser.parse_args()
    
    asyncio.run(main(args.api_url, args.email, args.password, args.username, args.profile_id)) 