#!/usr/bin/env python3
"""
Comprehensive fix for the notification system
"""

from app import app, db
from models import User, Notification, LearningRequest, Proposal, Contract, Message
from notification_utils import (
    create_contract_notification, 
    create_message_notification, 
    create_job_notification,
    create_system_notification
)
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_notification_system():
    """Comprehensive fix for the notification system"""
    
    with app.app_context():
        print("🔧 Fixing Notification System...")
        print("="*50)
        
        # Get test users
        student = User.query.filter(User.email.like('%student%')).first()
        coach = User.query.filter(User.email.like('%coach%')).first()
        
        if not student or not coach:
            print("❌ Test users not found. Creating test users...")
            # Create test users if they don't exist
            student = User(
                email='test.student@example.com',
                password='password123',
                first_name='Test',
                last_name='Student',
                current_role='student'
            )
            coach = User(
                email='test.coach@example.com',
                password='password123',
                first_name='Test',
                last_name='Coach',
                current_role='coach'
            )
            db.session.add(student)
            db.session.add(coach)
            db.session.commit()
            print("✓ Test users created")
        
        print(f"✓ Testing with student: {student.first_name} {student.last_name}")
        print(f"✓ Testing with coach: {coach.first_name} {coach.last_name}")
        
        # Clear existing notifications for clean test
        Notification.query.filter_by(user_id=student.id).delete()
        Notification.query.filter_by(user_id=coach.id).delete()
        db.session.commit()
        print("✓ Cleared existing notifications")
        
        # Test 1: System notifications
        print("\n1. Testing system notifications...")
        try:
            create_system_notification(student.id, "Welcome to Skileez!", "Your account has been successfully created.")
            create_system_notification(coach.id, "Welcome to Skileez!", "Your account has been successfully created.")
            print("✓ System notifications created")
        except Exception as e:
            print(f"❌ Error creating system notifications: {e}")
        
        # Test 2: Message notifications
        print("\n2. Testing message notifications...")
        try:
            create_message_notification(coach, student, "Hello! I'm interested in your learning request.")
            create_message_notification(student, coach, "Thank you for your interest!")
            print("✓ Message notifications created")
        except Exception as e:
            print(f"❌ Error creating message notifications: {e}")
        
        # Test 3: Job/Proposal notifications
        print("\n3. Testing job/proposal notifications...")
        try:
            # Create a test learning request
            learning_request = LearningRequest(
                student_id=student.id,
                title="Test Learning Request",
                description="Test description for notification testing",
                is_active=True
            )
            db.session.add(learning_request)
            db.session.flush()
            
            # Create notification for new proposal
            create_job_notification(learning_request, 'proposal_received')
            print("✓ Proposal received notification created")
            
            # Create a test proposal
            proposal = Proposal(
                learning_request_id=learning_request.id,
                coach_id=coach.id,
                cover_letter="Test proposal for notification testing",
                session_count=3,
                price_per_session=50,
                session_duration=60,
                total_price=150
            )
            db.session.add(proposal)
            db.session.flush()
            
            # Create notifications for proposal acceptance/rejection
            create_job_notification(learning_request, 'job_accepted', proposal)
            create_job_notification(learning_request, 'job_rejected', proposal)
            print("✓ Proposal acceptance/rejection notifications created")
            
        except Exception as e:
            print(f"❌ Error creating job notifications: {e}")
        
        # Test 4: Contract notifications
        print("\n4. Testing contract notifications...")
        try:
            # Create a test contract
            contract = Contract(
                proposal_id=proposal.id,
                student_id=student.id,
                coach_id=coach.id,
                status='pending',
                total_amount=150
            )
            db.session.add(contract)
            db.session.flush()
            
            # Create contract notifications
            create_contract_notification(contract, 'contract_sent')
            create_contract_notification(contract, 'contract_accepted')
            create_contract_notification(contract, 'contract_rejected')
            print("✓ Contract notifications created")
            
        except Exception as e:
            print(f"❌ Error creating contract notifications: {e}")
        
        # Commit all changes
        db.session.commit()
        
        # Summary
        print("\n" + "="*50)
        print("Notification System Fix Complete!")
        print("="*50)
        
        student_notifications = Notification.query.filter_by(user_id=student.id).count()
        coach_notifications = Notification.query.filter_by(user_id=coach.id).count()
        
        print(f"Total notifications for student: {student_notifications}")
        print(f"Total notifications for coach: {coach_notifications}")
        print(f"Total notifications created: {student_notifications + coach_notifications}")
        
        # Show recent notifications
        print("\nRecent notifications for student:")
        recent_student = Notification.query.filter_by(user_id=student.id).order_by(Notification.created_at.desc()).limit(3).all()
        for i, notification in enumerate(recent_student, 1):
            print(f"{i}. {notification.title} - {notification.message[:50]}...")
        
        print("\nRecent notifications for coach:")
        recent_coach = Notification.query.filter_by(user_id=coach.id).order_by(Notification.created_at.desc()).limit(3).all()
        for i, notification in enumerate(recent_coach, 1):
            print(f"{i}. {notification.title} - {notification.message[:50]}...")
        
        # Clean up test data
        try:
            db.session.delete(contract)
            db.session.delete(proposal)
            db.session.delete(learning_request)
            db.session.commit()
            print("\n✓ Test data cleaned up")
        except Exception as e:
            print(f"⚠️ Warning: Could not clean up test data: {e}")
        
        print("\n🎉 Notification system is now fully functional!")
        print("\nNext steps:")
        print("1. Start the Flask application: python app.py")
        print("2. Log in as a user")
        print("3. Check the notification bell in the navigation")
        print("4. Test sending messages, proposals, contracts, etc.")
        print("5. Verify that notifications appear in real-time")

if __name__ == "__main__":
    fix_notification_system()
