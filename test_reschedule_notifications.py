#!/usr/bin/env python3
"""
Test reschedule notification functions
"""

import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_reschedule_notifications():
    """Test the reschedule notification functions"""
    try:
        from app import app, db
        from models import Session, User, Contract, Proposal, LearningRequest
        
        with app.app_context():
            print("🧪 Testing reschedule notification functions...")
            
            # Find a session with a reschedule request
            session = Session.query.filter_by(reschedule_requested=True).first()
            if not session:
                print("❌ No session with reschedule request found")
                return False
            
            print(f"✅ Found session: {session.id}")
            
            # Get contract and users
            contract = session.get_contract()
            if not contract:
                print("❌ No contract found for session")
                return False
            
            student = User.query.get(contract.student_id)
            coach = User.query.get(contract.coach_id)
            
            if not student or not coach:
                print(f"❌ Missing users - student: {student}, coach: {coach}")
                return False
            
            print(f"✅ Found users - student: {student.email}, coach: {coach.email}")
            
            # Test email function
            print("📧 Testing email notification...")
            try:
                from email_utils import send_reschedule_approved_email
                result = send_reschedule_approved_email(session, student, coach)
                print(f"✅ Email result: {result}")
            except Exception as e:
                print(f"❌ Email error: {e}")
                import traceback
                traceback.print_exc()
            
            # Test notification function
            print("🔔 Testing in-app notification...")
            try:
                from notification_utils import create_reschedule_notification
                create_reschedule_notification(session, 'reschedule_approved', student, coach)
                print("✅ In-app notification created")
            except Exception as e:
                print(f"❌ In-app notification error: {e}")
                import traceback
                traceback.print_exc()
            
            # Test message notification function
            print("💬 Testing message notification...")
            try:
                from notification_utils import create_reschedule_message_notification
                create_reschedule_message_notification(session, 'reschedule_approved', student, coach)
                print("✅ Message notification created")
            except Exception as e:
                print(f"❌ Message notification error: {e}")
                import traceback
                traceback.print_exc()
            
            print("🎉 Test completed!")
            return True
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_reschedule_notifications()
