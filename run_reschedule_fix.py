#!/usr/bin/env python3
"""
Quick fix script to add reschedule_status column
Run this on production to fix the database schema issue
"""

import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    print("🔄 Running reschedule_status column fix...")
    
    try:
        from app import app, db
        
        with app.app_context():
            print("📝 Adding reschedule_status column to session table...")
            try:
                db.engine.execute("ALTER TABLE session ADD COLUMN reschedule_status VARCHAR(20) DEFAULT NULL")
                print("✅ Added reschedule_status to session table")
            except Exception as e:
                if "already exists" in str(e) or "duplicate column" in str(e):
                    print("✅ reschedule_status already exists in session table")
                else:
                    print(f"❌ Error adding to session table: {e}")
            
            print("📝 Adding reschedule_status column to scheduled_session table...")
            try:
                db.engine.execute("ALTER TABLE scheduled_session ADD COLUMN reschedule_status VARCHAR(20) DEFAULT NULL")
                print("✅ Added reschedule_status to scheduled_session table")
            except Exception as e:
                if "already exists" in str(e) or "duplicate column" in str(e):
                    print("✅ reschedule_status already exists in scheduled_session table")
                else:
                    print(f"❌ Error adding to scheduled_session table: {e}")
            
            print("✅ Database fix completed!")
            
    except Exception as e:
        print(f"❌ Fix failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("🎉 Reschedule status fix completed successfully!")
    else:
        print("💥 Reschedule status fix failed!")
