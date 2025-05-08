import requests
import sys

def test_proxy(image_url):
    """Test the image proxy endpoint with a given URL."""
    proxy_url = f"http://localhost:8000/api/proxy/image?url={requests.utils.quote(image_url)}"
    
    print(f"Testing proxy with URL: {image_url}")
    print(f"Proxy URL: {proxy_url}")
    
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
            print(f"Response: {response.text[:500]}")
            return False
    except Exception as e:
        print(f"❌ Error testing proxy: {str(e)}")
        return False

if __name__ == "__main__":
    # Use a test image URL or one provided as command line argument
    test_url = sys.argv[1] if len(sys.argv) > 1 else "https://picsum.photos/800/600"
    
    # Test the proxy
    success = test_proxy(test_url)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
