#!/usr/bin/env python3
"""
Test template rendering to see what's actually being output.
"""

import sys
import os

def test_template_rendering():
    """Test if the meeting setup template renders correctly"""
    
    try:
        print("🔍 Testing Template Rendering...")
        
        from app import app
        from routes import meeting_setup
        from models import ScheduledSession
        
        with app.app_context():
            # Get the test session we created
            session = ScheduledSession.query.first()
            if not session:
                print("❌ No session found to test with")
                return False
            
            print(f"   Using session: ID={session.id}, Session ID={session.session_id}")
            
            # Test the template rendering directly
            from flask import render_template_string
            
            # Simple test template
            test_template = """
            <h1>Test Template</h1>
            <p>Session ID: {{ session.session_id }}</p>
            <p>Coach ID: {{ session.coach_id }}</p>
            <p>Student ID: {{ session.student_id }}</p>
            <p>Scheduled: {{ session.scheduled_at }}</p>
            """
            
            try:
                rendered = render_template_string(test_template, session=session)
                print("   ✅ Simple template renders successfully")
                print(f"   Rendered content: {rendered[:200]}...")
            except Exception as e:
                print(f"   ❌ Simple template failed: {e}")
                return False
            
            # Test the actual meeting setup template
            print("\n🔍 Testing Actual Meeting Setup Template...")
            
            try:
                from flask import render_template
                rendered = render_template('google_meet/meeting_setup.html', session=session)
                print("   ✅ Meeting setup template renders successfully")
                print(f"   Template length: {len(rendered)} characters")
                print(f"   First 200 chars: {rendered[:200]}...")
                
                # Check for key content
                if "Meeting Setup" in rendered:
                    print("   ✅ 'Meeting Setup' title found")
                else:
                    print("   ❌ 'Meeting Setup' title NOT found")
                
                if "Session Details" in rendered:
                    print("   ✅ 'Session Details' section found")
                else:
                    print("   ❌ 'Session Details' section NOT found")
                
                if "Create Google Meet" in rendered:
                    print("   ✅ 'Create Google Meet' button found")
                else:
                    print("   ❌ 'Create Google Meet' button NOT found")
                
                if str(session.id) in rendered:
                    print(f"   ✅ Session ID {session.id} found in template")
                else:
                    print(f"   ❌ Session ID {session.id} NOT found in template")
                    
            except Exception as e:
                print(f"   ❌ Meeting setup template failed: {e}")
                import traceback
                traceback.print_exc()
                return False
            
            # Test the actual route function
            print("\n🔍 Testing Route Function...")
            
            try:
                result = meeting_setup(session.session_id)
                print(f"   ✅ Route function executed successfully")
                print(f"   Result type: {type(result)}")
                
                if hasattr(result, 'data'):
                    print(f"   Response data length: {len(result.data)}")
                    print(f"   Response preview: {result.data[:300]}...")
                    
                    # Check if the response contains the expected content
                    if b"Meeting Setup" in result.data:
                        print("   ✅ 'Meeting Setup' found in response")
                    else:
                        print("   ❌ 'Meeting Setup' NOT found in response")
                        
                    if b"Session Details" in result.data:
                        print("   ✅ 'Session Details' found in response")
                    else:
                        print("   ❌ 'Session Details' NOT found in response")
                        
                else:
                    print(f"   Result: {result}")
                    
            except Exception as e:
                print(f"   ❌ Route function failed: {e}")
                import traceback
                traceback.print_exc()
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_browser_access():
    """Test if the route is accessible via browser"""
    
    try:
        print("\n🔍 Testing Browser Access...")
        
        from app import app
        
        with app.test_client() as client:
            # Test the meeting setup route
            test_session_id = 1  # This should match our test session
            
            print(f"   Testing route: /session/{test_session_id}/meeting-setup")
            
            try:
                response = client.get(f'/session/{test_session_id}/meeting-setup')
                print(f"   Status code: {response.status_code}")
                
                if response.status_code == 200:
                    print("   ✅ Route returns 200 OK")
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
                        
                    # Show first part of response
                    print(f"   Response preview: {response.data[:500]}...")
                    
                elif response.status_code == 302:
                    print("   ⚠️ Route returns 302 (redirect)")
                    print(f"   Redirect location: {response.location}")
                    
                else:
                    print(f"   ❌ Route returns unexpected status: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error accessing route: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing browser access: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Template Rendering Test")
    print("=" * 50)
    
    # Test template rendering
    if not test_template_rendering():
        print("\n❌ Template rendering test failed.")
        sys.exit(1)
    
    # Test browser access
    if not test_browser_access():
        print("\n❌ Browser access test failed.")
        sys.exit(1)
    
    print("\n🎉 All template tests completed!")
    print("Check the results above to see what's happening with the template rendering.")
