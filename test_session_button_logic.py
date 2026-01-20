#!/usr/bin/env python3
"""
Test script for session button logic
"""

import os
import sys
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Session, User, Proposal, Contract, ScheduledSession

def test_session_button_logic():
    """Test the new session button logic"""
    
    with app.app_context():
        print("Testing Session Button Logic")
        print("=" * 50)
        
        # Create test data
        test_user = User.query.first()
        if not test_user:
            print("No users found in database")
            return
        
        # Create a test learning request first
        from models import LearningRequest
        learning_request = LearningRequest(
            student_id=test_user.id,
            title="Test Subject",
            description="Test learning request for button logic",
            duration="1 month",
            budget=50.00,
            experience_level="beginner",
            skill_type="short_term",
            is_active=True
        )
        db.session.add(learning_request)
        db.session.commit()
        
        # Create a test proposal
        proposal = Proposal(
            learning_request_id=learning_request.id,
            coach_id=test_user.id,
            cover_letter="Test cover letter for button logic",
            session_count=5,
            price_per_session=20.00,
            session_duration=60,
            total_price=100.00,
            status='accepted'
        )
        db.session.add(proposal)
        db.session.commit()
        
        # Create a test contract
        contract = Contract(
            proposal_id=proposal.id,
            student_id=test_user.id,
            coach_id=test_user.id,
            contract_number=f"TEST-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            status='active',
            start_date=datetime.utcnow().date(),
            total_sessions=5,
            completed_sessions=0,
            total_amount=100.00,
            payment_model='per_session',
            rate=20.00,
            duration_minutes=60
        )
        db.session.add(contract)
        db.session.commit()
        
        # Create test sessions with different times
        now = datetime.utcnow()
        
        # Session 1: Future session (should show "Setup Meeting" for coach, "View Details" for student)
        future_session = Session(
            proposal_id=proposal.id,
            session_number=1,
            scheduled_at=now + timedelta(hours=2),
            duration_minutes=60,
            status='scheduled'
        )
        db.session.add(future_session)
        
        # Session 2: Active session (should show dual buttons for coach, "Join Session" for student)
        active_session = Session(
            proposal_id=proposal.id,
            session_number=2,
            scheduled_at=now - timedelta(minutes=30),
            duration_minutes=60,
            status='active',
            meeting_started_at=now - timedelta(minutes=30)
        )
        db.session.add(active_session)
        
        # Session 3: Completed session (should show "Meeting Completed" for both)
        completed_session = Session(
            proposal_id=proposal.id,
            session_number=3,
            scheduled_at=now - timedelta(hours=2),
            duration_minutes=60,
            status='completed',
            completed_date=now - timedelta(hours=1)
        )
        db.session.add(completed_session)
        
        db.session.commit()
        
        # Test button states
        print("\n1. Testing Future Session (scheduled in 2 hours):")
        print(f"   Coach button: {future_session.get_button_state('coach')}")
        print(f"   Student button: {future_session.get_button_state('student')}")
        
        print("\n2. Testing Active Session (started 30 minutes ago):")
        print(f"   Coach button: {active_session.get_button_state('coach')}")
        print(f"   Student button: {active_session.get_button_state('student')}")
        
        print("\n3. Testing Completed Session (completed 1 hour ago):")
        print(f"   Coach button: {completed_session.get_button_state('coach')}")
        print(f"   Student button: {completed_session.get_button_state('student')}")
        
        # Test auto-completion
        print("\n4. Testing Auto-completion:")
        session_to_complete = Session(
            proposal_id=proposal.id,
            session_number=4,
            scheduled_at=now - timedelta(hours=2),
            duration_minutes=60,
            status='active',
            meeting_started_at=now - timedelta(hours=2)
        )
        db.session.add(session_to_complete)
        db.session.commit()
        
        print(f"   Before auto-complete: {session_to_complete.status}")
        session_to_complete.auto_complete_if_needed()
        print(f"   After auto-complete: {session_to_complete.status}")
        
        # Clean up test data
        db.session.delete(session_to_complete)
        db.session.delete(completed_session)
        db.session.delete(active_session)
        db.session.delete(future_session)
        db.session.delete(contract)
        db.session.delete(proposal)
        db.session.delete(learning_request)
        db.session.commit()
        
        print("\nTest completed successfully!")

if __name__ == "__main__":
    test_session_button_logic()
