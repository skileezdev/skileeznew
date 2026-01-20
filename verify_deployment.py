#!/usr/bin/env python3
"""
Deployment verification script
This script verifies that the application is ready for deployment
"""

import sys
import os

def verify_dependencies():
    """Verify that all required dependencies are available"""
    print("🔍 Verifying dependencies...")
    
    required_packages = [
        'flask',
        'sqlalchemy', 
        'jinja2',
        'pytz',
        'jwt',
        'stripe',
        'requests',
        'schedule',
        # 'livekit' - Video functionality has been removed from this application
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        return False
    
    print("✅ All dependencies available")
    return True

def verify_environment():
    """Verify that required environment variables are set"""
    print("\n🔍 Verifying environment variables...")
    
    required_vars = [
        'DATABASE_URL',
        'FLASK_ENV',
        'SESSION_SECRET'
    ]
    
    optional_vars = [
                # LiveKit environment variables removed - video functionality no longer available
        'STRIPE_SECRET_KEY',
        'MAIL_USERNAME'
    ]
    
    missing_required = []
    missing_optional = []
    
    for var in required_vars:
        if os.environ.get(var):
            print(f"✅ {var}")
        else:
            print(f"❌ {var} (required)")
            missing_required.append(var)
    
    for var in optional_vars:
        if os.environ.get(var):
            print(f"✅ {var}")
        else:
            print(f"⚠️  {var} (optional)")
            missing_optional.append(var)
    
    if missing_required:
        print(f"\n❌ Missing required environment variables: {', '.join(missing_required)}")
        return False
    
    print("✅ Environment variables configured")
    return True

def verify_app_imports():
    """Verify that the Flask app can be imported"""
    print("\n🔍 Verifying app imports...")
    
    try:
        from app import app
        print("✅ Flask app imported successfully")
        
        # Test basic app functionality
        with app.app_context():
            print("✅ App context created successfully")
        
        return True
    except Exception as e:
        print(f"❌ App import failed: {e}")
        return False

def main():
    """Run all verification checks"""
    print("🚀 Deployment Verification")
    print("=" * 50)
    
    deps_ok = verify_dependencies()
    env_ok = verify_environment()
    app_ok = verify_app_imports()
    
    print("\n" + "=" * 50)
    print("📊 Verification Results:")
    print(f"   Dependencies: {'✅ PASS' if deps_ok else '❌ FAIL'}")
    print(f"   Environment: {'✅ PASS' if env_ok else '❌ FAIL'}")
    print(f"   App Import: {'✅ PASS' if app_ok else '❌ FAIL'}")
    
    if deps_ok and env_ok and app_ok:
        print("\n🎉 Deployment verification passed!")
        print("✅ Application is ready for deployment")
        return 0
    else:
        print("\n❌ Deployment verification failed!")
        print("❌ Please fix issues before deploying")
        return 1

if __name__ == "__main__":
    sys.exit(main())
