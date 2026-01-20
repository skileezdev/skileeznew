#!/usr/bin/env python3
"""
Deploy reschedule_status column fix to production database
This script adds the reschedule_status column to both Session and ScheduledSession tables
"""

import os
import sys
import logging
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def deploy_reschedule_status_fix():
    """Add reschedule_status column to production database"""
    try:
        from app import app, db
        
        with app.app_context():
            logger.info("🚀 Starting reschedule_status column deployment...")
            
            # Check if columns already exist
            try:
                # Test if reschedule_status column exists in session table
                db.engine.execute("SELECT reschedule_status FROM session LIMIT 1")
                logger.info("✅ reschedule_status column already exists in session table")
                session_exists = True
            except Exception:
                session_exists = False
                logger.info("❌ reschedule_status column missing in session table")
            
            try:
                # Test if reschedule_status column exists in scheduled_session table
                db.engine.execute("SELECT reschedule_status FROM scheduled_session LIMIT 1")
                logger.info("✅ reschedule_status column already exists in scheduled_session table")
                scheduled_session_exists = True
            except Exception:
                scheduled_session_exists = False
                logger.info("❌ reschedule_status column missing in scheduled_session table")
            
            # Add reschedule_status column to session table if missing
            if not session_exists:
                try:
                    logger.info("📝 Adding reschedule_status column to session table...")
                    db.engine.execute("ALTER TABLE session ADD COLUMN reschedule_status VARCHAR(20)")
                    logger.info("✅ Successfully added reschedule_status column to session table")
                except Exception as e:
                    logger.error(f"❌ Failed to add reschedule_status column to session table: {e}")
                    return False
            
            # Add reschedule_status column to scheduled_session table if missing
            if not scheduled_session_exists:
                try:
                    logger.info("📝 Adding reschedule_status column to scheduled_session table...")
                    db.engine.execute("ALTER TABLE scheduled_session ADD COLUMN reschedule_status VARCHAR(20)")
                    logger.info("✅ Successfully added reschedule_status column to scheduled_session table")
                except Exception as e:
                    logger.error(f"❌ Failed to add reschedule_status column to scheduled_session table: {e}")
                    return False
            
            # Commit all changes
            db.session.commit()
            logger.info("✅ Database migration completed successfully!")
            
            # Verify the columns exist
            try:
                db.engine.execute("SELECT reschedule_status FROM session LIMIT 1")
                db.engine.execute("SELECT reschedule_status FROM scheduled_session LIMIT 1")
                logger.info("✅ Verification successful - both columns exist and are accessible")
            except Exception as e:
                logger.error(f"❌ Verification failed: {e}")
                return False
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Deployment failed: {e}")
        return False

if __name__ == "__main__":
    success = deploy_reschedule_status_fix()
    if success:
        print("🎉 Reschedule status column deployment completed successfully!")
        sys.exit(0)
    else:
        print("💥 Reschedule status column deployment failed!")
        sys.exit(1)
