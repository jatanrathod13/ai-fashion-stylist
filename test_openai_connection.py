#!/usr/bin/env python3
"""
Test OpenAI API connection.

This script tests the connection to the OpenAI API using the API key from the .env file.
"""

import os
import asyncio
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_openai_connection():
    """Test the connection to the OpenAI API"""
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_TEXT_MODEL", "gpt-4-turbo-preview")
    
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment variables")
        return
    
    print(f"Using API key: {api_key[:10]}...{api_key[-4:]}")
    print(f"Using model: {model}")
    
    try:
        # Initialize OpenAI client
        client = openai.AsyncOpenAI(api_key=api_key)
        
        # Simple completions request
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello! What's the weather like?"}
            ],
            max_tokens=50
        )
        
        # Print response
        print("\nResponse from OpenAI API:")
        print(response.choices[0].message.content)
        print("\nConnection test successful!")
        
    except Exception as e:
        print(f"\nError connecting to OpenAI API: {type(e).__name__}: {str(e)}")
        if hasattr(e, 'response'):
            print(f"Response status: {e.response.status}")
            print(f"Response body: {e.response.text}")

if __name__ == "__main__":
    asyncio.run(test_openai_connection()) 