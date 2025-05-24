"""
Test script for the Brand Voice Generator API endpoints.

This script tests the FastAPI endpoints for the brand voice generator
by making HTTP requests and validating the responses.
"""
import sys
import os
import json
import requests
from typing import Dict, Any

# Add the parent directory to the path so we can import the app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configuration
API_BASE_URL = "http://localhost:8001"  # Adjust if your server runs on a different port
API_PREFIX = "/api"
GENERATE_ENDPOINT = f"{API_BASE_URL}{API_PREFIX}/brand-voice-generator/generate/"
SAVE_ENDPOINT = f"{API_BASE_URL}{API_PREFIX}/brand-voice-generator/save/"

# Sample content for testing
SAMPLE_CONTENT = """
At Eco-Friendly Solutions, we believe that small changes can make a big impact. 
Our sustainable products are designed with the planet in mind, using only 
recyclable materials and ethical manufacturing processes. 
We're committed to reducing waste and helping our customers live more 
environmentally conscious lives. Join us in our mission to create a greener future!
"""

# Test auth token (for development only)
DEV_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTEyMyIsInRlbmFudF9pZCI6InRlbmFudC0xMjMiLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3NDc5NzcxNzV9.iRGPvHgK3GaH3ZDwgbfpZBgOhCCYe7pLRl3c1YROj6c"

def test_generate_endpoint():
    """Test the /generate/ endpoint of the brand voice generator API."""
    print("Testing /generate/ endpoint...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEV_TOKEN}"
    }
    
    payload = {
        "content": SAMPLE_CONTENT,
        "brand_name": "Eco-Friendly Solutions",
        "industry": "retail",
        "options": {
            "generation_depth": "basic",
            "include_sample_content": True
        }
    }
    
    try:
        response = requests.post(GENERATE_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        
        result = response.json()
        validate_generator_response(result)
        
        print("✅ /generate/ endpoint test passed")
        return result
    except requests.exceptions.RequestException as e:
        print(f"❌ /generate/ endpoint test failed: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            try:
                print(f"Response body: {e.response.json()}")
            except:
                print(f"Response body: {e.response.text}")
        raise

def test_save_endpoint(generated_result: Dict[str, Any]):
    """Test the /save/ endpoint of the brand voice generator API."""
    print("Testing /save/ endpoint...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEV_TOKEN}"
    }
    
    # Prepare the save payload using the result from the generate endpoint
    payload = {
        "brand_voice_components": generated_result["brand_voice_components"],
        "generation_metadata": generated_result["generation_metadata"],
        "source_content": SAMPLE_CONTENT,
        "name": "Test Brand Voice",
        "description": "A test brand voice generated for API testing",
        "tenant_id": "tenant-123"  # Use a test tenant ID
    }
    
    try:
        response = requests.post(SAVE_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        
        result = response.json()
        validate_save_response(result)
        
        print("✅ /save/ endpoint test passed")
        return result
    except requests.exceptions.RequestException as e:
        print(f"❌ /save/ endpoint test failed: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            try:
                print(f"Response body: {e.response.json()}")
            except:
                print(f"Response body: {e.response.text}")
        raise

def validate_generator_response(response: Dict[str, Any]):
    """Validate the structure of the generator API response."""
    assert isinstance(response, dict), "Response should be a dictionary"
    assert "success" in response, "Response should have a 'success' key"
    assert response["success"] is True, "Response should be successful"
    
    # Check if brand_voice_components exists
    assert "brand_voice_components" in response, "Response should have brand_voice_components"
    components = response["brand_voice_components"]
    
    # Validate components
    assert "personality_traits" in components, "Missing personality_traits"
    assert "tonality" in components, "Missing tonality"
    assert "identity" in components, "Missing identity"
    assert "dos" in components, "Missing dos"
    assert "donts" in components, "Missing donts"
    
    # Check if generation_metadata exists
    assert "generation_metadata" in response, "Response should have generation_metadata"

def validate_save_response(response: Dict[str, Any]):
    """Validate the structure of the save API response."""
    assert isinstance(response, dict), "Response should be a dictionary"
    assert "success" in response, "Response should have a 'success' key"
    assert response["success"] is True, "Response should be successful"
    
    # Check if brand_voice_id exists
    assert "brand_voice_id" in response, "Response should have brand_voice_id"
    assert isinstance(response["brand_voice_id"], str), "brand_voice_id should be a string"
    assert len(response["brand_voice_id"]) > 0, "brand_voice_id should not be empty"

def check_server_status():
    """Check if the API server is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API server is running")
            return True
        else:
            print(f"❌ API server returned status code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server. Make sure it's running.")
        return False

if __name__ == "__main__":
    print("Running Brand Voice Generator API Endpoint Tests")
    print("-----------------------------------------------")
    
    if not check_server_status():
        print("Please start the API server before running this test.")
        sys.exit(1)
    
    try:
        # Test the generate endpoint
        generated_result = test_generate_endpoint()
        
        # Test the save endpoint using the result from the generate endpoint
        save_result = test_save_endpoint(generated_result)
        
        print("\nAll API endpoint tests passed! ✅")
        print(f"Generated brand voice ID: {save_result.get('brand_voice_id', 'N/A')}")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        sys.exit(1)
