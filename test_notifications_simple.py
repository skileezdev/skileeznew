#!/usr/bin/env python3
"""
Simple test to verify notifications work
"""

def test_notifications():
    """Test that notifications work"""
    
    print("🧪 Testing Notifications...")
    print("="*50)
    
    try:
        # Import and test the app
        from app import app, db
        
        with app.app_context():
            # Test 1: Check if notification table exists
            from sqlalchemy import text
            result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='notification';"))
            table_exists = result.scalar() is not None
            
            if table_exists:
                print("✅ Notification table exists")
            else:
                print("❌ Notification table does not exist")
                return False
            
            # Test 2: Test notification creation
            from models import User, Notification
            
            # Get a test user
            user = User.query.first()
            if not user:
                print("❌ No users found in database")
                return False
            
            print(f"✅ Testing with user: {user.first_name} {user.last_name}")
            
            # Create a test notification
            notification = Notification.create_notification(
                user_id=user.id,
                title="Test Notification",
                message="This is a test notification to verify the system works",
                notification_type='system'
            )
            
            if notification:
                print("✅ Notification created successfully")
                
                # Clean up
                db.session.delete(notification)
                db.session.commit()
                print("✅ Test notification cleaned up")
            else:
                print("❌ Failed to create notification")
                return False
            
            # Test 3: Test notification utilities
            from notification_utils import create_system_notification
            create_system_notification(user.id, "System Test", "Testing system notifications")
            print("✅ System notification utility works")
            
            # Clean up
            Notification.query.filter_by(user_id=user.id, title="System Test").delete()
            db.session.commit()
            
            print("\n" + "="*50)
            print("🎉 All notification tests passed!")
            print("="*50)
            return True
            
    except Exception as e:
        print(f"❌ Error testing notifications: {e}")
        return False

if __name__ == "__main__":
    test_notifications()
