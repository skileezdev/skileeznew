#!/usr/bin/env python3
"""
Test script to verify the user deletion fix works correctly.
This script tests the safe_delete_user_data function with the new ScheduledCall and ScheduledSession deletion steps.
"""

import os
import sys
from datetime import datetime, timedelta

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, ScheduledCall, ScheduledSession
from utils import safe_delete_user_data

def test_user_deletion_fix():
    """Test the user deletion fix"""
    print("Testing user deletion fix...")
    
    with app.app_context():
        try:
            # Check if there are any existing users
            users = User.query.all()
            print(f"Found {len(users)} existing users")
            
            if len(users) == 0:
                print("No users found to test with. Creating test users...")
                
                # Create test users
                test_student = User(
                    email='test_student@example.com',
                    first_name='Test',
                    last_name='Student',
                    is_student=True,
                    current_role='student'
                )
                test_student.set_password('password123')
                
                test_coach = User(
                    email='test_coach@example.com',
                    first_name='Test',
                    last_name='Coach',
                    is_coach=True,
                    current_role='coach'
                )
                test_coach.set_password('password123')
                
                db.session.add(test_student)
                db.session.add(test_coach)
                db.session.commit()
                
                print(f"Created test users: {test_student.id} and {test_coach.id}")
                
                # Create a test scheduled call
                test_call = ScheduledCall(
                    student_id=test_student.id,
                    coach_id=test_coach.id,
                    call_type='free_consultation',
                    scheduled_at=datetime.utcnow() + timedelta(hours=1),
                    duration_minutes=15,
                    status='scheduled'
                )
                db.session.add(test_call)
                db.session.commit()
                
                print(f"Created test scheduled call: {test_call.id}")
                
                # Create a test scheduled session
                test_session = ScheduledSession(
                    coach_id=test_coach.id,
                    student_id=test_student.id,
                    session_id=1,  # Dummy session ID
                    scheduled_at=datetime.utcnow() + timedelta(hours=2),
                    duration_minutes=60,
                    session_type='paid',
                    status='scheduled'
                )
                db.session.add(test_session)
                db.session.commit()
                
                print(f"Created test scheduled session: {test_session.id}")
            
            # Get the first user to test deletion
            test_user = User.query.first()
            if not test_user:
                print("No users found to test deletion")
                return False
            
            print(f"Testing deletion of user: {test_user.id} ({test_user.email})")
            
            # Test the deletion
            success = safe_delete_user_data(test_user.id)
            
            if success:
                print("✅ User deletion test PASSED - no foreign key constraint violations")
                return True
            else:
                print("❌ User deletion test FAILED - user not found or deletion failed")
                return False
                
        except Exception as e:
            print(f"❌ User deletion test FAILED with error: {str(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return False

if __name__ == '__main__':
    success = test_user_deletion_fix()
    if success:
        print("\n🎉 User deletion fix is working correctly!")
        sys.exit(0)
    else:
        print("\n💥 User deletion fix still has issues!")
        sys.exit(1)
