"""
Test script for the rich content API with proper authentication.
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv
from app.core.security import create_access_token
from app.models.models import User
from datetime import timedelta
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.db.database import SessionLocal

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# API endpoint
BASE_URL = "http://localhost:8000"
API_ENDPOINT = f"{BASE_URL}/api/rich-content/generate"

def create_test_token():
    """Create a test token for API access."""
    # Create a database session
    db: Session = SessionLocal()
    
    try:
        # Get the first user from the database
        user = db.query(User).first()
        
        if not user:
            print("No users found in the database. Please create a user first.")
            return None
        
        # Create an access token
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        return access_token, user.id, user.tenant_id
    finally:
        db.close()

def test_rich_content_generation():
    """Test the rich content generation API."""
    # Get test token
    token_data = create_test_token()
    if not token_data:
        print("Failed to create test token.")
        return
    
    token, user_id, tenant_id = token_data
    
    # Headers for authentication
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test data
    data = {
        "prompt": "Create a marketing flyer for a new eco-friendly coffee shop called 'Green Bean' that emphasizes sustainable sourcing and biodegradable packaging.",
        "content_type": "flyer",
        "image_model": "dall-e-3",
        "image_quality": "standard",
        "image_size": "1024x1024",
        "image_style": "natural"
    }
    
    # Make the request
    print("Testing rich content generation...")
    print(f"User ID: {user_id}")
    print(f"Tenant ID: {tenant_id}")
    print(f"Sending request to {API_ENDPOINT}...")
    
    response = requests.post(API_ENDPOINT, headers=headers, json=data)
    
    # Print the response
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Action: {result.get('action')}")
        print(f"Status: {result.get('status')}")
        
        # Save the full response to a file for inspection
        with open("rich_content_response.json", "w") as f:
            json.dump(result, f, indent=2)
            print("\nFull response saved to rich_content_response.json")
        
        # Print a summary of the response
        if 'result' in result:
            print("\nGenerated text content:")
            text_content = result['result'].get('text_content', '')
            print(text_content[:500] + "..." if len(text_content) > 500 else text_content)
            
            # Print image information
            images = result['result'].get('images', [])
            print(f"\nGenerated {len(images)} images:")
            for i, img in enumerate(images):
                print(f"Image {i+1}:")
                print(f"  Model: {img.get('model', 'unknown')}")
                print(f"  URL: {img.get('url', 'No URL')[:100]}...")
                print(f"  Description: {img.get('description', 'No description')[:100]}...")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_rich_content_generation()
