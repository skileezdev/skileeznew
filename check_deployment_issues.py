#!/usr/bin/env python3
"""
Check for common deployment issues that could cause authentication problems.
"""

import sys
import os

def check_environment_variables():
    """Check if critical environment variables are set"""
    
    print("🔍 Checking Environment Variables...")
    
    critical_vars = [
        'SESSION_SECRET',
        'DATABASE_URL',
        'FLASK_ENV',
        'FLASK_DEBUG'
    ]
    
    missing_vars = []
    for var in critical_vars:
        value = os.environ.get(var)
        if value:
            # Mask sensitive values
            if 'SECRET' in var or 'KEY' in var:
                masked_value = value[:8] + "..." if len(value) > 8 else "***"
                print(f"   ✅ {var}: {masked_value}")
            else:
                print(f"   ✅ {var}: {value}")
        else:
            print(f"   ❌ {var}: NOT SET")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️ Missing critical environment variables: {missing_vars}")
        print("   This could cause authentication and session issues!")
    else:
        print("\n✅ All critical environment variables are set")
    
    return len(missing_vars) == 0

def check_session_configuration():
    """Check Flask session configuration"""
    
    print("\n🔍 Checking Session Configuration...")
    
    try:
        from app import app
        
        # Check secret key
        secret_key = app.secret_key
        if secret_key and secret_key != "dev-secret-key-change-in-production":
            print(f"   ✅ Secret key is set (not default)")
        else:
            print(f"   ❌ Secret key is default or missing")
            print("   This will cause session management to fail!")
        
        # Check session configuration
        print(f"   Session type: {type(app.session_interface).__name__}")
        
        # Check if sessions are enabled
        if hasattr(app, 'session_interface'):
            print("   ✅ Session interface is configured")
        else:
            print("   ❌ No session interface configured")
            
    except Exception as e:
        print(f"   ❌ Error checking session config: {e}")
        return False
    
    return True

def check_database_connection():
    """Check database connection and session data"""
    
    print("\n🔍 Checking Database Connection...")
    
    try:
        from app import app, db
        
        with app.app_context():
            # Test database connection
            try:
                db.session.execute(db.text("SELECT 1"))
                print("   ✅ Database connection successful")
            except Exception as e:
                print(f"   ❌ Database connection failed: {e}")
                return False
            
            # Check if we can access user data
            from models import User, ScheduledSession
            
            user_count = User.query.count()
            print(f"   Users in database: {user_count}")
            
            session_count = ScheduledSession.query.count()
            print(f"   ScheduledSessions in database: {session_count}")
            
            if session_count == 0:
                print("   ⚠️ No sessions found - this could be the issue!")
                
    except Exception as e:
        print(f"   ❌ Error checking database: {e}")
        return False
    
    return True

def check_authentication_flow():
    """Test the authentication flow"""
    
    print("\n🔍 Testing Authentication Flow...")
    
    try:
        from app import app
        
        with app.test_client() as client:
            # Test login route
            response = client.get('/login')
            if response.status_code == 200:
                print("   ✅ Login route accessible")
            else:
                print(f"   ❌ Login route returned {response.status_code}")
            
            # Test dashboard route (should redirect to login)
            response = client.get('/dashboard')
            if response.status_code == 302:
                print("   ✅ Dashboard correctly redirects unauthenticated users")
            else:
                print(f"   ⚠️ Dashboard returned {response.status_code}")
                
    except Exception as e:
        print(f"   ❌ Error testing auth flow: {e}")
        return False
    
    return True

def check_session_storage():
    """Check if sessions are being stored properly"""
    
    print("\n🔍 Checking Session Storage...")
    
    try:
        from app import app
        
        with app.test_client() as client:
            # Test setting a session
            with client.session_transaction() as sess:
                sess['test_key'] = 'test_value'
                sess['user_id'] = 123
            
            # Test reading the session
            with client.session_transaction() as sess:
                test_value = sess.get('test_key')
                user_id = sess.get('user_id')
                
                if test_value == 'test_value' and user_id == 123:
                    print("   ✅ Session storage working correctly")
                else:
                    print(f"   ❌ Session storage failed")
                    print(f"      Expected: test_value, 123")
                    print(f"      Got: {test_value}, {user_id}")
                    
    except Exception as e:
        print(f"   ❌ Error testing session storage: {e}")
        return False
    
    return True

def generate_deployment_checklist():
    """Generate a deployment checklist"""
    
    print("\n📋 Deployment Checklist:")
    print("=" * 50)
    
    print("1. Environment Variables:")
    print("   ✅ SESSION_SECRET must be set (not default)")
    print("   ✅ DATABASE_URL must be correct")
    print("   ✅ FLASK_ENV should be 'production'")
    
    print("\n2. Session Configuration:")
    print("   ✅ Secret key must be unique and secure")
    print("   ✅ Session interface must be configured")
    print("   ✅ CSRF protection must be working")
    
    print("\n3. Database:")
    print("   ✅ Database must be accessible")
    print("   ✅ User tables must exist")
    print("   ✅ Session data must persist")
    
    print("\n4. Authentication:")
    print("   ✅ Login route must work")
    print("   ✅ Session cookies must be set")
    print("   ✅ @login_required must work")
    
    print("\n5. Common Issues:")
    print("   ❌ Missing SESSION_SECRET environment variable")
    print("   ❌ Default secret key in production")
    print("   ❌ Database connection failures")
    print("   ❌ Session cookie domain issues")
    print("   ❌ HTTPS/HTTP mixed content")

if __name__ == "__main__":
    print("🚀 Deployment Issue Checker")
    print("=" * 50)
    
    # Run all checks
    env_ok = check_environment_variables()
    session_ok = check_session_configuration()
    db_ok = check_database_connection()
    auth_ok = check_authentication_flow()
    storage_ok = check_session_storage()
    
    # Summary
    print("\n🎯 Summary:")
    print("=" * 30)
    
    checks = [
        ("Environment Variables", env_ok),
        ("Session Configuration", session_ok),
        ("Database Connection", db_ok),
        ("Authentication Flow", auth_ok),
        ("Session Storage", storage_ok)
    ]
    
    all_passed = True
    for check_name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {check_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All checks passed! The issue might be elsewhere.")
    else:
        print("\n⚠️ Some checks failed. This could explain the authentication issues.")
    
    # Generate checklist
    generate_deployment_checklist()
    
    print("\n💡 Next Steps:")
    if not env_ok:
        print("   1. Set SESSION_SECRET environment variable")
        print("   2. Ensure DATABASE_URL is correct")
    if not session_ok:
        print("   1. Check Flask session configuration")
        print("   2. Verify secret key is set")
    if not db_ok:
        print("   1. Check database connection")
        print("   2. Verify database schema")
