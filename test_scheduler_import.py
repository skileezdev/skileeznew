#!/usr/bin/env python3
"""
Test script to check if scheduler functions can be imported
"""

import urllib.request
import json

def test_scheduler_import():
    """Test if scheduler functions can be imported"""
    try:
        from notification_scheduler import (
            check_calls_ready,
            send_24h_reminders,
            send_1h_reminders,
            mark_overdue_calls,
            cleanup_old_notifications
        )
        print("✅ Scheduler functions imported successfully")
        return True
    except Exception as e:
        print(f"❌ Error importing scheduler functions: {e}")
        return False

def test_scheduler_endpoint():
    """Test the scheduler endpoint with a simple request"""
    url = "https://skileez-q89g.onrender.com/api/scheduler"
    
    # Simple test data
    data = {"task": "all"}
    json_data = json.dumps(data).encode('utf-8')
    
    req = urllib.request.Request(
        url,
        data=json_data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            status = response.getcode()
            response_data = response.read().decode('utf-8')
            
            print(f"Status: {status}")
            print(f"Response: {response_data}")
            
            if status == 200:
                print("✅ Scheduler endpoint is working!")
                return True
            else:
                print(f"❌ Scheduler endpoint returned status {status}")
                return False
                
    except Exception as e:
        print(f"❌ Error calling scheduler endpoint: {e}")
        return False

if __name__ == "__main__":
    print("Testing scheduler import...")
    import_success = test_scheduler_import()
    
    print("\nTesting scheduler endpoint...")
    endpoint_success = test_scheduler_endpoint()
    
    if import_success and endpoint_success:
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Some tests failed")
