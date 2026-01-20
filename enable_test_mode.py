#!/usr/bin/env python3
"""
Quick script to enable test mode and verify it's working
"""

import os
import sys

def enable_test_mode():
    """Enable test mode and provide instructions"""
    
    print("🧪 Payment Test Mode Enabler")
    print("=" * 40)
    
    # Set environment variable
    os.environ['TEST_MODE'] = 'true'
    
    print("✅ Test mode environment variable set to 'true'")
    print()
    print("📋 Next Steps:")
    print("1. Restart your Flask application:")
    print("   - Stop the current app (Ctrl+C)")
    print("   - Run: python app.py")
    print()
    print("2. Verify test mode is active:")
    print("   - Log in as admin")
    print("   - Go to admin dashboard")
    print("   - Look for 'Payment Test Mode' section")
    print("   - Should show 'ON' status")
    print()
    print("3. Test payment flow:")
    print("   - Log in as student")
    print("   - Navigate to a contract payment page")
    print("   - Should see yellow 'Test Mode Active' banner")
    print("   - Should see blue 'Process Test Payment' button")
    print()
    print("🔧 If test mode still doesn't work:")
    print("   - Check that you restarted the application")
    print("   - Verify TEST_MODE=true in your environment")
    print("   - Check browser console for JavaScript errors")
    print("   - Clear browser cache")
    
    return True

def check_test_mode():
    """Check if test mode is currently enabled"""
    
    test_mode = os.environ.get('TEST_MODE', 'false')
    print(f"Current TEST_MODE setting: {test_mode}")
    
    if test_mode.lower() == 'true':
        print("✅ Test mode is enabled")
        return True
    else:
        print("❌ Test mode is disabled")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        check_test_mode()
    else:
        enable_test_mode()
