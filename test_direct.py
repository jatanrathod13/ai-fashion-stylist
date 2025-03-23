#!/usr/bin/env python3
"""
Simple test for the recommendation endpoint with more debugging information.
"""

import asyncio
import httpx
import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_recommendation_endpoint():
    """Test the recommendation endpoint."""
    base_url = "http://localhost:8001"
    
    # Authentication
    logger.info("Authenticating...")
    auth_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    async with httpx.AsyncClient(base_url=base_url, timeout=30.0) as client:
        try:
            # Get token
            auth_response = await client.post(
                "/api/auth/token",
                data=auth_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if auth_response.status_code != 200:
                logger.error(f"Authentication failed: {auth_response.status_code} - {auth_response.text}")
                return
            
            token_data = auth_response.json()
            token = token_data.get("access_token")
            logger.info("Authentication successful!")
            
            # Make recommendation request
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            recommendation_data = {
                "title": "Test Recommendation",
                "occasion": "casual weekend",
                "season": "summer",
                "budget_min": 100,
                "budget_max": 400,
                "specific_requests": "Comfortable yet stylish outfits"
            }
            
            logger.info(f"Sending recommendation request: {json.dumps(recommendation_data)}")
            recommendation_response = await client.post(
                "/api/recommendations/generate",
                json=recommendation_data,
                headers=headers
            )
            
            logger.info(f"Response status: {recommendation_response.status_code}")
            logger.info(f"Response headers: {recommendation_response.headers}")
            
            try:
                response_data = recommendation_response.json()
                logger.info(f"Response data: {json.dumps(response_data, indent=2)}")
            except:
                logger.error(f"Failed to parse JSON response: {recommendation_response.text}")
            
        except Exception as e:
            logger.error(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_recommendation_endpoint()) 