#!/usr/bin/env python3
"""
Test Email Verification Functionality
"""

import os
import sys

def test_email_verification_config():
    """Test email verification configuration"""
    print("🔍 Testing Email Verification Configuration...")
    
    # Set test environment
    os.environ.setdefault('ENABLE_EMAIL_VERIFICATION', 'true')
    os.environ.setdefault('MAIL_SERVER', 'smtp.gmail.com')
    os.environ.setdefault('MAIL_USERNAME', 'skileezverf@gmail.com')
    os.environ.setdefault('MAIL_PASSWORD', 'wghd tnjr kbda mjie')
    os.environ.setdefault('SESSION_SECRET', 'test-secret-key')
    os.environ.setdefault('DATABASE_URL', 'sqlite:///test.db')
    
    try:
        # Import and create app
        from app import app
        
        with app.app_context():
            # Test email verification configuration
            from utils import is_email_verification_enabled
            
            email_enabled = is_email_verification_enabled()
            print(f"   ✅ Email verification enabled: {email_enabled}")
            
            # Test mail configuration
            mail_server = app.config.get('MAIL_SERVER')
            mail_username = app.config.get('MAIL_USERNAME')
            mail_password = app.config.get('MAIL_PASSWORD')
            
            print(f"   ✅ Mail server: {mail_server}")
            print(f"   ✅ Mail username: {mail_username}")
            print(f"   ✅ Mail password: {'***' if mail_password else 'NOT SET'}")
            
            # Test email verification function
            if email_enabled:
                print("   ✅ Email verification is properly configured!")
                return True
            else:
                print("   ❌ Email verification is disabled!")
                return False
                
    except Exception as e:
        print(f"   ❌ Error testing email verification: {e}")
        return False

def test_email_sending():
    """Test if email can be sent"""
    print("\n🔍 Testing Email Sending...")
    
    try:
        from app import app
        
        with app.app_context():
            from email_utils import send_verification_email
            from models import User
            
            # Create a test user
            test_user = User(
                first_name="Test",
                last_name="User",
                email="test@example.com",
                email_verified=False
            )
            
            print("   📧 Attempting to send test verification email...")
            
            # This will test the email sending without actually sending
            # The function should return True if email verification is enabled
            result = send_verification_email(test_user)
            
            if result:
                print("   ✅ Email verification system is working!")
                return True
            else:
                print("   ❌ Email verification system failed!")
                return False
                
    except Exception as e:
        print(f"   ❌ Error testing email sending: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 EMAIL VERIFICATION TEST")
    print("=" * 50)
    
    # Run tests
    config_ok = test_email_verification_config()
    sending_ok = test_email_sending()
    
    print("\n🎯 Results:")
    print("=" * 20)
    
    tests = [
        ("Email Verification Config", config_ok),
        ("Email Sending Test", sending_ok)
    ]
    
    all_passed = True
    for test_name, passed in tests:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 Email verification is working correctly!")
        print("\n📋 Next steps:")
        print("   1. Deploy your changes to Render")
        print("   2. Set ENABLE_EMAIL_VERIFICATION=true in Render environment variables")
        print("   3. Test creating a new account")
        print("   4. Check email for verification link")
    else:
        print("\n⚠️ Some tests failed. Check the configuration.")
        print("\n🔧 Common fixes:")
        print("   1. Ensure ENABLE_EMAIL_VERIFICATION=true")
        print("   2. Check MAIL_USERNAME and MAIL_PASSWORD are set")
        print("   3. Verify MAIL_SERVER is configured")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
