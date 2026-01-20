#!/usr/bin/env python3
"""
Reset migration state to fix duplicate revision issues
"""

import os
import sys
import logging
from flask_migrate import stamp
from app import app, db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_migration_state():
    """Reset the migration state to fix duplicate revision issues"""
    try:
        with app.app_context():
            logger.info("🔄 Resetting migration state...")
            
            # Drop the alembic_version table if it exists
            try:
                db.session.execute(db.text("DROP TABLE IF EXISTS alembic_version"))
                db.session.commit()
                logger.info("✅ Dropped alembic_version table")
            except Exception as e:
                logger.warning(f"⚠️ Could not drop alembic_version table: {e}")
            
            # Stamp the database with the latest revision
            stamp()
            logger.info("✅ Database stamped with latest revision")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Failed to reset migration state: {e}")
        return False

def main():
    """Main function"""
    logger.info("🚀 Starting migration reset...")
    
    # Check if we're in production (Render)
    is_production = os.environ.get('RENDER', False)
    if is_production:
        logger.info("🏭 Running in production environment (Render)")
    else:
        logger.info("🛠️ Running in development environment")
    
    # Reset migration state
    if reset_migration_state():
        logger.info("🎉 Migration reset completed successfully!")
    else:
        logger.error("❌ Migration reset failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
