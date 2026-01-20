#!/usr/bin/env python3
"""
Test the meeting setup route with an authenticated user.
"""

import sys
import os

def test_authenticated_route():
    """Test the meeting setup route with authentication"""
    
    try:
        print("🔍 Testing Authenticated Meeting Setup Route...")
        
        from app import app, db
        from models import User, ScheduledSession
        
        with app.test_client() as client:
            # First, get a coach user
            with app.app_context():
                coach = User.query.filter_by(is_coach=True).first()
                if not coach:
                    print("❌ No coach found in database")
                    return False
                
                print(f"   Using coach: {coach.email} (ID: {coach.id})")
                
                # Get the test session
                session = ScheduledSession.query.first()
                if not session:
                    print("❌ No session found in database")
                    return False
                
                print(f"   Using session: ID={session.id}, Session ID={session.session_id}")
            
            # Simulate login by setting session data
            with client.session_transaction() as sess:
                sess['user_id'] = coach.id
                sess['csrf_token'] = 'test_token'
            
            print(f"   Set session user_id to {coach.id}")
            
            # Now test the route
            test_session_id = session.session_id
            print(f"   Testing route: /session/{test_session_id}/meeting-setup")
            
            try:
                response = client.get(f'/session/{test_session_id}/meeting-setup')
                print(f"   Status code: {response.status_code}")
                
                if response.status_code == 200:
                    print("   ✅ Route returns 200 OK - User is authenticated!")
                    print(f"   Response length: {len(response.data)} characters")
                    
                    # Check response content
                    if b"Meeting Setup" in response.data:
                        print("   ✅ 'Meeting Setup' found in response")
                    else:
                        print("   ❌ 'Meeting Setup' NOT found in response")
                        
                    if b"Session Details" in response.data:
                        print("   ✅ 'Session Details' found in response")
                    else:
                        print("   ❌ 'Session Details' NOT found in response")
                        
                    if b"Create Google Meet" in response.data:
                        print("   ✅ 'Create Google Meet' button found in response")
                    else:
                        print("   ❌ 'Create Google Meet' button NOT found in response")
                        
                    # Show first part of response
                    print(f"\n   Response preview (first 500 chars):")
                    print(f"   {response.data[:500].decode('utf-8')}")
                    
                    # Check if it's HTML
                    if b"<!DOCTYPE html>" in response.data or b"<html" in response.data:
                        print("   ✅ Response contains HTML")
                    else:
                        print("   ❌ Response does NOT contain HTML")
                        
                    # Check if it extends base template
                    if b"extends" in response.data:
                        print("   ✅ Template inheritance detected")
                    else:
                        print("   ❌ No template inheritance detected")
                        
                elif response.status_code == 302:
                    print("   ⚠️ Route returns 302 (redirect)")
                    print(f"   Redirect location: {response.location}")
                    
                    if '/login' in response.location:
                        print("   ❌ Still redirecting to login - authentication issue")
                    else:
                        print(f"   ⚠️ Redirecting to: {response.location}")
                        
                elif response.status_code == 404:
                    print("   ❌ Route returns 404 (not found)")
                    
                else:
                    print(f"   ❌ Route returns unexpected status: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error accessing route: {e}")
                import traceback
                traceback.print_exc()
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Authenticated Route Test")
    print("=" * 50)
    
    # Test the authenticated route
    if not test_authenticated_route():
        print("\n❌ Authenticated route test failed.")
        sys.exit(1)
    
    print("\n🎉 Test completed!")
    print("Check the results above to see if the route works when authenticated.")
