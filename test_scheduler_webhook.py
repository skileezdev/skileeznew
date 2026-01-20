#!/usr/bin/env python3
"""
Test Scheduler Webhook Script for Skileez
This script tests the scheduler webhook functionality
"""

import urllib.request
import json
import sys
from datetime import datetime

def test_scheduler_webhook(base_url):
    """Test the scheduler webhook"""
    webhook_url = f"{base_url}/api/scheduler"
    
    print(f"🔍 Testing scheduler webhook...")
    print(f"URL: {webhook_url}")
    
    # Test data for all tasks
    test_data = {"task": "all"}
    json_data = json.dumps(test_data).encode('utf-8')
    
    # Create request
    req = urllib.request.Request(
        webhook_url,
        data=json_data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            status_code = response.getcode()
            response_data = response.read().decode('utf-8')
            
            print(f"Status Code: {status_code}")
            print(f"Response: {response_data}")
            
            if status_code == 200:
                result = json.loads(response_data)
                print("✅ Scheduler webhook is working!")
                print(f"Results: {json.dumps(result.get('results', {}), indent=2)}")
                return True
            else:
                print(f"❌ Scheduler webhook returned status {status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Scheduler webhook test failed: {e}")
        return False

def test_individual_tasks(base_url):
    """Test individual scheduler tasks"""
    webhook_url = f"{base_url}/api/scheduler"
    
    tasks = ['calls_ready', 'reminders_24h', 'reminders_1h', 'session_reminders', 'mark_overdue', 'cleanup']
    
    print("\n🔍 Testing individual tasks...")
    
    for task in tasks:
        print(f"\nTesting task: {task}")
        
        test_data = {"task": task}
        json_data = json.dumps(test_data).encode('utf-8')
        
        req = urllib.request.Request(
            webhook_url,
            data=json_data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                status_code = response.getcode()
                response_data = response.read().decode('utf-8')
                
                if status_code == 200:
                    result = json.loads(response_data)
                    print(f"✅ {task}: Success")
                    print(f"   Results: {result.get('results', {}).get(task, 'No results')}")
                else:
                    print(f"❌ {task}: Failed (Status {status_code})")
                    print(f"   Response: {response_data}")
                    
        except Exception as e:
            print(f"❌ {task}: Error - {e}")

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python test_scheduler_webhook.py <your-app-url>")
        print("Example: python test_scheduler_webhook.py https://skileez.onrender.com")
        print()
        print("Make sure to replace with your actual Render app URL!")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    
    print("=" * 60)
    print("SKILEEZ SCHEDULER WEBHOOK TEST")
    print("=" * 60)
    print(f"Timestamp: {datetime.now()}")
    print(f"App URL: {base_url}")
    print()
    
    # Test main webhook
    success = test_scheduler_webhook(base_url)
    
    if success:
        # Test individual tasks
        test_individual_tasks(base_url)
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print("🎉 Scheduler webhook is working!")
        print()
        print("Next steps:")
        print("1. ✅ Your scheduler webhook is responding")
        print("2. 🔄 Set up cron-job.org to call your webhook every 5 minutes")
        print("3. 📧 Check that email notifications are being sent")
        print("4. 📊 Monitor your Render logs for scheduler activity")
        print()
        print("Cron job URL to set up:")
        print(f"POST {base_url}/api/scheduler")
        print("Body: {\"task\": \"all\"}")
        print("Schedule: Every 5 minutes")
    else:
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print("❌ Scheduler webhook test failed")
        print()
        print("Troubleshooting:")
        print("1. Check if your app is deployed on Render")
        print("2. Verify the URL is correct")
        print("3. Check Render logs for errors")
        print("4. Make sure your code is up to date")

if __name__ == "__main__":
    main()
