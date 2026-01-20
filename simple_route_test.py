#!/usr/bin/env python3
"""
Simple test to check what the meeting setup route is actually returning.
"""

import sys
import os

def test_meeting_setup_route():
    """Test the meeting setup route directly"""
    
    try:
        print("🔍 Testing Meeting Setup Route...")
        
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

def test_template_file_exists():
    """Check if the template file actually exists and is readable"""
    
    try:
        print("\n🔍 Checking Template File...")
        
        template_path = "templates/google_meet/meeting_setup.html"
        
        if os.path.exists(template_path):
            print(f"   ✅ Template file exists: {template_path}")
            
            # Check file size
            file_size = os.path.getsize(template_path)
            print(f"   File size: {file_size} bytes")
            
            if file_size > 0:
                print("   ✅ Template file is not empty")
                
                # Read first few lines
                with open(template_path, 'r', encoding='utf-8') as f:
                    first_lines = f.readlines()[:5]
                    print("   First 5 lines:")
                    for i, line in enumerate(first_lines, 1):
                        print(f"     {i}: {line.strip()}")
                        
            else:
                print("   ❌ Template file is empty!")
                
        else:
            print(f"   ❌ Template file NOT found: {template_path}")
            
            # Check what's in the templates directory
            templates_dir = "templates"
            if os.path.exists(templates_dir):
                print(f"   Contents of {templates_dir}:")
                for item in os.listdir(templates_dir):
                    print(f"     - {item}")
                    
                google_meet_dir = os.path.join(templates_dir, "google_meet")
                if os.path.exists(google_meet_dir):
                    print(f"   Contents of {google_meet_dir}:")
                    for item in os.listdir(google_meet_dir):
                        print(f"     - {item}")
                        
        return True
        
    except Exception as e:
        print(f"❌ Error checking template file: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Simple Route Test")
    print("=" * 50)
    
    # Check template file
    if not test_template_file_exists():
        print("\n❌ Template file check failed.")
        sys.exit(1)
    
    # Test the route
    if not test_meeting_setup_route():
        print("\n❌ Route test failed.")
        sys.exit(1)
    
    print("\n🎉 All tests completed!")
    print("Check the results above to see what's happening with the meeting setup route.")
