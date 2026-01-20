#!/usr/bin/env python3
"""
Test Flask app context and route registration
"""
from app import app

def test_app_context():
    """Test Flask app context"""
    print("🧪 Testing Flask App Context...")
    print("="*50)
    
    with app.app_context():
        print("✅ App context created successfully")
        
        # Test route registration
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(rule.rule)
        
        print(f"✅ Number of routes in context: {len(routes)}")
        
        # Check for specific routes
        route_names = [rule.rule for rule in app.url_map.iter_rules()]
        
        important_routes = ['/', '/about', '/notifications', '/api/notifications']
        for route in important_routes:
            if route in route_names:
                print(f"✅ Route {route} is registered in context")
            else:
                print(f"❌ Route {route} is NOT registered in context")
        
        # Test route matching
        print("\n🔍 Testing route matching...")
        try:
            # Test root route
            adapter = app.url_map.bind('localhost')
            endpoint, values = adapter.match('/')
            print(f"✅ Root route (/) matches endpoint: {endpoint}")
        except Exception as e:
            print(f"❌ Root route matching failed: {e}")
        
        try:
            # Test about route
            adapter = app.url_map.bind('localhost')
            endpoint, values = adapter.match('/about')
            print(f"✅ About route (/about) matches endpoint: {endpoint}")
        except Exception as e:
            print(f"❌ About route matching failed: {e}")
        
        try:
            # Test notifications route
            adapter = app.url_map.bind('localhost')
            endpoint, values = adapter.match('/notifications')
            print(f"✅ Notifications route (/notifications) matches endpoint: {endpoint}")
        except Exception as e:
            print(f"❌ Notifications route matching failed: {e}")
    
    print("\n" + "="*50)
    print("🎉 App context test completed!")
    print("="*50)

if __name__ == "__main__":
    test_app_context()
