"""
Simple test script to test the brand voice generator API.
"""
import requests
import json
import sys

# API endpoint
API_URL = "http://localhost:8001/api/brand-voice-generator/generate/"

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

def test_generate_brand_voice():
    """Test the brand voice generator API."""
    print("Testing brand voice generator API...")
    
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
        print(f"Sending request to {API_URL}...")
        response = requests.post(API_URL, headers=headers, json=payload)
        
        # Print response status
        print(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\nAPI Response (truncated):")
            print(json.dumps(result, indent=2)[:500] + "...\n")
            
            # Validate the response structure
            if result.get("success") == True:
                print("✅ API test successful!")
                
                # Print some details from the response
                components = result.get("brand_voice_components", {})
                print("\nGenerated Brand Voice Components:")
                print(f"- Personality Traits: {components.get('personality_traits', [])}")
                print(f"- Tonality (excerpt): {components.get('tonality', '')[:100]}...")
                print(f"- Do's (first 3): {components.get('dos', [])[:3]}")
                print(f"- Don'ts (first 3): {components.get('donts', [])[:3]}")
                
                return True
            else:
                print(f"❌ API returned error: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ API request failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_generate_brand_voice()
    sys.exit(0 if success else 1)
