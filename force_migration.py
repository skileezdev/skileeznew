#!/usr/bin/env python3
"""
FORCE MIGRATION - This script MUST run to fix the database
"""

import os
import psycopg2
import sys

def force_migration():
    print("🚨 FORCE MIGRATION STARTING - Adding missing Google Meet columns...")
    
    # Get database URL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found!")
        return False
    
    try:
        # Connect to database
        print("🔗 Connecting to database...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("✅ Connected! Adding columns now...")
        
        # Force add all columns to scheduled_session
        print("➕ Adding columns to scheduled_session...")
        try:
            cursor.execute("ALTER TABLE scheduled_session ADD COLUMN google_meet_url TEXT")
            print("✅ Added google_meet_url")
        except:
            print("⚠️ google_meet_url already exists")
            
        try:
            cursor.execute("ALTER TABLE scheduled_session ADD COLUMN meeting_status VARCHAR(50) DEFAULT 'pending'")
            print("✅ Added meeting_status")
        except:
            print("⚠️ meeting_status already exists")
            
        try:
            cursor.execute("ALTER TABLE scheduled_session ADD COLUMN meeting_created_at TIMESTAMP")
            print("✅ Added meeting_created_at")
        except:
            print("⚠️ meeting_created_at already exists")
            
        try:
            cursor.execute("ALTER TABLE scheduled_session ADD COLUMN meeting_created_by INTEGER")
            print("✅ Added meeting_created_by")
        except:
            print("⚠️ meeting_created_by already exists")
            
        try:
            cursor.execute("ALTER TABLE scheduled_session ADD COLUMN meeting_notes TEXT")
            print("✅ Added meeting_notes")
        except:
            print("⚠️ meeting_notes already exists")
        
        # Force add all columns to scheduled_call
        print("➕ Adding columns to scheduled_call...")
        try:
            cursor.execute("ALTER TABLE scheduled_call ADD COLUMN google_meet_url TEXT")
            print("✅ Added google_meet_url")
        except:
            print("⚠️ google_meet_url already exists")
            
        try:
            cursor.execute("ALTER TABLE scheduled_call ADD COLUMN meeting_status VARCHAR(50) DEFAULT 'pending'")
            print("✅ Added meeting_status")
        except:
            print("⚠️ meeting_status already exists")
            
        try:
            cursor.execute("ALTER TABLE scheduled_call ADD COLUMN meeting_created_at TIMESTAMP")
            print("✅ Added meeting_created_at")
        except:
            print("⚠️ meeting_created_at already exists")
            
        try:
            cursor.execute("ALTER TABLE scheduled_call ADD COLUMN meeting_created_by INTEGER")
            print("✅ Added meeting_created_by")
        except:
            print("⚠️ meeting_created_by already exists")
            
        try:
            cursor.execute("ALTER TABLE scheduled_call ADD COLUMN meeting_notes TEXT")
            print("✅ Added meeting_notes")
        except:
            print("⚠️ meeting_notes already exists")
        
        # Commit and close
        conn.commit()
        cursor.close()
        conn.close()
        
        print("🎯 FORCE MIGRATION COMPLETED!")
        print("✅ All Google Meet columns are now available!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = force_migration()
    if success:
        print("🚀 Database is now ready for Google Meet!")
    else:
        print("💥 Migration failed - check logs!")
        sys.exit(1)
