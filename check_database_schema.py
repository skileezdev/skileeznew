#!/usr/bin/env python3
"""
Check database schema and existing data to understand what's available.
"""

import sys
import os

def check_database_schema():
    """Check what tables exist and their structure"""
    
    try:
        print("🔍 Checking Database Schema...")
        
        from app import app, db
        
        with app.app_context():
            # Get database inspector
            inspector = db.inspect(db.engine)
            table_names = inspector.get_table_names()
            
            print(f"\n📋 Available Tables: {len(table_names)}")
            for table in sorted(table_names):
                print(f"   - {table}")
            
            print("\n🔍 Checking Session-related Tables...")
            
            # Check session-related tables
            session_tables = [t for t in table_names if 'session' in t.lower()]
            print(f"   Session-related tables: {session_tables}")
            
            for table in session_tables:
                print(f"\n📊 Table: {table}")
                try:
                    # Get column info
                    columns = inspector.get_columns(table)
                    print(f"   Columns ({len(columns)}):")
                    for col in columns:
                        print(f"     - {col['name']}: {col['type']}")
                    
                    # Check row count
                    result = db.session.execute(db.text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"   Row count: {count}")
                    
                    if count > 0:
                        # Show sample data
                        result = db.session.execute(db.text(f"SELECT * FROM {table} LIMIT 1"))
                        row = result.fetchone()
                        if row:
                            print(f"   Sample row: {dict(row._mapping)}")
                            
                except Exception as e:
                    print(f"   ❌ Error checking table {table}: {e}")
            
            print("\n🔍 Checking User and Coach Tables...")
            
            # Check user-related tables
            user_tables = [t for t in table_names if 'user' in t.lower() or 'coach' in t.lower()]
            print(f"   User-related tables: {user_tables}")
            
            for table in user_tables:
                try:
                    result = db.session.execute(db.text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"   {table}: {count} rows")
                except Exception as e:
                    print(f"   ❌ Error checking {table}: {e}")
            
            print("\n🔍 Checking Contract Tables...")
            
            # Check contract-related tables
            contract_tables = [t for t in table_names if 'contract' in t.lower()]
            print(f"   Contract-related tables: {contract_tables}")
            
            for table in contract_tables:
                try:
                    result = db.session.execute(db.text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"   {table}: {count} rows")
                except Exception as e:
                    print(f"   ❌ Error checking {table}: {e}")
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def check_available_routes():
    """Check what routes are actually working"""
    
    try:
        print("\n🔍 Checking Available Routes...")
        
        from app import app
        
        with app.test_client() as client:
            # Test basic routes
            routes_to_test = [
                '/',
                '/dashboard',
                '/login',
                '/test-route'
            ]
            
            for route in routes_to_test:
                try:
                    response = client.get(route)
                    print(f"   {route}: {response.status_code}")
                except Exception as e:
                    print(f"   {route}: ❌ Error - {e}")
                    
    except Exception as e:
        print(f"❌ Error checking routes: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Database Schema Check")
    print("=" * 50)
    
    # Check database schema
    if not check_database_schema():
        print("\n❌ Database schema check failed.")
        sys.exit(1)
    
    # Check available routes
    if not check_available_routes():
        print("\n❌ Route check failed.")
        sys.exit(1)
    
    print("\n🎉 Database check completed!")
    print("Check the results above to see what's available in your database.")
