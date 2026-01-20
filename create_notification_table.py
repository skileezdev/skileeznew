#!/usr/bin/env python3
"""
Script to create the notification table in the production database
"""

from app import app, db
from sqlalchemy import text

def create_notification_table():
    """Create the notification table if it doesn't exist"""
    
    with app.app_context():
        print("🔧 Creating Notification Table...")
        print("="*50)
        
        try:
            # Check if the notification table already exists
            # Use different syntax for SQLite vs PostgreSQL
            db_url = str(db.engine.url)
            is_postgresql = 'postgresql' in db_url.lower()
            
            if is_postgresql:
                result = db.session.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'notification'
                    );
                """))
            else:
                # SQLite syntax
                result = db.session.execute(text("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='notification';
                """))
            
            table_exists = result.scalar() is not None
            
            if table_exists:
                print("✓ Notification table already exists")
                return True
            
            # Create the notification table
            print("Creating notification table...")
            
            if is_postgresql:
                # PostgreSQL syntax
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
                
                # Create indexes for better performance
                db.session.execute(text("""
                    CREATE INDEX idx_notification_user_id ON notification(user_id);
                    CREATE INDEX idx_notification_is_read ON notification(is_read);
                    CREATE INDEX idx_notification_created_at ON notification(created_at);
                    CREATE INDEX idx_notification_type ON notification(type);
                """))
                
                # Add foreign key constraint
                db.session.execute(text("""
                    ALTER TABLE notification 
                    ADD CONSTRAINT fk_notification_user_id 
                    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE;
                """))
            else:
                # SQLite syntax
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
                
                # Create indexes for better performance
                db.session.execute(text("""
                    CREATE INDEX idx_notification_user_id ON notification(user_id);
                    CREATE INDEX idx_notification_is_read ON notification(is_read);
                    CREATE INDEX idx_notification_created_at ON notification(created_at);
                    CREATE INDEX idx_notification_type ON notification(type);
                """))
            
            db.session.commit()
            print("✓ Notification table created successfully")
            
            # Verify the table was created
            result = db.session.execute(text("""
                SELECT COUNT(*) FROM notification;
            """))
            
            count = result.scalar()
            print(f"✓ Notification table verification successful - {count} notifications found")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating notification table: {e}")
            return False

if __name__ == "__main__":
    create_notification_table()
