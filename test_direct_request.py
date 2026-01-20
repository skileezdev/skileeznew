#!/usr/bin/env python3
"""
Direct test of Flask app requests
"""
import requests
import time

def test_direct_request():
    """Test direct request to Flask app"""
    print("🧪 Testing Direct Request...")
    print("="*50)
    
    # Wait a moment for Flask to fully start
    time.sleep(2)
    
    base_url = "http://127.0.0.1:5000"
    
    try:
        # Test root route
        print("Testing root route...")
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Content length: {len(response.content)}")
        
        if response.status_code == 200:
            print("✅ Root route working!")
        elif response.status_code == 302:
            print("✅ Root route redirecting (expected)")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - Flask app not running")
    except requests.exceptions.Timeout:
        print("❌ Timeout - Flask app not responding")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*50)
    print("🎉 Direct request test completed!")
    print("="*50)

if __name__ == "__main__":
    test_direct_request()
