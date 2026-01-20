#!/usr/bin/env python3
"""
Script to add notification table to production database.
Run this script manually on Render or your production environment.
"""

import os
import sys
from sqlalchemy import text, create_engine
from app import app

def add_notification_table():
    """Add notification table to database"""
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
                # Check if notification table already exists
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_name = 'notification'
                """))
                
                if result.fetchone():
                    print("Notification table already exists")
                    return True
                
                # Add notification table
                print("Adding notification table...")
                conn.execute(text("""
                    CREATE TABLE notification (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        title VARCHAR(255) NOT NULL,
                        message TEXT NOT NULL,
                        type VARCHAR(50) NOT NULL,
                        is_read BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        related_id INTEGER,
                        related_type VARCHAR(50),
                        FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
                    )
                """))
                
                # Add indexes for better performance
                conn.execute(text("""
                    CREATE INDEX idx_notification_user_id ON notification(user_id);
                    CREATE INDEX idx_notification_type ON notification(type);
                    CREATE INDEX idx_notification_is_read ON notification(is_read);
                    CREATE INDEX idx_notification_created_at ON notification(created_at);
                """))
                
                conn.commit()
                print("✅ Successfully added notification table")
                return True
                
        except Exception as e:
            print(f"❌ Error adding notification table: {e}")
            return False

def verify_notification_table():
    """Verify that notification table was added successfully"""
    with app.app_context():
        try:
            from sqlalchemy import text
            
            # Test query to see if notification table exists
            result = db.session.execute(text('SELECT COUNT(*) FROM notification')).scalar()
            print(f"✅ Notification table verification successful - {result} notifications found")
            return True
                
        except Exception as e:
            print(f"❌ Error verifying notification table: {e}")
            return False

if __name__ == "__main__":
    print("=== Notification Table Deployment Script ===")
    print()
    
    # Add the notification table
    if add_notification_table():
        print()
        print("=== Verification ===")
        verify_notification_table()
        print()
        print("=== Next Steps ===")
        print("1. Uncomment notification imports in routes.py")
        print("2. Uncomment notification creation in send_message function")
        print("3. Deploy the updated code")
        print("4. Test notification functionality")
    else:
        print("❌ Deployment failed")
        sys.exit(1)
