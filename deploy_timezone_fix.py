#!/usr/bin/env python3
"""
Deployment script to add timezone column to production database.
Run this script manually on Render or your production environment.
"""

import os
import sys
from sqlalchemy import text, create_engine
from app import app

def add_timezone_column():
    """Add timezone column to user table"""
    with app.app_context():
        try:
            # Get database URL from environment
            database_url = os.environ.get('DATABASE_URL')
            if not database_url:
                print("ERROR: DATABASE_URL environment variable not found")
                return False
            
            # Create engine
            engine = create_engine(database_url)
            
            with engine.connect() as conn:
                # Check if timezone column already exists
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'user' AND column_name = 'timezone'
                """))
                
                if result.fetchone():
                    print("Timezone column already exists")
                    return True
                
                # Add timezone column
                print("Adding timezone column to user table...")
                conn.execute(text("""
                    ALTER TABLE "user" ADD COLUMN timezone VARCHAR(50) DEFAULT 'UTC'
                """))
                
                # Update existing users to have UTC timezone
                print("Updating existing users with UTC timezone...")
                conn.execute(text("""
                    UPDATE "user" SET timezone = 'UTC' WHERE timezone IS NULL
                """))
                
                # Add comment to column
                conn.execute(text("""
                    COMMENT ON COLUMN "user".timezone IS 'User timezone preference for displaying dates and times'
                """))
                
                conn.commit()
                print("✅ Successfully added timezone column to user table")
                return True
                
        except Exception as e:
            print(f"❌ Error adding timezone column: {e}")
            return False

def verify_timezone_column():
    """Verify that timezone column was added successfully"""
    with app.app_context():
        try:
            from models import User
            from sqlalchemy import text
            
            # Test query to see if timezone column exists
            result = db.session.execute(text('SELECT timezone FROM "user" LIMIT 1')).fetchone()
            if result is not None:
                print("✅ Timezone column verification successful")
                return True
            else:
                print("❌ Timezone column verification failed")
                return False
                
        except Exception as e:
            print(f"❌ Error verifying timezone column: {e}")
            return False

if __name__ == "__main__":
    print("=== Timezone Column Deployment Script ===")
    print()
    
    # Add the timezone column
    if add_timezone_column():
        print()
        print("=== Verification ===")
        verify_timezone_column()
        print()
        print("=== Next Steps ===")
        print("1. Uncomment the timezone column in models.py")
        print("2. Deploy the updated code")
        print("3. Test the timezone functionality")
    else:
        print("❌ Deployment failed")
        sys.exit(1)
