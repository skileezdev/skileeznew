#!/usr/bin/env python3
"""
Test script to verify notification creation for specific scenarios
"""

from app import app, db
from models import User, Notification, LearningRequest, Proposal, Contract, Message
from notification_utils import create_contract_notification, create_message_notification, create_job_notification
from datetime import datetime

def test_notification_scenarios():
    """Test notification creation for various scenarios"""
    
    with app.app_context():
        print("Testing Notification Scenarios...")
        
        # Get test users
        student = User.query.filter(User.email.like('%student%')).first()
        coach = User.query.filter(User.email.like('%coach%')).first()
        
        if not student or not coach:
            print("❌ Test users not found. Please run demo_notifications.py first.")
            return
        
        print(f"✓ Testing with student: {student.first_name} {student.last_name}")
        print(f"✓ Testing with coach: {coach.first_name} {coach.last_name}")
        
        # Clear existing notifications for clean test
        Notification.query.filter_by(user_id=student.id).delete()
        Notification.query.filter_by(user_id=coach.id).delete()
        
        # Test 1: New proposal notification
        print("\n1. Testing new proposal notification...")
        try:
            # Create a test learning request
            learning_request = LearningRequest(
                student_id=student.id,
                title="Test Learning Request",
                description="Test description",
                is_active=True
            )
            db.session.add(learning_request)
            db.session.flush()
            
            # Create notification for new proposal
            create_job_notification(learning_request, 'proposal_received')
            
            # Check if notification was created
            notifications = Notification.query.filter_by(user_id=student.id).all()
            if notifications:
                print(f"✓ New proposal notification created: {notifications[-1].title}")
            else:
                print("❌ New proposal notification not created")
                
        except Exception as e:
            print(f"❌ Error testing proposal notification: {e}")
        
        # Test 2: Proposal accepted notification
        print("\n2. Testing proposal accepted notification...")
        try:
            # Create a test proposal
            proposal = Proposal(
                learning_request_id=learning_request.id,
                coach_id=coach.id,
                cover_letter="Test proposal",
                session_count=3,
                price_per_session=50,
                total_price=150
            )
            db.session.add(proposal)
            db.session.flush()
            
            # Create notification for accepted proposal
            create_job_notification(learning_request, 'job_accepted', proposal)
            
            # Check if notification was created
            notifications = Notification.query.filter_by(user_id=coach.id).all()
            if notifications:
                print(f"✓ Proposal accepted notification created: {notifications[-1].title}")
            else:
                print("❌ Proposal accepted notification not created")
                
        except Exception as e:
            print(f"❌ Error testing proposal accepted notification: {e}")
        
        # Test 3: Proposal rejected notification
        print("\n3. Testing proposal rejected notification...")
        try:
            # Create notification for rejected proposal
            create_job_notification(learning_request, 'job_rejected', proposal)
            
            # Check if notification was created
            notifications = Notification.query.filter_by(user_id=coach.id).all()
            if notifications:
                print(f"✓ Proposal rejected notification created: {notifications[-1].title}")
            else:
                print("❌ Proposal rejected notification not created")
                
        except Exception as e:
            print(f"❌ Error testing proposal rejected notification: {e}")
        
        # Test 4: Contract sent notification
        print("\n4. Testing contract sent notification...")
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
            
            # Create notification for contract sent
            create_contract_notification(contract, 'contract_sent')
            
            # Check if notification was created
            notifications = Notification.query.filter_by(user_id=student.id).all()
            if notifications:
                print(f"✓ Contract sent notification created: {notifications[-1].title}")
            else:
                print("❌ Contract sent notification not created")
                
        except Exception as e:
            print(f"❌ Error testing contract sent notification: {e}")
        
        # Test 5: Contract accepted notification
        print("\n5. Testing contract accepted notification...")
        try:
            # Create notification for contract accepted
            create_contract_notification(contract, 'contract_accepted')
            
            # Check if notification was created
            notifications = Notification.query.filter_by(user_id=coach.id).all()
            if notifications:
                print(f"✓ Contract accepted notification created: {notifications[-1].title}")
            else:
                print("❌ Contract accepted notification not created")
                
        except Exception as e:
            print(f"❌ Error testing contract accepted notification: {e}")
        
        # Test 6: Contract rejected notification
        print("\n6. Testing contract rejected notification...")
        try:
            # Create notification for contract rejected
            create_contract_notification(contract, 'contract_rejected')
            
            # Check if notification was created
            notifications = Notification.query.filter_by(user_id=coach.id).all()
            if notifications:
                print(f"✓ Contract rejected notification created: {notifications[-1].title}")
            else:
                print("❌ Contract rejected notification not created")
                
        except Exception as e:
            print(f"❌ Error testing contract rejected notification: {e}")
        
        # Test 7: Message notification
        print("\n7. Testing message notification...")
        try:
            # Create notification for new message
            create_message_notification(coach, student, "Hello! I'm interested in your services...")
            
            # Check if notification was created
            notifications = Notification.query.filter_by(user_id=student.id).all()
            if notifications:
                print(f"✓ Message notification created: {notifications[-1].title}")
            else:
                print("❌ Message notification not created")
                
        except Exception as e:
            print(f"❌ Error testing message notification: {e}")
        
        # Summary
        print("\n" + "="*50)
        print("Notification Scenarios Test Complete!")
        print("="*50)
        
        student_notifications = Notification.query.filter_by(user_id=student.id).count()
        coach_notifications = Notification.query.filter_by(user_id=coach.id).count()
        
        print(f"Total notifications for student: {student_notifications}")
        print(f"Total notifications for coach: {coach_notifications}")
        print(f"Total notifications created: {student_notifications + coach_notifications}")
        
        # Clean up test data
        db.session.delete(contract)
        db.session.delete(proposal)
        db.session.delete(learning_request)
        db.session.commit()
        
        print("\n✓ Test data cleaned up")

if __name__ == "__main__":
    test_notification_scenarios()
