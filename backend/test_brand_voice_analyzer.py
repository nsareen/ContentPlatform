#!/usr/bin/env python
"""
Test script for the Brand Voice Analyzer API.
This script authenticates with the API and tests the brand voice analyzer endpoints.
"""

import requests
import json
import sys
from pprint import pprint

# API configuration
BASE_URL = "http://localhost:8000"
AUTH_URL = f"{BASE_URL}/api/token"
ANALYZER_URL = f"{BASE_URL}/api/brand-voice-analyzer/analyze"

# Development credentials
DEV_USERNAME = "admin@example.com"
DEV_PASSWORD = "password123"

def get_auth_token():
    """Get authentication token using development credentials."""
    print("Getting authentication token...")
    
    try:
        response = requests.post(
            AUTH_URL,
            data={
                "username": DEV_USERNAME,
                "password": DEV_PASSWORD
            }
        )
        
        if response.status_code == 200:
            token_data = response.json()
            print("Authentication successful!")
            return token_data["access_token"]
        else:
            print(f"Authentication failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"Error during authentication: {str(e)}")
        return None

def test_brand_voice_analyzer(token, brand_voice_id):
    """Test the brand voice analyzer API."""
    print(f"\nTesting brand voice analyzer with brand voice ID: {brand_voice_id}")
    
    # Sample content to analyze
    test_content = """
    Just do it! Our new line of running shoes is designed to help you push your limits 
    and achieve your personal best. With advanced cushioning technology and breathable materials, 
    these shoes are perfect for both casual joggers and serious athletes.
    """
    
    # Request payload
    payload = {
        "content": test_content,
        "brand_voice_id": brand_voice_id,
        "options": {
            "analysis_depth": "detailed",
            "include_suggestions": True,
            "highlight_issues": True,
            "max_suggestions": 5,
            "generate_report": True
        }
    }
    
    # Set up headers with authentication token
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Make the request
        response = requests.post(
            ANALYZER_URL,
            headers=headers,
            json=payload
        )
        
        # Check response
        if response.status_code == 200:
            result = response.json()
            print("Analysis successful!")
            print("\nAnalysis Result:")
            pprint(result)
            return result
        else:
            print(f"Analysis failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        return None

def main():
    """Main function to run the test."""
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("Failed to get authentication token. Exiting.")
        sys.exit(1)
    
    # Brand voice ID to test with (Nike India from our database)
    brand_voice_id = "84311b94-1782-4712-8330-fb248b7a4b25"
    
    # Test the brand voice analyzer
    result = test_brand_voice_analyzer(token, brand_voice_id)
    
    # Exit with appropriate status code
    if result and result.get("success"):
        print("\nTest completed successfully!")
        sys.exit(0)
    else:
        print("\nTest failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
