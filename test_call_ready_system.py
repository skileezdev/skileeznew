#!/usr/bin/env python3
"""
Test script for the call ready system
This script helps test the automatic room creation and notifications
"""

import requests
import json
import sys
from datetime import datetime, timedelta

def test_call_ready_trigger(base_url):
    """Test triggering the call ready system"""
    print(f"Testing call ready trigger at {base_url}/api/scheduler")
    
    try:
        # Test just the calls_ready task
        response = requests.post(
            f"{base_url}/api/scheduler",
            json={"task": "calls_ready"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            result = data.get('results', {}).get('calls_ready', {})
            print(f"Call Ready Result: {result}")
            
            if result.get('notifications_sent', 0) > 0:
                print("✅ Call ready notifications were sent!")
            else:
                print("ℹ️  No calls were ready to join at this time")
        else:
            print(f"Response: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error testing call ready: {e}")
        return False

def test_manual_scheduler(base_url):
    """Test the manual scheduler endpoint"""
    print(f"\nTesting manual scheduler at {base_url}/api/test-scheduler")
    
    try:
        response = requests.get(
            f"{base_url}/api/test-scheduler",
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("\nManual Scheduler Results:")
            for task, result in data.get('results', {}).items():
                print(f"  {task}: {result}")
        else:
            print(f"Response: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error testing manual scheduler: {e}")
        return False

def check_scheduled_calls_info(base_url):
    """Get information about scheduled calls"""
    print(f"\nChecking scheduled calls information...")
    
    try:
        # This would require an endpoint to list scheduled calls
        # For now, we'll just test the scheduler
        print("ℹ️  To see scheduled calls, check your database or create an admin endpoint")
        print("ℹ️  The system will automatically trigger when calls reach their scheduled time")
        
    except Exception as e:
        print(f"Error checking scheduled calls: {e}")

def main():
    """Main test function"""
    if len(sys.argv) < 2:
        print("Usage: python test_call_ready_system.py <base_url>")
        print("Example: python test_call_ready_system.py https://skileez.onrender.com")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    
    print("=== Call Ready System Test ===")
    print(f"Testing against: {base_url}")
    print(f"Current time (UTC): {datetime.utcnow()}")
    print()
    
    # Test 1: Check scheduled calls info
    check_scheduled_calls_info(base_url)
    
    # Test 2: Test call ready trigger
    test_call_ready_trigger(base_url)
    
    # Test 3: Test manual scheduler
    test_manual_scheduler(base_url)
    
    print("\n=== Test Complete ===")
    print("How the system works:")
    print("1. When a call is scheduled for 10:35 PM UTC")
    print("2. At exactly 10:35 PM UTC, the cron job will trigger")
    print("3. The system will:")
    print("   - Video functionality has been removed from this application")
    print("   - Send email notifications to both users")
    print("   - Send in-app notifications")
    print("   - Update call status to 'ready'")
    print("4. Users can then click 'Join Call' to enter the video room")
    print()
    print("To test this:")
    print("1. Schedule a call for a few minutes from now")
    print("2. Wait for the scheduled time")
    print("3. Check your email and in-app notifications")
    print("4. Try joining the call")

if __name__ == "__main__":
    main()
