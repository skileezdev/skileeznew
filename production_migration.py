#!/usr/bin/env python3
"""
Production Database Migration Script
Adds reschedule_proposed_time column to session table
"""

import os
import sys
import psycopg2
from datetime import datetime

def run_production_migration():
    """Run the production database migration"""
    
    print("=" * 60)
    print("PRODUCTION DATABASE MIGRATION")
    print("=" * 60)
    print(f"Timestamp: {datetime.now()}")
    print()
    
    # Check for database URL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable not found!")
        print("Please set DATABASE_URL before running this script")
        return False
    
    try:
        # Handle different database URL formats
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        
        print(f"🔌 Connecting to production database...")
        
        # Connect to database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        print("✅ Connected successfully")
        
        # Check if column already exists
        print("🔍 Checking if reschedule_proposed_time column exists...")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'session' 
            AND column_name = 'reschedule_proposed_time'
        """)
        
        if cursor.fetchone():
            print("✅ Column reschedule_proposed_time already exists")
            return True
        
        # Add the new column
        print("📝 Adding reschedule_proposed_time column...")
        cursor.execute("""
            ALTER TABLE session 
            ADD COLUMN reschedule_proposed_time TIMESTAMP
        """)
        
        # Commit the change
        conn.commit()
        print("✅ Column added successfully")
        
        # Verify the column was added
        print("🔍 Verifying column addition...")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'session' 
            AND column_name = 'reschedule_proposed_time'
        """)
        
        column_info = cursor.fetchone()
        if column_info:
            print(f"✅ Column verification successful:")
            print(f"   - Name: {column_info[0]}")
            print(f"   - Type: {column_info[1]}")
            print(f"   - Nullable: {column_info[2]}")
        else:
            print("❌ Column verification failed")
            return False
        
        print()
        print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
        print("The reschedule_proposed_time column has been added to the session table")
        print("Your application should now work without errors!")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print()
        print("Error details:")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")
        print()
        print("🚨 MIGRATION FAILED")
        return False
        
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()
            print("🔌 Database connection closed")

def main():
    """Main migration process"""
    
    print("🚀 Starting production database migration...")
    print("This will add the reschedule_proposed_time column to your session table")
    print()
    
    # Confirm before proceeding
    response = input("Do you want to continue? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("Migration cancelled")
        return
    
    # Run migration
    success = run_production_migration()
    
    if success:
        print()
        print("✅ Migration completed successfully!")
        print("Your application should now work properly")
    else:
        print()
        print("💥 Migration failed!")
        print("Please check the error messages above")
        sys.exit(1)

if __name__ == "__main__":
    main()
