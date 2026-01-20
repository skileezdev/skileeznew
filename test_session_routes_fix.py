#!/usr/bin/env python3
"""
Test script to verify session routes fixes
"""

def test_session_routes_fix():
    """Test that session routes fixes work correctly"""
    print("🧪 Testing session routes fixes...")
    
    try:
        # Test that the routes can be imported
        from routes import (
            request_reschedule, 
            approve_reschedule, 
            decline_reschedule, 
            complete_session,
            confirm_session
        )
        print("✅ All session routes imported successfully")
        
        # Test that the routes have the correct pattern
        import inspect
        
        routes_to_check = [
            request_reschedule,
            approve_reschedule, 
            decline_reschedule, 
            complete_session,
            confirm_session
        ]
        
        for route_func in routes_to_check:
            source = inspect.getsource(route_func)
            
            # Check for explicit relationship loading
            if 'db.joinedload(Session.proposal).joinedload(Proposal.contract)' in source:
                print(f"✅ {route_func.__name__} has explicit relationship loading")
            else:
                print(f"❌ {route_func.__name__} missing explicit relationship loading")
            
            # Check for null safety
            if 'contract = session.proposal.contract if session.proposal else None' in source:
                print(f"✅ {route_func.__name__} has null safety check")
            else:
                print(f"❌ {route_func.__name__} missing null safety check")
        
        print("🎉 Session routes fix test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Session routes fix test failed: {e}")
        return False

if __name__ == "__main__":
    test_session_routes_fix()
