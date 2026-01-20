#!/usr/bin/env python3
"""
Comprehensive production database migration script
This script ensures all required columns exist in the production database
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import ProgrammingError

def migrate_production_database():
    """Migrate production database to ensure all required columns exist"""
    print("Starting production database migration...")
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("No DATABASE_URL found, skipping migration")
        return
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        # Check and fix scheduled_call table
        fix_scheduled_call_table(engine)
        
        # Check and fix other tables
        fix_notification_table(engine)
        fix_call_notification_table(engine)
        fix_coach_availability_table(engine)
        fix_booking_rule_table(engine)
        fix_calendar_integration_table(engine)
        fix_message_table(engine)
        
        print("Production database migration completed successfully")
        
    except Exception as e:
        print(f"Error during production database migration: {e}")
        # Don't fail the deployment if migration fails
        pass

def fix_scheduled_call_table(engine):
    """Fix scheduled_call table schema"""
    print("Checking scheduled_call table...")
    
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if 'scheduled_call' not in existing_tables:
        print("Creating scheduled_call table...")
        create_scheduled_call_table(engine)
    else:
        print("scheduled_call table exists, checking columns...")
        fix_scheduled_call_columns(engine)

def create_scheduled_call_table(engine):
    """Create scheduled_call table with all required columns"""
    create_table_sql = """
    CREATE TABLE scheduled_call (
        id SERIAL PRIMARY KEY,
        student_id INTEGER NOT NULL,
        coach_id INTEGER NOT NULL,
        call_type VARCHAR(20) NOT NULL DEFAULT 'free_consultation',
        scheduled_at TIMESTAMP NOT NULL,
        duration_minutes INTEGER NOT NULL DEFAULT 15,
        status VARCHAR(20) NOT NULL DEFAULT 'scheduled',
        
        contract_id INTEGER,
        session_id INTEGER,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        started_at TIMESTAMP,
        ended_at TIMESTAMP,
        rescheduled_from INTEGER,
        reschedule_reason TEXT,
        CONSTRAINT fk_scheduled_call_student FOREIGN KEY (student_id) REFERENCES "user" (id) ON DELETE CASCADE,
        CONSTRAINT fk_scheduled_call_coach FOREIGN KEY (coach_id) REFERENCES "user" (id) ON DELETE CASCADE,
        CONSTRAINT fk_scheduled_call_contract FOREIGN KEY (contract_id) REFERENCES contract (id) ON DELETE SET NULL,
        CONSTRAINT fk_scheduled_call_session FOREIGN KEY (session_id) REFERENCES session (id) ON DELETE SET NULL,
        CONSTRAINT fk_scheduled_call_rescheduled_from FOREIGN KEY (rescheduled_from) REFERENCES scheduled_call (id) ON DELETE SET NULL
    );
    """
    
    create_indexes_sql = """
    CREATE INDEX IF NOT EXISTS ix_scheduled_call_student_id ON scheduled_call (student_id);
    CREATE INDEX IF NOT EXISTS ix_scheduled_call_coach_id ON scheduled_call (coach_id);
    CREATE INDEX IF NOT EXISTS ix_scheduled_call_scheduled_at ON scheduled_call (scheduled_at);
    CREATE INDEX IF NOT EXISTS ix_scheduled_call_status ON scheduled_call (status);
    CREATE INDEX IF NOT EXISTS ix_scheduled_call_call_type ON scheduled_call (call_type);
    """
    
    with engine.connect() as conn:
        conn.execute(text(create_table_sql))
        conn.execute(text(create_indexes_sql))
        conn.commit()
    
    print("scheduled_call table created successfully")

def fix_scheduled_call_columns(engine):
    """Add missing columns to scheduled_call table"""
    required_columns = {
        
        'session_id': 'INTEGER',
        'rescheduled_from': 'INTEGER',
        'reschedule_reason': 'TEXT',
        'started_at': 'TIMESTAMP',
        'ended_at': 'TIMESTAMP'
    }
    
    inspector = inspect(engine)
    existing_columns = [col['name'] for col in inspector.get_columns('scheduled_call')]
    
    with engine.connect() as conn:
        for column_name, column_type in required_columns.items():
            if column_name not in existing_columns:
                print(f"Adding missing column {column_name} to scheduled_call table...")
                try:
                    conn.execute(text(f"ALTER TABLE scheduled_call ADD COLUMN {column_name} {column_type}"))
                    conn.commit()
                    print(f"Column {column_name} added successfully")
                except Exception as e:
                    print(f"Error adding column {column_name}: {e}")
            else:
                print(f"Column {column_name} already exists")

def fix_notification_table(engine):
    """Fix notification table schema"""
    print("Checking notification table...")
    
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if 'notification' not in existing_tables:
        print("Creating notification table...")
        create_notification_table_sql = """
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
            CONSTRAINT fk_notification_user FOREIGN KEY (user_id) REFERENCES "user" (id) ON DELETE CASCADE
        );
        """
        
        create_indexes_sql = """
        CREATE INDEX IF NOT EXISTS ix_notification_user_id ON notification (user_id);
        CREATE INDEX IF NOT EXISTS ix_notification_is_read ON notification (is_read);
        CREATE INDEX IF NOT EXISTS ix_notification_created_at ON notification (created_at);
        """
        
        with engine.connect() as conn:
            conn.execute(text(create_notification_table_sql))
            conn.execute(text(create_indexes_sql))
            conn.commit()
        
        print("Notification table created successfully")
    else:
        print("Notification table already exists")

def fix_call_notification_table(engine):
    """Fix call_notification table schema"""
    print("Checking call_notification table...")
    
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if 'call_notification' not in existing_tables:
        print("Creating call_notification table...")
        create_table_sql = """
        CREATE TABLE call_notification (
            id SERIAL PRIMARY KEY,
            call_id INTEGER NOT NULL,
            notification_type VARCHAR(50) NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            sent_to_student BOOLEAN DEFAULT FALSE,
            sent_to_coach BOOLEAN DEFAULT FALSE,
            email_sent BOOLEAN DEFAULT FALSE,
            notification_sent BOOLEAN DEFAULT FALSE,
            CONSTRAINT fk_call_notification_call FOREIGN KEY (call_id) REFERENCES scheduled_call (id) ON DELETE CASCADE
        );
        """
        
        create_indexes_sql = """
        CREATE INDEX IF NOT EXISTS ix_call_notification_call_id ON call_notification (call_id);
        CREATE INDEX IF NOT EXISTS ix_call_notification_notification_type ON call_notification (notification_type);
        """
        
        with engine.connect() as conn:
            conn.execute(text(create_table_sql))
            conn.execute(text(create_indexes_sql))
            conn.commit()
        
        print("Call notification table created successfully")
    else:
        print("Call notification table already exists")

def fix_coach_availability_table(engine):
    """Fix coach_availability table schema"""
    print("Checking coach_availability table...")
    
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if 'coach_availability' not in existing_tables:
        print("Creating coach_availability table...")
        create_table_sql = """
        CREATE TABLE coach_availability (
            id SERIAL PRIMARY KEY,
            coach_id INTEGER NOT NULL,
            is_available BOOLEAN DEFAULT TRUE,
            timezone VARCHAR(50) DEFAULT 'UTC',
            monday_start INTEGER DEFAULT 540,
            monday_end INTEGER DEFAULT 1020,
            tuesday_start INTEGER DEFAULT 540,
            tuesday_end INTEGER DEFAULT 1020,
            wednesday_start INTEGER DEFAULT 540,
            wednesday_end INTEGER DEFAULT 1020,
            thursday_start INTEGER DEFAULT 540,
            thursday_end INTEGER DEFAULT 1020,
            friday_start INTEGER DEFAULT 540,
            friday_end INTEGER DEFAULT 1020,
            saturday_start INTEGER DEFAULT 540,
            saturday_end INTEGER DEFAULT 1020,
            sunday_start INTEGER DEFAULT 540,
            sunday_end INTEGER DEFAULT 1020,
            session_duration INTEGER DEFAULT 60,
            buffer_before INTEGER DEFAULT 0,
            buffer_after INTEGER DEFAULT 15,
            advance_booking_days INTEGER DEFAULT 30,
            same_day_booking BOOLEAN DEFAULT FALSE,
            instant_confirmation BOOLEAN DEFAULT TRUE,
            consultation_duration INTEGER DEFAULT 15,
            consultation_available BOOLEAN DEFAULT TRUE,
            consultation_advance_hours INTEGER DEFAULT 2,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_coach_availability_user FOREIGN KEY (coach_id) REFERENCES "user" (id) ON DELETE CASCADE
        );
        """
        
        with engine.connect() as conn:
            conn.execute(text(create_table_sql))
            conn.commit()
        
        print("Coach availability table created successfully")
    else:
        print("Coach availability table already exists")

def fix_booking_rule_table(engine):
    """Fix booking_rule table schema"""
    print("Checking booking_rule table...")
    
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if 'booking_rule' not in existing_tables:
        print("Creating booking_rule table...")
        create_table_sql = """
        CREATE TABLE booking_rule (
            id SERIAL PRIMARY KEY,
            coach_id INTEGER NOT NULL,
            cancellation_hours INTEGER DEFAULT 24,
            reschedule_hours INTEGER DEFAULT 12,
            no_show_policy VARCHAR(50) DEFAULT 'charge_full',
            require_payment_before BOOLEAN DEFAULT TRUE,
            allow_partial_payment BOOLEAN DEFAULT FALSE,
            send_reminder_hours INTEGER DEFAULT 24,
            send_confirmation BOOLEAN DEFAULT TRUE,
            send_cancellation BOOLEAN DEFAULT TRUE,
            sync_with_calendar BOOLEAN DEFAULT FALSE,
            calendar_provider VARCHAR(50),
            calendar_id VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_booking_rule_user FOREIGN KEY (coach_id) REFERENCES "user" (id) ON DELETE CASCADE
        );
        """
        
        with engine.connect() as conn:
            conn.execute(text(create_table_sql))
            conn.commit()
        
        print("Booking rule table created successfully")
    else:
        print("Booking rule table already exists")

def fix_calendar_integration_table(engine):
    """Fix calendar_integration table schema"""
    print("Checking calendar_integration table...")
    
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if 'calendar_integration' not in existing_tables:
        print("Creating calendar_integration table...")
        create_table_sql = """
        CREATE TABLE calendar_integration (
            id SERIAL PRIMARY KEY,
            coach_id INTEGER NOT NULL,
            provider VARCHAR(50) NOT NULL,
            calendar_id VARCHAR(255),
            access_token TEXT,
            refresh_token TEXT,
            token_expires_at TIMESTAMP,
            sync_enabled BOOLEAN DEFAULT TRUE,
            sync_direction VARCHAR(20) DEFAULT 'bidirectional',
            last_sync_at TIMESTAMP,
            selected_calendars TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_calendar_integration_user FOREIGN KEY (coach_id) REFERENCES "user" (id) ON DELETE CASCADE
        );
        """
        
        with engine.connect() as conn:
            conn.execute(text(create_table_sql))
            conn.commit()
        
        print("Calendar integration table created successfully")
    else:
        print("Calendar integration table already exists")

def fix_message_table(engine):
    """Fix message table schema to add call_id column"""
    print("Checking message table...")
    
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if 'message' in existing_tables:
        # Check if call_id column exists
        columns = [col['name'] for col in inspector.get_columns('message')]
        
        if 'call_id' not in columns:
            print("Adding call_id column to message table...")
            with engine.connect() as conn:
                # Add call_id column
                conn.execute(text("ALTER TABLE message ADD COLUMN call_id INTEGER"))
                
                # Add foreign key constraint
                try:
                    conn.execute(text("""
                        ALTER TABLE message 
                        ADD CONSTRAINT fk_message_call_id 
                        FOREIGN KEY (call_id) REFERENCES scheduled_call(id) ON DELETE SET NULL
                    """))
                except ProgrammingError:
                    # Foreign key might already exist or scheduled_call table might not exist yet
                    pass
                
                # Add index
                try:
                    conn.execute(text("CREATE INDEX ix_message_call_id ON message (call_id)"))
                except ProgrammingError:
                    # Index might already exist
                    pass
                
                conn.commit()
            print("call_id column added to message table successfully")
        else:
            print("call_id column already exists in message table")
    else:
        print("Message table does not exist, skipping call_id column addition")

if __name__ == "__main__":
    migrate_production_database()
