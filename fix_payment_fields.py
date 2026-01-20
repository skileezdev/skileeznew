#!/usr/bin/env python3
"""
Quick fix script to add payment fields with correct PostgreSQL data types
"""

import os
import sys
from app import app, db
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_payment_fields():
    """Fix payment fields with correct PostgreSQL data types"""
    try:
        with app.app_context():
            logger.info("🔧 Fixing contract payment fields...")
            
            # Check if payment_status column exists
            try:
                result = db.session.execute(db.text("SELECT column_name FROM information_schema.columns WHERE table_name = 'contract' AND column_name = 'payment_status'"))
                if not result.fetchone():
                    # Add payment_status column
                    db.session.execute(db.text("ALTER TABLE contract ADD COLUMN payment_status VARCHAR(20) NOT NULL DEFAULT 'pending'"))
                    logger.info("✅ Added column: contract.payment_status")
                else:
                    logger.info("✅ Column contract.payment_status already exists")
            except Exception as e:
                logger.warning(f"⚠️ Could not add contract.payment_status: {e}")
            
            # Check if stripe_payment_intent_id column exists
            try:
                result = db.session.execute(db.text("SELECT column_name FROM information_schema.columns WHERE table_name = 'contract' AND column_name = 'stripe_payment_intent_id'"))
                if not result.fetchone():
                    # Add stripe_payment_intent_id column
                    db.session.execute(db.text("ALTER TABLE contract ADD COLUMN stripe_payment_intent_id VARCHAR(255)"))
                    logger.info("✅ Added column: contract.stripe_payment_intent_id")
                else:
                    logger.info("✅ Column contract.stripe_payment_intent_id already exists")
            except Exception as e:
                logger.warning(f"⚠️ Could not add contract.stripe_payment_intent_id: {e}")
            
            # Check if payment_date column exists
            try:
                result = db.session.execute(db.text("SELECT column_name FROM information_schema.columns WHERE table_name = 'contract' AND column_name = 'payment_date'"))
                if not result.fetchone():
                    # Add payment_date column with correct PostgreSQL type
                    db.session.execute(db.text("ALTER TABLE contract ADD COLUMN payment_date TIMESTAMP"))
                    logger.info("✅ Added column: contract.payment_date")
                else:
                    logger.info("✅ Column contract.payment_date already exists")
            except Exception as e:
                logger.warning(f"⚠️ Could not add contract.payment_date: {e}")
            
            db.session.commit()
            logger.info("✅ Contract payment fields fixed")
            
            # Create indexes
            logger.info("🔧 Creating payment indexes...")
            
            indexes = [
                "CREATE INDEX IF NOT EXISTS ix_contract_payment_status ON contract(payment_status)",
                "CREATE INDEX IF NOT EXISTS ix_contract_stripe_payment_intent_id ON contract(stripe_payment_intent_id)"
            ]
            
            for index_sql in indexes:
                try:
                    db.session.execute(db.text(index_sql))
                    logger.info(f"✅ Index created: {index_sql.split('ON')[1].strip()}")
                except Exception as e:
                    logger.warning(f"⚠️ Index creation warning: {e}")
            
            db.session.commit()
            logger.info("✅ Payment indexes created")
            return True
            
    except Exception as e:
        logger.error(f"❌ Failed to fix payment fields: {e}")
        db.session.rollback()
        return False

def main():
    """Main function"""
    logger.info("🚀 Starting payment fields fix...")
    
    # Test database connection
    try:
        with app.app_context():
            db.session.execute(db.text("SELECT 1"))
            db.session.commit()
            logger.info("✅ Database connection successful")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        sys.exit(1)
    
    # Fix payment fields
    if fix_payment_fields():
        logger.info("🎉 Payment fields fix completed successfully!")
    else:
        logger.error("❌ Payment fields fix failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
