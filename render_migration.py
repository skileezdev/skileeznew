#!/usr/bin/env python3
"""
Render deployment migration script.
This script runs automatically during deployment to fix the reschedule_proposed_time column.
"""

import os
import sys
import psycopg2
from urllib.parse import urlparse

def run_migration():
    """Run the database migration for Render deployment"""
    print("🚀 Starting Render deployment migration...")
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("⚠️ No DATABASE_URL found - skipping migration")
        return True
    
    try:
        print("🔄 Connecting to production database...")
        
        # Parse and fix the database URL
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        # Connect to database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("✅ Connected to production database")
        
        # Check if column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'session' 
            AND column_name = 'reschedule_proposed_time'
        """)
        
        if cursor.fetchone():
            print("✅ Column 'reschedule_proposed_time' already exists")
            cursor.close()
            conn.close()
            return True
        
        # Add the column
        print("🔄 Adding reschedule_proposed_time column...")
        cursor.execute("""
            ALTER TABLE session 
            ADD COLUMN reschedule_proposed_time TIMESTAMP NULL
        """)
        
        conn.commit()
        print("✅ Successfully added reschedule_proposed_time column")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = run_migration()
    if not success:
        sys.exit(1)
    print("✅ Migration completed successfully!")
