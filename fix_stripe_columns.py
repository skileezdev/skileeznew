#!/usr/bin/env python3
"""
Quick fix script to add missing Stripe columns to production database
Run this manually on Render to fix the immediate database issue
"""

import os
import sys
import logging
from app import app, db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_stripe_columns():
    """Add missing Stripe columns to existing tables"""
    try:
        with app.app_context():
            logger.info("🔧 Adding missing Stripe columns to production database...")
            
            # Check if we're in production
            is_production = os.environ.get('RENDER', False)
            if is_production:
                logger.info("🏭 Running in production environment (Render)")
            else:
                logger.info("🛠️ Running in development environment")
            
            # Test database connection
            db.session.execute(db.text("SELECT 1"))
            db.session.commit()
            logger.info("✅ Database connection successful")
            
            # Add stripe_customer_id to user table
            logger.info("🔧 Adding stripe_customer_id to user table...")
            try:
                db.session.execute(db.text("ALTER TABLE \"user\" ADD COLUMN stripe_customer_id VARCHAR(255)"))
                db.session.commit()
                logger.info("✅ Added column: user.stripe_customer_id")
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info("✅ Column user.stripe_customer_id already exists")
                else:
                    logger.warning(f"⚠️ Could not add user.stripe_customer_id: {e}")
            
            # Add stripe_account_id to coach_profile table
            logger.info("🔧 Adding stripe_account_id to coach_profile table...")
            try:
                db.session.execute(db.text("ALTER TABLE coach_profile ADD COLUMN stripe_account_id VARCHAR(255)"))
                db.session.commit()
                logger.info("✅ Added column: coach_profile.stripe_account_id")
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info("✅ Column coach_profile.stripe_account_id already exists")
                else:
                    logger.warning(f"⚠️ Could not add coach_profile.stripe_account_id: {e}")
            
            # Create indexes for better performance
            logger.info("🔧 Creating Stripe indexes...")
            
            # Index for user.stripe_customer_id
            try:
                db.session.execute(db.text("CREATE UNIQUE INDEX IF NOT EXISTS ix_user_stripe_customer_id ON \"user\" (stripe_customer_id)"))
                db.session.commit()
                logger.info("✅ Created index: ix_user_stripe_customer_id")
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info("✅ Index ix_user_stripe_customer_id already exists")
                else:
                    logger.warning(f"⚠️ Could not create index ix_user_stripe_customer_id: {e}")
            
            # Index for coach_profile.stripe_account_id
            try:
                db.session.execute(db.text("CREATE UNIQUE INDEX IF NOT EXISTS ix_coach_profile_stripe_account_id ON coach_profile (stripe_account_id)"))
                db.session.commit()
                logger.info("✅ Created index: ix_coach_profile_stripe_account_id")
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info("✅ Index ix_coach_profile_stripe_account_id already exists")
                else:
                    logger.warning(f"⚠️ Could not create index ix_coach_profile_stripe_account_id: {e}")
            
            logger.info("🎉 Stripe columns fix completed successfully!")
            logger.info("📋 Your application should now work without errors")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Stripe columns fix failed: {e}")
        db.session.rollback()
        return False

if __name__ == "__main__":
    success = add_stripe_columns()
    if success:
        logger.info("✅ Stripe columns fix completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Stripe columns fix failed!")
        sys.exit(1)
