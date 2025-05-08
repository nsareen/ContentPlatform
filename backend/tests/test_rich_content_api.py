"""
Test script for the rich content generation API endpoint.
"""

import requests
import json
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from app
sys.path.append(str(Path(__file__).parent.parent))

from app.core.auth import create_access_token
from app.models.models import User

def test_rich_content_generation():
    """Test the rich content generation API endpoint."""
    # Create a mock user and token
    mock_user = User(
        id="test-user-id",
        email="admin@example.com",
        tenant_id="test-tenant-id",
        is_active=True
    )
    
    # Create a token for the mock user
    token_data = {"sub": mock_user.email, "tenant_id": mock_user.tenant_id, "user_id": mock_user.id}
    token = create_access_token(token_data)
    
    # Define the API endpoint
    api_url = "http://localhost:8000/api/rich-content/generate"
    
    # Define the request data
    request_data = {
        "prompt": "Create a marketing flyer for a new eco-friendly water bottle that keeps drinks cold for 24 hours",
        "content_type": "flyer",
        "context": {
            "force_intent": "generate_rich_content"
        }
    }
    
    # Set up headers with the token
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    print(f"Making request to {api_url} with token: {token[:10]}...")
    
    # Make the request
    try:
        response = requests.post(api_url, json=request_data, headers=headers)
        
        # Check the response
        if response.status_code == 200:
            result = response.json()
            print("API call successful!")
            print(f"Status: {result.get('status')}")
            print(f"Action: {result.get('action')}")
            
            # Print the full response for debugging
            print("\nFull response:")
            print(json.dumps(result, indent=2))
            
            # Print the text content
            if 'result' in result and 'text_content' in result['result']:
                print("\nGenerated Text Content:")
                print("-" * 50)
                print(result['result']['text_content'])
                print("-" * 50)
            elif 'result' in result and 'content' in result['result']:
                print("\nGenerated Content:")
                print("-" * 50)
                print(result['result']['content'])
                print("-" * 50)
            
            # Print information about generated images
            if 'result' in result and 'images' in result['result']:
                images = result['result']['images']
                print(f"\nGenerated {len(images)} images:")
                for i, image in enumerate(images):
                    print(f"Image {i+1}: {image.get('url', 'No URL')[:50]}...")
            
            return True
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Exception: {str(e)}")
        return False

if __name__ == "__main__":
    test_rich_content_generation()
