#!/usr/bin/env python3
"""
Debug script to test contract progress update
"""

import os
import sys
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Session, User, Proposal, Contract, LearningRequest

def debug_contract_progress():
    """Debug the contract progress update issue"""
    
    with app.app_context():
        print("Debugging Contract Progress Update")
        print("=" * 50)
        
        # Create test data
        test_user = User.query.first()
        if not test_user:
            print("No users found in database")
            return
        
        # Create a test learning request
        learning_request = LearningRequest(
            student_id=test_user.id,
            title="Debug Test Subject",
            description="Debug test learning request",
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
            cover_letter="Debug test cover letter",
            session_count=3,
            price_per_session=20.00,
            session_duration=60,
            total_price=60.00,
            status='accepted'
        )
        db.session.add(proposal)
        db.session.commit()
        
        # Create a test contract
        contract = Contract(
            proposal_id=proposal.id,
            student_id=test_user.id,
            coach_id=test_user.id,
            contract_number=f"DEBUG-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            status='active',
            start_date=datetime.utcnow().date(),
            total_sessions=3,
            completed_sessions=0,
            total_amount=60.00,
            payment_model='per_session',
            rate=20.00,
            duration_minutes=60
        )
        db.session.add(contract)
        db.session.commit()
        
        print(f"Created contract: {contract.contract_number}")
        print(f"Initial completed_sessions: {contract.completed_sessions}")
        print(f"Total sessions: {contract.total_sessions}")
        
        # Create a session that should be auto-completed
        now = datetime.utcnow()
        session = Session(
            proposal_id=proposal.id,
            session_number=1,
            scheduled_at=now - timedelta(hours=2),  # 2 hours ago
            duration_minutes=60,
            status='active',
            meeting_started_at=now - timedelta(hours=2)
        )
        db.session.add(session)
        db.session.commit()
        
        print(f"\nCreated session: {session.id}")
        print(f"Session status: {session.status}")
        print(f"Session scheduled_at: {session.scheduled_at}")
        print(f"Session duration_minutes: {session.duration_minutes}")
        
        # Test the contract relationship
        print(f"\nTesting contract relationship:")
        print(f"Session proposal_id: {session.proposal_id}")
        print(f"Session proposal: {session.proposal}")
        print(f"Session get_contract(): {session.get_contract()}")
        
        # Test should_be_completed
        print(f"\nTesting should_be_completed:")
        print(f"should_be_completed(): {session.should_be_completed()}")
        
        # Test auto_complete_if_needed
        print(f"\nTesting auto_complete_if_needed:")
        print(f"Before auto_complete - Session status: {session.status}")
        print(f"Before auto_complete - Contract completed_sessions: {contract.completed_sessions}")
        
        result = session.auto_complete_if_needed()
        print(f"auto_complete_if_needed() returned: {result}")
        
        # Refresh the contract from database
        db.session.refresh(contract)
        print(f"After auto_complete - Session status: {session.status}")
        print(f"After auto_complete - Contract completed_sessions: {contract.completed_sessions}")
        print(f"After auto_complete - Contract status: {contract.status}")
        
        # Clean up test data
        db.session.delete(session)
        db.session.delete(contract)
        db.session.delete(proposal)
        db.session.delete(learning_request)
        db.session.commit()
        
        print("\nDebug completed!")

if __name__ == "__main__":
    debug_contract_progress()
