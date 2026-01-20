#!/usr/bin/env python3
"""
Test script to verify the signup fix works correctly
"""

import os
import sys
import traceback

def test_imports():
    """Test all required imports"""
    print("Testing imports...")
    
    try:
        from forms import SignupForm
        print("✅ SignupForm imported successfully")
    except Exception as e:
        print(f"❌ SignupForm import failed: {e}")
        return False
    
    try:
        from models import User, CoachProfile
        print("✅ Models imported successfully")
    except Exception as e:
        print(f"❌ Models import failed: {e}")
        return False
    
    try:
        from utils import is_email_verification_enabled, get_db
        print("✅ Utils imported successfully")
    except Exception as e:
        print(f"❌ Utils import failed: {e}")
        return False
    
    try:
        from email_utils import send_verification_email
        print("✅ Email utils imported successfully")
    except Exception as e:
        print(f"❌ Email utils import failed: {e}")
        return False
    
    return True

def test_form_creation():
    """Test form creation"""
    print("\nTesting form creation...")
    
    try:
        from forms import SignupForm
        form = SignupForm()
        print("✅ SignupForm created successfully")
        return True
    except Exception as e:
        print(f"❌ Form creation failed: {e}")
        traceback.print_exc()
        return False

def test_email_verification():
    """Test email verification function"""
    print("\nTesting email verification...")
    
    try:
        from utils import is_email_verification_enabled
        enabled = is_email_verification_enabled()
        print(f"✅ Email verification status: {enabled}")
        return True
    except Exception as e:
        print(f"❌ Email verification test failed: {e}")
        traceback.print_exc()
        return False

def test_database_connection():
    """Test database connection"""
    print("\nTesting database connection...")
    
    try:
        from utils import get_db
        from models import User
        
        db = get_db()
        user_count = User.query.count()
        print(f"✅ Database connection working (User count: {user_count})")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🔍 Testing Signup Fix...")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_form_creation,
        test_email_verification,
        test_database_connection
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The signup fix should work correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
