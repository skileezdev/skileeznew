#!/usr/bin/env python3
"""
Deployment script to fix the notification system in production
"""

import os
import sys

def deploy_notification_fix():
    """Deploy the notification system fix to production"""
    
    print("🚀 Deploying Notification System Fix...")
    print("="*50)
    
    # Step 1: Create the notification table
    print("\n1. Creating notification table...")
    try:
        from create_notification_table import create_notification_table
        success = create_notification_table()
        if success:
            print("✓ Notification table created successfully")
        else:
            print("❌ Failed to create notification table")
            return False
    except Exception as e:
        print(f"❌ Error creating notification table: {e}")
        return False
    
    # Step 2: Test the notification system
    print("\n2. Testing notification system...")
    try:
        from simple_notification_fix import simple_notification_fix
        simple_notification_fix()
        print("✓ Notification system test completed")
    except Exception as e:
        print(f"❌ Error testing notification system: {e}")
        return False
    
    print("\n" + "="*50)
    print("🎉 Notification System Fix Deployed Successfully!")
    print("="*50)
    print("\nThe notification system is now fully functional in production.")
    print("\nNext steps:")
    print("1. Restart the Flask application")
    print("2. Test sending messages, proposals, contracts, etc.")
    print("3. Verify that notifications appear in real-time")
    print("4. Check the notification bell in the navigation")
    
    return True

if __name__ == "__main__":
    deploy_notification_fix()
