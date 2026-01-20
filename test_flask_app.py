#!/usr/bin/env python3
"""
Test script to check if Flask app is working properly
"""
from app import app

def test_flask_app():
    """Test if Flask app is working"""
    print("🧪 Testing Flask App...")
    print("="*50)
    
    # Test 1: Check if app exists
    print(f"✅ Flask app exists: {app is not None}")
    
    # Test 2: Check app name
    print(f"✅ App name: {app.name}")
    
    # Test 3: Check if routes are registered
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(rule.rule)
    
    print(f"✅ Number of routes registered: {len(routes)}")
    
    # Test 4: Check for specific routes
    route_names = [rule.rule for rule in app.url_map.iter_rules()]
    
    important_routes = ['/', '/about', '/notifications', '/api/notifications']
    for route in important_routes:
        if route in route_names:
            print(f"✅ Route {route} is registered")
        else:
            print(f"❌ Route {route} is NOT registered")
    
    # Test 5: Show first 10 routes
    print(f"\n📝 First 10 routes:")
    for i, route in enumerate(routes[:10]):
        print(f"   {i+1}. {route}")
    
    print("\n" + "="*50)
    print("🎉 Flask app test completed!")
    print("="*50)

if __name__ == "__main__":
    test_flask_app()
