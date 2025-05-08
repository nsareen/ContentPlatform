"""
Test script for the updated rich content API with enhanced image generation capabilities.
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# API endpoint
BASE_URL = "http://localhost:8000"
API_ENDPOINT = f"{BASE_URL}/api/rich-content/generate"

# Test user credentials
TEST_USER = {
    "username": "test@example.com",
    "password": "password123"
}

def get_auth_token():
    """Get authentication token for the test user."""
    auth_url = f"{BASE_URL}/api/auth/token"
    response = requests.post(auth_url, data=TEST_USER)
    
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Error getting auth token: {response.text}")
        return None

def test_rich_content_generation():
    """Test the rich content generation API with different image models."""
    # Get auth token
    token = get_auth_token()
    if not token:
        print("Failed to get auth token. Make sure the server is running and the test user exists.")
        return
    
    # Headers for authentication
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test data for DALL-E 3
    data_dalle3 = {
        "prompt": "Create a marketing flyer for a new eco-friendly coffee shop called 'Green Bean' that emphasizes sustainable sourcing and biodegradable packaging.",
        "content_type": "flyer",
        "image_model": "dall-e-3",
        "image_quality": "standard",
        "image_size": "1024x1024",
        "image_style": "natural"
    }
    
    # Make the request
    print("Testing rich content generation with DALL-E 3...")
    response = requests.post(API_ENDPOINT, headers=headers, json=data_dalle3)
    
    # Print the response
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Action: {result.get('action')}")
        print(f"Status: {result.get('status')}")
        
        # Print the generated content
        if 'result' in result:
            print("\nGenerated text content:")
            print(result['result'].get('text_content', '')[:500] + "...")
            
            # Print image information
            images = result['result'].get('images', [])
            print(f"\nGenerated {len(images)} images:")
            for i, img in enumerate(images):
                print(f"Image {i+1}:")
                print(f"  Model: {img.get('model', 'unknown')}")
                print(f"  URL: {img.get('url', 'No URL')[:100]}...")
                print(f"  Description: {img.get('description', 'No description')[:100]}...")
        
        # Save the full response to a file for inspection
        with open("rich_content_response.json", "w") as f:
            json.dump(result, f, indent=2)
            print("\nFull response saved to rich_content_response.json")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_rich_content_generation()
