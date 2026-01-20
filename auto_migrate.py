#!/usr/bin/env python3
"""
Automatic Database Migration Script for Render
This script runs during the build process to ensure the database schema is up to date.
"""

import os
import sys
import time
import psycopg2
from urllib.parse import urlparse

def wait_for_database(database_url, max_attempts=30, delay=2):
    """Wait for database to be available during build"""
    print("⏳ Waiting for database to be available...")
    
    for attempt in range(max_attempts):
        try:
            conn = psycopg2.connect(database_url)
            conn.close()
            print("✅ Database is available!")
            return True
        except Exception as e:
            if attempt < max_attempts - 1:
                print(f"⏳ Attempt {attempt + 1}/{max_attempts}: Database not ready yet...")
                time.sleep(delay)
            else:
                print(f"❌ Database connection failed after {max_attempts} attempts")
                return False
    
    return False

def run_migration(database_url):
    """Run the database migration to add Google Meet columns"""
    try:
        print("🔗 Connecting to database...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("✅ Connected to database successfully!")
        
        # Check if columns already exist
        print("🔍 Checking existing columns...")
        
        # Check scheduled_session table
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'scheduled_session' 
            AND column_name IN ('google_meet_url', 'meeting_status', 'meeting_created_at', 'meeting_created_by', 'meeting_notes')
        """)
        
        existing_session_columns = [row[0] for row in cursor.fetchall()]
        print(f"Existing columns in scheduled_session: {existing_session_columns}")
        
        # Check scheduled_call table
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'scheduled_call' 
            AND column_name IN ('google_meet_url', 'meeting_status', 'meeting_created_at', 'meeting_created_by', 'meeting_notes')
        """)
        
        existing_call_columns = [row[0] for row in cursor.fetchall()]
        print(f"Existing columns in scheduled_call: {existing_call_columns}")
        
        # Add missing columns to scheduled_session
        print("➕ Adding columns to scheduled_session table...")
        
        if 'google_meet_url' not in existing_session_columns:
            cursor.execute("ALTER TABLE scheduled_session ADD COLUMN google_meet_url TEXT")
            print("✅ Added google_meet_url to scheduled_session")
        
        if 'meeting_status' not in existing_session_columns:
            cursor.execute("ALTER TABLE scheduled_session ADD COLUMN meeting_status VARCHAR(50) DEFAULT 'pending'")
            print("✅ Added meeting_status to scheduled_session")
        
        if 'meeting_created_at' not in existing_session_columns:
            cursor.execute("ALTER TABLE scheduled_session ADD COLUMN meeting_created_at TIMESTAMP")
            print("✅ Added meeting_created_at to scheduled_session")
        
        if 'meeting_created_by' not in existing_session_columns:
            cursor.execute("ALTER TABLE scheduled_session ADD COLUMN meeting_created_by INTEGER")
            print("✅ Added meeting_created_by to scheduled_session")
        
        if 'meeting_notes' not in existing_session_columns:
            cursor.execute("ALTER TABLE scheduled_session ADD COLUMN meeting_notes TEXT")
            print("✅ Added meeting_notes to scheduled_session")
        
        # Add missing columns to scheduled_call
        print("➕ Adding columns to scheduled_call table...")
        
        if 'google_meet_url' not in existing_call_columns:
            cursor.execute("ALTER TABLE scheduled_call ADD COLUMN google_meet_url TEXT")
            print("✅ Added google_meet_url to scheduled_call")
        
        if 'meeting_status' not in existing_call_columns:
            cursor.execute("ALTER TABLE scheduled_call ADD COLUMN meeting_status VARCHAR(50) DEFAULT 'pending'")
            print("✅ Added meeting_status to scheduled_call")
        
        if 'meeting_created_at' not in existing_call_columns:
            cursor.execute("ALTER TABLE scheduled_call ADD COLUMN meeting_created_at TIMESTAMP")
            print("✅ Added meeting_created_at to scheduled_call")
        
        if 'meeting_created_by' not in existing_call_columns:
            cursor.execute("ALTER TABLE scheduled_call ADD COLUMN meeting_created_by INTEGER")
            print("✅ Added meeting_created_by to scheduled_call")
        
        if 'meeting_notes' not in existing_call_columns:
            cursor.execute("ALTER TABLE scheduled_call ADD COLUMN meeting_notes TEXT")
            print("✅ Added meeting_notes to scheduled_call")
        
        # Commit changes
        conn.commit()
        cursor.close()
        conn.close()
        
        print("🎯 Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main migration function"""
    print("🚀 Starting automatic database migration...")
    
    # Get database URL from environment (Render sets this)
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        print("Available environment variables:")
        for key, value in os.environ.items():
            if 'DATABASE' in key or 'POSTGRES' in key:
                print(f"  {key}: {value}")
        return False
    
    # Wait for database to be available
    if not wait_for_database(database_url):
        print("⚠️ Proceeding without database migration...")
        return False
    
    # Run the migration
    success = run_migration(database_url)
    
    if success:
        print("✅ Automatic migration successful!")
        print("🎯 Google Meet functionality is now ready!")
    else:
        print("❌ Automatic migration failed!")
        print("⚠️ App will start but Google Meet may not work properly")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
