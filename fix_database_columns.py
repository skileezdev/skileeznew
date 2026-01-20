#!/usr/bin/env python3
"""
Quick fix script to add missing columns to production database
Run this manually on Render to fix the immediate database issue
"""

import os
import psycopg2
from urllib.parse import urlparse

def fix_database_columns():
    """Add Google Meet columns directly to database"""
    
    print("🚀 Starting database fix script...")
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    print(f"🔍 DATABASE_URL found: {'Yes' if database_url else 'No'}")
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        print("💡 Please check your .env file or environment variables")
        return False
    
    try:
        # Parse database URL
        url = urlparse(database_url)
        
        # Connect to database
        conn = psycopg2.connect(
            host=url.hostname,
            port=url.port,
            database=url.path[1:],
            user=url.username,
            password=url.password
        )
        
        cursor = conn.cursor()
        
        print("🎥 Adding Google Meet columns to scheduled_session table...")
        
        # Add columns to scheduled_session
        cursor.execute("""
            ALTER TABLE scheduled_session 
            ADD COLUMN IF NOT EXISTS google_meet_url TEXT
        """)
        
        cursor.execute("""
            ALTER TABLE scheduled_session 
            ADD COLUMN IF NOT EXISTS meeting_status VARCHAR(50) DEFAULT 'pending'
        """)
        
        cursor.execute("""
            ALTER TABLE scheduled_session 
            ADD COLUMN IF NOT EXISTS meeting_created_at TIMESTAMP
        """)
        
        cursor.execute("""
            ALTER TABLE scheduled_session 
            ADD COLUMN IF NOT EXISTS meeting_created_by INTEGER
        """)
        
        cursor.execute("""
            ALTER TABLE scheduled_session 
            ADD COLUMN IF NOT EXISTS meeting_notes TEXT
        """)
        
        print("🎥 Adding Google Meet columns to scheduled_call table...")
        
        # Add columns to scheduled_call
        cursor.execute("""
            ALTER TABLE scheduled_call 
            ADD COLUMN IF NOT EXISTS google_meet_url TEXT
        """)
        
        cursor.execute("""
            ALTER TABLE scheduled_call 
            ADD COLUMN IF NOT EXISTS meeting_status VARCHAR(50) DEFAULT 'pending'
        """)
        
        cursor.execute("""
            ALTER TABLE scheduled_call 
            ADD COLUMN IF NOT EXISTS meeting_created_at TIMESTAMP
        """)
        
        cursor.execute("""
            ALTER TABLE scheduled_call 
            ADD COLUMN IF NOT EXISTS meeting_created_by INTEGER
        """)
        
        cursor.execute("""
            ALTER TABLE scheduled_call 
            ADD COLUMN IF NOT EXISTS meeting_notes TEXT
        """)
        
        # Commit changes
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Database columns added successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("📋 Script execution started...")
    try:
        success = fix_database_columns()
        if success:
            print("✅ Database fixed successfully!")
        else:
            print("❌ Database fix failed!")
    except Exception as e:
        print(f"💥 Script crashed with error: {e}")
        import traceback
        traceback.print_exc()
