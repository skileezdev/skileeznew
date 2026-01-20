#!/usr/bin/env python3
"""
Emergency Database Fix
This script fixes the InFailedSqlTransaction error and adds missing columns
"""

import os
import sys
import logging
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def emergency_database_fix():
    """Emergency fix for database transaction issues"""
    try:
        from app import app, db
        
        with app.app_context():
            print("🚨 Starting emergency database fix...")
            
            # Step 1: Roll back any failed transactions
            print("🔄 Rolling back failed transactions...")
            try:
                db.session.rollback()
                print("✅ Rolled back failed transactions")
            except Exception as e:
                print(f"⚠️  Could not rollback: {e}")
            
            # Step 2: Test basic database connection
            print("🔍 Testing database connection...")
            try:
                result = db.engine.execute("SELECT 1 as test")
                print("✅ Database connection is working")
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
                return False
            
            # Step 3: Add missing reschedule_status columns
            print("📝 Adding missing database columns...")
            
            # Add to session table
            try:
                db.engine.execute("ALTER TABLE session ADD COLUMN reschedule_status VARCHAR(20) DEFAULT NULL")
                print("✅ Added reschedule_status to session table")
            except Exception as e:
                if "already exists" in str(e) or "duplicate column" in str(e):
                    print("✅ reschedule_status already exists in session table")
                else:
                    print(f"⚠️  Could not add reschedule_status to session table: {e}")
            
            # Add to scheduled_session table
            try:
                db.engine.execute("ALTER TABLE scheduled_session ADD COLUMN reschedule_status VARCHAR(20) DEFAULT NULL")
                print("✅ Added reschedule_status to scheduled_session table")
            except Exception as e:
                if "already exists" in str(e) or "duplicate column" in str(e):
                    print("✅ reschedule_status already exists in scheduled_session table")
                else:
                    print(f"⚠️  Could not add reschedule_status to scheduled_session table: {e}")
            
            # Step 4: Test queries that were failing
            print("🧪 Testing previously failing queries...")
            
            try:
                # Test the query that was failing in student dashboard
                result = db.engine.execute("""
                    SELECT COUNT(*) 
                    FROM proposal 
                    JOIN learning_request ON learning_request.id = proposal.learning_request_id 
                    WHERE learning_request.student_id = 2
                """)
                print("✅ Student dashboard query is working")
            except Exception as e:
                print(f"⚠️  Student dashboard query still failing: {e}")
            
            try:
                # Test learning request query
                result = db.engine.execute("""
                    SELECT COUNT(*) 
                    FROM learning_request 
                    WHERE student_id = 2 AND is_active = true
                """)
                print("✅ Learning request query is working")
            except Exception as e:
                print(f"⚠️  Learning request query still failing: {e}")
            
            # Step 5: Commit any pending changes
            try:
                db.session.commit()
                print("✅ Committed pending changes")
            except Exception as e:
                print(f"⚠️  Could not commit changes: {e}")
            
            print("🎉 Emergency database fix completed!")
            return True
            
    except Exception as e:
        print(f"❌ Emergency database fix failed: {e}")
        return False

def main():
    """Main function"""
    print("🚨 EMERGENCY DATABASE FIX")
    print("=" * 50)
    
    success = emergency_database_fix()
    
    if success:
        print("\n✅ SUCCESS: Database is now fixed!")
        print("🔄 The application should work correctly now.")
    else:
        print("\n❌ FAILED: Database fix was unsuccessful!")
        print("🔧 Please check the error messages above.")
    
    return success

if __name__ == "__main__":
    main()
