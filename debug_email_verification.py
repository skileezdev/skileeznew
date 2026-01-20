#!/usr/bin/env python3
"""
Debug Email Verification Issue
"""

import os
import sys

def debug_email_verification():
    """Debug why email verification is not working"""
    print("🔍 DEBUGGING EMAIL VERIFICATION ISSUE")
    print("=" * 50)
    
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
            print("📧 MAIL CONFIGURATION:")
            print(f"   MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
            print(f"   MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")
            print(f"   MAIL_PASSWORD: {'***' if app.config.get('MAIL_PASSWORD') else 'NOT SET'}")
            print(f"   ENABLE_EMAIL_VERIFICATION: {app.config.get('ENABLE_EMAIL_VERIFICATION')}")
            
            print("\n🔍 TESTING EMAIL VERIFICATION FUNCTION:")
            
            # Test the function step by step
            from utils import is_email_verification_enabled
            
            print("   Step 1: Getting app config...")
            enabled = app.config.get('ENABLE_EMAIL_VERIFICATION', True)
            print(f"   ENABLE_EMAIL_VERIFICATION from config: {enabled}")
            
            print("   Step 2: Checking mail server...")
            mail_server = app.config.get('MAIL_SERVER')
            print(f"   MAIL_SERVER from config: {mail_server}")
            
            print("   Step 3: Testing is_email_verification_enabled()...")
            result = is_email_verification_enabled()
            print(f"   Function result: {result}")
            
            print("\n🔍 TESTING EMAIL SENDING:")
            try:
                from email_utils import send_verification_email
                from models import User
                
                # Create a test user
                test_user = User(
                    first_name="Test",
                    last_name="User", 
                    email="test@example.com",
                    email_verified=False
                )
                
                print("   Attempting to send verification email...")
                email_result = send_verification_email(test_user)
                print(f"   Email send result: {email_result}")
                
            except Exception as e:
                print(f"   Email sending error: {e}")
                import traceback
                print(f"   Traceback: {traceback.format_exc()}")
            
            return result
            
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    """Main debug function"""
    result = debug_email_verification()
    
    print("\n🎯 SUMMARY:")
    print("=" * 20)
    
    if result:
        print("✅ Email verification should be working!")
        print("\n🔧 If it's still not working, check:")
        print("   1. Environment variables in Render dashboard")
        print("   2. Gmail app password is correct")
        print("   3. Check Render logs for email sending errors")
    else:
        print("❌ Email verification is disabled!")
        print("\n🔧 Fixes:")
        print("   1. Set ENABLE_EMAIL_VERIFICATION=true in Render")
        print("   2. Ensure MAIL_SERVER is configured")
        print("   3. Check MAIL_USERNAME and MAIL_PASSWORD")

if __name__ == "__main__":
    debug_email_verification()
