import requests
import time
import json

def get_dev_token():
    """Get a development token for testing."""
    print("Getting development token...")
    
    # Token endpoint
    token_url = "http://localhost:8000/api/token"
    
    try:
        # Request a dev token using form data (OAuth2 password flow expects form data, not JSON)
        response = requests.post(token_url, data={
            "username": "admin@example.com",
            "password": "password123"
        })
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            print("✅ Successfully obtained dev token")
            return token
        else:
            print(f"❌ Failed to get dev token: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Error getting dev token: {str(e)}")
        return None

def test_rich_content_generation():
    """Test the rich content generation API endpoint."""
    print("Testing rich content generation API...")
    
    # Get auth token
    token = get_dev_token()
    if not token:
        print("Cannot proceed without authentication token")
        return False
    
    # API endpoint
    api_url = "http://localhost:8000/api/rich-content/generate"
    
    # Test data matching the frontend API call structure
    data = {
        "prompt": "Create a promotional image for a coffee shop with a steaming cup of coffee and pastries",
        "content_type": "flyer",
        "image_quality": "standard",
        "image_style": "natural"
    }
    
    # Headers with authentication
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    try:
        # Make the request
        print(f"Sending request to {api_url}...")
        response = requests.post(api_url, json=data, headers=headers)
        
        # Check response
        if response.status_code == 200:
            result = response.json()
            print(f"Response status: {result.get('status')}")
            print(f"Response action: {result.get('action')}")
            
            # Check for images in the result
            if 'result' in result and 'images' in result['result']:
                images = result['result']['images']
                print(f"\nGenerated {len(images)} images:")
                
                # Test each image URL with the proxy
                for i, image in enumerate(images):
                    image_url = image.get('url', '')
                    if image_url:
                        print(f"\nImage {i+1} URL: {image_url[:50]}...")
                        test_proxy_with_url(image_url)
                    else:
                        print(f"Image {i+1}: No URL found")
            else:
                print("No images found in the response")
                
            return True
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Exception: {str(e)}")
        return False

def test_proxy_with_url(image_url):
    """Test the image proxy endpoint with a given URL."""
    proxy_url = f"http://localhost:8000/api/proxy/image?url={requests.utils.quote(image_url)}"
    
    print(f"Testing proxy with URL: {image_url[:50]}...")
    print(f"Proxy URL: {proxy_url[:100]}...")
    
    try:
        # Make request to the proxy endpoint
        response = requests.get(proxy_url)
        
        # Print response information
        print(f"Status code: {response.status_code}")
        print(f"Content type: {response.headers.get('Content-Type')}")
        print(f"Content length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            print("✅ Proxy request successful")
            return True
        else:
            print(f"❌ Proxy request failed with status {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Error testing proxy: {str(e)}")
        return False

if __name__ == "__main__":
    # Test rich content generation
    test_rich_content_generation()
