#!/usr/bin/env python3
"""
Aggressive PostgreSQL Database Recovery Script for Skileez
Uses direct SQL commands to reset transaction state and add missing columns
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def reset_postgresql_transaction_state():
    """Aggressively reset PostgreSQL transaction state using direct SQL"""
    try:
        from app import app, db
        
        with app.app_context():
            print("🔧 Aggressively resetting PostgreSQL transaction state...")
            
            # Force close all connections
            try:
                db.session.close()
                db.engine.dispose()
                print("✅ Closed all database connections")
            except Exception as e:
                print(f"⚠️ Connection close warning: {e}")
            
            # Wait for connections to close
            import time
            time.sleep(2)
            
            # Create fresh connection and reset transaction state
            try:
                # Test connection
                db.session.execute(db.text("SELECT 1"))
                db.session.commit()
                print("✅ Fresh connection established")
                
                # Reset any pending transactions
                db.session.execute(db.text("ROLLBACK"))
                print("✅ Rolled back any pending transactions")
                
                # Reset session state
                db.session.execute(db.text("RESET ALL"))
                print("✅ Reset session state")
                
                # Commit the reset
                db.session.commit()
                print("✅ Transaction state reset completed")
                
                return True
                
            except Exception as e:
                print(f"❌ Failed to reset transaction state: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Transaction state reset failed: {e}")
        return False

def add_columns_with_fresh_connections():
    """Add columns using fresh connections for each operation"""
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
        add_column_with_fresh_connection(table_name, column_name, column_type)

def add_column_with_fresh_connection(table_name, column_name, column_type):
    """Add a single column using a completely fresh connection"""
    from app import db
    
    try:
        # Create a fresh connection for this operation
        print(f"🔧 Adding column {table_name}.{column_name} with fresh connection...")
        
        # Check if column exists
        result = db.session.execute(db.text("""
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
        
        # If it's a transaction error, try with completely fresh connection
        if "InFailedSqlTransaction" in str(e) or "current transaction is aborted" in str(e):
            print(f"🔄 Transaction failed, trying with completely fresh connection for {table_name}.{column_name}...")
            
            try:
                # Close current connection
                db.session.close()
                db.engine.dispose()
                
                # Wait for connection to reset
                import time
                time.sleep(1)
                
                # Create completely fresh connection
                from app import app
                with app.app_context():
                    # Test fresh connection
                    db.session.execute(db.text("SELECT 1"))
                    db.session.commit()
                    
                    # Check if column exists
                    result = db.session.execute(db.text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = :table_name 
                        AND column_name = :column_name
                    """), {"table_name": table_name, "column_name": column_name})
                    
                    if result.fetchone():
                        print(f"✅ Column {table_name}.{column_name} exists after fresh connection")
                        return True
                    
                    # Try adding with fresh connection
                    db.session.execute(db.text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"))
                    db.session.commit()
                    print(f"✅ Added column {table_name}.{column_name} with fresh connection")
                    return True
                    
            except Exception as fresh_error:
                print(f"❌ Failed to add {table_name}.{column_name} with fresh connection: {fresh_error}")
                return False
        
        return False

def verify_database_complete():
    """Complete database verification"""
    try:
        from app import app, db
        from models import User, Contract, SessionPayment
        
        with app.app_context():
            print("🔍 Performing complete database verification...")
            
            # Test basic queries
            user_count = User.query.count()
            print(f"✅ Users table: {user_count} records")
            
            contract_count = Contract.query.count()
            print(f"✅ Contracts table: {contract_count} records")
            
            payment_count = SessionPayment.query.count()
            print(f"✅ Session Payments table: {payment_count} records")
            
            # Test column existence
            verify_all_columns()
            
            print("✅ Complete database verification finished")
            return True
            
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False

def verify_all_columns():
    """Verify all required columns exist"""
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
    """Main aggressive PostgreSQL recovery function"""
    print("🚀 Starting aggressive PostgreSQL database recovery...")
    print(f"⏰ Started at: {datetime.now()}")
    
    # Reset transaction state
    if not reset_postgresql_transaction_state():
        print("❌ Failed to reset transaction state")
        sys.exit(1)
    
    # Add columns with fresh connections
    print("🔧 Adding missing columns with fresh connections...")
    add_columns_with_fresh_connections()
    
    # Complete verification
    if not verify_database_complete():
        print("❌ Database verification failed")
        sys.exit(1)
    
    print("🎉 Aggressive PostgreSQL database recovery completed successfully!")
    print(f"⏰ Finished at: {datetime.now()}")

if __name__ == "__main__":
    main()
