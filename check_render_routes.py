#!/usr/bin/env python3
"""
Check what routes are actually registered and accessible on the deployed app.
"""

import sys
import os
import requests

def check_render_routes():
    """Check what routes are accessible on the deployed app"""
    
    print("🔍 Checking Render Routes...")
    
    # Your deployed URL
    base_url = "https://skileez-prru.onrender.com"
    
    # Routes to test
    routes_to_test = [
        '/',
        '/login',
        '/dashboard',
        '/session/5/meeting-setup',  # The problematic route
        '/session/1/meeting-setup',  # Alternative session ID
        '/about',
        '/signup'
    ]
    
    print(f"   Testing routes on: {base_url}")
    print()
    
    for route in routes_to_test:
        full_url = base_url + route
        print(f"   Testing: {route}")
        
        try:
            response = requests.get(full_url, timeout=10)
            status = response.status_code
            
            if status == 200:
                print(f"      ✅ 200 OK - Route accessible")
            elif status == 302:
                print(f"      ⚠️ 302 Redirect - {response.headers.get('Location', 'Unknown')}")
            elif status == 404:
                print(f"      ❌ 404 Not Found - Route doesn't exist!")
            else:
                print(f"      ⚠️ {status} - Unexpected status")
                
        except requests.exceptions.RequestException as e:
            print(f"      ❌ Error: {e}")
        
        print()

def check_route_patterns():
    """Check if the route pattern is correct"""
    
    print("🔍 Checking Route Patterns...")
    
    # The URL you're trying to access
    problem_url = "/session/5/meeting-setup"
    
    print(f"   Problem URL: {problem_url}")
    print(f"   Route pattern: /session/<int:session_id>/meeting-setup")
    print()
    
    # Check if this matches our route definition
    print("   Route definition in routes.py:")
    print("   @app.route('/session/<int:session_id>/meeting-setup')")
    print()
    
    # Check if the route is being registered
    print("   Route registration in register_routes():")
    print("   app.add_url_rule('/session/<int:session_id>/meeting-setup', 'meeting_setup', meeting_setup, methods=['GET'])")
    print()
    
    # Check if there are any conflicting routes
    print("   Potential issues:")
    print("   1. Route not being registered on Render")
    print("   2. Route being overridden by another definition")
    print("   3. Import/registration order issue")
    print("   4. Environment-specific route loading")

def check_deployment_differences():
    """Check for differences between local and Render deployment"""
    
    print("🔍 Checking Deployment Differences...")
    
    print("   Local vs Render differences:")
    print("   1. Environment variables")
    print("   2. Database connections")
    print("   3. Route registration timing")
    print("   4. Import order")
    print("   5. Flask app initialization")
    print()
    
    print("   Common Render-specific issues:")
    print("   ❌ Routes not being imported")
    print("   ❌ Circular import problems")
    print("   ❌ Module loading order")
    print("   ❌ Environment variable differences")
    print("   ❌ Database connection timing")

def generate_debug_instructions():
    """Generate debugging instructions for Render"""
    
    print("🔧 Debug Instructions for Render:")
    print("=" * 50)
    
    print("1. Check Render Logs:")
    print("   - Go to your Render dashboard")
    print("   - Check the 'Logs' tab")
    print("   - Look for any import errors or route registration issues")
    print()
    
    print("2. Add Debug Logging:")
    print("   - Add print statements in register_routes()")
    print("   - Check if routes are being registered")
    print("   - Verify the meeting_setup route is added")
    print()
    
    print("3. Test Route Registration:")
    print("   - Add a simple test route")
    print("   - Check if it's accessible")
    print("   - Compare with working routes")
    print()
    
    print("4. Check Environment Variables:")
    print("   - Verify all required env vars are set")
    print("   - Check for any Render-specific config")
    print("   - Ensure database connections work")

if __name__ == "__main__":
    print("🚀 Render Route Checker")
    print("=" * 50)
    
    # Check routes on Render
    check_render_routes()
    
    # Check route patterns
    check_route_patterns()
    
    # Check deployment differences
    check_deployment_differences()
    
    # Generate debug instructions
    generate_debug_instructions()
    
    print("\n🎯 Next Steps:")
    print("1. Check Render logs for errors")
    print("2. Verify route registration is working")
    print("3. Test with a simple route first")
    print("4. Compare working vs non-working routes")
