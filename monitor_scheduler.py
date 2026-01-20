#!/usr/bin/env python3
"""
Scheduler Monitoring Script for Skileez
This script helps you monitor your scheduling system
"""

import urllib.request
import json
import sys
from datetime import datetime, timedelta

def check_webhook_status(base_url):
    """Check if the webhook is responding"""
    webhook_url = f"{base_url}/api/scheduler"
    
    print(f"🔍 Checking webhook status...")
    print(f"URL: {webhook_url}")
    
    # Test data
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
            
            if status_code == 200:
                result = json.loads(response_data)
                print("✅ Webhook is working!")
                print(f"Response: {json.dumps(result, indent=2)}")
                return True
            else:
                print(f"❌ Webhook returned status {status_code}")
                print(f"Response: {response_data}")
                return False
                
    except Exception as e:
        print(f"❌ Webhook check failed: {e}")
        return False

def check_app_status(base_url):
    """Check if the main app is responding"""
    try:
        with urllib.request.urlopen(f"{base_url}/", timeout=10) as response:
            if response.getcode() == 200:
                print("✅ Main app is responding")
                return True
            else:
                print(f"❌ Main app returned status {response.getcode()}")
                return False
    except Exception as e:
        print(f"❌ Main app check failed: {e}")
        return False

def generate_status_report(base_url):
    """Generate a comprehensive status report"""
    print("=" * 60)
    print("SKILEEZ SCHEDULER STATUS REPORT")
    print("=" * 60)
    print(f"Timestamp: {datetime.now()}")
    print(f"App URL: {base_url}")
    print()
    
    # Check main app
    app_status = check_app_status(base_url)
    print()
    
    # Check webhook
    webhook_status = check_webhook_status(base_url)
    print()
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if app_status and webhook_status:
        print("🎉 All systems are working!")
        print()
        print("Next steps:")
        print("1. ✅ Your app is running")
        print("2. ✅ Your webhook is responding")
        print("3. 🔄 cron-job.org should be calling your webhook every 5 minutes")
        print("4. 📧 Check your email notifications are working")
        print("5. 📊 Monitor your Render logs for scheduler activity")
    else:
        print("❌ Some issues detected:")
        if not app_status:
            print("- Main app is not responding")
        if not webhook_status:
            print("- Webhook is not working")
        print()
        print("Troubleshooting:")
        print("1. Check if your app is deployed on Render")
        print("2. Verify the URL is correct")
        print("3. Check Render logs for errors")
        print("4. Make sure your code is up to date")

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python monitor_scheduler.py <your-app-url>")
        print("Example: python monitor_scheduler.py https://skileez.onrender.com")
        print()
        print("Make sure to replace with your actual Render app URL!")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    generate_status_report(base_url)

if __name__ == "__main__":
    main()
