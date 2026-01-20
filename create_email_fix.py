#!/usr/bin/env python3
"""
Force Email Verification Fix
This script creates a simple fix to ensure email verification works
"""

def create_simple_email_fix():
    """Create a simple email verification fix"""
    
    print("🔧 Creating simple email verification fix...")
    
    # Create a simple test script
    test_script = '''#!/usr/bin/env python3
"""
Simple Email Verification Test
"""

import os
import sys

# Set environment variables
os.environ['ENABLE_EMAIL_VERIFICATION'] = 'true'
os.environ['MAIL_SERVER'] = 'smtp.gmail.com'
os.environ['MAIL_USERNAME'] = 'skileezverf@gmail.com'
os.environ['MAIL_PASSWORD'] = 'wghd tnjr kbda mjie'
os.environ['SESSION_SECRET'] = 'test-secret-key'
os.environ['DATABASE_URL'] = 'sqlite:///test.db'

def test_email_verification():
    """Test email verification"""
    try:
        from app import app
        
        with app.app_context():
            print("🔍 Testing email verification...")
            
            # Test configuration
            print(f"ENABLE_EMAIL_VERIFICATION: {app.config.get('ENABLE_EMAIL_VERIFICATION')}")
            print(f"MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
            print(f"MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")
            print(f"MAIL_PASSWORD: {'SET' if app.config.get('MAIL_PASSWORD') else 'NOT SET'}")
            
            # Test function
            from utils import is_email_verification_enabled
            result = is_email_verification_enabled()
            print(f"is_email_verification_enabled(): {result}")
            
            return result
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    result = test_email_verification()
    print(f"\\nResult: {'SUCCESS' if result else 'FAILED'}")
    sys.exit(0 if result else 1)
'''
    
    with open('simple_email_test.py', 'w') as f:
        f.write(test_script)
    
    print("✅ Created simple_email_test.py")
    
    # Create a fix for the utils.py function
    fix_script = '''
# TEMPORARY FIX FOR EMAIL VERIFICATION
# Add this to the top of your signup route to force email verification

def force_email_verification_enabled():
    """Force email verification to be enabled"""
    return True

# Replace the email verification check in your signup route with:
email_verification_enabled = force_email_verification_enabled()
'''
    
    with open('email_verification_fix.txt', 'w') as f:
        f.write(fix_script)
    
    print("✅ Created email_verification_fix.txt")
    
    print("\\n🎯 NEXT STEPS:")
    print("1. Run: python simple_email_test.py")
    print("2. Check the output to see what's wrong")
    print("3. If it fails, use the temporary fix in email_verification_fix.txt")

if __name__ == "__main__":
    create_simple_email_fix()
