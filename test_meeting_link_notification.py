#!/usr/bin/env python3
"""
Test script for meeting link notification system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, ScheduledSession, Message
from notification_utils import create_meeting_link_notification

def test_meeting_link_notification():
    """Test the meeting link notification system"""
    
    with app.app_context():
        try:
            print("🧪 Testing Meeting Link Notification System...")
            
            # Check if we have users and sessions
            users = User.query.all()
            if not users:
                print("❌ No users found in database")
                return False
                
            print(f"✅ Found {len(users)} users")
            
            # Look for a coach and student
            coach = None
            student = None
            
            for user in users:
                if user.is_coach and not coach:
                    coach = user
                elif user.is_student and not student:
                    student = user
                    
            if not coach:
                print("❌ No coach found in database")
                return False
                
            if not student:
                print("❌ No student found in database")
                return False
                
            print(f"✅ Found coach: {coach.first_name} {coach.last_name}")
            print(f"✅ Found student: {student.first_name} {student.last_name}")
            
            # Look for a scheduled session
            sessions = ScheduledSession.query.filter_by(
                coach_id=coach.id,
                student_id=student.id
            ).all()
            
            if not sessions:
                print("❌ No scheduled sessions found between coach and student")
                return False
                
            session = sessions[0]
            print(f"✅ Found session: {session.id}")
            
            # Test creating a meeting link notification
            meeting_url = "https://meet.google.com/test-session-123"
            
            print("📝 Creating meeting link notification...")
            message = create_meeting_link_notification(session, meeting_url)
            
            if message:
                print(f"✅ Successfully created notification message: {message.id}")
                print(f"   Message type: {message.message_type}")
                print(f"   Content: {message.content[:100]}...")
                
                # Verify the message was saved
                saved_message = Message.query.get(message.id)
                if saved_message:
                    print("✅ Message was saved to database")
                else:
                    print("❌ Message was not saved to database")
                    
            else:
                print("❌ Failed to create meeting link notification")
                return False
                
            print("\n🎉 Meeting Link Notification Test Completed Successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error during test: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = test_meeting_link_notification()
    sys.exit(0 if success else 1)
