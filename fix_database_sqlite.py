#!/usr/bin/env python3
"""
SQLite Database Recovery Script for Skileez
Fixes transaction issues and adds missing columns for SQLite
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
            add_columns_safely_sqlite()
            
            print("✅ Database recovery completed successfully")
            return True
            
    except Exception as e:
        print(f"❌ Database recovery failed: {e}")
        return False

def add_columns_safely_sqlite():
    """Add columns safely with individual transactions for SQLite"""
    from app import db
    
    # List of columns to add
    columns_to_add = [
        # Coach Profile Stripe columns
        ("coach_profile", "stripe_account_id", "TEXT"),
        ("coach_profile", "stripe_account_status", "TEXT"),
        
        # Contract Payment columns
        ("contract", "stripe_payment_intent_id", "TEXT"),
        ("contract", "payment_date", "DATETIME"),
        
        # Session Payment columns
        ("session_payment", "stripe_transfer_id", "TEXT"),
        ("session_payment", "transfer_date", "DATETIME"),
    ]
    
    for table_name, column_name, column_type in columns_to_add:
        add_single_column_sqlite(table_name, column_name, column_type)

def add_single_column_sqlite(table_name, column_name, column_type):
    """Add a single column with proper error handling for SQLite"""
    from app import db
    
    try:
        # Check if column already exists using SQLite pragma
        result = db.session.execute(db.text(f"PRAGMA table_info({table_name})"))
        columns = result.fetchall()
        column_names = [col[1] for col in columns]  # Column name is at index 1
        
        if column_name in column_names:
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
            verify_columns_sqlite()
            
            print("✅ Database verification completed")
            return True
            
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False

def verify_columns_sqlite():
    """Verify that all required columns exist using SQLite pragma"""
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
            result = db.session.execute(db.text(f"PRAGMA table_info({table_name})"))
            columns = result.fetchall()
            column_names = [col[1] for col in columns]  # Column name is at index 1
            
            if column_name in column_names:
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
    print("🚀 Starting SQLite database recovery...")
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
