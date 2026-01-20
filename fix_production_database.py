#!/usr/bin/env python3
"""
Fix production database issues
This script runs during Render deployment to ensure the database schema is up to date
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import ProgrammingError

def fix_production_database():
    """Fix production database schema issues"""
    print("Checking production database schema...")
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("No DATABASE_URL found, skipping database fixes")
        return
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        # Check if notification table exists
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        # Create notification table if missing
        if 'notification' not in existing_tables:
            print("Notification table missing, creating it...")
            
            create_notification_table_sql = """
            CREATE TABLE IF NOT EXISTS notification (
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
        
        # Check and add missing columns to user table
        try:
            with engine.connect() as conn:
                # Get existing columns
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'user'
                """))
                existing_columns = [row[0] for row in result.fetchall()]
                
                # Define required columns and their definitions
                required_columns = {
                    'timezone': 'VARCHAR(50) DEFAULT \'UTC\'',
                    'new_email': 'VARCHAR(120)',
                    'email_change_token': 'VARCHAR(255)',
                    'email_change_token_created_at': 'TIMESTAMP',
                    'role_switch_enabled': 'BOOLEAN DEFAULT TRUE',
                    'last_role_switch': 'TIMESTAMP',
                    'role_switch_count': 'INTEGER DEFAULT 0',
                    'preferred_default_role': 'VARCHAR(20)',
                    'current_role': 'VARCHAR(20)',
                    'email_verified': 'BOOLEAN DEFAULT FALSE',
                    'verification_token': 'VARCHAR(255)',
                    'token_created_at': 'TIMESTAMP',
                    'stripe_customer_id': 'VARCHAR(255)'
                }
                
                # Add missing columns
                for column_name, column_def in required_columns.items():
                    if column_name not in existing_columns:
                        print(f"Adding missing {column_name} column to user table...")
                        try:
                            conn.execute(text(f'ALTER TABLE "user" ADD COLUMN {column_name} {column_def}'))
                            print(f"{column_name} column added successfully")
                        except Exception as col_error:
                            print(f"Error adding {column_name} column: {col_error}")
                
                conn.commit()
                print("User table column check completed")
        except Exception as e:
            print(f"Error checking/adding user table columns: {e}")
        
        # Create scheduled_call table if missing
        if 'scheduled_call' not in existing_tables:
            print("Scheduled call table missing, creating it...")
            
            create_scheduled_call_table_sql = """
            CREATE TABLE IF NOT EXISTS scheduled_call (
                id SERIAL PRIMARY KEY,
                student_id INTEGER NOT NULL,
                coach_id INTEGER NOT NULL,
                call_type VARCHAR(50) NOT NULL DEFAULT 'free_consultation',
                scheduled_at TIMESTAMP NOT NULL,
                duration_minutes INTEGER NOT NULL DEFAULT 15,
                status VARCHAR(50) NOT NULL DEFAULT 'scheduled',
                
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
                CONSTRAINT fk_scheduled_call_contract FOREIGN KEY (contract_id) REFERENCES contract (id) ON DELETE SET NULL
            );
            """
            
            create_scheduled_call_indexes_sql = """
            CREATE INDEX IF NOT EXISTS ix_scheduled_call_student_id ON scheduled_call (student_id);
            CREATE INDEX IF NOT EXISTS ix_scheduled_call_coach_id ON scheduled_call (coach_id);
            CREATE INDEX IF NOT EXISTS ix_scheduled_call_scheduled_at ON scheduled_call (scheduled_at);
            CREATE INDEX IF NOT EXISTS ix_scheduled_call_status ON scheduled_call (status);
            CREATE INDEX IF NOT EXISTS ix_scheduled_call_contract_id ON scheduled_call (contract_id);
            """
            
            with engine.connect() as conn:
                conn.execute(text(create_scheduled_call_table_sql))
                conn.execute(text(create_scheduled_call_indexes_sql))
                conn.commit()
            
            print("Scheduled call table created successfully")
        else:
            print("Scheduled call table already exists")
            

        
        # Create call_notification table if missing
        if 'call_notification' not in existing_tables:
            print("Call notification table missing, creating it...")
            
            create_call_notification_table_sql = """
            CREATE TABLE IF NOT EXISTS call_notification (
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
            
            create_call_notification_indexes_sql = """
            CREATE INDEX IF NOT EXISTS ix_call_notification_call_id ON call_notification (call_id);
            CREATE INDEX IF NOT EXISTS ix_call_notification_type ON call_notification (notification_type);
            CREATE INDEX IF NOT EXISTS ix_call_notification_sent_at ON call_notification (sent_at);
            """
            
            with engine.connect() as conn:
                conn.execute(text(create_call_notification_table_sql))
                conn.execute(text(create_call_notification_indexes_sql))
                conn.commit()
            
            print("Call notification table created successfully")
        else:
            print("Call notification table already exists")
        
        # Create coach_availability table if missing
        if 'coach_availability' not in existing_tables:
            print("Coach availability table missing, creating it...")
            
            create_coach_availability_table_sql = """
            CREATE TABLE IF NOT EXISTS coach_availability (
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
                conn.execute(text(create_coach_availability_table_sql))
                conn.commit()
            
            print("Coach availability table created successfully")
        else:
            print("Coach availability table already exists")
        
        # Create booking_rule table if missing
        if 'booking_rule' not in existing_tables:
            print("Booking rule table missing, creating it...")
            
            create_booking_rule_table_sql = """
            CREATE TABLE IF NOT EXISTS booking_rule (
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
                conn.execute(text(create_booking_rule_table_sql))
                conn.commit()
            
            print("Booking rule table created successfully")
        else:
            print("Booking rule table already exists")
        
        # Create calendar_integration table if missing
        if 'calendar_integration' not in existing_tables:
            print("Calendar integration table missing, creating it...")
            
            create_calendar_integration_table_sql = """
            CREATE TABLE IF NOT EXISTS calendar_integration (
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
                conn.execute(text(create_calendar_integration_table_sql))
                conn.commit()
            
            print("Calendar integration table created successfully")
        else:
            print("Calendar integration table already exists")
        
        # Check if duration_minutes column exists in contract table
        try:
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'contract' 
                    AND column_name = 'duration_minutes'
                """))
                if not result.fetchone():
                    print("Adding missing duration_minutes column to contract table...")
                    conn.execute(text("ALTER TABLE contract ADD COLUMN duration_minutes INTEGER NOT NULL DEFAULT 60"))
                    conn.commit()
                    print("duration_minutes column added successfully")
                else:
                    print("duration_minutes column already exists")
        except Exception as e:
            print(f"Error checking/adding duration_minutes column: {e}")
            
    except Exception as e:
        print(f"Error fixing production database: {e}")
        # Don't fail the deployment if database fix fails
        pass

if __name__ == "__main__":
    fix_production_database()
