#!/usr/bin/env python3
"""
Simple Deployment Script for Skileez
Handles database setup and deployment without complex migrations
Supports both SQLite and PostgreSQL
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_database():
    """Set up database tables and handle migrations safely"""
    try:
        from app import app, db
        from models import User, StudentProfile, CoachProfile, LearningRequest, Proposal, Session, Contract, SessionPayment, RoleSwitchLog
        
        with app.app_context():
            print("🔧 Setting up database...")
            
            # Create all tables
            print("📋 Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Handle column additions with transaction recovery
            print("🔧 Adding missing columns...")
            add_missing_columns()
            
            print("✅ Database setup completed successfully")
            
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        sys.exit(1)

def add_missing_columns():
    """Add missing columns with proper transaction handling for both SQLite and PostgreSQL"""
    from app import db
    
    # Detect database type
    db_url = str(db.engine.url)
    is_sqlite = 'sqlite' in db_url.lower()
    
    print(f"🔍 Detected database type: {'SQLite' if is_sqlite else 'PostgreSQL'}")
    
    # List of columns to add with their table and column info
    columns_to_add = [
        # Coach Profile Stripe columns
        ("coach_profile", "stripe_account_id", "VARCHAR(255)" if not is_sqlite else "TEXT"),
        ("coach_profile", "stripe_account_status", "VARCHAR(50)" if not is_sqlite else "TEXT"),
        
        # Contract Payment columns
        ("contract", "stripe_payment_intent_id", "VARCHAR(255)" if not is_sqlite else "TEXT"),
        ("contract", "payment_date", "TIMESTAMP" if not is_sqlite else "DATETIME"),
        
        # Session Payment columns
        ("session_payment", "stripe_transfer_id", "VARCHAR(255)" if not is_sqlite else "TEXT"),
        ("session_payment", "transfer_date", "TIMESTAMP" if not is_sqlite else "DATETIME"),
        
        # Google Meet columns for scheduled_call table
        ("scheduled_call", "google_meet_url", "TEXT"),
        ("scheduled_call", "meeting_status", "VARCHAR(50) DEFAULT 'pending'" if not is_sqlite else "TEXT"),
        ("scheduled_call", "meeting_created_at", "TIMESTAMP" if not is_sqlite else "DATETIME"),
        ("scheduled_call", "meeting_created_by", "INTEGER"),
        ("scheduled_call", "meeting_notes", "TEXT"),
        
        # Google Meet columns for scheduled_session table (if it exists)
        ("scheduled_session", "google_meet_url", "TEXT"),
        ("scheduled_session", "meeting_status", "VARCHAR(50) DEFAULT 'pending'" if not is_sqlite else "TEXT"),
        ("scheduled_session", "meeting_created_at", "TIMESTAMP" if not is_sqlite else "DATETIME"),
        ("scheduled_session", "meeting_created_by", "INTEGER"),
        ("scheduled_session", "meeting_notes", "TEXT"),
    ]
    
    for table_name, column_name, column_type in columns_to_add:
        add_column_safely(table_name, column_name, column_type, is_sqlite)

def add_column_safely(table_name, column_name, column_type, is_sqlite):
    """Add a single column safely with proper error handling"""
    from app import db
    
    try:
        # First check if table exists
        if is_sqlite:
            # Use SQLite pragma to check if table exists
            result = db.session.execute(db.text(f"PRAGMA table_info({table_name})"))
            if not result.fetchall():
                print(f"⚠️  Table {table_name} does not exist, skipping column {column_name}")
                return False
        else:
            # Use PostgreSQL information_schema to check if table exists
            result = db.session.execute(db.text(f"""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = :table_name
            """), {"table_name": table_name})
            
            if not result.fetchone():
                print(f"⚠️  Table {table_name} does not exist, skipping column {column_name}")
                return False
        
        # Check if column already exists
        if is_sqlite:
            # Use SQLite pragma
            result = db.session.execute(db.text(f"PRAGMA table_info({table_name})"))
            columns = result.fetchall()
            column_names = [col[1] for col in columns]  # Column name is at index 1
            
            if column_name in column_names:
                print(f"✅ Column {table_name}.{column_name} already exists")
                return True
        else:
            # Use PostgreSQL information_schema
            result = db.session.execute(db.text(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = :table_name 
                AND column_name = :column_name
            """), {"table_name": table_name, "column_name": column_name})
            
            if result.fetchone():
                print(f"✅ Column {table_name}.{column_name} already exists")
                return True
        
        # Add column with fresh transaction
        db.session.execute(db.text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"))
        db.session.commit()
        print(f"✅ Added column {table_name}.{column_name}")
        
    except Exception as e:
        # Rollback and try again with fresh transaction
        try:
            db.session.rollback()
            print(f"🔄 Retrying {table_name}.{column_name} after rollback...")
            
            # Check again after rollback
            if is_sqlite:
                result = db.session.execute(db.text(f"PRAGMA table_info({table_name})"))
                columns = result.fetchall()
                column_names = [col[1] for col in columns]
                
                if column_name in column_names:
                    print(f"✅ Column {table_name}.{column_name} exists after rollback")
                    return True
            else:
                result = db.session.execute(db.text(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = :table_name 
                    AND column_name = :column_name
                """), {"table_name": table_name, "column_name": column_name})
                
                if result.fetchone():
                    print(f"✅ Column {table_name}.{column_name} exists after rollback")
                    return True
            
            # Try adding again
            db.session.execute(db.text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"))
            db.session.commit()
            print(f"✅ Added column {table_name}.{column_name} after retry")
            
        except Exception as retry_error:
            print(f"⚠️ Could not add {table_name}.{column_name}: {retry_error}")
            # Continue with other columns instead of failing completely
            return False

def create_sample_data():
    """Create sample data for testing"""
    try:
        from app import app, db
        from models import User, StudentProfile, CoachProfile, LearningRequest, Proposal, Session, Contract, SessionPayment, RoleSwitchLog
        
        with app.app_context():
            print("🔧 Creating sample data...")
            
            # Check if sample data already exists
            existing_users = User.query.count()
            if existing_users > 0:
                print(f"✅ Sample data already exists ({existing_users} users)")
                return
            
            # Create sample users
            print("👥 Creating sample users...")
            
            # Sample Student
            student = User(
                email="student@example.com",
                password="password123",
                first_name="John",
                last_name="Student",
                current_role="student"
            )
            db.session.add(student)
            db.session.flush()  # Get the ID
            
            student_profile = StudentProfile(
                user_id=student.id,
                age=25,
                location="New York, NY",
                bio="I'm passionate about learning new skills and improving myself.",
                learning_goals="I want to learn web development and improve my programming skills.",
                experience_level="beginner",
                preferred_learning_style="hands_on",
                availability="weekends",
                budget_range="100-500"
            )
            db.session.add(student_profile)
            
            # Sample Coach
            coach = User(
                email="coach@example.com",
                password="password123",
                first_name="Sarah",
                last_name="Coach",
                current_role="coach"
            )
            db.session.add(coach)
            db.session.flush()  # Get the ID
            
            coach_profile = CoachProfile(
                user_id=coach.id,
                age=30,
                location="San Francisco, CA",
                bio="Experienced web developer with 8+ years of experience. I love teaching and helping others learn.",
                skills="JavaScript, Python, React, Node.js, Web Development",
                experience_years=8,
                education="Bachelor's in Computer Science",
                hourly_rate=75.00,
                is_approved=True,
                rating=4.8,
                total_earnings=0.0
            )
            db.session.add(coach_profile)
            
            # Sample Learning Request
            learning_request = LearningRequest(
                student_id=student.id,
                title="Learn Web Development Fundamentals",
                description="I want to learn the basics of web development including HTML, CSS, and JavaScript. I'm a complete beginner and need someone patient to guide me through the process.",
                skills_needed="HTML, CSS, JavaScript, Web Development",
                experience_level="beginner",
                budget=300.00,
                duration="3 months",
                sessions_needed=12,
                preferred_learning_style="hands_on",
                availability="weekends",
                is_active=True
            )
            db.session.add(learning_request)
            
            db.session.commit()
            print("✅ Sample data created successfully")
            
    except Exception as e:
        print(f"❌ Sample data creation failed: {e}")
        # Don't exit, just log the error

def verify_database():
    """Verify database is working correctly"""
    try:
        from app import app, db
        from models import User, Contract, SessionPayment
        
        with app.app_context():
            print("🔍 Verifying database...")
            
            # Test basic queries
            user_count = User.query.count()
            print(f"✅ Users table: {user_count} records")
            
            contract_count = Contract.query.count()
            print(f"✅ Contracts table: {contract_count} records")
            
            payment_count = SessionPayment.query.count()
            print(f"✅ Session Payments table: {payment_count} records")
            
            print("✅ Database verification completed")
            return True
            
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False

def main():
    """Main deployment function"""
    print("🚀 Starting Skileez deployment...")
    print(f"⏰ Started at: {datetime.now()}")
    
    # Set up database
    setup_database()
    
    # Create sample data
    create_sample_data()
    
    # Verify database
    verify_database()
    
    print("🎉 Deployment completed successfully!")
    print(f"⏰ Finished at: {datetime.now()}")

if __name__ == "__main__":
    main()
