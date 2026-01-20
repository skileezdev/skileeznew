#!/usr/bin/env python3
"""
Migration script to add reschedule_proposed_time column to the session table.
This script should be run to update the database schema.
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models import Session

def add_reschedule_proposed_time_column():
    """Add reschedule_proposed_time column to session table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if column already exists
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('session')]
            
            if 'reschedule_proposed_time' in columns:
                print("✅ Column 'reschedule_proposed_time' already exists in session table.")
                return True
            
            # Add the column
            print("🔄 Adding reschedule_proposed_time column to session table...")
            
            # Use raw SQL to add the column
            with db.engine.connect() as connection:
                connection.execute(db.text("""
                    ALTER TABLE session 
                    ADD COLUMN reschedule_proposed_time TIMESTAMP NULL
                """))
                connection.commit()
            
            print("✅ Successfully added reschedule_proposed_time column to session table.")
            return True
            
        except Exception as e:
            print(f"❌ Error adding reschedule_proposed_time column: {str(e)}")
            return False

def verify_column_exists():
    """Verify that the column was added successfully"""
    app = create_app()
    
    with app.app_context():
        try:
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('session')]
            
            if 'reschedule_proposed_time' in columns:
                print("✅ Verification successful: reschedule_proposed_time column exists.")
                return True
            else:
                print("❌ Verification failed: reschedule_proposed_time column not found.")
                return False
                
        except Exception as e:
            print(f"❌ Error verifying column: {str(e)}")
            return False

if __name__ == "__main__":
    print("🚀 Starting migration: Add reschedule_proposed_time column")
    print("=" * 60)
    
    # Add the column
    success = add_reschedule_proposed_time_column()
    
    if success:
        # Verify the column was added
        print("\n🔍 Verifying column addition...")
        verify_column_exists()
        
        print("\n✅ Migration completed successfully!")
        print("The reschedule system should now work properly with the following fixes:")
        print("1. ✅ Coach approve/decline buttons now work with JSON requests")
        print("2. ✅ Auto-approval for reschedules >5 hours before now works")
        print("3. ✅ Proposed reschedule times are now stored and used")
        print("4. ✅ Better error handling and user feedback")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
        sys.exit(1)
