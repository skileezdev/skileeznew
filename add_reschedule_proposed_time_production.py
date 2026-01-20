#!/usr/bin/env python3
"""
Production migration script to add reschedule_proposed_time column to session table.
This fixes the error: column session.reschedule_proposed_time does not exist
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError

def add_reschedule_proposed_time_column():
    """Add reschedule_proposed_time column to session table in production"""
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable not found")
        return False
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                print("🔍 Checking if reschedule_proposed_time column exists...")
                
                # Check if column exists
                inspector = inspect(engine)
                columns = [col['name'] for col in inspector.get_columns('session')]
                
                if 'reschedule_proposed_time' in columns:
                    print("✅ Column 'reschedule_proposed_time' already exists in session table.")
                    trans.rollback()
                    return True
                
                print("🔄 Adding reschedule_proposed_time column to session table...")
                
                # Add the column
                conn.execute(text("""
                    ALTER TABLE session 
                    ADD COLUMN reschedule_proposed_time TIMESTAMP NULL
                """))
                
                print("✅ Successfully added reschedule_proposed_time column to session table.")
                
                # Commit the transaction
                trans.commit()
                
                # Verify the column was added
                inspector = inspect(engine)
                columns = [col['name'] for col in inspector.get_columns('session')]
                
                if 'reschedule_proposed_time' in columns:
                    print("✅ Verification successful: reschedule_proposed_time column exists.")
                    return True
                else:
                    print("❌ Verification failed: reschedule_proposed_time column not found.")
                    return False
                    
            except Exception as e:
                print(f"❌ Error during migration: {str(e)}")
                trans.rollback()
                return False
                
    except SQLAlchemyError as e:
        print(f"❌ Database connection error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def main():
    """Main function to run the migration"""
    print("🚀 Starting production migration: Add reschedule_proposed_time column")
    print("=" * 60)
    
    success = add_reschedule_proposed_time_column()
    
    print("=" * 60)
    if success:
        print("🎉 Migration completed successfully!")
        print("✅ The reschedule_proposed_time column has been added to the session table")
        print("✅ The reschedule approval functionality should now work correctly")
    else:
        print("❌ Migration failed!")
        print("❌ Please check the error messages above and try again")
        sys.exit(1)

if __name__ == '__main__':
    main()
