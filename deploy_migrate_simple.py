#!/usr/bin/env python3
"""
Simple migration runner for contract system
This script applies the migration manually without Alembic
"""

import os
import sys
import logging
from app import app, db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_learning_request_columns():
    """Add new columns to learning_request table"""
    try:
        with app.app_context():
            logger.info("🔧 Adding columns to learning_request table...")
            
            # Check if columns already exist
            inspector = db.inspect(db.engine)
            existing_columns = [col['name'] for col in inspector.get_columns('learning_request')]
            
            columns_to_add = [
                ('preferred_times', 'TEXT'),
                ('sessions_needed', 'INTEGER'),
                ('timeframe', 'VARCHAR(100)'),
                ('skill_tags', 'TEXT')
            ]
            
            for col_name, col_type in columns_to_add:
                if col_name not in existing_columns:
                    logger.info(f"➕ Adding column: {col_name}")
                    db.session.execute(db.text(f"ALTER TABLE learning_request ADD COLUMN {col_name} {col_type}"))
                else:
                    logger.info(f"✅ Column {col_name} already exists")
            
            db.session.commit()
            logger.info("✅ Learning request columns updated")
            return True
            
    except Exception as e:
        logger.error(f"❌ Failed to add learning request columns: {e}")
        db.session.rollback()
        return False

def add_proposal_columns():
    """Add new columns to proposal table"""
    try:
        with app.app_context():
            logger.info("🔧 Adding columns to proposal table...")
            
            # Check if columns already exist
            inspector = db.inspect(db.engine)
            existing_columns = [col['name'] for col in inspector.get_columns('proposal')]
            
            columns_to_add = [
                ('accepted_at', 'TIMESTAMP'),
                ('accepted_terms', 'TEXT'),
                ('availability_match', 'BOOLEAN DEFAULT FALSE'),
                ('approach_summary', 'TEXT'),
                ('answers', 'TEXT'),
                ('payment_model', 'VARCHAR(20) DEFAULT \'per_session\''),
                ('hourly_rate', 'FLOAT')
            ]
            
            for col_name, col_type in columns_to_add:
                if col_name not in existing_columns:
                    logger.info(f"➕ Adding column: {col_name}")
                    db.session.execute(db.text(f"ALTER TABLE proposal ADD COLUMN {col_name} {col_type}"))
                else:
                    logger.info(f"✅ Column {col_name} already exists")
            
            db.session.commit()
            logger.info("✅ Proposal columns updated")
            return True
            
    except Exception as e:
        logger.error(f"❌ Failed to add proposal columns: {e}")
        db.session.rollback()
        return False

def add_session_columns():
    """Add new columns to session table"""
    try:
        with app.app_context():
            logger.info("🔧 Adding columns to session table...")
            
            # Check if columns already exist
            inspector = db.inspect(db.engine)
            existing_columns = [col['name'] for col in inspector.get_columns('session')]
            
            columns_to_add = [
                ('scheduled_at', 'TIMESTAMP'),
                ('duration_minutes', 'INTEGER'),
                ('timezone', 'VARCHAR(50) DEFAULT \'UTC\''),
                ('reschedule_requested', 'BOOLEAN DEFAULT FALSE'),
                ('reschedule_requested_by', 'VARCHAR(20)'),
                ('reschedule_reason', 'TEXT'),
                ('reschedule_deadline', 'TIMESTAMP'),
                ('confirmed_by_coach', 'BOOLEAN DEFAULT FALSE')
            ]
            
            for col_name, col_type in columns_to_add:
                if col_name not in existing_columns:
                    logger.info(f"➕ Adding column: {col_name}")
                    db.session.execute(db.text(f"ALTER TABLE session ADD COLUMN {col_name} {col_type}"))
                else:
                    logger.info(f"✅ Column {col_name} already exists")
            
            db.session.commit()
            logger.info("✅ Session columns updated")
            return True
            
    except Exception as e:
        logger.error(f"❌ Failed to add session columns: {e}")
        db.session.rollback()
        return False

