#!/usr/bin/env python3
"""
Test script for the notification system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Notification
from notification_utils import (
    create_contract_notification,
    create_message_notification,
    create_system_notification,
    create_profile_notification,
    create_payment_notification,
    create_session_notification
)

def test_notification_system():
    """Test the notification system"""
    with app.app_context():
        print("Testing Notification System...")
        
        # Get a test user
        user = User.query.first()
        if not user:
            print("No users found in database. Please create a user first.")
            return
        
        print(f"Testing with user: {user.first_name} {user.last_name} (ID: {user.id})")
        
        # Test 1: Create a system notification
        print("\n1. Testing system notification...")
        try:
            create_system_notification(
                user_id=user.id,
                title="Test System Notification",
                message="This is a test system notification to verify the notification system is working properly."
            )
            print("✓ System notification created successfully")
        except Exception as e:
            print(f"✗ Error creating system notification: {e}")
        
        # Test 2: Create a profile notification
        print("\n2. Testing profile notification...")
        try:
            create_profile_notification(user, 'profile_updated')
            print("✓ Profile notification created successfully")
        except Exception as e:
            print(f"✗ Error creating profile notification: {e}")
        
        # Test 3: Create a payment notification
        print("\n3. Testing payment notification...")
        try:
            create_payment_notification(user, 99.99, 'success', 'Test Contract')
            print("✓ Payment notification created successfully")
        except Exception as e:
            print(f"✗ Error creating payment notification: {e}")
        
        # Test 4: Test Notification model methods
        print("\n4. Testing Notification model methods...")
        try:
            # Get unread count
            unread_count = Notification.get_unread_count(user.id)
            print(f"✓ Unread count: {unread_count}")
            
            # Get recent notifications
            recent_notifications = Notification.get_recent_notifications(user.id, limit=5)
            print(f"✓ Recent notifications: {len(recent_notifications)}")
            
            # Test to_dict method
            if recent_notifications:
                notification_dict = recent_notifications[0].to_dict()
                print(f"✓ to_dict method works: {notification_dict.get('title', 'N/A')}")
            
        except Exception as e:
            print(f"✗ Error testing Notification methods: {e}")
        
        # Test 5: Test mark as read functionality
        print("\n5. Testing mark as read functionality...")
        try:
            unread_notifications = Notification.query.filter_by(
                user_id=user.id, 
                is_read=False
            ).limit(1).all()
            
            if unread_notifications:
                notification = unread_notifications[0]
                success = Notification.mark_as_read(notification.id, user.id)
                if success:
                    print("✓ Mark as read functionality works")
                else:
                    print("✗ Mark as read failed")
            else:
                print("✓ No unread notifications to test")
                
        except Exception as e:
            print(f"✗ Error testing mark as read: {e}")
        
        # Test 6: Test mark all as read
        print("\n6. Testing mark all as read functionality...")
        try:
            Notification.mark_all_as_read(user.id)
            unread_count_after = Notification.get_unread_count(user.id)
            print(f"✓ Mark all as read completed. Unread count: {unread_count_after}")
        except Exception as e:
            print(f"✗ Error testing mark all as read: {e}")
        
        # Test 7: Test notification creation with different types
        print("\n7. Testing different notification types...")
        try:
            # Create notifications with different types
            notification_types = ['contract', 'session', 'message', 'job', 'system']
            
            for ntype in notification_types:
                Notification.create_notification(
                    user_id=user.id,
                    title=f"Test {ntype.title()} Notification",
                    message=f"This is a test {ntype} notification",
                    notification_type=ntype
                )
                print(f"✓ Created {ntype} notification")
                
        except Exception as e:
            print(f"✗ Error creating type-specific notifications: {e}")
        
        print("\n" + "="*50)
        print("Notification System Test Complete!")
        print("="*50)
        
        # Summary
        total_notifications = Notification.query.filter_by(user_id=user.id).count()
        unread_notifications = Notification.query.filter_by(user_id=user.id, is_read=False).count()
        
        print(f"\nSummary:")
        print(f"Total notifications for user: {total_notifications}")
        print(f"Unread notifications: {unread_notifications}")
        print(f"Read notifications: {total_notifications - unread_notifications}")

if __name__ == "__main__":
    test_notification_system()
