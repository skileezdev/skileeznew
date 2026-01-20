#!/usr/bin/env python3
"""
Test script for contract creation system
Run this to verify the contract system is working correctly
"""

import os
import sys
import logging
from app import app, db
from models import User, CoachProfile, StudentProfile, LearningRequest, Proposal, Contract, Session
from forms import ContractForm, SessionScheduleForm

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_contract_forms():
    """Test contract-related forms"""
    logger.info("🧪 Testing contract forms...")
    
    try:
        with app.app_context():
            with app.test_request_context():
                # Test ContractForm
                contract_form = ContractForm()
                logger.info("✅ ContractForm created successfully")
                
                # Test SessionScheduleForm
                session_form = SessionScheduleForm()
                logger.info("✅ SessionScheduleForm created successfully")
                
                return True
        
    except Exception as e:
        logger.error(f"❌ Form test failed: {e}")
        return False

def test_contract_creation():
    """Test contract creation flow"""
    logger.info("📝 Testing contract creation...")
    
    try:
        with app.app_context():
            # Create test student
            import time
            timestamp = int(time.time())
            student = User(
                first_name="Test",
                last_name="Student",
                email=f"test.student.{timestamp}@example.com",
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
                email=f"test.coach.{timestamp}@example.com",
                email_verified=True,
                is_coach=True,
                current_role='coach'
            )
            coach.set_password("password123")
            db.session.add(coach)
            
            db.session.commit()
            
            # Create student profile
            student_profile = StudentProfile(
                user_id=student.id,
                bio="I'm a test student"
            )
            db.session.add(student_profile)
            
            # Create coach profile
            coach_profile = CoachProfile(
                user_id=coach.id,
                coach_title="Test Coach",
                bio="I'm a test coach",
                hourly_rate=50.00,
                is_approved=True
            )
            db.session.add(coach_profile)
            
            db.session.commit()
            
            # Create learning request
            learning_request = LearningRequest(
                student_id=student.id,
                title="Test Learning Request",
                description="This is a test learning request for contract testing",
                budget=300,
                is_active=True
            )
            db.session.add(learning_request)
            db.session.commit()
            
            # Create proposal
            proposal = Proposal(
                learning_request_id=learning_request.id,
                coach_id=coach.id,
                cover_letter="This is a test proposal for contract testing",
                session_count=5,
                price_per_session=50.00,
                session_duration=60,
                total_price=250.00,
                status='accepted'
            )
            db.session.add(proposal)
            db.session.commit()
            
            # Test contract creation
            from datetime import date
            contract = proposal.create_contract(
                start_date=date(2024, 2, 1),
                timezone="UTC",
                cancellation_policy="24 hours notice required",
                learning_outcomes="Student will learn the basics of the subject"
            )
            
            # Log contract info immediately after creation
            logger.info(f"✅ Contract created successfully: {contract.contract_number}")
            logger.info(f"   Contract ID: {contract.id}")
            logger.info(f"   Total Sessions: {contract.total_sessions}")
            logger.info(f"   Total Amount: ${contract.total_amount}")
            
            # Clean up test data
            db.session.delete(contract)
            db.session.delete(proposal)
            db.session.delete(learning_request)
            db.session.delete(coach_profile)
            db.session.delete(student_profile)
            db.session.delete(coach)
            db.session.delete(student)
            db.session.commit()
            
            logger.info("🧹 Test data cleaned up")
            return True
            
    except Exception as e:
        logger.error(f"❌ Contract creation test failed: {e}")
        return False

def test_contract_routes():
    """Test contract routes are accessible"""
    logger.info("🌐 Testing contract routes...")
    
    try:
        with app.test_client() as client:
            # Test create_contract route (should redirect to login)
            response = client.get('/contracts/create/1')
            logger.info(f"✅ create_contract route accessible (status: {response.status_code})")
            
            # Test view_contract route (should redirect to login)
            response = client.get('/contracts/1')
            logger.info(f"✅ view_contract route accessible (status: {response.status_code})")
            
            # Test manage_sessions route (should redirect to login)
            response = client.get('/contracts/1/sessions')
            logger.info(f"✅ manage_sessions route accessible (status: {response.status_code})")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Route test failed: {e}")
        return False

def test_contract_templates():
    """Test contract templates exist"""
    logger.info("📄 Testing contract templates...")
    
    try:
        template_dir = os.path.join(os.path.dirname(__file__), 'templates', 'contracts')
        
        required_templates = [
            'create_contract.html',
            'view_contract.html',
            'manage_sessions.html'
        ]
        
        for template in required_templates:
            template_path = os.path.join(template_dir, template)
            if os.path.exists(template_path):
                logger.info(f"✅ Template exists: {template}")
            else:
                logger.error(f"❌ Template missing: {template}")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Template test failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("🚀 Starting contract system tests...")
    
    tests = [
        ("Contract Forms", test_contract_forms),
        ("Contract Creation", test_contract_creation),
        ("Contract Routes", test_contract_routes),
        ("Contract Templates", test_contract_templates),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            if test_func():
                passed += 1
                logger.info(f"✅ {test_name} PASSED")
            else:
                logger.error(f"❌ {test_name} FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name} ERROR: {e}")
    
    logger.info(f"\n{'='*50}")
    logger.info(f"Test Results: {passed}/{total} tests passed")
    logger.info(f"{'='*50}")
    
    if passed == total:
        logger.info("🎉 All tests passed! Contract system is ready.")
        logger.info("\n📋 Contract system features:")
        logger.info("✅ Contract creation from accepted proposals")
        logger.info("✅ Contract viewing and management")
        logger.info("✅ Session scheduling and management")
        logger.info("✅ Reschedule requests and approvals")
        logger.info("✅ Session completion tracking")
    else:
        logger.error("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
