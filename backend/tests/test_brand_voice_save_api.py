"""
Simple test script to test the brand voice save API.
"""
import requests
import json
import sys

# API endpoints
GENERATE_URL = "http://localhost:8001/api/brand-voice-generator/generate/"
SAVE_URL = "http://localhost:8001/api/brand-voice-generator/save/"

# Test auth token (for development only)
DEV_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTEyMyIsInRlbmFudF9pZCI6InRlbmFudC0xMjMiLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3NDc5NzcxNzV9.iRGPvHgK3GaH3ZDwgbfpZBgOhCCYe7pLRl3c1YROj6c"

# Sample content for testing
SAMPLE_CONTENT = """
At Eco-Friendly Solutions, we believe that small changes can make a big impact. 
Our sustainable products are designed with the planet in mind, using only 
recyclable materials and ethical manufacturing processes. 
We're committed to reducing waste and helping our customers live more 
environmentally conscious lives. Join us in our mission to create a greener future!
"""

def test_save_brand_voice():
    """Test the brand voice save API."""
    print("Testing brand voice save API flow...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEV_TOKEN}"
    }
    
    # Step 1: Generate a brand voice
    print("\nStep 1: Generating a brand voice...")
    generate_payload = {
        "content": SAMPLE_CONTENT,
        "brand_name": "Eco-Friendly Solutions",
        "industry": "retail",
        "options": {
            "generation_depth": "basic",
            "include_sample_content": True
        }
    }
    
    try:
        generate_response = requests.post(GENERATE_URL, headers=headers, json=generate_payload)
        
        if generate_response.status_code != 200:
            print(f"❌ Generate API request failed with status code {generate_response.status_code}")
            print(f"Response: {generate_response.text}")
            return False
        
        generate_result = generate_response.json()
        
        if not generate_result.get("success"):
            print(f"❌ Generate API returned error: {generate_result.get('error', 'Unknown error')}")
            return False
        
        print("✅ Brand voice generated successfully")
        
        # Step 2: Save the generated brand voice
        print("\nStep 2: Saving the generated brand voice...")
        save_payload = {
            "brand_voice_components": generate_result["brand_voice_components"],
            "generation_metadata": generate_result["generation_metadata"],
            "source_content": SAMPLE_CONTENT,
            "name": "API Test Brand Voice",
            "description": "A brand voice created during API testing",
            "tenant_id": "tenant-123"  # Use a test tenant ID
        }
        
        save_response = requests.post(SAVE_URL, headers=headers, json=save_payload)
        
        print(f"Save API response status code: {save_response.status_code}")
        
        if save_response.status_code == 200:
            save_result = save_response.json()
            print("\nSave API Response:")
            print(json.dumps(save_result, indent=2))
            
            if save_result.get("success") == True:
                print("✅ Save API test successful!")
                print(f"Brand Voice ID: {save_result.get('brand_voice_id')}")
                return True
            else:
                print(f"❌ Save API returned error: {save_result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Save API request failed with status code {save_response.status_code}")
            print(f"Response: {save_response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_save_brand_voice()
    sys.exit(0 if success else 1)
