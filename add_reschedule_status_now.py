#!/usr/bin/env python3
"""
Add reschedule_status column immediately
This script adds the missing column to fix the indicators
"""

import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def add_reschedule_status_column():
    """Add reschedule_status column to both tables"""
    try:
        from app import app, db
        
        with app.app_context():
            print("🚀 Adding reschedule_status column...")
            
            # Add to session table
            try:
                db.engine.execute("ALTER TABLE session ADD COLUMN reschedule_status VARCHAR(20) DEFAULT NULL")
                print("✅ Added reschedule_status to session table")
            except Exception as e:
                if "already exists" in str(e) or "duplicate column" in str(e):
                    print("✅ reschedule_status already exists in session table")
                else:
                    print(f"⚠️  Error adding to session table: {e}")
            
            # Add to scheduled_session table
            try:
                db.engine.execute("ALTER TABLE scheduled_session ADD COLUMN reschedule_status VARCHAR(20) DEFAULT NULL")
                print("✅ Added reschedule_status to scheduled_session table")
            except Exception as e:
                if "already exists" in str(e) or "duplicate column" in str(e):
                    print("✅ reschedule_status already exists in scheduled_session table")
                else:
                    print(f"⚠️  Error adding to scheduled_session table: {e}")
            
            print("🎉 Column addition completed!")
            return True
            
    except Exception as e:
        print(f"❌ Failed to add column: {e}")
        return False

if __name__ == "__main__":
    add_reschedule_status_column()
