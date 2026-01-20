#!/usr/bin/env python3
"""
Test script to verify notification API endpoints
"""

import requests
import json

def test_notification_api():
    """Test notification API endpoints"""
    
    base_url = "http://localhost:5000"
    
    print("Testing Notification API Endpoints...")
    print("="*50)
    
    # Test 1: Get notifications (this will fail without authentication, but we can test the endpoint)
    print("\n1. Testing /api/notifications endpoint...")
    try:
        response = requests.get(f"{base_url}/api/notifications")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Get unread count
    print("\n2. Testing /api/notifications/unread-count endpoint...")
    try:
        response = requests.get(f"{base_url}/api/notifications/unread-count")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Test notifications page
    print("\n3. Testing /notifications page...")
    try:
        response = requests.get(f"{base_url}/notifications")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✓ Notifications page is accessible")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50)
    print("API Test Complete!")
    print("="*50)
    print("\nNote: These tests will show authentication errors because we're not logged in.")
    print("This is expected behavior. The important thing is that the endpoints are responding.")

if __name__ == "__main__":
    test_notification_api()
