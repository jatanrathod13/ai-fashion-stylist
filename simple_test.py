#!/usr/bin/env python3
"""
Simple test script to check if the FastAPI server is running and accessible.
This is useful for troubleshooting connection issues before running the full test.
"""

import requests
import sys
import time
import argparse

def test_server_root(base_url: str) -> bool:
    """
    Test if the server is running and responding to the root endpoint.
    
    Args:
        base_url: The base URL of the API
        
    Returns:
        bool: True if server is running, False otherwise
    """
    try:
        # Try to access the root endpoint
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print(f"✅ Server is running! Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return True
        else:
            print(f"⚠️ Server returned status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Server is not running or not accessible at the given URL")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout: Server is taking too long to respond")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_docs_endpoint(base_url: str) -> bool:
    """
    Test if the server's documentation endpoint is accessible.
    
    Args:
        base_url: The base URL of the API
        
    Returns:
        bool: True if docs are accessible, False otherwise
    """
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        if response.status_code == 200:
            print(f"✅ API documentation is accessible! Status code: {response.status_code}")
            return True
        else:
            print(f"⚠️ API documentation returned status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing API documentation: {str(e)}")
        return False

def test_api_endpoints(base_url: str) -> None:
    """
    Test various API endpoints to see which ones are accessible.
    
    Args:
        base_url: The base URL of the API
    """
    endpoints = [
        "/",
        "/api/users/",
        "/api/auth/token",
        "/api/profiles/",
        "/api/recommendations/",
        "/openapi.json"
    ]
    
    print("\n🔍 Testing API endpoints:")
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            status = response.status_code
            if status in [200, 401, 403]:  # 401/403 are acceptable for protected endpoints
                print(f"  ✅ {endpoint}: Status {status}")
            else:
                print(f"  ❌ {endpoint}: Status {status}")
        except Exception as e:
            print(f"  ❌ {endpoint}: Error - {str(e)}")

def main(base_url: str, wait_time: int = 0) -> None:
    """
    Main function to test the server.
    
    Args:
        base_url: The base URL of the API
        wait_time: Optional time to wait before testing (useful for server startup)
    """
    print(f"🔍 Testing server at: {base_url}")
    
    if wait_time > 0:
        print(f"⏳ Waiting {wait_time} seconds for server to start...")
        time.sleep(wait_time)
    
    # Test root endpoint
    if test_server_root(base_url):
        # If root check passes, test docs
        test_docs_endpoint(base_url)
        
        # Test various API endpoints
        test_api_endpoints(base_url)
        
        print("\n✅ Server is running and responding to requests.")
        print("You can now run the full test script: python test_recommendation.py")
    else:
        print("\n❌ Server health check failed.")
        print("Make sure the server is running with: python run.py")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test if FastAPI server is running and accessible")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of the API")
    parser.add_argument("--wait", type=int, default=0, help="Seconds to wait before testing (for server startup)")
    
    args = parser.parse_args()
    
    main(args.url, args.wait) 