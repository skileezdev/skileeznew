#!/usr/bin/env python3
"""
PostgreSQL Database Recovery Script for Skileez
Fixes transaction issues and adds missing columns for PostgreSQL
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def reset_postgresql_connection():
    """Completely reset PostgreSQL connection to clear failed transactions"""
    try:
        from app import app, db
        
        with app.app_context():
            print("🔧 Resetting PostgreSQL connection...")
            
            # Force close all connections
            try:
                db.session.close()
                db.engine.dispose()
                print("✅ Closed all database connections")
            except Exception as e:
                print(f"⚠️ Connection close warning: {e}")
            
            # Wait a moment for connections to fully close
            import time
            time.sleep(1)
            
            # Test new connection
            try:
                db.session.execute(db.text("SELECT 1"))
                db.session.commit()
                print("✅ New database connection established")
                return True
            except Exception as e:
                print(f"❌ Failed to establish new connection: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Connection reset failed: {e}")
        return False

def add_columns_postgresql():
    """Add missing columns with PostgreSQL-specific handling"""
    from app import db
    
    # List of columns to add
    columns_to_add = [
        # Coach Profile Stripe columns
        ("coach_profile", "stripe_account_id", "VARCHAR(255)"),
        ("coach_profile", "stripe_account_status", "VARCHAR(50)"),
        
        # Contract Payment columns
        ("contract", "stripe_payment_intent_id", "VARCHAR(255)"),
        ("contract", "payment_date", "TIMESTAMP"),
        
        # Session Payment columns
        ("session_payment", "stripe_transfer_id", "VARCHAR(255)"),
        ("session_payment", "transfer_date", "TIMESTAMP"),
    ]
    
    for table_name, column_name, column_type in columns_to_add:
        add_single_column_postgresql(table_name, column_name, column_type)

def add_single_column_postgresql(table_name, column_name, column_type):
    """Add a single column with PostgreSQL-specific error handling"""
    from app import db
    
    try:
        # Check if column already exists
        result = db.session.execute(db.text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = :table_name 
            AND column_name = :column_name
        """), {"table_name": table_name, "column_name": column_name})
        
        if result.fetchone():
            print(f"✅ Column {table_name}.{column_name} already exists")
            return True
        
        # Add column with fresh transaction
        print(f"🔧 Adding column {table_name}.{column_name}...")
        db.session.execute(db.text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"))
        db.session.commit()
        print(f"✅ Added column {table_name}.{column_name}")
        return True
        
    except Exception as e:
        print(f"⚠️ Could not add {table_name}.{column_name}: {e}")
        
        # If it's a transaction error, reset connection and retry
        if "InFailedSqlTransaction" in str(e) or "current transaction is aborted" in str(e):
            print(f"🔄 Transaction failed, resetting connection for {table_name}.{column_name}...")
            
            # Reset connection
            try:
                db.session.rollback()
                db.session.close()
                db.engine.dispose()
                
                # Wait for connection to reset
                import time
                time.sleep(1)
                
                # Test new connection
                db.session.execute(db.text("SELECT 1"))
                db.session.commit()
                
                # Check if column exists after reset
                result = db.session.execute(db.text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = :table_name 
                    AND column_name = :column_name
                """), {"table_name": table_name, "column_name": column_name})
                
                if result.fetchone():
                    print(f"✅ Column {table_name}.{column_name} exists after connection reset")
                    return True
                
                # Try adding again with fresh connection
                db.session.execute(db.text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"))
                db.session.commit()
                print(f"✅ Added column {table_name}.{column_name} after connection reset")
                return True
                
            except Exception as retry_error:
                print(f"❌ Failed to add {table_name}.{column_name} after reset: {retry_error}")
                return False
        
        # For other errors, just continue
        try:
            db.session.rollback()
        except:
            pass
        
        return False

def verify_database_postgresql():
    """Verify database is working correctly for PostgreSQL"""
    try:
        from app import app, db
        from models import User, Contract, SessionPayment
        
        with app.app_context():
            print("🔍 Verifying PostgreSQL database...")
            
            # Test basic queries
            user_count = User.query.count()
            print(f"✅ Users table: {user_count} records")
            
            contract_count = Contract.query.count()
            print(f"✅ Contracts table: {contract_count} records")
            
            payment_count = SessionPayment.query.count()
            print(f"✅ Session Payments table: {payment_count} records")
            
            # Test column existence
            verify_columns_postgresql()
            
            print("✅ PostgreSQL database verification completed")
            return True
            
    except Exception as e:
        print(f"❌ PostgreSQL database verification failed: {e}")
        return False

def verify_columns_postgresql():
    """Verify that all required columns exist using PostgreSQL information_schema"""
    from app import db
    
    required_columns = [
        ("coach_profile", "stripe_account_id"),
        ("coach_profile", "stripe_account_status"),
        ("contract", "stripe_payment_intent_id"),
        ("contract", "payment_date"),
        ("session_payment", "stripe_transfer_id"),
        ("session_payment", "transfer_date"),
    ]
    
    missing_columns = []
    
    for table_name, column_name in required_columns:
        try:
            result = db.session.execute(db.text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = :table_name 
                AND column_name = :column_name
            """), {"table_name": table_name, "column_name": column_name})
            
            if result.fetchone():
                print(f"✅ Column {table_name}.{column_name} exists")
            else:
                print(f"❌ Column {table_name}.{column_name} missing")
                missing_columns.append(f"{table_name}.{column_name}")
                
        except Exception as e:
            print(f"⚠️ Could not check {table_name}.{column_name}: {e}")
            missing_columns.append(f"{table_name}.{column_name}")
    
    if missing_columns:
        print(f"⚠️ Missing columns: {', '.join(missing_columns)}")
    else:
        print("✅ All required columns exist")

def main():
    """Main PostgreSQL recovery function"""
    print("🚀 Starting PostgreSQL database recovery...")
    print(f"⏰ Started at: {datetime.now()}")
    
    # Reset PostgreSQL connection
    if not reset_postgresql_connection():
        print("❌ Failed to reset database connection")
        sys.exit(1)
    
    # Add missing columns
    print("🔧 Adding missing columns...")
    add_columns_postgresql()
    
    # Verify database
    if not verify_database_postgresql():
        print("❌ Database verification failed")
        sys.exit(1)
    
    print("🎉 PostgreSQL database recovery completed successfully!")
    print(f"⏰ Finished at: {datetime.now()}")

if __name__ == "__main__":
    main()
