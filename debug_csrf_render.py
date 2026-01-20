#!/usr/bin/env python3
"""
Debug CSRF token generation issues on Render deployment
"""

import requests
import json

def test_csrf_token_generation():
    """Test if CSRF tokens are being generated on Render"""
    
    base_url = "https://skileez-prru.onrender.com"
    
    print("🔍 Testing CSRF token generation on Render...")
    print("=" * 60)
    
    # Test 1: Check if the meeting setup page loads
    print("1️⃣ Testing meeting setup page load...")
    try:
        # First, we need to get a session cookie by visiting the main page
        session = requests.Session()
        
        # Visit main page to get session cookie
        main_response = session.get(f"{base_url}/")
        print(f"   Main page status: {main_response.status_code}")
        
        if main_response.status_code == 200:
            print("   ✅ Main page loaded successfully")
            
            # Check if we have session cookies
            cookies = session.cookies
            print(f"   Session cookies: {dict(cookies)}")
            
            # Now try to access the meeting setup page
            meeting_url = f"{base_url}/session/1/meeting-setup"
            meeting_response = session.get(meeting_url)
            
            print(f"   Meeting setup status: {meeting_response.status_code}")
            
            if meeting_response.status_code == 200:
                print("   ✅ Meeting setup page loaded")
                
                # Check if CSRF token is in the HTML
                html_content = meeting_response.text
                if 'csrf_token' in html_content:
                    print("   ✅ CSRF token found in HTML")
                    
                    # Look for the actual token value
                    if 'name="csrf_token"' in html_content:
                        print("   ✅ CSRF token input field found")
                        
                        # Extract the token value
                        import re
                        token_match = re.search(r'name="csrf_token"\s+value="([^"]+)"', html_content)
                        if token_match:
                            token = token_match.group(1)
                            print(f"   ✅ CSRF token value: {token[:20]}...")
                            
                            # Test form submission with the token
                            print("\n2️⃣ Testing form submission with CSRF token...")
                            
                            form_data = {
                                'csrf_token': token,
                                'meeting_url': 'https://meet.google.com/test-123',
                                'meeting_notes': 'Test meeting'
                            }
                            
                            submit_response = session.post(
                                f"{base_url}/session/1/save-meeting-link",
                                data=form_data
                            )
                            
                            print(f"   Form submission status: {submit_response.status_code}")
                            
                            if submit_response.status_code == 200:
                                print("   ✅ Form submission successful!")
                                return True
                            elif submit_response.status_code == 302:
                                print("   ✅ Form submission redirected (likely success)")
                                return True
                            else:
                                print(f"   ❌ Form submission failed: {submit_response.text[:200]}...")
                                return False
                        else:
                            print("   ❌ CSRF token value not found in HTML")
                            return False
                    else:
                        print("   ❌ CSRF token input field not found")
                        return False
                else:
                    print("   ❌ CSRF token not found in HTML")
                    print(f"   HTML preview: {html_content[:500]}...")
                    return False
            else:
                print(f"   ❌ Meeting setup page failed: {meeting_response.status_code}")
                print(f"   Response: {meeting_response.text[:200]}...")
                return False
        else:
            print(f"   ❌ Main page failed: {main_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error during testing: {e}")
        return False

def check_environment_variables():
    """Check if critical environment variables are set on Render"""
    
    print("\n3️⃣ Checking environment variables...")
    print("=" * 60)
    
    # These are the critical variables for CSRF to work
    critical_vars = [
        'SESSION_SECRET',
        'SECRET_KEY', 
        'FLASK_SECRET_KEY'
    ]
    
    print("   Note: Environment variables are not accessible from client side")
    print("   You need to check these in your Render dashboard:")
    
    for var in critical_vars:
        print(f"   🔑 {var}")
    
    print("\n   To check in Render:")
    print("   1. Go to your Render dashboard")
    print("   2. Click on your service")
    print("   3. Go to 'Environment' tab")
    print("   4. Verify these variables are set")
    
    return True

def main():
    """Main diagnostic function"""
    
    print("🚀 CSRF Token Generation Diagnostic for Render")
    print("=" * 60)
    
    # Test CSRF token generation
    csrf_working = test_csrf_token_generation()
    
    # Check environment variables
    check_environment_variables()
    
    print("\n" + "=" * 60)
    if csrf_working:
        print("✅ CSRF tokens are working properly!")
        print("   The issue might be resolved.")
    else:
        print("❌ CSRF tokens are not working.")
        print("   Check the environment variables above.")
    
    print("\n🔧 Next Steps:")
    if not csrf_working:
        print("   1. Verify SESSION_SECRET is set in Render")
        print("   2. Ensure it's a strong, unique value")
        print("   3. Redeploy after setting variables")
    else:
        print("   1. CSRF protection is working")
        print("   2. Forms should submit successfully")
        print("   3. Security is properly maintained")

if __name__ == "__main__":
    main()
