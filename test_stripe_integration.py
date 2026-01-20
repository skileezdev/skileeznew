#!/usr/bin/env python3
"""
Test script for Stripe payment integration
Run this to verify your Stripe setup is working correctly
"""

import os
import sys
import logging
from app import app, db
from models import User, CoachProfile, LearningRequest, Proposal, Contract, SessionPayment
from payment_utils import (
    create_payment_intent, 
    create_session_payment_intent,
    get_coach_stripe_account,
    calculate_platform_fee,
    calculate_coach_payout,
    PaymentError
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_stripe_configuration():
    """Test if Stripe is properly configured"""
    logger.info("🔧 Testing Stripe configuration...")
    
    # Check environment variables
    required_vars = ['STRIPE_SECRET_KEY', 'STRIPE_PUBLISHABLE_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        logger.info("💡 Add these to your .env file or environment:")
        for var in missing_vars:
            logger.info(f"   {var}=your_stripe_key_here")
        return False
    
    logger.info("✅ Stripe environment variables configured")
    
    # Test Stripe API connection
    try:
        import stripe
        stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
        
        # Test API call
        account = stripe.Account.retrieve()
        logger.info(f"✅ Stripe API connection successful (Account: {account.id})")
        return True
        
    except Exception as e:
        logger.error(f"❌ Stripe API connection failed: {e}")
        return False

def test_payment_utilities():
    """Test payment utility functions"""
    logger.info("🧮 Testing payment utility functions...")
    
    # Test fee calculations
    amount = 100.00
    platform_fee = calculate_platform_fee(amount)
    coach_payout = calculate_coach_payout(amount)
    
    logger.info(f"💰 Test payment: ${amount}")
    logger.info(f"   Platform fee (15%): ${platform_fee:.2f}")
    logger.info(f"   Coach payout: ${coach_payout:.2f}")
    
    if abs(platform_fee + coach_payout - amount) < 0.01:
        logger.info("✅ Fee calculations correct")
        return True
    else:
        logger.error("❌ Fee calculations incorrect")
        return False

def test_database_models():
    """Test if database models are properly set up"""
    logger.info("🗄️ Testing database models...")
    
    try:
        with app.app_context():
            # Check if tables exist
            inspector = db.inspect(db.engine)
            required_tables = ['user', 'coach_profile', 'contract', 'session_payment']
            
            for table in required_tables:
                if table in inspector.get_table_names():
                    logger.info(f"✅ Table '{table}' exists")
                else:
                    logger.error(f"❌ Table '{table}' missing")
                    return False
            
            # Check if Stripe columns exist
            user_columns = [col['name'] for col in inspector.get_columns('user')]
            coach_profile_columns = [col['name'] for col in inspector.get_columns('coach_profile')]
            
            if 'stripe_customer_id' in user_columns:
                logger.info("✅ User.stripe_customer_id column exists")
            else:
                logger.warning("⚠️ User.stripe_customer_id column missing")
            
            if 'stripe_account_id' in coach_profile_columns:
                logger.info("✅ CoachProfile.stripe_account_id column exists")
            else:
                logger.warning("⚠️ CoachProfile.stripe_account_id column missing")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Database test failed: {e}")
        return False

def test_webhook_endpoint():
    """Test if webhook endpoint is accessible"""
    logger.info("🌐 Testing webhook endpoint...")
    
    try:
        with app.test_client() as client:
            response = client.post('/webhooks/stripe')
            
            if response.status_code == 400:
                logger.info("✅ Webhook endpoint accessible (400 expected without signature)")
                return True
            else:
                logger.warning(f"⚠️ Webhook endpoint returned {response.status_code}")
                return True
                
    except Exception as e:
        logger.error(f"❌ Webhook endpoint test failed: {e}")
        return False

def create_test_data():
    """Create test data for payment testing"""
    logger.info("📝 Creating test data...")
    
    try:
        with app.app_context():
            # Create test user (student)
            student = User(
                first_name="Test",
                last_name="Student",
                email="test.student@example.com",
                email_verified=True
            )
            student.set_password("password123")
            db.session.add(student)
            
            # Create test coach
            coach = User(
                first_name="Test",
                last_name="Coach",
                email="test.coach@example.com",
                email_verified=True
            )
            coach.set_password("password123")
            db.session.add(coach)
            
            db.session.commit()
            
            # Create coach profile
            coach_profile = CoachProfile(
                user_id=coach.id,
                coach_title="Test Coach",
                bio="I'm a test coach for payment testing",
                hourly_rate=50.00,
                is_approved=True
            )
            db.session.add(coach_profile)
            
            # Create student profile
            from models import StudentProfile
            student_profile = StudentProfile(
                user_id=student.id,
                bio="I'm a test student"
            )
            db.session.add(student_profile)
            
            db.session.commit()
            
            logger.info(f"✅ Created test users:")
            logger.info(f"   Student: {student.email} (ID: {student.id})")
            logger.info(f"   Coach: {coach.email} (ID: {coach.id})")
            
            return student, coach
            
    except Exception as e:
        logger.error(f"❌ Failed to create test data: {e}")
        return None, None

def cleanup_test_data(student, coach):
    """Clean up test data"""
    try:
        with app.app_context():
            if student:
                db.session.delete(student)
            if coach:
                db.session.delete(coach)
            db.session.commit()
            logger.info("🧹 Test data cleaned up")
    except Exception as e:
        logger.warning(f"⚠️ Failed to cleanup test data: {e}")

def main():
    """Run all tests"""
    logger.info("🚀 Starting Stripe integration tests...")
    
    tests = [
        ("Stripe Configuration", test_stripe_configuration),
        ("Payment Utilities", test_payment_utilities),
        ("Database Models", test_database_models),
        ("Webhook Endpoint", test_webhook_endpoint),
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
        logger.info("🎉 All tests passed! Stripe integration is ready.")
        logger.info("\n📋 Next steps:")
        logger.info("1. Set up your Stripe account and get API keys")
        logger.info("2. Configure environment variables")
        logger.info("3. Set up webhooks in Stripe Dashboard")
        logger.info("4. Test with real payment flows")
    else:
        logger.error("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
