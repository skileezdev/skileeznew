#!/usr/bin/env python3
"""
Add reschedule_status column to Session and ScheduledSession tables
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Session, ScheduledSession

def add_reschedule_status_column():
    """Add reschedule_status column to both Session and ScheduledSession tables"""
    with app.app_context():
        try:
            # Add reschedule_status column to Session table
            db.engine.execute("ALTER TABLE session ADD COLUMN reschedule_status VARCHAR(20)")
            print("✅ Added reschedule_status column to Session table")
        except Exception as e:
            print(f"⚠️  Column reschedule_status might already exist in Session table: {e}")
        
        try:
            # Add reschedule_status column to ScheduledSession table
            db.engine.execute("ALTER TABLE scheduled_session ADD COLUMN reschedule_status VARCHAR(20)")
            print("✅ Added reschedule_status column to ScheduledSession table")
        except Exception as e:
            print(f"⚠️  Column reschedule_status might already exist in ScheduledSession table: {e}")
        
        # Commit changes
        db.session.commit()
        print("✅ Database migration completed successfully")

if __name__ == "__main__":
    add_reschedule_status_column()
