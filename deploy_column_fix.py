#!/usr/bin/env python3
"""
Simple deployment script to add the reschedule_proposed_time column.
This script will be run during Render deployment.
"""

import os
import sys

def add_column():
    """Add the missing column to the database"""
    print("🚀 Adding reschedule_proposed_time column...")
    
    # Get database URL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("⚠️ No DATABASE_URL - skipping migration")
        return True
    
    try:
        import psycopg2
        
        # Fix postgres:// URL
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        # Connect and add column
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("""
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'session' AND column_name = 'reschedule_proposed_time'
        """)
        
        if cursor.fetchone():
            print("✅ Column already exists")
        else:
            # Add the column
            cursor.execute("""
                ALTER TABLE session 
                ADD COLUMN reschedule_proposed_time TIMESTAMP NULL
            """)
            print("✅ Column added successfully")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = add_column()
    if not success:
        sys.exit(1)
    print("✅ Migration completed!")
