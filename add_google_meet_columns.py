import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def add_google_meet_columns():
    """Add Google Meet columns to existing database tables"""
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return False
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Add columns to scheduled_session table
            print("🎥 Adding Google Meet columns to scheduled_session table...")
            
            # Check if columns already exist
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'scheduled_session' 
                AND column_name IN ('google_meet_url', 'meeting_status', 'meeting_created_at', 'meeting_created_by', 'meeting_notes')
            """))
            
            existing_columns = [row[0] for row in result]
            
            if 'google_meet_url' not in existing_columns:
                conn.execute(text("ALTER TABLE scheduled_session ADD COLUMN google_meet_url TEXT"))
                print("✅ Added google_meet_url column")
            
            if 'meeting_status' not in existing_columns:
                conn.execute(text("ALTER TABLE scheduled_session ADD COLUMN meeting_status VARCHAR(50) DEFAULT 'pending'"))
                print("✅ Added meeting_status column")
            
            if 'meeting_created_at' not in existing_columns:
                conn.execute(text("ALTER TABLE scheduled_session ADD COLUMN meeting_created_at TIMESTAMP"))
                print("✅ Added meeting_created_at column")
            
            if 'meeting_created_by' not in existing_columns:
                conn.execute(text("ALTER TABLE scheduled_session ADD COLUMN meeting_created_by INTEGER"))
                print("✅ Added meeting_created_by column")
            
            if 'meeting_notes' not in existing_columns:
                conn.execute(text("ALTER TABLE scheduled_session ADD COLUMN meeting_notes TEXT"))
                print("✅ Added meeting_notes column")
            
            # Add columns to scheduled_call table
            print("🎥 Adding Google Meet columns to scheduled_call table...")
            
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'scheduled_call' 
                AND column_name IN ('google_meet_url', 'meeting_status', 'meeting_created_at', 'meeting_created_by', 'meeting_notes')
            """))
            
            existing_columns = [row[0] for row in result]
            
            if 'google_meet_url' not in existing_columns:
                conn.execute(text("ALTER TABLE scheduled_call ADD COLUMN google_meet_url TEXT"))
                print("✅ Added google_meet_url column to scheduled_call")
            
            if 'meeting_status' not in existing_columns:
                conn.execute(text("ALTER TABLE scheduled_call ADD COLUMN meeting_status VARCHAR(50) DEFAULT 'pending'"))
                print("✅ Added meeting_status column to scheduled_call")
            
            if 'meeting_created_at' not in existing_columns:
                conn.execute(text("ALTER TABLE scheduled_call ADD COLUMN meeting_created_at TIMESTAMP"))
                print("✅ Added meeting_created_at column to scheduled_call")
            
            if 'meeting_created_by' not in existing_columns:
                conn.execute(text("ALTER TABLE scheduled_call ADD COLUMN meeting_created_by INTEGER"))
                print("✅ Added meeting_created_by column to scheduled_call")
            
            if 'meeting_notes' not in existing_columns:
                conn.execute(text("ALTER TABLE scheduled_call ADD COLUMN meeting_notes TEXT"))
                print("✅ Added meeting_notes column to scheduled_call")
            
            conn.commit()
            print("🎉 Database migration completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False

if __name__ == "__main__":
    success = add_google_meet_columns()
    if success:
        print("✅ Google Meet columns added successfully!")
    else:
        print("❌ Migration failed!")
        sys.exit(1)
