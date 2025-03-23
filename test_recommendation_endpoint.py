#!/usr/bin/env python3
"""
Test the recommendation endpoint with proper authentication.

This script tests the recommendation API endpoint by:
1. Authenticating with the API using username/password
2. Making a request to the recommendation endpoint with the auth token

Usage:
    python test_recommendation_endpoint.py [--api-url API_URL] [--username USERNAME] [--password PASSWORD]
"""

import os
import json
import asyncio
import argparse
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class RecommendationAPITester:
    """Class to test the recommendation API endpoint"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        """Initialize the API tester"""
        self.api_url = api_url
        self.token = None
        self.client = httpx.AsyncClient(base_url=api_url, timeout=30.0)
    
    async def authenticate(self, username: str, password: str) -> bool:
        """
        Authenticate with the API and get an access token
        
        Args:
            username: User's username or email
            password: User's password
            
        Returns:
            True if authentication was successful, False otherwise
        """
        print(f"Authenticating as {username}...")
        
        # OAuth2 form data
        try:
            form_data = {
                "username": username,
                "password": password
            }
            
            response = await self.client.post(
                "/api/auth/token",
                data=form_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                print("Authentication successful!")
                return True
            else:
                print(f"Authentication failed: {response.status_code} - {response.text}")
                return False
        
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            return False
    
    async def get_user_profile(self) -> dict:
        """
        Get the current user's profile
        
        Returns:
            User profile data or empty dict on failure
        """
        if not self.token:
            print("Error: Not authenticated")
            return {}
        
        try:
            response = await self.client.get(
                "/api/auth/me",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get user profile: {response.status_code} - {response.text}")
                return {}
                
        except Exception as e:
            print(f"Error getting user profile: {str(e)}")
            return {}
    
    async def get_style_profiles(self) -> list:
        """
        Get the user's style profiles
        
        Returns:
            List of style profiles or empty list on failure
        """
        if not self.token:
            print("Error: Not authenticated")
            return []
        
        try:
            print(f"Requesting style profiles from: {self.api_url}/api/style-profiles")
            response = await self.client.get(
                "/api/style-profiles",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {response.headers}")
            
            if response.status_code == 200:
                profiles = response.json()
                print(f"Found {len(profiles)} style profile(s)")
                return profiles
            elif response.status_code == 307:  # Temporary Redirect
                redirect_url = response.headers.get('location', 'unknown')
                print(f"Redirected to: {redirect_url}")
                # Follow the redirect manually
                print(f"Following redirect to: {redirect_url}")
                redirect_response = await self.client.get(
                    redirect_url,
                    headers={"Authorization": f"Bearer {self.token}"}
                )
                print(f"Redirect response status: {redirect_response.status_code}")
                if redirect_response.status_code == 200:
                    profiles = redirect_response.json()
                    print(f"Found {len(profiles)} style profile(s) after redirect")
                    return profiles
                else:
                    print(f"Failed to get style profiles after redirect: {redirect_response.status_code} - {redirect_response.text}")
                    return []
            else:
                print(f"Failed to get style profiles: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"Error getting style profiles: {str(e)}")
            return []
    
    async def generate_recommendation(self, style_profile_id: int = None) -> dict:
        """
        Generate a recommendation using the API
        
        Args:
            style_profile_id: Optional style profile ID to use
            
        Returns:
            Recommendation data or empty dict on failure
        """
        if not self.token:
            print("Error: Not authenticated")
            return {}
        
        try:
            # Recommendation request data
            request_data = {
                "title": "Test Recommendation",
                "occasion": "casual weekend",
                "season": "summer",
                "budget_min": 100,
                "budget_max": 400,
                "specific_requests": "Comfortable yet stylish outfits"
            }
            
            # Add style profile ID if provided
            if style_profile_id:
                request_data["style_profile_id"] = style_profile_id
            
            print("Sending recommendation request...")
            print(f"Request data: {json.dumps(request_data, indent=2)}")
            print(f"Requesting recommendation from: {self.api_url}/api/recommendations/generate")
            
            response = await self.client.post(
                "/api/recommendations/generate",
                json=request_data,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                }
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {response.headers}")
            
            if response.status_code == 200:
                recommendations = response.json()
                print(f"Successfully generated {len(recommendations)} recommendation(s)")
                return recommendations
            else:
                print(f"Failed to generate recommendation: {response.status_code} - {response.text}")
                return {}
                
        except Exception as e:
            print(f"Error generating recommendation: {str(e)}")
            return {}
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


async def main(args):
    """Main function"""
    # Create the API tester
    tester = RecommendationAPITester(api_url=args.api_url)
    
    try:
        # Step 1: Authenticate
        auth_success = await tester.authenticate(args.username, args.password)
        if not auth_success:
            print("Authentication failed. Exiting.")
            return
        
        # Step 2: Get user profile (optional, for verification)
        user_profile = await tester.get_user_profile()
        if user_profile:
            print(f"Logged in as: {user_profile.get('username', 'Unknown')}")
        
        # Step 3: Get style profiles
        style_profiles = await tester.get_style_profiles()
        
        # Choose a profile ID if available
        profile_id = None
        if style_profiles and args.use_profile:
            profile_id = style_profiles[0].get("id")
            print(f"Using style profile: {profile_id}")
        
        # Step 4: Generate recommendation
        try:
            recommendations = await tester.generate_recommendation(profile_id)
            
            # Print a sample of the recommendations
            if recommendations and len(recommendations) > 0:
                print("\n===== First Recommendation =====")
                rec = recommendations[0]
                print(f"ID: {rec.get('id')}")
                print(f"Title: {rec.get('title')}")
                print(f"Occasion: {rec.get('occasion')}")
                
                # Print items if available
                outfits = rec.get('outfits', [])
                if outfits:
                    print(f"\nOutfits ({len(outfits)}):")
                    for i, outfit in enumerate(outfits, 1):
                        print(f"  {i}. {outfit.get('name', 'N/A')}")
                        components = outfit.get('components', [])
                        print(f"     Components: {len(components)}")
                        
                        for j, component in enumerate(components[:3], 1):
                            print(f"       {j}. {component.get('type')} - {component.get('description')}")
                            
                        if len(components) > 3:
                            print(f"       ... plus {len(components) - 3} more components")
                
                print("================================\n")
        except Exception as e:
            import traceback
            print(f"Exception while generating recommendation: {type(e).__name__}: {str(e)}")
            print(traceback.format_exc())
        
        print("Test completed successfully!")
    
    finally:
        # Clean up
        await tester.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the recommendation API endpoint")
    
    # API URL
    parser.add_argument("--api-url", default="http://localhost:8000", help="API base URL")
    
    # Authentication
    parser.add_argument("--username", default="test@example.com", help="Username or email for authentication")
    parser.add_argument("--password", default="testpassword123", help="Password for authentication")
    
    # Options
    parser.add_argument("--use-profile", action="store_true", help="Use a style profile if available")
    
    args = parser.parse_args()
    
    asyncio.run(main(args)) 