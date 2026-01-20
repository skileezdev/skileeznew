#!/usr/bin/env python3
"""
Demo script to showcase the notification system functionality
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

def demo_notification_system():
    """Demonstrate the notification system with various scenarios"""
    with app.app_context():
        print("🎉 Notification System Demo")
        print("=" * 50)
        
        # Get a test user
        user = User.query.first()
        if not user:
            print("❌ No users found in database. Please create a user first.")
            return
        
        print(f"👤 Demo user: {user.first_name} {user.last_name}")
        print()
        
        # Clear existing notifications for clean demo
        Notification.query.filter_by(user_id=user.id).delete()
        db.session.commit()
        
        # Demo 1: Welcome notification
        print("📢 Demo 1: Welcome Notification")
        create_system_notification(
            user.id,
            "Welcome to Skileez! 🎉",
            "Thank you for joining our platform. We're excited to help you learn and grow!"
        )
        print("✅ Welcome notification created")
        print()
        
        # Demo 2: Profile update notification
        print("📢 Demo 2: Profile Update Notification")
        create_profile_notification(user, 'profile_updated')
        print("✅ Profile update notification created")
        print()
        
        # Demo 3: Payment notification
        print("📢 Demo 3: Payment Notification")
        create_payment_notification(user, 149.99, 'success', 'Advanced Python Course')
        print("✅ Payment notification created")
        print()
        
        # Demo 4: Message notification
        print("📢 Demo 4: Message Notification")
        # Create a mock sender
        sender = User.query.filter(User.id != user.id).first()
        if sender:
            create_message_notification(sender, user, "Hi! I'm interested in your coaching services...")
            print("✅ Message notification created")
        else:
            print("⚠️  No other users found for message demo")
        print()
        
        # Demo 5: Multiple notifications of different types
        print("📢 Demo 5: Multiple Notification Types")
        notification_types = [
            ('contract', 'New Contract Proposal', 'You have received a new contract proposal'),
            ('session', 'Session Scheduled', 'Your coaching session has been scheduled'),
            ('job', 'New Job Posted', 'A new job matching your skills has been posted'),
            ('system', 'System Maintenance', 'Scheduled maintenance will occur tonight')
        ]
        
        for ntype, title, message in notification_types:
            Notification.create_notification(
                user_id=user.id,
                title=title,
                message=message,
                notification_type=ntype
            )
            print(f"✅ {ntype.title()} notification created")
        print()
        
        # Show notification statistics
        print("📊 Notification Statistics")
        print("-" * 30)
        total_notifications = Notification.query.filter_by(user_id=user.id).count()
        unread_notifications = Notification.query.filter_by(user_id=user.id, is_read=False).count()
        
        print(f"Total notifications: {total_notifications}")
        print(f"Unread notifications: {unread_notifications}")
        print(f"Read notifications: {total_notifications - unread_notifications}")
        print()
        
        # Show notification breakdown by type
        print("📋 Notification Breakdown by Type")
        print("-" * 35)
        for ntype in ['contract', 'session', 'message', 'job', 'system']:
            count = Notification.query.filter_by(user_id=user.id, type=ntype).count()
            print(f"{ntype.title()}: {count}")
        print()
        
        # Demo notification methods
        print("🔧 Demo 6: Notification Methods")
        print("-" * 30)
        
        # Get unread count
        unread_count = Notification.get_unread_count(user.id)
        print(f"Unread count: {unread_count}")
        
        # Get recent notifications
        recent = Notification.get_recent_notifications(user.id, limit=3)
        print(f"Recent notifications: {len(recent)}")
        
        # Mark one as read
        if recent:
            first_notification = recent[0]
            success = Notification.mark_as_read(first_notification.id, user.id)
            print(f"Marked notification '{first_notification.title}' as read: {success}")
        
        # Show updated stats
        new_unread_count = Notification.get_unread_count(user.id)
        print(f"Updated unread count: {new_unread_count}")
        print()
        
        print("🎯 Demo Complete!")
        print("=" * 50)
        print("💡 Next steps:")
        print("1. Start the Flask application: python app.py")
        print("2. Log in as the demo user")
        print("3. Check the notification bell in the navigation")
        print("4. Click the bell to see the dropdown notifications")
        print("5. Visit /notifications to see all notifications")
        print()
        print("🚀 The notification system is now fully functional!")

if __name__ == "__main__":
    demo_notification_system()