def create_contract_table():
    """Create contract table"""
    try:
        with app.app_context():
            logger.info("🔧 Creating contract table...")
            
            # Check if table already exists
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            if 'contract' in existing_tables:
                logger.info("✅ Contract table already exists")
                return True
            
            # Create contract table
            contract_sql = """
            CREATE TABLE contract (
                id SERIAL PRIMARY KEY,
                proposal_id INTEGER NOT NULL REFERENCES proposal(id),
                student_id INTEGER NOT NULL REFERENCES user(id),
                coach_id INTEGER NOT NULL REFERENCES user(id),
                contract_number VARCHAR(50) UNIQUE NOT NULL,
                status VARCHAR(20) DEFAULT 'active',
                start_date DATE NOT NULL,
                end_date DATE,
                total_sessions INTEGER NOT NULL,
                completed_sessions INTEGER DEFAULT 0,
                total_amount NUMERIC(10,2) NOT NULL,
                paid_amount NUMERIC(10,2) DEFAULT 0.00,
                payment_model VARCHAR(20) NOT NULL,
                rate NUMERIC(10,2) NOT NULL,
                timezone VARCHAR(50) DEFAULT 'UTC',
                cancellation_policy TEXT,
                learning_outcomes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            db.session.execute(db.text(contract_sql))
            db.session.commit()
            logger.info("✅ Contract table created")
            return True
            
    except Exception as e:
        logger.error(f"❌ Failed to create contract table: {e}")
        db.session.rollback()
        return False

def create_session_payment_table():
    """Create session_payment table"""
    try:
        with app.app_context():
            logger.info("🔧 Creating session_payment table...")
            
            # Check if table already exists
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            if 'session_payment' in existing_tables:
                logger.info("✅ Session payment table already exists")
                return True
            
            # Create session_payment table
            payment_sql = """
            CREATE TABLE session_payment (
                id SERIAL PRIMARY KEY,
                session_id INTEGER NOT NULL REFERENCES session(id),
                contract_id INTEGER NOT NULL REFERENCES contract(id),
                amount NUMERIC(10,2) NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                stripe_payment_intent_id VARCHAR(255),
                stripe_transfer_id VARCHAR(255),
                paid_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            db.session.execute(db.text(payment_sql))
            db.session.commit()
            logger.info("✅ Session payment table created")
            return True
            
    except Exception as e:
        logger.error(f"❌ Failed to create session payment table: {e}")
        db.session.rollback()
        return False

def add_stripe_columns():
    """Add Stripe columns to existing tables"""
    try:
        with app.app_context():
            logger.info("🔧 Adding Stripe columns...")
            
            # Add stripe_customer_id to user table
            try:
                db.session.execute(db.text("ALTER TABLE \"user\" ADD COLUMN stripe_customer_id VARCHAR(255)"))
                logger.info("✅ Added column: user.stripe_customer_id")
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info("✅ Column user.stripe_customer_id already exists")
                else:
                    logger.warning(f"⚠️ Could not add user.stripe_customer_id: {e}")
            
            # Add stripe_account_id to coach_profile table
            try:
                db.session.execute(db.text("ALTER TABLE coach_profile ADD COLUMN stripe_account_id VARCHAR(255)"))
                logger.info("✅ Added column: coach_profile.stripe_account_id")
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info("✅ Column coach_profile.stripe_account_id already exists")
                else:
                    logger.warning(f"⚠️ Could not add coach_profile.stripe_account_id: {e}")
            
            db.session.commit()
            logger.info("✅ Stripe columns added")
            return True
            
    except Exception as e:
        logger.error(f"❌ Failed to add Stripe columns: {e}")
        db.session.rollback()
        return False

def add_contract_payment_fields():
    """Add payment fields to contract table"""
    try:
        with app.app_context():
            logger.info("🔧 Adding contract payment fields...")
            
            # Add payment_status to contract table
            try:
                db.session.execute(db.text("ALTER TABLE contract ADD COLUMN payment_status VARCHAR(20) NOT NULL DEFAULT 'pending'"))
                logger.info("✅ Added column: contract.payment_status")
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info("✅ Column contract.payment_status already exists")
                else:
                    logger.warning(f"⚠️ Could not add contract.payment_status: {e}")
            
            # Add stripe_payment_intent_id to contract table
            try:
                db.session.execute(db.text("ALTER TABLE contract ADD COLUMN stripe_payment_intent_id VARCHAR(255)"))
                logger.info("✅ Added column: contract.stripe_payment_intent_id")
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info("✅ Column contract.stripe_payment_intent_id already exists")
                else:
                    logger.warning(f"⚠️ Could not add contract.stripe_payment_intent_id: {e}")
            
            # Add payment_date to contract table
            try:
                db.session.execute(db.text("ALTER TABLE contract ADD COLUMN payment_date TIMESTAMP"))
                logger.info("✅ Added column: contract.payment_date")
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info("✅ Column contract.payment_date already exists")
                else:
                    logger.warning(f"⚠️ Could not add contract.payment_date: {e}")
            
            db.session.commit()
            logger.info("✅ Contract payment fields added")
            return True
            
    except Exception as e:
        logger.error(f"❌ Failed to add contract payment fields: {e}")
        db.session.rollback()
        return False

def create_indexes():
    """Create indexes for better performance"""
    try:
        with app.app_context():
            logger.info("🔧 Creating indexes...")
            
            indexes = [
                "CREATE INDEX IF NOT EXISTS ix_contract_contract_number ON contract(contract_number)",
                "CREATE INDEX IF NOT EXISTS ix_contract_status ON contract(status)",
                "CREATE INDEX IF NOT EXISTS ix_contract_student_id ON contract(student_id)",
                "CREATE INDEX IF NOT EXISTS ix_contract_coach_id ON contract(coach_id)",
                "CREATE INDEX IF NOT EXISTS ix_contract_payment_status ON contract(payment_status)",
                "CREATE INDEX IF NOT EXISTS ix_contract_stripe_payment_intent_id ON contract(stripe_payment_intent_id)",
                "CREATE INDEX IF NOT EXISTS ix_session_payment_status ON session_payment(status)",
                "CREATE INDEX IF NOT EXISTS ix_session_payment_contract_id ON session_payment(contract_id)",
                "CREATE UNIQUE INDEX IF NOT EXISTS ix_user_stripe_customer_id ON \"user\"(stripe_customer_id)",
                "CREATE UNIQUE INDEX IF NOT EXISTS ix_coach_profile_stripe_account_id ON coach_profile(stripe_account_id)"
            ]
            
            for index_sql in indexes:
                try:
                    db.session.execute(db.text(index_sql))
                    logger.info(f"✅ Index created: {index_sql.split('ON')[1].strip()}")
                except Exception as e:
                    logger.warning(f"⚠️ Index creation warning: {e}")
            
            db.session.commit()
            logger.info("✅ Indexes created")
            return True
            
    except Exception as e:
        logger.error(f"❌ Failed to create indexes: {e}")
        db.session.rollback()
        return False

def verify_migration():
    """Verify that all tables and columns were created correctly"""
    try:
        with app.app_context():
            logger.info("🔍 Verifying migration...")
            
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            required_tables = ['contract', 'session_payment']
            for table in required_tables:
                if table in tables:
                    logger.info(f"✅ {table} table exists")
                else:
                    logger.error(f"❌ {table} table missing")
                    return False
            
            # Check learning_request columns
            learning_request_columns = [col['name'] for col in inspector.get_columns('learning_request')]
            required_columns = ['preferred_times', 'sessions_needed', 'timeframe', 'skill_tags']
            for col in required_columns:
                if col in learning_request_columns:
                    logger.info(f"✅ learning_request.{col} column exists")
                else:
                    logger.error(f"❌ learning_request.{col} column missing")
                    return False
            
            logger.info("✅ Migration verification passed")
            return True
            
    except Exception as e:
        logger.error(f"❌ Migration verification failed: {e}")
        return False

def main():
    """Main migration function"""
    logger.info("🚀 Starting contract system migration...")
    
    # Check if we're in production (Render)
    is_production = os.environ.get('RENDER', False)
    if is_production:
        logger.info("🏭 Running in production environment (Render)")
    else:
        logger.info("🛠️ Running in development environment")
    
    # Test database connection
    try:
        with app.app_context():
            db.session.execute(db.text("SELECT 1"))
            db.session.commit()
            logger.info("✅ Database connection successful")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        sys.exit(1)
    
    # Apply migrations
    migrations = [
        ("Learning Request Columns", add_learning_request_columns),
        ("Proposal Columns", add_proposal_columns),
        ("Session Columns", add_session_columns),
        ("Contract Table", create_contract_table),
        ("Session Payment Table", create_session_payment_table),
        ("Stripe Columns", add_stripe_columns),
        ("Contract Payment Fields", add_contract_payment_fields),
        ("Indexes", create_indexes)
    ]
    
    for migration_name, migration_func in migrations:
        logger.info(f"🔄 Running migration: {migration_name}")
        if migration_func():
            logger.info(f"✅ {migration_name} completed")
        else:
            logger.error(f"❌ {migration_name} failed")
            sys.exit(1)
    
    # Verify migration
    if verify_migration():
        logger.info("🎉 Migration completed successfully!")
        logger.info("📋 Contract system is now ready to use")
    else:
        logger.error("❌ Migration verification failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 