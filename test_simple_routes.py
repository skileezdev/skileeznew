#!/usr/bin/env python3
"""
Simple test to check if basic routes are working
"""
import requests

def test_basic_routes():
    """Test basic routes"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Basic Routes...")
    print("="*50)
    
    # Test root route
    try:
        response = requests.get(f"{base_url}/", allow_redirects=False)
        print(f"Root route (/) - Status: {response.status_code}")
        if response.status_code == 302:
            print("   → Redirecting (expected)")
    except Exception as e:
        print(f"Root route error: {e}")
    
    # Test about route
    try:
        response = requests.get(f"{base_url}/about", allow_redirects=False)
        print(f"About route (/about) - Status: {response.status_code}")
    except Exception as e:
        print(f"About route error: {e}")
    
    # Test notifications route
    try:
        response = requests.get(f"{base_url}/notifications", allow_redirects=False)
        print(f"Notifications route (/notifications) - Status: {response.status_code}")
        if response.status_code == 302:
            print("   → Redirecting to login (expected)")
    except Exception as e:
        print(f"Notifications route error: {e}")
    
    # Test API route
    try:
        response = requests.get(f"{base_url}/api/notifications", allow_redirects=False)
        print(f"API route (/api/notifications) - Status: {response.status_code}")
        if response.status_code == 302:
            print("   → Redirecting to login (expected)")
    except Exception as e:
        print(f"API route error: {e}")
    
    print("\n" + "="*50)
    print("🎉 Basic routes test completed!")
    print("="*50)

if __name__ == "__main__":
    test_basic_routes()
