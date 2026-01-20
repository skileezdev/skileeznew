#!/usr/bin/env python3
"""
Debug script to troubleshoot payment test mode issues
"""

import os
import sys
from dotenv import load_dotenv

def debug_payment_test_mode():
    """Debug payment test mode configuration and potential issues"""
    
    print("🔍 Payment Test Mode Debug")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Check environment
    test_mode_env = os.environ.get('TEST_MODE', 'false')
    print(f"1. Environment TEST_MODE: {test_mode_env}")
    
    # Check .env file
    if os.path.exists('.env'):
        print("2. ✅ .env file exists")
        with open('.env', 'r') as f:
            content = f.read()
            if 'TEST_MODE=true' in content:
                print("   ✅ TEST_MODE=true found")
            else:
                print("   ❌ TEST_MODE=true not found")
    else:
        print("2. ❌ .env file missing")
    
    # Simulate app config
    test_mode_config = test_mode_env.lower() == 'true'
    print(f"3. App TEST_MODE config: {test_mode_config}")
    
    # Check potential issues
    print("\n🔍 Potential Issues:")
    
    if not test_mode_config:
        print("❌ Test mode not enabled - this is the main issue")
        print("   Solution: Ensure .env file contains TEST_MODE=true")
        return
    
    print("✅ Test mode is enabled")
    print("\n🔍 If you're not seeing test mode interface:")
    print("1. ❓ Did you restart the Flask app after creating .env?")
    print("   - Stop current app (Ctrl+C)")
    print("   - Run: python app.py")
    print()
    print("2. ❓ Are you on the correct payment page?")
    print("   - URL should be: /contracts/{id}/payment")
    print("   - Contract status should be 'accepted'")
    print()
    print("3. ❓ Browser cache issues?")
    print("   - Try hard refresh (Ctrl+F5)")
    print("   - Clear browser cache")
    print("   - Try incognito/private mode")
    print()
    print("4. ❓ JavaScript errors?")
    print("   - Open browser developer tools (F12)")
    print("   - Check Console tab for errors")
    print()
    print("5. ❓ Template rendering issues?")
    print("   - Check if config.TEST_MODE is being passed to template")
    print("   - Look for yellow banner and blue button")
    
    print("\n🔧 Quick Fix Steps:")
    print("1. Stop Flask app (Ctrl+C)")
    print("2. Run: python create_env_file.py")
    print("3. Run: python app.py")
    print("4. Navigate to contract payment page")
    print("5. Look for yellow 'Test Mode Active' banner")

def check_template_rendering():
    """Check if template would render test mode correctly"""
    
    print("\n📄 Template Rendering Check")
    print("=" * 30)
    
    # Simulate template logic
    test_mode = os.environ.get('TEST_MODE', 'false').lower() == 'true'
    
    print(f"config.TEST_MODE: {test_mode}")
    
    if test_mode:
        print("✅ Template should show:")
        print("   - Yellow 'Test Mode Active' banner")
        print("   - Blue 'Process Test Payment' button")
        print("   - test_mode=true in form")
    else:
        print("❌ Template will NOT show test mode elements")

if __name__ == "__main__":
    debug_payment_test_mode()
    check_template_rendering()
