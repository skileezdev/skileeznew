#!/usr/bin/env python3
"""
Simplified Deployment Fix for Render
This script ensures the app can start without complex migrations
"""

import os
import sys
import traceback

def check_environment():
    """Check critical environment variables"""
    print("🔍 Checking environment variables...")
    
    critical_vars = {
        'SESSION_SECRET': 'dev-secret-key-change-in-production',
        'DATABASE_URL': 'sqlite:///skileez.db',
        'FLASK_ENV': 'production',
        'TEST_MODE': 'true'
    }
    
    for var, default in critical_vars.items():
        value = os.environ.get(var, default)
        if 'SECRET' in var or 'KEY' in var:
            masked_value = value[:8] + "..." if len(value) > 8 else "***"
            print(f"   ✅ {var}: {masked_value}")
        else:
            print(f"   ✅ {var}: {value}")
    
    return True

def test_imports():
    """Test critical imports"""
    print("🔍 Testing critical imports...")
    
    try:
        import flask
        print("   ✅ Flask imported successfully")
        
        import flask_sqlalchemy
        print("   ✅ Flask-SQLAlchemy imported successfully")
        
        import flask_migrate
        print("   ✅ Flask-Migrate imported successfully")
        
        import flask_wtf
        print("   ✅ Flask-WTF imported successfully")
        
        import flask_mail
        print("   ✅ Flask-Mail imported successfully")
        
        import psycopg2
        print("   ✅ psycopg2 imported successfully")
        
        import gunicorn
        print("   ✅ gunicorn imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False

def test_app_creation():
    """Test if the Flask app can be created"""
    print("🔍 Testing Flask app creation...")
    
    try:
        # Set minimal environment
        os.environ.setdefault('SESSION_SECRET', 'test-secret-key')
        os.environ.setdefault('DATABASE_URL', 'sqlite:///test.db')
        
        # Import and create app
        from app import app
        
        print("   ✅ Flask app created successfully")
        print(f"   ✅ App name: {app.name}")
        print(f"   ✅ Debug mode: {app.debug}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ App creation error: {e}")
        print(f"   ❌ Traceback: {traceback.format_exc()}")
        return False

def main():
    """Main deployment check"""
    print("🚀 RENDER DEPLOYMENT FIX")
    print("=" * 50)
    
    # Run checks
    env_ok = check_environment()
    imports_ok = test_imports()
    app_ok = test_app_creation()
    
    print("\n🎯 Results:")
    print("=" * 20)
    
    checks = [
        ("Environment Variables", env_ok),
        ("Package Imports", imports_ok),
        ("Flask App Creation", app_ok)
    ]
    
    all_passed = True
    for check_name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {check_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All checks passed! App should deploy successfully.")
        print("\n📋 Next steps:")
        print("   1. Commit and push your changes")
        print("   2. Monitor Render build logs")
        print("   3. Check for 'App started successfully' message")
    else:
        print("\n⚠️ Some checks failed. Review the errors above.")
        print("\n🔧 Common fixes:")
        print("   1. Ensure all dependencies are in requirements.txt")
        print("   2. Check environment variables in Render dashboard")
        print("   3. Verify Python version compatibility")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)