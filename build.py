#!/usr/bin/env python3
"""
Build Script for Render Deployment
Runs database migration before deploying the new code
"""

import os
import sys
import psycopg2
from datetime import datetime

def run_build_migration():
    """Run database migration during build process"""
    
    print("=" * 60)
    print("BUILD PROCESS: Database Migration")
    print("=" * 60)
    print(f"Timestamp: {datetime.now()}")
    print(f"Environment: {os.getenv('RENDER_ENVIRONMENT', 'Unknown')}")
    print()
    
    # Check if we're in a build environment
    if not os.getenv('DATABASE_URL'):
        print("⚠️ DATABASE_URL not found - skipping migration")
        print("This is normal for local development")
        return True
    
    try:
        # Get database URL from environment
        database_url = os.getenv('DATABASE_URL')
        
        # Handle different database URL formats
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        
        print(f"🔌 Connecting to database...")
        print(f"Host: {database_url.split('@')[1].split('/')[0] if '@' in database_url else 'Unknown'}")
        
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
        print("🎉 BUILD MIGRATION COMPLETED SUCCESSFULLY!")
        print("Database is ready for the new rescheduling system!")
        
        return True
        
    except Exception as e:
        print(f"❌ Build migration failed: {e}")
        print()
        print("Error details:")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")
        print()
        print("🚨 BUILD FAILED - Migration error")
        return False
        
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()
            print("🔌 Database connection closed")

def main():
    """Main build process"""
    
    print("🚀 Starting build process...")
    
    # Run database migration
    migration_success = run_build_migration()
    
    if not migration_success:
        print("💥 Build failed due to migration error")
        sys.exit(1)
    
    print()
    print("✅ Build completed successfully!")
    print("Database is ready for deployment")
    print("=" * 60)

if __name__ == "__main__":
    main()
