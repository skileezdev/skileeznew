#!/usr/bin/env python3
"""
Fix Database Transaction Issue
This script resolves the InFailedSqlTransaction error by rolling back failed transactions
and ensuring the database is in a clean state.
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

def fix_database_transaction():
    """Fix database transaction issues and add missing columns"""
    try:
        from app import app, db
        
        with app.app_context():
            logger.info("🔄 Starting database transaction fix...")
            
            # Roll back any failed transactions
            try:
                db.session.rollback()
                logger.info("✅ Rolled back failed transactions")
            except Exception as e:
                logger.warning(f"⚠️  Could not rollback: {e}")
            
            # Test database connection
            try:
                db.engine.execute("SELECT 1")
                logger.info("✅ Database connection is working")
            except Exception as e:
                logger.error(f"❌ Database connection failed: {e}")
                return False
            
            # Add missing reschedule_status columns
            try:
                # Check if reschedule_status column exists in session table
                result = db.engine.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'session' AND column_name = 'reschedule_status'
                """)
                
                if not result.fetchone():
                    logger.info("📝 Adding reschedule_status column to session table...")
                    db.engine.execute("ALTER TABLE session ADD COLUMN reschedule_status VARCHAR(20) DEFAULT NULL")
                    logger.info("✅ Added reschedule_status to session table")
                else:
                    logger.info("✅ reschedule_status already exists in session table")
                    
            except Exception as e:
                logger.error(f"❌ Failed to add reschedule_status to session table: {e}")
            
            try:
                # Check if reschedule_status column exists in scheduled_session table
                result = db.engine.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'scheduled_session' AND column_name = 'reschedule_status'
                """)
                
                if not result.fetchone():
                    logger.info("📝 Adding reschedule_status column to scheduled_session table...")
                    db.engine.execute("ALTER TABLE scheduled_session ADD COLUMN reschedule_status VARCHAR(20) DEFAULT NULL")
                    logger.info("✅ Added reschedule_status to scheduled_session table")
                else:
                    logger.info("✅ reschedule_status already exists in scheduled_session table")
                    
            except Exception as e:
                logger.error(f"❌ Failed to add reschedule_status to scheduled_session table: {e}")
            
            # Test a simple query to ensure everything is working
            try:
                result = db.engine.execute("SELECT COUNT(*) FROM session LIMIT 1")
                logger.info("✅ Database queries are working correctly")
            except Exception as e:
                logger.error(f"❌ Database queries still failing: {e}")
                return False
            
            logger.info("🎉 Database transaction fix completed successfully!")
            return True
            
    except Exception as e:
        logger.error(f"❌ Failed to fix database transaction: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Starting database transaction fix...")
    
    success = fix_database_transaction()
    
    if success:
        print("✅ Database transaction fix completed successfully!")
        print("🔄 The application should now work correctly.")
    else:
        print("❌ Database transaction fix failed!")
        print("🔧 Please check the logs and try again.")
    
    return success

if __name__ == "__main__":
    main()
