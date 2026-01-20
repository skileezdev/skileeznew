#!/usr/bin/env python3
"""
Simple test to debug contract creation
"""

from app import app, db
from models import User, CoachProfile, StudentProfile, LearningRequest, Proposal, Contract
from datetime import date

def test_simple_contract():
    with app.app_context():
        print("Creating test data...")
        
        # Create test student
        student = User(
            first_name="Test",
            last_name="Student",
            email="test.student.simple@example.com",
            email_verified=True,
            is_student=True,
            current_role='student'
        )
        student.set_password("password123")
        db.session.add(student)
        
        # Create test coach
        coach = User(
            first_name="Test",
            last_name="Coach",
            email="test.coach.simple@example.com",
            email_verified=True,
            is_coach=True,
            current_role='coach'
        )
        coach.set_password("password123")
        db.session.add(coach)
        
        db.session.commit()
        print(f"Created users: Student {student.id}, Coach {coach.id}")
        
        # Create profiles
        student_profile = StudentProfile(user_id=student.id, bio="Test student")
        coach_profile = CoachProfile(
            user_id=coach.id,
            coach_title="Test Coach",
            bio="Test coach",
            hourly_rate=50.00,
            is_approved=True
        )
        db.session.add(student_profile)
        db.session.add(coach_profile)
        db.session.commit()
        print("Created profiles")
        
        # Create learning request
        learning_request = LearningRequest(
            student_id=student.id,
            title="Test Learning Request",
            description="Test description",
            budget=300,
            is_active=True
        )
        db.session.add(learning_request)
        db.session.commit()
        print(f"Created learning request: {learning_request.id}")
        
        # Create proposal
        proposal = Proposal(
            learning_request_id=learning_request.id,
            coach_id=coach.id,
            cover_letter="Test proposal",
            session_count=5,
            price_per_session=50.00,
            session_duration=60,
            total_price=250.00,
            status='accepted'
        )
        db.session.add(proposal)
        db.session.commit()
        print(f"Created proposal: {proposal.id}")
        
        # Create contract
        try:
            contract = proposal.create_contract(
                start_date=date(2024, 2, 1),
                timezone="UTC",
                cancellation_policy="24 hours notice required",
                learning_outcomes="Student will learn the basics"
            )
            print(f"✅ Contract created: {contract.contract_number}")
            print(f"   ID: {contract.id}")
            print(f"   Total sessions: {contract.total_sessions}")
            print(f"   Total amount: ${contract.total_amount}")
            
            # Clean up
            db.session.delete(contract)
            db.session.delete(proposal)
            db.session.delete(learning_request)
            db.session.delete(coach_profile)
            db.session.delete(student_profile)
            db.session.delete(coach)
            db.session.delete(student)
            db.session.commit()
            print("✅ Cleanup completed")
            
        except Exception as e:
            print(f"❌ Error creating contract: {e}")
            db.session.rollback()

if __name__ == "__main__":
    test_simple_contract()
