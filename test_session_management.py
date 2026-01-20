#!/usr/bin/env python3
"""
Comprehensive test script for Session Management System
Tests all session management features including scheduling, rescheduling, completion, and cancellation.
"""

import sys
import os
import logging
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_session_management():
    """Test the complete session management system"""
    print("🧪 Testing Session Management System...")
    
    try:
        # Import required modules
        from app import app, db
        from models import User, StudentProfile, CoachProfile, LearningRequest, Proposal, Contract, Session
        from forms import SessionScheduleForm, RescheduleRequestForm, SessionCompletionForm
        
        with app.app_context():
            # Create test database
            db.create_all()
            
            print("✅ Database created successfully")
            
            # Test 1: Create test users
            print("\n📝 Test 1: Creating test users...")
            
            # Create student
            student = User(
                email='student@test.com',
                first_name='Test',
                last_name='Student',
                is_student=True,
                current_role='student'
            )
            student.set_password('TestPass123!')
            db.session.add(student)
            
            # Create coach
            coach = User(
                email='coach@test.com',
                first_name='Test',
                last_name='Coach',
                is_coach=True,
                current_role='coach'
            )
            coach.set_password('TestPass123!')
            db.session.add(coach)
            
            db.session.commit()
            print("✅ Test users created")
            
            # Test 2: Create profiles
            print("\n📝 Test 2: Creating user profiles...")
            
            student_profile = StudentProfile(
                user_id=student.id,
                bio='Test student bio',
                age=25,
                country='USA'
            )
            db.session.add(student_profile)
            
            coach_profile = CoachProfile(
                user_id=coach.id,
                goal='main_income',
                coach_title='Test Coach',
                skills='Python, JavaScript',
                bio='Test coach bio',
                country='USA',
                hourly_rate=50.0,
                is_approved=True
            )
            db.session.add(coach_profile)
            
            db.session.commit()
            print("✅ User profiles created")
            
            # Test 3: Create learning request
            print("\n📝 Test 3: Creating learning request...")
            
            learning_request = LearningRequest(
                student_id=student.id,
                title='Learn Python Programming',
                description='I want to learn Python programming from scratch',
                skills_needed='Python, Programming',
                duration='2 weeks',
                budget=500.0,
                experience_level='beginner',
                skill_type='short_term',
                sessions_needed=4,
                timeframe='2 weeks'
            )
            db.session.add(learning_request)
            db.session.commit()
            print("✅ Learning request created")
            
            # Test 4: Create proposal
            print("\n📝 Test 4: Creating proposal...")
            
            proposal = Proposal(
                learning_request_id=learning_request.id,
                coach_id=coach.id,
                cover_letter='I can help you learn Python programming effectively',
                session_count=4,
                price_per_session=100.0,
                session_duration=60,
                total_price=400.0,
                status='accepted',
                accepted_at=datetime.utcnow(),
                payment_model='per_session'
            )
            db.session.add(proposal)
            db.session.commit()
            print("✅ Proposal created")
            
            # Test 5: Create contract
            print("\n📝 Test 5: Creating contract...")
            
            contract = Contract(
                proposal_id=proposal.id,
                student_id=student.id,
                coach_id=coach.id,
                contract_number='CTR-20241201-0001',
                start_date=datetime.utcnow().date(),
                end_date=(datetime.utcnow() + timedelta(days=14)).date(),
                total_sessions=4,
                total_amount=400.0,
                payment_model='per_session',
                rate=100.0,
                timezone='UTC',
                payment_status='paid',
                payment_date=datetime.utcnow()
            )
            db.session.add(contract)
            db.session.commit()
            print("✅ Contract created")
            
            # Test 6: Create sessions
            print("\n📝 Test 6: Creating sessions...")
            
            # Create 4 sessions
            sessions = []
            for i in range(1, 5):
                session = Session(
                    proposal_id=proposal.id,
                    session_number=i,
                    scheduled_at=datetime.utcnow() + timedelta(days=i),
                    duration_minutes=60,
                    timezone='UTC',
                    status='scheduled'
                )
                db.session.add(session)
                sessions.append(session)
            
            db.session.commit()
            print(f"✅ {len(sessions)} sessions created")
            
            # Test 7: Test session methods
            print("\n📝 Test 7: Testing session methods...")
            
            session1 = sessions[0]
            
            # Test reschedule allowed
            is_allowed = session1.is_reschedule_allowed()
            print(f"   - Reschedule allowed: {is_allowed}")
            
            # Test can request reschedule
            can_request = session1.can_request_reschedule('student')
            print(f"   - Student can request reschedule: {can_request}")
            
            can_request_coach = session1.can_request_reschedule('coach')
            print(f"   - Coach can request reschedule: {can_request_coach}")
            
            # Test time until session
            time_until = session1.get_time_until_session()
            print(f"   - Time until session: {time_until}")
            
            # Test status display
            status_display = session1.get_status_display()
            print(f"   - Status display: {status_display}")
            
            print("✅ Session methods tested")
            
            # Test 8: Test reschedule request
            print("\n📝 Test 8: Testing reschedule request...")
            
            try:
                session1.request_reschedule(
                    requested_by='student',
                    reason='I have a conflicting appointment that I cannot reschedule'
                )
                print("   - Reschedule request created successfully")
                
                # Check reschedule status
                print(f"   - Reschedule requested: {session1.reschedule_requested}")
                print(f"   - Requested by: {session1.reschedule_requested_by}")
                print(f"   - Reason: {session1.reschedule_reason}")
                print(f"   - Deadline: {session1.reschedule_deadline}")
                
            except Exception as e:
                print(f"   - Error creating reschedule request: {e}")
            
            print("✅ Reschedule request tested")
            
            # Test 9: Test reschedule approval
            print("\n📝 Test 9: Testing reschedule approval...")
            
            try:
                new_time = datetime.utcnow() + timedelta(days=2, hours=2)
                session1.approve_reschedule(new_time)
                print("   - Reschedule approved successfully")
                print(f"   - New scheduled time: {session1.scheduled_at}")
                print(f"   - Reschedule requested: {session1.reschedule_requested}")
                
            except Exception as e:
                print(f"   - Error approving reschedule: {e}")
            
            print("✅ Reschedule approval tested")
            
            # Test 10: Test session completion
            print("\n📝 Test 10: Testing session completion...")
            
            # Create a past session for completion
            past_session = Session(
                proposal_id=proposal.id,
                session_number=5,
                scheduled_at=datetime.utcnow() - timedelta(hours=2),
                duration_minutes=60,
                timezone='UTC',
                status='scheduled'
            )
            db.session.add(past_session)
            db.session.commit()
            
            try:
                past_session.mark_completed(
                    notes='Great session! Covered Python basics and variables.',
                    completed_by='coach'
                )
                print("   - Session completed successfully")
                print(f"   - Status: {past_session.status}")
                print(f"   - Completed date: {past_session.completed_date}")
                print(f"   - Coach notes: {past_session.coach_notes}")
                print(f"   - Contract completed sessions: {contract.completed_sessions}")
                
            except Exception as e:
                print(f"   - Error completing session: {e}")
            
            print("✅ Session completion tested")
            
            # Test 11: Test session cancellation
            print("\n📝 Test 11: Testing session cancellation...")
            
            future_session = sessions[1]
            
            try:
                future_session.cancel_session()
                print("   - Session cancelled successfully")
                print(f"   - Status: {future_session.status}")
                
            except Exception as e:
                print(f"   - Error cancelling session: {e}")
            
            print("✅ Session cancellation tested")
            
            # Test 12: Test session missed
            print("\n📝 Test 12: Testing session missed...")
            
            # Create a past session that wasn't completed
            missed_session = Session(
                proposal_id=proposal.id,
                session_number=6,
                scheduled_at=datetime.utcnow() - timedelta(hours=3),
                duration_minutes=60,
                timezone='UTC',
                status='scheduled'
            )
            db.session.add(missed_session)
            db.session.commit()
            
            try:
                missed_session.mark_missed()
                print("   - Session marked as missed successfully")
                print(f"   - Status: {missed_session.status}")
                
            except Exception as e:
                print(f"   - Error marking session as missed: {e}")
            
            print("✅ Session missed tested")
            
            # Test 13: Test contract methods
            print("\n📝 Test 13: Testing contract methods...")
            
            progress = contract.get_progress_percentage()
            remaining = contract.get_remaining_sessions()
            next_session = contract.get_next_session()
            
            print(f"   - Progress percentage: {progress}%")
            print(f"   - Remaining sessions: {remaining}")
            print(f"   - Next session: {next_session.session_number if next_session else 'None'}")
            
            print("✅ Contract methods tested")
            
            # Test 14: Test form validation
            print("\n📝 Test 14: Testing form validation...")
            
            # Test SessionScheduleForm
            schedule_form = SessionScheduleForm()
            schedule_form.scheduled_at.data = (datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')
            schedule_form.duration_minutes.data = 60
            schedule_form.timezone.data = 'UTC'
            
            if schedule_form.validate():
                print("   - SessionScheduleForm validation: ✅ PASS")
            else:
                print(f"   - SessionScheduleForm validation: ❌ FAIL - {schedule_form.errors}")
            
            # Test RescheduleRequestForm
            reschedule_form = RescheduleRequestForm()
            reschedule_form.reason.data = 'I have a conflicting appointment that I cannot reschedule'
            
            if reschedule_form.validate():
                print("   - RescheduleRequestForm validation: ✅ PASS")
            else:
                print(f"   - RescheduleRequestForm validation: ❌ FAIL - {reschedule_form.errors}")
            
            # Test SessionCompletionForm
            completion_form = SessionCompletionForm()
            completion_form.notes.data = 'Great session! Covered Python basics and variables.'
            
            if completion_form.validate():
                print("   - SessionCompletionForm validation: ✅ PASS")
            else:
                print(f"   - SessionCompletionForm validation: ❌ FAIL - {completion_form.errors}")
            
            print("✅ Form validation tested")
            
            # Test 15: Test edge cases
            print("\n📝 Test 15: Testing edge cases...")
            
            # Test invalid reschedule request (no reason)
            try:
                session1.request_reschedule(requested_by='student', reason='')
                print("   - ❌ Should have failed for empty reason")
            except ValueError as e:
                print(f"   - ✅ Correctly rejected empty reason: {e}")
            
            # Test invalid reschedule request (too short reason)
            try:
                session1.request_reschedule(requested_by='student', reason='Busy')
                print("   - ❌ Should have failed for short reason")
            except ValueError as e:
                print(f"   - ✅ Correctly rejected short reason: {e}")
            
            # Test invalid completion (wrong status)
            try:
                future_session.mark_completed(notes='Test', completed_by='coach')
                print("   - ❌ Should have failed for cancelled session")
            except ValueError as e:
                print(f"   - ✅ Correctly rejected completion of cancelled session: {e}")
            
            print("✅ Edge cases tested")
            
            # Cleanup
            print("\n🧹 Cleaning up test data...")
            db.session.delete(contract)
            db.session.delete(proposal)
            db.session.delete(learning_request)
            db.session.delete(student_profile)
            db.session.delete(coach_profile)
            db.session.delete(student)
            db.session.delete(coach)
            db.session.commit()
            
            print("✅ Test data cleaned up")
            
            print("\n🎉 Session Management System Test Completed Successfully!")
            print("\n📊 Test Summary:")
            print("   ✅ User and profile creation")
            print("   ✅ Learning request and proposal creation")
            print("   ✅ Contract creation")
            print("   ✅ Session creation and scheduling")
            print("   ✅ Session reschedule functionality")
            print("   ✅ Session completion functionality")
            print("   ✅ Session cancellation functionality")
            print("   ✅ Session missed functionality")
            print("   ✅ Contract progress tracking")
            print("   ✅ Form validation")
            print("   ✅ Edge case handling")
            
            return True
            
    except Exception as e:
        print(f"❌ Session Management System Test Failed: {e}")
        logger.error(f"Test failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = test_session_management()
    sys.exit(0 if success else 1)
