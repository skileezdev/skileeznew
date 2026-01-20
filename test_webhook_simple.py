#!/usr/bin/env python3
"""
Simple test script for the scheduler webhook
This version uses only built-in Python libraries
"""

import urllib.request
import urllib.parse
import json
import sys
from datetime import datetime

def test_webhook_simple(base_url):
    """Test the scheduler webhook using only built-in libraries"""
    
    webhook_url = f"{base_url}/api/scheduler"
    
    print(f"Testing webhook at: {webhook_url}")
    print("-" * 50)
    
    # Test data
    test_data = {
        "task": "all"
    }
    
    # Convert to JSON
    json_data = json.dumps(test_data).encode('utf-8')
    
    # Create request
    req = urllib.request.Request(
        webhook_url,
        data=json_data,
        headers={
            'Content-Type': 'application/json',
            'User-Agent': 'Skileez-Test/1.0'
        },
        method='POST'
    )
    
    try:
        # Make the request
        with urllib.request.urlopen(req, timeout=30) as response:
            status_code = response.getcode()
            response_data = response.read().decode('utf-8')
            
            print(f"Status Code: {status_code}")
            
            if status_code == 200:
                print("✅ Webhook call successful!")
                
                try:
                    result = json.loads(response_data)
                    print(f"Response: {json.dumps(result, indent=2)}")
                    
                    if result.get('success'):
                        print("✅ All scheduler tasks completed successfully")
                        
                        results = result.get('results', {})
                        for task, task_result in results.items():
                            if 'error' in task_result:
                                print(f"❌ {task}: {task_result['error']}")
                            else:
                                print(f"✅ {task}: Completed")
                    else:
                        print(f"❌ Scheduler failed: {result.get('error', 'Unknown error')}")
                        
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON response: {response_data}")
                    
            else:
                print(f"❌ Webhook call failed with status {status_code}")
                print(f"Response: {response_data}")
                
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error: {e.code} - {e.reason}")
        print(f"Response: {e.read().decode('utf-8')}")
        return False
    except urllib.error.URLError as e:
        print(f"❌ URL Error: {e.reason}")
        return False
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False
    
    return status_code == 200

def main():
    """Main test function"""
    
    if len(sys.argv) != 2:
        print("Usage: python test_webhook_simple.py <base_url>")
        print("Example: python test_webhook_simple.py https://your-app.onrender.com")
        print("\nMake sure to replace 'your-app' with your actual Render app name!")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    
    print(f"Scheduler Webhook Test")
    print(f"Timestamp: {datetime.utcnow()}")
    print(f"Base URL: {base_url}")
    print("=" * 60)
    
    # Test the webhook
    success = test_webhook_simple(base_url)
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 Webhook test successful!")
        print("\nNext steps:")
        print("1. Set up cron-job.org or EasyCron")
        print("2. Configure it to call your webhook every 5 minutes")
        print("3. Monitor your Render logs for scheduler activity")
        print("4. Test with actual scheduled calls in your database")
    else:
        print("\n❌ Webhook test failed. Please check:")
        print("1. Your app is deployed and running on Render")
        print("2. The URL is correct (replace 'your-app' with your actual app name)")
        print("3. The webhook endpoint is accessible")
        print("4. Your application logs for errors")

if __name__ == "__main__":
    main()
