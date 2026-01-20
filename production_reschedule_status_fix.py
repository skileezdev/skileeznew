#!/usr/bin/env python3
"""
Production Database Migration: Add reschedule_status column
This script safely adds the reschedule_status column to both Session and ScheduledSession tables
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

def check_column_exists(engine, table_name, column_name):
    """Check if a column exists in a table"""
    try:
        # For PostgreSQL
        result = engine.execute(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}' AND column_name = '{column_name}'
        """)
        return result.fetchone() is not None
    except Exception as e:
        logger.error(f"Error checking column {column_name} in {table_name}: {e}")
        return False

def add_column_safely(engine, table_name, column_name, column_definition):
    """Safely add a column to a table if it doesn't exist"""
    try:
        if not check_column_exists(engine, table_name, column_name):
            logger.info(f"Adding {column_name} column to {table_name} table...")
            engine.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}")
            logger.info(f"✅ Successfully added {column_name} column to {table_name} table")
            return True
        else:
            logger.info(f"✅ {column_name} column already exists in {table_name} table")
            return True
    except Exception as e:
        logger.error(f"❌ Failed to add {column_name} column to {table_name} table: {e}")
        return False

def deploy_reschedule_status_fix():
    """Deploy reschedule_status column fix to production database"""
    try:
        from app import app, db
        
        with app.app_context():
            logger.info("🚀 Starting reschedule_status column deployment...")
            logger.info(f"Database URL: {app.config.get('DATABASE_URL', 'Not set')}")
            
            # Get database engine
            engine = db.engine
            
            # Add reschedule_status column to session table
            session_success = add_column_safely(
                engine, 
                'session', 
                'reschedule_status', 
                'VARCHAR(20) DEFAULT NULL'
            )
            
            # Add reschedule_status column to scheduled_session table
            scheduled_session_success = add_column_safely(
                engine, 
                'scheduled_session', 
                'reschedule_status', 
                'VARCHAR(20) DEFAULT NULL'
            )
            
            if session_success and scheduled_session_success:
                logger.info("✅ All database migrations completed successfully!")
                
                # Verify the columns exist and are accessible
                try:
                    logger.info("🔍 Verifying column accessibility...")
                    engine.execute("SELECT reschedule_status FROM session LIMIT 1")
                    engine.execute("SELECT reschedule_status FROM scheduled_session LIMIT 1")
                    logger.info("✅ Verification successful - both columns exist and are accessible")
                    return True
                except Exception as e:
                    logger.error(f"❌ Verification failed: {e}")
                    return False
            else:
                logger.error("❌ Some migrations failed")
                return False
            
    except Exception as e:
        logger.error(f"❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔄 Starting reschedule_status column deployment...")
    success = deploy_reschedule_status_fix()
    if success:
        print("🎉 Reschedule status column deployment completed successfully!")
        print("✅ The application should now work without database errors")
        sys.exit(0)
    else:
        print("💥 Reschedule status column deployment failed!")
        print("❌ Please check the logs and try again")
        sys.exit(1)
