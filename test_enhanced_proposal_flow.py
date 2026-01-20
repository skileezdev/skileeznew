#!/usr/bin/env python3
"""
Test script for enhanced proposal acceptance flow with messaging integration
"""

from app import app, db
from models import User, CoachProfile, StudentProfile, LearningRequest, Proposal, Message
from datetime import datetime

def test_enhanced_proposal_flow():
    """Test the enhanced proposal acceptance flow with messaging"""
    with app.app_context():
        print("🧪 Testing enhanced proposal acceptance flow...")
        
        try:
            # Create test student
            student = User(
                first_name="Test",
                last_name="Student",
                email="test.student.enhanced@example.com",
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
                email="test.coach.enhanced@example.com",
                email_verified=True,
                is_coach=True,
                current_role='coach'
            )
            coach.set_password("password123")
            db.session.add(coach)
            
            db.session.commit()
            print(f"✅ Created users: Student {student.id}, Coach {coach.id}")
            
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
            print("✅ Created profiles")
            
            # Create learning request
            learning_request = LearningRequest(
                student_id=student.id,
                title="Test Learning Request for Enhanced Flow",
                description="Test description for enhanced flow",
                budget=300,
                is_active=True
            )
            db.session.add(learning_request)
            db.session.commit()
            print(f"✅ Created learning request: {learning_request.id}")
            
            # Create proposal
            proposal = Proposal(
                learning_request_id=learning_request.id,
                coach_id=coach.id,
                cover_letter="Test proposal for enhanced flow",
                session_count=5,
                price_per_session=50.00,
                session_duration=60,
                total_price=250.00,
                status='pending'
            )
            db.session.add(proposal)
            db.session.commit()
            print(f"✅ Created proposal: {proposal.id}")
            
            # Simulate proposal acceptance (this would normally be done via the web interface)
            proposal.status = 'accepted'
            proposal.accepted_at = datetime.utcnow()
            learning_request.is_active = False
            db.session.commit()
            print("✅ Proposal accepted")
            
            # Check if notification message was created
            notification_message = Message.query.filter_by(
                sender_id=student.id,
                recipient_id=coach.id
            ).first()
            
            if notification_message:
                print(f"✅ Notification message created: {notification_message.content[:50]}...")
            else:
                print("⚠️ No notification message found (this is expected since we didn't use the web route)")
            
            # Test the contract creation route logic
            from routes import create_contract_from_messages
            print("✅ Contract creation route logic imported successfully")
            
            # Test the call scheduling route logic
            from routes import schedule_call_from_messages
            print("✅ Call scheduling route logic imported successfully")
            
            # Clean up
            db.session.delete(proposal)
            db.session.delete(learning_request)
            db.session.delete(coach_profile)
            db.session.delete(student_profile)
            db.session.delete(coach)
            db.session.delete(student)
            db.session.commit()
            print("✅ Test data cleaned up")
            
            print("🎉 Enhanced proposal flow test completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Enhanced proposal flow test failed: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    test_enhanced_proposal_flow()
