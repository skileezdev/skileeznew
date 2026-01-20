#!/usr/bin/env python3
"""
Automatic migration script that runs when the app starts.
This will add the reschedule_proposed_time column if it doesn't exist.
"""

import os
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError

def auto_migrate_reschedule_column():
    """Automatically add reschedule_proposed_time column if it doesn't exist"""
    
    # Only run in production (when DATABASE_URL is set)
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ℹ️  Not in production environment, skipping migration")
        return True
    
    try:
        print("🔄 Auto-migration: Checking reschedule_proposed_time column...")
        
        # Create engine
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Check if column exists
            inspector = inspect(engine)
            columns = [col['name'] for col in inspector.get_columns('session')]
            
            if 'reschedule_proposed_time' in columns:
                print("✅ reschedule_proposed_time column already exists")
                return True
            
            print("🔄 Adding reschedule_proposed_time column...")
            
            # Add the column
            conn.execute(text("""
                ALTER TABLE session 
                ADD COLUMN reschedule_proposed_time TIMESTAMP NULL
            """))
            conn.commit()
            
            print("✅ Successfully added reschedule_proposed_time column")
            return True
            
    except SQLAlchemyError as e:
        print(f"❌ Database error during auto-migration: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during auto-migration: {str(e)}")
        return False

if __name__ == '__main__':
    auto_migrate_reschedule_column()
