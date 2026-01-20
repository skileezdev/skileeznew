import os
import psycopg2
from urllib.parse import urlparse
import sys

def fix_render_database():
    """Add Google Meet columns to Render database"""
    
    # Get database URL from environment (Render sets this)
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        print("Available environment variables:")
        for key, value in os.environ.items():
            if 'DATABASE' in key or 'POSTGRES' in key:
                print(f"  {key}: {value}")
        return False
    
    try:
        print(f"🔗 Connecting to database...")
        print(f"Database URL: {database_url[:20]}...")
        
        # Connect to database
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

if __name__ == "__main__":
    print("🚀 Starting Render database migration...")
    success = fix_render_database()
    if success:
        print("✅ Database migration successful!")
        print("🎯 Google Meet functionality should now work!")
    else:
        print("❌ Database migration failed!")
        sys.exit(1)
