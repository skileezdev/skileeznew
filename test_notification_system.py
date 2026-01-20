#!/usr/bin/env python3
"""
Test script for the notification system
This script helps test and debug notification issues
"""

import requests
import json
import sys
from datetime import datetime, timedelta

def test_scheduler_webhook(base_url):
    """Test the scheduler webhook endpoint"""
    print(f"Testing scheduler webhook at {base_url}/api/scheduler")
    
    try:
        response = requests.post(
            f"{base_url}/api/scheduler",
            json={"task": "all"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("\nScheduler Results:")
            for task, result in data.get('results', {}).items():
                print(f"  {task}: {result}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error testing scheduler: {e}")
        return False

def test_scheduler_manually(base_url):
    """Test the manual scheduler endpoint"""
    print(f"\nTesting manual scheduler at {base_url}/api/test-scheduler")
    
    try:
        response = requests.get(
            f"{base_url}/api/test-scheduler",
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("\nManual Scheduler Results:")
            for task, result in data.get('results', {}).items():
                print(f"  {task}: {result}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error testing manual scheduler: {e}")
        return False

def check_scheduled_calls(base_url):
    """Check for scheduled calls in the system"""
    print(f"\nChecking scheduled calls at {base_url}/api/scheduler")
    
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
            print(f"Calls Ready Result: {result}")
        else:
            print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Error checking scheduled calls: {e}")

def main():
    """Main test function"""
    if len(sys.argv) < 2:
        print("Usage: python test_notification_system.py <base_url>")
        print("Example: python test_notification_system.py https://skileez.onrender.com")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    
    print("=== Notification System Test ===")
    print(f"Testing against: {base_url}")
    print(f"Current time (UTC): {datetime.utcnow()}")
    print()
    
    # Test 1: Check scheduled calls
    check_scheduled_calls(base_url)
    
    # Test 2: Test manual scheduler
    test_scheduler_manually(base_url)
    
    # Test 3: Test webhook scheduler
    test_scheduler_webhook(base_url)
    
    print("\n=== Test Complete ===")
    print("If you see errors, check:")
    print("1. The app is running and accessible")
    print("2. Database connection is working")
    print("3. Email configuration is set up")
    print("4. There are scheduled calls in the system")

if __name__ == "__main__":
    main()
