#!/usr/bin/env python3
"""
Manual script to create notification table in production
Run this script once in production to create the notification table
"""

import os
import sys

def create_notification_table():
    """Create the notification table manually"""
    
    print("🔧 Creating Notification Table Manually...")
    print("="*50)
    
    try:
        # Set up environment for production
        os.environ['FLASK_ENV'] = 'production'
        
        from app import app, db
        
        with app.app_context():
            print("✅ App context created successfully")
            
            # Check database type
            db_url = str(db.engine.url)
            is_postgresql = 'postgresql' in db_url.lower()
            print(f"✅ Database type: {'PostgreSQL (Production)' if is_postgresql else 'SQLite (Local)'}")
            
            # Check if table already exists
            from sqlalchemy import text
            
            if is_postgresql:
                # Check if table exists in PostgreSQL
                result = db.session.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'notification'
                    );
                """))
                table_exists = result.scalar()
            else:
                # Check if table exists in SQLite
                result = db.session.execute(text("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='notification';
                """))
                table_exists = result.scalar() is not None
            
            if table_exists:
                print("✅ Notification table already exists!")
                return True
            
            print("📝 Creating notification table...")
            
            if is_postgresql:
                # Create table in PostgreSQL
                db.session.execute(text("""
                    CREATE TABLE notification (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        title VARCHAR(255) NOT NULL,
                        message TEXT NOT NULL,
                        type VARCHAR(50) NOT NULL,
                        is_read BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        related_id INTEGER,
                        related_type VARCHAR(50)
                    );
                """))
                
                # Create indexes
                db.session.execute(text("""
                    CREATE INDEX idx_notification_user_id ON notification(user_id);
                    CREATE INDEX idx_notification_is_read ON notification(is_read);
                    CREATE INDEX idx_notification_created_at ON notification(created_at);
                    CREATE INDEX idx_notification_type ON notification(type);
                """))
                
                # Add foreign key
                db.session.execute(text("""
                    ALTER TABLE notification 
                    ADD CONSTRAINT fk_notification_user_id 
                    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE;
                """))
            else:
                # Create table in SQLite
                db.session.execute(text("""
                    CREATE TABLE notification (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        title VARCHAR(255) NOT NULL,
                        message TEXT NOT NULL,
                        type VARCHAR(50) NOT NULL,
                        is_read BOOLEAN DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        related_id INTEGER,
                        related_type VARCHAR(50),
                        FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
                    );
                """))
                
                # Create indexes
                db.session.execute(text("""
                    CREATE INDEX idx_notification_user_id ON notification(user_id);
                    CREATE INDEX idx_notification_is_read ON notification(is_read);
                    CREATE INDEX idx_notification_created_at ON notification(created_at);
                    CREATE INDEX idx_notification_type ON notification(type);
                """))
            
            db.session.commit()
            print("✅ Notification table created successfully!")
            
            # Verify the table was created
            if is_postgresql:
                result = db.session.execute(text("""
                    SELECT COUNT(*) FROM notification;
                """))
            else:
                result = db.session.execute(text("""
                    SELECT COUNT(*) FROM notification;
                """))
            
            count = result.scalar()
            print(f"✅ Table verification successful - {count} notifications found")
            
            print("\n" + "="*50)
            print("🎉 NOTIFICATION TABLE CREATED SUCCESSFULLY!")
            print("="*50)
            print("\nNext steps:")
            print("1. Re-enable notifications in routes.py")
            print("2. Restart the Flask application")
            print("3. Test sending messages, proposals, contracts")
            print("4. Verify that notifications appear in real-time")
            
            return True
            
    except Exception as e:
        print(f"❌ Error creating notification table: {e}")
        return False

if __name__ == "__main__":
    create_notification_table()
