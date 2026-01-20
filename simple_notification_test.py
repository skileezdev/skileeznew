#!/usr/bin/env python3
"""
Simple test to verify notification creation
"""

from app import app, db
from models import User, Notification
from notification_utils import create_system_notification, create_message_notification
from datetime import datetime

def test_simple_notifications():
    """Test basic notification creation"""
    
    with app.app_context():
        print("Testing Simple Notifications...")
        
        # Get a test user
        user = User.query.first()
        if not user:
            print("❌ No users found in database")
            return
        
        print(f"✓ Testing with user: {user.first_name} {user.last_name}")
        
        # Clear existing notifications for clean test
        Notification.query.filter_by(user_id=user.id).delete()
        db.session.commit()
        
        # Test 1: System notification
        print("\n1. Testing system notification...")
        try:
            create_system_notification(user.id, "Test System Notification", "This is a test system notification")
            
            notifications = Notification.query.filter_by(user_id=user.id).all()
            if notifications:
                print(f"✓ System notification created: {notifications[-1].title}")
            else:
                print("❌ System notification not created")
                
        except Exception as e:
            print(f"❌ Error creating system notification: {e}")
        
        # Test 2: Message notification
        print("\n2. Testing message notification...")
        try:
            # Create a sender user
            sender = User.query.filter(User.id != user.id).first()
            if sender:
                create_message_notification(sender, user, "Hello! This is a test message...")
                
                notifications = Notification.query.filter_by(user_id=user.id).all()
                if len(notifications) > 1:
                    print(f"✓ Message notification created: {notifications[-1].title}")
                else:
                    print("❌ Message notification not created")
            else:
                print("❌ No sender user found for message notification")
                
        except Exception as e:
            print(f"❌ Error creating message notification: {e}")
        
        # Summary
        print("\n" + "="*50)
        print("Simple Notification Test Complete!")
        print("="*50)
        
        total_notifications = Notification.query.filter_by(user_id=user.id).count()
        unread_notifications = Notification.query.filter_by(user_id=user.id, is_read=False).count()
        
        print(f"Total notifications for user: {total_notifications}")
        print(f"Unread notifications: {unread_notifications}")
        print(f"Read notifications: {total_notifications - unread_notifications}")
        
        # Show notification details
        if total_notifications > 0:
            print("\nRecent notifications:")
            recent = Notification.query.filter_by(user_id=user.id).order_by(Notification.created_at.desc()).limit(3).all()
            for i, notification in enumerate(recent, 1):
                print(f"{i}. {notification.title} - {notification.message[:50]}...")
        
        print("\n✓ Test completed successfully!")

if __name__ == "__main__":
    test_simple_notifications()
