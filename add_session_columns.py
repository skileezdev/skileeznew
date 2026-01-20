#!/usr/bin/env python3
"""
Add missing columns to session table for button logic
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db

def add_session_columns():
    """Add missing columns to session table"""
    
    with app.app_context():
        print("Adding missing columns to session table...")
        
        try:
            # Check if columns exist and add them if they don't
            inspector = db.inspect(db.engine)
            existing_columns = [col['name'] for col in inspector.get_columns('session')]
            
            columns_to_add = [
                'auto_activated',
                'reminder_sent', 
                'early_join_enabled',
                'buffer_minutes',
                'meeting_started_at',
                'meeting_ended_at',
                'waiting_room_enabled',
                'calendar_event_id',
                'calendar_provider'
            ]
            
            for column in columns_to_add:
                if column not in existing_columns:
                    print(f"Adding column: {column}")
                    if column in ['auto_activated', 'reminder_sent', 'early_join_enabled', 'waiting_room_enabled']:
                        db.session.execute(db.text(f"ALTER TABLE session ADD COLUMN {column} BOOLEAN DEFAULT 0"))
                    elif column in ['buffer_minutes']:
                        db.session.execute(db.text(f"ALTER TABLE session ADD COLUMN {column} INTEGER DEFAULT 0"))
                    elif column in ['meeting_started_at', 'meeting_ended_at']:
                        db.session.execute(db.text(f"ALTER TABLE session ADD COLUMN {column} DATETIME"))
                    elif column in ['calendar_event_id', 'calendar_provider']:
                        db.session.execute(db.text(f"ALTER TABLE session ADD COLUMN {column} VARCHAR(255)"))
                    else:
                        db.session.execute(db.text(f"ALTER TABLE session ADD COLUMN {column} VARCHAR(50)"))
                else:
                    print(f"Column {column} already exists")
            
            db.session.commit()
            
            print("✓ Session table updated successfully!")
            
        except Exception as e:
            print(f"Error updating session table: {e}")
            return False
        
        return True

if __name__ == "__main__":
    add_session_columns()
