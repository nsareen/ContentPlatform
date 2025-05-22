#!/usr/bin/env python3
"""
CORS Diagnostic Tool for ContentPlatform Backend

This script performs a series of tests to diagnose CORS issues with the backend API.
It uses the requests library to make direct HTTP requests to the backend API and
analyzes the responses to identify potential CORS configuration issues.
"""

import requests
import json
import sys
from urllib.parse import urljoin

# Configuration
BACKEND_URL = "http://localhost:8000/api"
ENDPOINTS = [
    "/",
    "/voices/",
    "/dev-token/",
    "/token/"
]
ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3005",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3005"
]

def print_header(message):
    """Print a formatted header message."""
    print("\n" + "=" * 80)
    print(f" {message} ".center(80, "="))
    print("=" * 80)

def print_result(success, message, data=None):
    """Print a formatted result message."""
    status = "✅ SUCCESS" if success else "❌ FAILURE"
    print(f"{status}: {message}")
    if data:
        if isinstance(data, dict) or isinstance(data, list):
            print(json.dumps(data, indent=2))
        else:
            print(data)

def test_endpoint_availability():
    """Test if the backend API is available."""
    print_header("Testing Backend Availability")
    
    try:
        response = requests.get(urljoin(BACKEND_URL, "/"))
        print_result(
            response.status_code < 400,
            f"Backend responded with status code {response.status_code}",
            response.json() if response.headers.get("content-type") == "application/json" else response.text
        )
        return True
    except requests.RequestException as e:
        print_result(False, f"Failed to connect to backend: {str(e)}")
        return False

def test_options_preflight(endpoint, origin):
    """Test OPTIONS preflight request for a specific endpoint and origin."""
    url = urljoin(BACKEND_URL, endpoint)
    
    headers = {
        "Origin": origin,
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "Content-Type, Authorization"
    }
    
    try:
        response = requests.options(url, headers=headers)
        
        # Check for CORS headers
        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
            "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
            "Access-Control-Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials")
        }
        
        success = (
            response.status_code < 400 and
            cors_headers["Access-Control-Allow-Origin"] is not None
        )
        
        print_result(
            success,
            f"OPTIONS {endpoint} from {origin}: {response.status_code}",
            {
                "status": response.status_code,
                "headers": cors_headers
            }
        )
        
        return success
    except requests.RequestException as e:
        print_result(False, f"Failed to send OPTIONS request to {endpoint} from {origin}: {str(e)}")
        return False

def test_get_request(endpoint, origin, with_credentials=False):
    """Test GET request for a specific endpoint and origin."""
    url = urljoin(BACKEND_URL, endpoint)
    
    headers = {
        "Origin": origin,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(
            url, 
            headers=headers,
            # Only include cookies if with_credentials is True
            cookies={} if with_credentials else None
        )
        
        # Check for CORS headers
        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials")
        }
        
        success = (
            response.status_code < 400 and
            cors_headers["Access-Control-Allow-Origin"] is not None
        )
        
        credentials_text = "with credentials" if with_credentials else "without credentials"
        print_result(
            success,
            f"GET {endpoint} from {origin} {credentials_text}: {response.status_code}",
            {
                "status": response.status_code,
                "headers": cors_headers,
                "response": response.json() if response.headers.get("content-type") == "application/json" else response.text[:200]
            }
        )
        
        return success
    except requests.RequestException as e:
        credentials_text = "with credentials" if with_credentials else "without credentials"
        print_result(False, f"Failed to send GET request to {endpoint} from {origin} {credentials_text}: {str(e)}")
        return False

def run_all_tests():
    """Run all CORS diagnostic tests."""
    if not test_endpoint_availability():
        print("\n⚠️  Backend is not available. Please start the backend server and try again.")
        return
    
    print_header("Testing OPTIONS Preflight Requests")
    for endpoint in ENDPOINTS:
        for origin in ORIGINS:
            test_options_preflight(endpoint, origin)
    
    print_header("Testing GET Requests Without Credentials")
    for endpoint in ENDPOINTS:
        for origin in ORIGINS:
            test_get_request(endpoint, origin, with_credentials=False)
    
    print_header("Testing GET Requests With Credentials")
    for endpoint in ENDPOINTS:
        for origin in ORIGINS:
            test_get_request(endpoint, origin, with_credentials=True)
    
    print_header("Diagnosis Summary")
    print("""
Based on the test results above, here are potential issues to check:

1. CORS Configuration:
   - Check if the backend's CORS middleware is properly configured
   - Ensure 'allow_origins' includes all frontend origins
   - Verify 'allow_credentials' is set correctly if using credentials

2. FastAPI Routes:
   - Ensure all routes properly handle OPTIONS requests
   - Check for any middleware that might be interfering with CORS

3. Authentication:
   - If using authentication, ensure the token endpoints are properly configured
   - Check if the frontend is correctly sending authentication headers

4. Network:
   - Verify the backend is running on the expected port (8000)
   - Check for any firewalls or proxies that might be blocking requests
""")

if __name__ == "__main__":
    run_all_tests()
