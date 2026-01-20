#!/usr/bin/env python3
"""
Render.com Production Deployment Fix for Skileez
Handles PostgreSQL transaction issues in production environment
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_production_database():
    """Fix PostgreSQL database in production environment"""
    try:
        from app import app, db
        
        with app.app_context():
            print("🚀 Starting production database fix...")
            print(f"⏰ Started at: {datetime.now()}")
            
            # Force reset all connections
            print("🔧 Resetting production database connections...")
            try:
                db.session.close()
                db.engine.dispose()
                print("✅ Closed all database connections")
            except Exception as e:
                print(f"⚠️ Connection close warning: {e}")
            
            # Wait for connections to close
            import time
            time.sleep(2)
            
            # Test fresh connection
            try:
                db.session.execute(db.text("SELECT 1"))
                db.session.commit()
                print("✅ Fresh production connection established")
            except Exception as e:
                print(f"❌ Failed to establish fresh connection: {e}")
                return False
            
            # Add missing columns with individual transactions
            print("🔧 Adding missing Stripe columns...")
            add_stripe_columns_production()
            
            print("✅ Production database fix completed successfully")
            return True
            
    except Exception as e:
        print(f"❌ Production database fix failed: {e}")
        return False

def add_stripe_columns_production():
    """Add Stripe columns with production-safe handling"""
    from app import db
    
    # List of columns that need to be added
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
        add_single_column_production(table_name, column_name, column_type)

def add_single_column_production(table_name, column_name, column_type):
    """Add a single column with production-safe error handling"""
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
            
            try:
                # Reset connection
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

def verify_production_database():
    """Verify production database is working correctly"""
    try:
        from app import app, db
        from models import User, Contract, SessionPayment
        
        with app.app_context():
            print("🔍 Verifying production database...")
            
            # Test basic queries
            user_count = User.query.count()
            print(f"✅ Users table: {user_count} records")
            
            contract_count = Contract.query.count()
            print(f"✅ Contracts table: {contract_count} records")
            
            payment_count = SessionPayment.query.count()
            print(f"✅ Session Payments table: {payment_count} records")
            
            # Test column existence
            verify_production_columns()
            
            print("✅ Production database verification completed")
            return True
            
    except Exception as e:
        print(f"❌ Production database verification failed: {e}")
        return False

def verify_production_columns():
    """Verify that all required columns exist in production"""
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
        return False
    else:
        print("✅ All required columns exist")
        return True

def main():
    """Main production fix function"""
    print("🚀 Starting Render.com production database fix...")
    print(f"⏰ Started at: {datetime.now()}")
    
    # Check if we're in production
    is_production = os.environ.get('RENDER', False)
    if is_production:
        print("🏭 Running in production environment (Render)")
    else:
        print("🛠️ Running in development environment")
    
    # Fix production database
    if not fix_production_database():
        print("❌ Production database fix failed")
        sys.exit(1)
    
    # Verify production database
    if not verify_production_database():
        print("❌ Production database verification failed")
        sys.exit(1)
    
    print("🎉 Render.com production database fix completed successfully!")
    print(f"⏰ Finished at: {datetime.now()}")

if __name__ == "__main__":
    main()
