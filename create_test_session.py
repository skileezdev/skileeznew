#!/usr/bin/env python3
"""
Create test session data to test the meeting setup functionality.
"""

import sys
import os
from datetime import datetime, timedelta, timezone

def create_test_session():
    """Create a test ScheduledSession record"""
    
    try:
        print("🔧 Creating Test Session Data...")
        
        from app import app, db
        from models import ScheduledSession, User, Contract
        
        with app.app_context():
            print("\n1️⃣ Checking existing data...")
            
            # Get a coach and student
            coach = User.query.filter_by(is_coach=True).first()
            student = User.query.filter_by(is_student=True).first()
            
            if not coach:
                print("❌ No coach found in database")
                return False
                
            if not student:
                print("❌ No student found in database")
                return False
            
            print(f"   Coach: {coach.email} (ID: {coach.id})")
            print(f"   Student: {student.email} (ID: {student.id})")
            
            # Check if we already have a session
            existing_session = ScheduledSession.query.first()
            if existing_session:
                print(f"   ✅ Session already exists: ID {existing_session.id}")
                return True
            
            print("\n2️⃣ Creating test ScheduledSession...")
            
            # Create a test session for tomorrow
            tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
            tomorrow = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)  # 2 PM
            
            test_session = ScheduledSession(
                session_id=1,  # This will be the session_id in the URL
                coach_id=coach.id,
                student_id=student.id,
                scheduled_at=tomorrow,
                duration_minutes=60,
                timezone='UTC',
                session_type='paid',
                status='scheduled',
                payment_status='paid'
            )
            
            db.session.add(test_session)
            db.session.commit()
            
            print(f"   ✅ Created test session:")
            print(f"      - ID: {test_session.id}")
            print(f"      - Session ID: {test_session.session_id}")
            print(f"      - Scheduled: {test_session.scheduled_at}")
            print(f"      - Duration: {test_session.duration_minutes} minutes")
            print(f"      - Coach: {coach.email}")
            print(f"      - Student: {student.email}")
            
            print(f"\n3️⃣ Test URL:")
            print(f"   Meeting Setup: /session/{test_session.session_id}/meeting-setup")
            print(f"   This should now work and show the meeting setup page!")
            
            return True
            
    except Exception as e:
        print(f"❌ Error creating test session: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_session_data():
    """Verify that the session data was created correctly"""
    
    try:
        print("\n🔍 Verifying Session Data...")
        
        from app import app, db
        from models import ScheduledSession
        
        with app.app_context():
            # Check if session exists
            session = ScheduledSession.query.first()
            if session:
                print(f"   ✅ Session found:")
                print(f"      - ID: {session.id}")
                print(f"      - Session ID: {session.session_id}")
                print(f"      - Coach ID: {session.coach_id}")
                print(f"      - Student ID: {session.student_id}")
                print(f"      - Scheduled: {session.scheduled_at}")
                print(f"      - Status: {session.status}")
                
                # Test the query that the meeting setup uses
                test_session_id = session.session_id
                result = ScheduledSession.query.filter_by(session_id=test_session_id).first()
                
                if result:
                    print(f"   ✅ Query test successful: Found session with session_id = {test_session_id}")
                else:
                    print(f"   ❌ Query test failed: No session found with session_id = {test_session_id}")
                    
            else:
                print("   ❌ No session found in database")
                
    except Exception as e:
        print(f"❌ Error verifying session: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Create Test Session Data")
    print("=" * 50)
    
    # Create test session
    if not create_test_session():
        print("\n❌ Failed to create test session.")
        sys.exit(1)
    
    # Verify the data
    if not verify_session_data():
        print("\n❌ Failed to verify session data.")
        sys.exit(1)
    
    print("\n🎉 Test session created successfully!")
    print("Now you should be able to:")
    print("1. Go to a session card")
    print("2. Click 'Setup Meeting'")
    print("3. See the meeting setup page with actual data!")
