#!/usr/bin/env python3
"""
Test script to verify sessions list shows updated contract progress
"""

import os
import sys
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Session, User, Proposal, Contract, LearningRequest

def test_sessions_list_progress():
    """Test that sessions list shows updated contract progress"""
    
    with app.app_context():
        print("Testing Sessions List Progress Update")
        print("=" * 50)
        
        # Create test data
        test_user = User.query.first()
        if not test_user:
            print("No users found in database")
            return
        
        # Create a test learning request
        learning_request = LearningRequest(
            student_id=test_user.id,
            title="Progress Test Subject",
            description="Test learning request for progress update",
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
            cover_letter="Progress test cover letter",
            session_count=2,
            price_per_session=20.00,
            session_duration=60,
            total_price=40.00,
            status='accepted'
        )
        db.session.add(proposal)
        db.session.commit()
        
        # Create a test contract
        contract = Contract(
            proposal_id=proposal.id,
            student_id=test_user.id,
            coach_id=test_user.id,
            contract_number=f"PROGRESS-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            status='active',
            start_date=datetime.utcnow().date(),
            total_sessions=2,
            completed_sessions=0,
            total_amount=40.00,
            payment_model='per_session',
            rate=20.00,
            duration_minutes=60
        )
        db.session.add(contract)
        db.session.commit()
        
        print(f"Created contract: {contract.contract_number}")
        print(f"Initial completed_sessions: {contract.completed_sessions}")
        print(f"Total sessions: {contract.total_sessions}")
        print(f"Progress percentage: {contract.get_progress_percentage()}%")
        
        # Create two sessions - one completed, one active that should be auto-completed
        now = datetime.utcnow()
        
        # Session 1: Already completed
        session1 = Session(
            proposal_id=proposal.id,
            session_number=1,
            scheduled_at=now - timedelta(hours=4),
            duration_minutes=60,
            status='completed',
            completed_date=now - timedelta(hours=3)
        )
        db.session.add(session1)
        
        # Session 2: Active but should be auto-completed
        session2 = Session(
            proposal_id=proposal.id,
            session_number=2,
            scheduled_at=now - timedelta(hours=2),
            duration_minutes=60,
            status='active',
            meeting_started_at=now - timedelta(hours=2)
        )
        db.session.add(session2)
        db.session.commit()
        
        print(f"\nCreated sessions:")
        print(f"Session 1: {session1.id} - Status: {session1.status}")
        print(f"Session 2: {session2.id} - Status: {session2.status}")
        
        # Simulate what happens when sessions_list route is called
        print(f"\nSimulating sessions_list route call...")
        
        # Get the contract (like the route does)
        contracts = Contract.query.filter(
            Contract.student_id == test_user.id,
            Contract.status == 'active'
        ).order_by(Contract.created_at.desc()).all()
        
        print(f"Found {len(contracts)} contracts")
        
        # Refresh contract progress (like the route does)
        for contract in contracts:
            print(f"Refreshing progress for contract: {contract.contract_number}")
            
            # Get all sessions for this contract
            sessions = Session.query.filter_by(proposal_id=contract.proposal_id).all()
            print(f"Found {len(sessions)} sessions")
            
            # Check if any sessions need to be auto-completed
            for session in sessions:
                if session.should_be_completed():
                    print(f"Auto-completing session {session.id}")
                    session.auto_complete_if_needed()
            
            # Refresh the contract to get updated progress
            db.session.refresh(contract)
            
            print(f"After refresh - completed_sessions: {contract.completed_sessions}")
            print(f"After refresh - progress percentage: {contract.get_progress_percentage()}%")
            print(f"After refresh - contract status: {contract.status}")
        
        # Clean up test data
        db.session.delete(session2)
        db.session.delete(session1)
        db.session.delete(contract)
        db.session.delete(proposal)
        db.session.delete(learning_request)
        db.session.commit()
        
        print("\nTest completed successfully!")

if __name__ == "__main__":
    test_sessions_list_progress()
