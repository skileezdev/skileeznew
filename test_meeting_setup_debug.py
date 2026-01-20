#!/usr/bin/env python3
"""
Debug script to test meeting setup functionality and database queries.
"""

import sys
import os

def test_database_queries():
    """Test database queries to see what's happening"""
    
    try:
        print("🔍 Testing Database Queries...")
        
        # Import the app and models
        from app import app, db
        from models import ScheduledSession, Session, User
        
        with app.app_context():
            print("\n1️⃣ Checking ScheduledSession table...")
            
            # Check if ScheduledSession table has data
            scheduled_sessions = ScheduledSession.query.all()
            print(f"   Total ScheduledSession records: {len(scheduled_sessions)}")
            
            if scheduled_sessions:
                for ss in scheduled_sessions[:3]:  # Show first 3
                    print(f"   - ID: {ss.id}, Session ID: {ss.session_id}, Coach: {ss.coach_id}, Student: {ss.student_id}")
            else:
                print("   ❌ No ScheduledSession records found!")
                
            print("\n2️⃣ Checking Session table...")
            
            # Check if Session table has data
            sessions = Session.query.all()
            print(f"   Total Session records: {len(sessions)}")
            
            if sessions:
                for s in sessions[:3]:  # Show first 3
                    print(f"   - ID: {s.id}, Type: {getattr(s, 'session_type', 'N/A')}")
            else:
                print("   ❌ No Session records found!")
                
            print("\n3️⃣ Checking User table...")
            
            # Check if User table has data
            users = User.query.all()
            print(f"   Total User records: {len(users)}")
            
            if users:
                for u in users[:3]:  # Show first 3
                    print(f"   - ID: {u.id}, Email: {u.email}, Role: {getattr(u, 'current_role', 'N/A')}")
            else:
                print("   ❌ No User records found!")
                
            print("\n4️⃣ Testing specific query...")
            
            # Test the specific query that was failing
            test_session_id = 123  # This is what the URL was trying to access
            print(f"   Testing query for session_id = {test_session_id}")
            
            try:
                result = ScheduledSession.query.filter_by(session_id=test_session_id).first()
                if result:
                    print(f"   ✅ Found ScheduledSession: ID={result.id}, Session ID={result.session_id}")
                else:
                    print(f"   ❌ No ScheduledSession found with session_id = {test_session_id}")
                    
                    # Let's see what session_ids actually exist
                    existing_session_ids = db.session.query(ScheduledSession.session_id).distinct().all()
                    if existing_session_ids:
                        print(f"   Available session_ids: {[sid[0] for sid in existing_session_ids]}")
                    else:
                        print("   No session_ids found in ScheduledSession table")
                        
            except Exception as e:
                print(f"   ❌ Error querying: {e}")
                
            print("\n5️⃣ Testing URL pattern...")
            print("   The URL /session/123/meeting-setup should:")
            print("   - Find ScheduledSession where session_id = 123")
            print("   - Not find ScheduledSession where id = 123")
            
            # Test both queries
            by_session_id = ScheduledSession.query.filter_by(session_id=test_session_id).first()
            by_id = ScheduledSession.query.get(test_session_id)
            
            print(f"   Query by session_id = {test_session_id}: {'✅ Found' if by_session_id else '❌ Not found'}")
            print(f"   Query by id = {test_session_id}: {'✅ Found' if by_id else '❌ Not found'}")
            
            if by_session_id:
                print(f"   Found record: ID={by_session_id.id}, Session ID={by_session_id.session_id}")
                
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_route_function():
    """Test the actual meeting_setup function"""
    
    try:
        print("\n🔍 Testing Meeting Setup Function...")
        
        from app import app
        from routes import meeting_setup
        
        with app.app_context():
            # Test with a session_id that should exist
            test_session_id = 1  # Try with ID 1
            
            print(f"   Testing meeting_setup function with session_id = {test_session_id}")
            
            try:
                # This will call the actual function
                result = meeting_setup(test_session_id)
                print(f"   ✅ Function executed successfully")
                print(f"   Result type: {type(result)}")
                
                if hasattr(result, 'status_code'):
                    print(f"   Status code: {result.status_code}")
                else:
                    print(f"   Result: {result}")
                    
            except Exception as e:
                print(f"   ❌ Function failed: {e}")
                import traceback
                traceback.print_exc()
                
    except Exception as e:
        print(f"❌ Error testing function: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Meeting Setup Debug Test")
    print("=" * 50)
    
    # Test 1: Database queries
    if not test_database_queries():
        print("\n❌ Database query test failed.")
        sys.exit(1)
    
    # Test 2: Route function
    if not test_route_function():
        print("\n❌ Route function test failed.")
        sys.exit(1)
    
    print("\n🎉 All debug tests completed!")
    print("Check the results above to see what's happening with the database and routes.")
