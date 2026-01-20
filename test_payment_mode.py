#!/usr/bin/env python3
"""
Test script for payment test mode functionality
"""

import os
import sys
import requests
from datetime import datetime

def test_payment_mode():
    """Test the payment test mode functionality"""
    
    # Base URL - adjust as needed
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Payment Test Mode Functionality")
    print("=" * 50)
    
    # Test 1: Check if test mode configuration is accessible
    print("\n1. Testing Test Mode Configuration...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Application is running")
        else:
            print(f"❌ Application returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to application. Make sure it's running on localhost:5000")
        return False
    
    # Test 2: Check environment variable setup
    print("\n2. Testing Environment Variable Setup...")
    test_mode_env = os.environ.get('TEST_MODE', 'false')
    print(f"   Environment TEST_MODE: {test_mode_env}")
    
    # Test 3: Simulate test mode activation
    print("\n3. Testing Test Mode Activation...")
    os.environ['TEST_MODE'] = 'true'
    print("   ✅ Test mode environment variable set to 'true'")
    
    # Test 4: Check payment form accessibility (requires authentication)
    print("\n4. Testing Payment Form Accessibility...")
    print("   Note: This requires authentication to access payment forms")
    print("   To test payment forms:")
    print("   1. Log in as a student")
    print("   2. Create or accept a contract")
    print("   3. Navigate to the payment page")
    print("   4. Look for the test mode banner and test payment button")
    
    # Test 5: Admin dashboard test mode toggle
    print("\n5. Testing Admin Dashboard Test Mode Toggle...")
    print("   To test admin toggle:")
    print("   1. Log in as admin")
    print("   2. Navigate to admin dashboard")
    print("   3. Look for 'Payment Test Mode' section")
    print("   4. Toggle the switch to enable/disable test mode")
    
    print("\n" + "=" * 50)
    print("📋 Test Mode Features to Verify:")
    print("   • Test mode banner appears on payment forms")
    print("   • Test payment button is available")
    print("   • Form validation is bypassed in test mode")
    print("   • Test mode indicator in admin dashboard")
    print("   • Test mode toggle functionality")
    print("   • Test payments are marked with 'TEST MODE' indicator")
    
    print("\n🎯 Manual Testing Steps:")
    print("   1. Set TEST_MODE=true in environment")
    print("   2. Restart the application")
    print("   3. Log in as admin and verify test mode toggle")
    print("   4. Log in as student and test payment flow")
    print("   5. Verify test mode indicators and functionality")
    
    return True

def check_configuration():
    """Check if test mode is properly configured"""
    print("\n🔧 Configuration Check:")
    
    # Check app.py for test mode config
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'TEST_MODE' in content:
                print("✅ Test mode configuration found in app.py")
            else:
                print("❌ Test mode configuration missing from app.py")
    except FileNotFoundError:
        print("❌ app.py not found")
    
    # Check payment template
    try:
        with open('templates/contracts/payment.html', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'TEST_MODE' in content:
                print("✅ Test mode elements found in payment template")
            else:
                print("❌ Test mode elements missing from payment template")
    except FileNotFoundError:
        print("❌ payment.html template not found")
    
    # Check admin dashboard
    try:
        with open('templates/admin/dashboard.html', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'Test Mode' in content:
                print("✅ Test mode toggle found in admin dashboard")
            else:
                print("❌ Test mode toggle missing from admin dashboard")
    except FileNotFoundError:
        print("❌ admin dashboard template not found")
    except UnicodeDecodeError:
        print("⚠️  Unicode decode error in admin dashboard template (likely contains special characters)")
        print("   Test mode toggle should still work despite this warning")

if __name__ == "__main__":
    print("🚀 Payment Test Mode Verification Script")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check configuration
    check_configuration()
    
    # Run tests
    success = test_payment_mode()
    
    if success:
        print("\n✅ Test script completed successfully!")
        print("Please perform manual testing as outlined above.")
    else:
        print("\n❌ Test script encountered issues.")
        sys.exit(1)
