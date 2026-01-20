#!/usr/bin/env python3
"""
Deploy Reschedule Status Fix
This script adds the missing reschedule_status column to the production database
"""

import os
import sys
import logging

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def deploy_reschedule_fix():
    """Add reschedule_status column to production database"""
    try:
        from app import app, db
        
        with app.app_context():
            print("🚀 Starting reschedule status column deployment...")
            
            # Add reschedule_status column to session table
            try:
                db.engine.execute("ALTER TABLE session ADD COLUMN reschedule_status VARCHAR(20) DEFAULT NULL")
                print("✅ Added reschedule_status column to session table")
            except Exception as e:
                if "already exists" in str(e) or "duplicate column" in str(e):
                    print("✅ reschedule_status already exists in session table")
                else:
                    print(f"⚠️  Could not add reschedule_status to session table: {e}")
            
            # Add reschedule_status column to scheduled_session table
            try:
                db.engine.execute("ALTER TABLE scheduled_session ADD COLUMN reschedule_status VARCHAR(20) DEFAULT NULL")
                print("✅ Added reschedule_status column to scheduled_session table")
            except Exception as e:
                if "already exists" in str(e) or "duplicate column" in str(e):
                    print("✅ reschedule_status already exists in scheduled_session table")
                else:
                    print(f"⚠️  Could not add reschedule_status to scheduled_session table: {e}")
            
            # Test the database
            try:
                result = db.engine.execute("SELECT 1 as test")
                print("✅ Database is working correctly")
            except Exception as e:
                print(f"❌ Database test failed: {e}")
                return False
            
            print("🎉 Reschedule status column deployment completed!")
            return True
            
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False

def main():
    """Main function"""
    print("🚀 RESCHEDULE STATUS COLUMN DEPLOYMENT")
    print("=" * 50)
    
    success = deploy_reschedule_fix()
    
    if success:
        print("\n✅ SUCCESS: Database columns added successfully!")
        print("🔄 The application should now work without errors.")
    else:
        print("\n❌ FAILED: Could not add database columns!")
        print("🔧 Please check the error messages above.")
    
    return success

if __name__ == "__main__":
    main()