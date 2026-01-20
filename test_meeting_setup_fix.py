#!/usr/bin/env python3
"""
Test script to verify that the meeting setup route is working after the fixes.
"""

import requests
import sys
import os

def test_meeting_setup_route():
    """Test if the meeting setup route is accessible"""
    
    # Base URL - adjust this to your actual server URL
    base_url = "http://localhost:5000"  # Change this if your server runs on a different port
    
    print("🔍 Testing Meeting Setup Route...")
    print(f"Base URL: {base_url}")
    
    # Test 1: Check if the main page loads
    try:
        print("\n1️⃣ Testing main page...")
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print("✅ Main page loads successfully")
        else:
            print(f"❌ Main page failed with status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error accessing main page: {e}")
        return False
    
    # Test 2: Check if the meeting setup route pattern is accessible
    try:
        print("\n2️⃣ Testing meeting setup route pattern...")
        # Test with a dummy session ID
        test_session_id = 123
        response = requests.get(f"{base_url}/session/{test_session_id}/meeting-setup", timeout=10)
        
        if response.status_code == 200:
            print("✅ Meeting setup route is accessible (returns 200)")
            print("📝 Note: This might redirect to login if not authenticated")
        elif response.status_code == 302:
            print("✅ Meeting setup route is accessible (redirects to login - expected)")
            print("📝 This is normal behavior for unauthenticated users")
        elif response.status_code == 404:
            print("❌ Meeting setup route returns 404 - route not found!")
            return False
        else:
            print(f"⚠️ Meeting setup route returned unexpected status: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error accessing meeting setup route: {e}")
        return False
    
    # Test 3: Check if the route is properly registered
    try:
        print("\n3️⃣ Testing route registration...")
        # Test a simple route that should exist
        response = requests.get(f"{base_url}/test-route", timeout=10)
        if response.status_code == 200:
            print("✅ Test route is accessible - routing system is working")
        else:
            print(f"⚠️ Test route returned status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error accessing test route: {e}")
    
    print("\n🎯 Summary:")
    print("If you see 'Meeting setup route is accessible' above, the route is working!")
    print("If you see '404 - route not found', there's still a routing issue.")
    print("\n💡 Next steps:")
    print("1. Make sure you're logged in as a coach")
    print("2. Try accessing the meeting setup from a session card")
    print("3. Check the browser console for any JavaScript errors")
    
    return True

def test_flask_app():
    """Test if Flask app can start without errors"""
    print("\n🐍 Testing Flask App Startup...")
    
    try:
        # Try to import and start the Flask app
        from app import app
        
        with app.test_client() as client:
            # Test if the app responds
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Flask app starts successfully")
                return True
            else:
                print(f"⚠️ Flask app starts but returns status: {response.status_code}")
                return True
                
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Flask app error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Meeting Setup Route Test")
    print("=" * 50)
    
    # Test 1: Flask app startup
    if not test_flask_app():
        print("\n❌ Flask app test failed. Check your app configuration.")
        sys.exit(1)
    
    # Test 2: Route accessibility
    if not test_meeting_setup_route():
        print("\n❌ Route test failed. Check your route configuration.")
        sys.exit(1)
    
    print("\n🎉 All tests completed!")
    print("Check the results above to see if your meeting setup route is working.")
