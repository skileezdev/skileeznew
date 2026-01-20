#!/usr/bin/env python3
"""
Test deployment configuration
This script tests the key components of the scheduling system
"""

import os
import sys

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import flask
        print("✅ Flask imported successfully")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    try:
        import sqlalchemy
        print("✅ SQLAlchemy imported successfully")
    except ImportError as e:
        print(f"❌ SQLAlchemy import failed: {e}")
        return False
    
    # Video functionality has been removed from this application
    print("✅ Video functionality has been removed from this application")
    
    try:
        import schedule
        print("✅ Schedule imported successfully")
    except ImportError as e:
        print(f"❌ Schedule import failed: {e}")
        return False
    
    return True

def test_environment():
    """Test environment variables"""
    print("\nTesting environment variables...")
    
    required_vars = [
        'DATABASE_URL',
        'FLASK_ENV',
        'SESSION_SECRET'
    ]
    
    optional_vars = [
            # Video functionality has been removed from this application
        'STRIPE_SECRET_KEY',
        'MAIL_USERNAME'
    ]
    
    all_good = True
    
    for var in required_vars:
        if os.environ.get(var):
            print(f"✅ {var} is set")
        else:
            print(f"❌ {var} is missing (required)")
            all_good = False
    
    for var in optional_vars:
        if os.environ.get(var):
            print(f"✅ {var} is set")
        else:
            print(f"⚠️  {var} is not set (optional)")
    
    return all_good

def test_video_config():
    """Video functionality has been removed from this application"""
    print("\nVideo functionality has been removed from this application")
    
    # Video functionality has been removed from this application
    
    print("✅ Video functionality has been removed from this application")
    return True

def main():
    """Run all tests"""
    print("🚀 Testing deployment configuration...")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_imports()
    
    # Test environment
    env_ok = test_environment()
    
    # Test video functionality
    video_ok = test_video_config()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"   Environment: {'✅ PASS' if env_ok else '❌ FAIL'}")
    print(f"   Video: {'✅ REMOVED'}")
    
    if imports_ok and env_ok:
        print("\n🎉 All critical tests passed! Deployment should work.")
        return 0
    else:
        print("\n❌ Some critical tests failed. Please fix before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
