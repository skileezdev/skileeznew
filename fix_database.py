#!/usr/bin/env python3
"""
Database Recovery Script for Skileez
Fixes transaction issues and adds missing columns
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_database_transaction():
    """Fix database transaction issues and add missing columns"""
    try:
        from app import app, db
        
        with app.app_context():
            print("🔧 Fixing database transaction issues...")
            
            # Force rollback any pending transactions
            try:
                db.session.rollback()
                print("✅ Rolled back any pending transactions")
            except Exception as e:
                print(f"⚠️ Rollback warning: {e}")
            
            # Close and recreate session
            db.session.close()
            print("✅ Closed database session")
            
            # Test connection
            try:
                db.session.execute(db.text("SELECT 1"))
                db.session.commit()
                print("✅ Database connection restored")
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
                return False
            
            # Add missing columns with individual transactions
            print("🔧 Adding missing columns...")
            add_columns_safely()
            
            print("✅ Database recovery completed successfully")
            return True
            
    except Exception as e:
        print(f"❌ Database recovery failed: {e}")
        return False

def add_columns_safely():
    """Add columns safely with individual transactions"""
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
        add_single_column(table_name, column_name, column_type)

def add_single_column(table_name, column_name, column_type):
    """Add a single column with proper error handling"""
    from app import db
    
    try:
        # Check if column already exists
        result = db.session.execute(db.text(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = :table_name 
            AND column_name = :column_name
        """), {"table_name": table_name, "column_name": column_name})
        
        if result.fetchone():
            print(f"✅ Column {table_name}.{column_name} already exists")
            return True
        
        # Add column
        db.session.execute(db.text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"))
        db.session.commit()
        print(f"✅ Added column {table_name}.{column_name}")
        return True
        
    except Exception as e:
        print(f"⚠️ Could not add {table_name}.{column_name}: {e}")
        
        # Try to rollback and continue
        try:
            db.session.rollback()
        except:
            pass
        
        return False

def verify_database():
    """Verify database is working correctly"""
    try:
        from app import app, db
        from models import User, Contract, SessionPayment
        
        with app.app_context():
            print("🔍 Verifying database...")
            
            # Test basic queries
            user_count = User.query.count()
            print(f"✅ Users table: {user_count} records")
            
            contract_count = Contract.query.count()
            print(f"✅ Contracts table: {contract_count} records")
            
            payment_count = SessionPayment.query.count()
            print(f"✅ Session Payments table: {payment_count} records")
            
            # Test column existence
            verify_columns()
            
            print("✅ Database verification completed")
            return True
            
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False

def verify_columns():
    """Verify that all required columns exist"""
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
            result = db.session.execute(db.text(f"""
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
    """Main recovery function"""
    print("🚀 Starting database recovery...")
    print(f"⏰ Started at: {datetime.now()}")
    
    # Fix transaction issues
    if not fix_database_transaction():
        print("❌ Database recovery failed")
        sys.exit(1)
    
    # Verify database
    if not verify_database():
        print("❌ Database verification failed")
        sys.exit(1)
    
    print("🎉 Database recovery completed successfully!")
    print(f"⏰ Finished at: {datetime.now()}")

if __name__ == "__main__":
    main()
