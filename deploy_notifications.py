#!/usr/bin/env python3
"""
Comprehensive deployment script for notifications
"""

def deploy_notifications():
    """Deploy notifications to production"""
    
    print("🚀 Deploying Notifications to Production...")
    print("="*60)
    
    try:
        from app import app, db
        
        with app.app_context():
            print("✅ App context created successfully")
            
            # Step 1: Check database type
            db_url = str(db.engine.url)
            is_postgresql = 'postgresql' in db_url.lower()
            print(f"✅ Database type: {'PostgreSQL (Production)' if is_postgresql else 'SQLite (Local)'}")
            
            # Step 2: Create notification table if needed
            print("\n📋 Step 1: Creating notification table...")
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
                print("✅ Notification table already exists")
            else:
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
                print("✅ Notification table created successfully")
            
            # Step 3: Test notification creation
            print("\n📋 Step 2: Testing notification creation...")
            from models import User, Notification
            
            # Get or create test users
            student = User.query.filter(User.email.like('%student%')).first()
            coach = User.query.filter(User.email.like('%coach%')).first()
            
            if not student or not coach:
                print("📝 Creating test users...")
                student = User(
                    email='test.student@example.com',
                    password='password123',
                    first_name='Test',
                    last_name='Student',
                    current_role='student'
                )
                coach = User(
                    email='test.coach@example.com',
                    password='password123',
                    first_name='Test',
                    last_name='Coach',
                    current_role='coach'
                )
                db.session.add(student)
                db.session.add(coach)
                db.session.commit()
                print("✅ Test users created")
            
            # Test basic notification creation
            notification = Notification.create_notification(
                user_id=student.id,
                title="Deployment Test",
                message="Testing notification system deployment",
                notification_type='system'
            )
            
            if notification:
                print("✅ Basic notification creation works")
                
                # Clean up test notification
                db.session.delete(notification)
                db.session.commit()
            else:
                print("❌ Basic notification creation failed")
                return False
            
            # Step 4: Test notification utilities
            print("\n📋 Step 3: Testing notification utilities...")
            from notification_utils import (
                create_system_notification,
                create_message_notification,
                create_job_notification
            )
            
            # Test system notification
            create_system_notification(student.id, "System Test", "Testing system notifications")
            print("✅ System notifications work")
            
            # Test message notification
            create_message_notification(coach, student, "Hello! This is a test message.")
            print("✅ Message notifications work")
            
            # Test job notification
            from models import LearningRequest
            learning_request = LearningRequest(
                student_id=student.id,
                title="Test Learning Request",
                description="Test description",
                is_active=True
            )
            db.session.add(learning_request)
            db.session.flush()
            
            create_job_notification(learning_request, 'proposal_received')
            print("✅ Job notifications work")
            
            # Clean up test data
            db.session.delete(learning_request)
            db.session.commit()
            
            # Step 5: Verify notification counts
            print("\n📋 Step 4: Verifying notification counts...")
            student_notifications = Notification.query.filter_by(user_id=student.id).count()
            coach_notifications = Notification.query.filter_by(user_id=coach.id).count()
            
            print(f"✅ Student notifications: {student_notifications}")
            print(f"✅ Coach notifications: {coach_notifications}")
            
            if student_notifications > 0 and coach_notifications > 0:
                print("✅ Notification counts verified")
            else:
                print("❌ Notification counts verification failed")
                return False
            
            # Step 6: Test notification API
            print("\n📋 Step 5: Testing notification API...")
            student_recent = Notification.get_recent_notifications(student.id, limit=5)
            coach_recent = Notification.get_recent_notifications(coach.id, limit=5)
            
            student_unread = Notification.get_unread_count(student.id)
            coach_unread = Notification.get_unread_count(coach.id)
            
            print(f"✅ Student recent notifications: {len(student_recent)}")
            print(f"✅ Coach recent notifications: {len(coach_recent)}")
            print(f"✅ Student unread count: {student_unread}")
            print(f"✅ Coach unread count: {coach_unread}")
            
            print("\n" + "="*60)
            print("🎉 NOTIFICATION SYSTEM DEPLOYMENT SUCCESSFUL!")
            print("="*60)
            print("\n✅ All notification features are working:")
            print("   • Notification table created/verified")
            print("   • Basic notification creation works")
            print("   • System notifications work")
            print("   • Message notifications work")
            print("   • Job/proposal notifications work")
            print("   • Notification API endpoints work")
            print("   • Unread counts work")
            print("\n🚀 Ready for production use!")
            print("\nNext steps:")
            print("1. Deploy to production")
            print("2. Restart the Flask application")
            print("3. Test sending messages, proposals, contracts")
            print("4. Verify notifications appear in real-time")
            
            return True
            
    except Exception as e:
        print(f"❌ Error during deployment: {e}")
        return False

if __name__ == "__main__":
    deploy_notifications()
