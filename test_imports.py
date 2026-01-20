#!/usr/bin/env python3
"""
Test all imports to ensure deployment will work
"""

import sys
import os

def test_imports():
    """Test all critical imports"""
    print("Testing imports...")
    
    try:
        # Test basic Flask imports
        from flask import Flask
        print("✅ Flask imported successfully")
        
        # Test forms import (this was the failing one)
        from forms import RoleSwitchForm
        print("✅ Forms imported successfully")
        
        # Test models import
        from models import User
        print("✅ Models imported successfully")
        
        # Test utils import
        from utils import get_available_timezones
        print("✅ Utils imported successfully")
        
        # Test scheduling imports
        from scheduling_utils import get_scheduling_options
        print("✅ Scheduling utils imported successfully")
        
        # Test notification imports
        from notification_utils import create_system_notification
        print("✅ Notification utils imported successfully")
        
        # Test email imports
        from email_utils import send_email
        print("✅ Email utils imported successfully")
        
            # Video functionality has been removed from this application
    print("✅ Video functionality has been removed from this application")
        
        # Test schedule import
        import schedule
        print("✅ Schedule imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_app_creation():
    """Test that the Flask app can be created"""
    print("\nTesting Flask app creation...")
    
    try:
        from app import app
        print("✅ Flask app created successfully")
        return True
    except Exception as e:
        print(f"❌ Flask app creation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing imports for deployment...")
    print("=" * 50)
    
    imports_ok = test_imports()
    app_ok = test_app_creation()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"   App Creation: {'✅ PASS' if app_ok else '❌ FAIL'}")
    
    if imports_ok and app_ok:
        print("\n🎉 All tests passed! Deployment should work.")
        return 0
    else:
        print("\n❌ Some tests failed. Please fix before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
