from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

FIX_SQL = """
-- Defensive script to align User table naming and fix constraints in Skileez V2
DO $$
BEGIN
    -- 1. If 'users' exists but 'user' does not, rename 'users' to 'user'
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users' AND table_schema = 'public') 
       AND NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'user' AND table_schema = 'public') THEN
        ALTER TABLE users RENAME TO "user";
        RAISE NOTICE 'Renamed users table to user';
    END IF;

    -- 2. If BOTH exist, resolve the conflict
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users' AND table_schema = 'public') 
       AND EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'user' AND table_schema = 'public') THEN
        
        -- Check if 'user' table is empty
        IF NOT EXISTS (SELECT 1 FROM "user" LIMIT 1) THEN
            -- 'user' is empty, safe to drop and rename 'users'
            DROP TABLE "user" CASCADE;
            ALTER TABLE users RENAME TO "user";
            RAISE NOTICE 'Dropped empty user table and renamed users to user';
        END IF;
    END IF;
END $$;

-- 3. Fix Foreign Key Constraints for all related tables
DO $$
BEGIN
    -- Student Profile
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE table_name = 'student_profile' AND constraint_name = 'student_profile_user_id_fkey') THEN
        ALTER TABLE student_profile DROP CONSTRAINT student_profile_user_id_fkey;
    END IF;
    ALTER TABLE student_profile ADD CONSTRAINT student_profile_user_id_fkey FOREIGN KEY (user_id) REFERENCES "user" (id) ON DELETE CASCADE;

    -- Coach Profile
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE table_name = 'coach_profile' AND constraint_name = 'coach_profile_user_id_fkey') THEN
        ALTER TABLE coach_profile DROP CONSTRAINT coach_profile_user_id_fkey;
    END IF;
    ALTER TABLE coach_profile ADD CONSTRAINT coach_profile_user_id_fkey FOREIGN KEY (user_id) REFERENCES "user" (id) ON DELETE CASCADE;

    -- Learning Request
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE table_name = 'learning_request' AND constraint_name = 'learning_request_student_id_fkey') THEN
        ALTER TABLE learning_request DROP CONSTRAINT learning_request_student_id_fkey;
    END IF;
    ALTER TABLE learning_request ADD CONSTRAINT learning_request_student_id_fkey FOREIGN KEY (student_id) REFERENCES "user" (id) ON DELETE CASCADE;

    -- Proposal
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE table_name = 'proposal' AND constraint_name = 'proposal_coach_id_fkey') THEN
        ALTER TABLE proposal DROP CONSTRAINT proposal_coach_id_fkey;
    END IF;
    ALTER TABLE proposal ADD CONSTRAINT proposal_coach_id_fkey FOREIGN KEY (coach_id) REFERENCES "user" (id) ON DELETE CASCADE;

    -- Contract (Student)
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE table_name = 'contract' AND constraint_name = 'contract_student_id_fkey') THEN
        ALTER TABLE contract DROP CONSTRAINT contract_student_id_fkey;
    END IF;
    ALTER TABLE contract ADD CONSTRAINT contract_student_id_fkey FOREIGN KEY (student_id) REFERENCES "user" (id) ON DELETE CASCADE;

    -- Contract (Coach)
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE table_name = 'contract' AND constraint_name = 'contract_coach_id_fkey') THEN
        ALTER TABLE contract DROP CONSTRAINT contract_coach_id_fkey;
    END IF;
    ALTER TABLE contract ADD CONSTRAINT contract_coach_id_fkey FOREIGN KEY (coach_id) REFERENCES "user" (id) ON DELETE CASCADE;

    -- Message Sender
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE table_name = 'message' AND constraint_name = 'message_sender_id_fkey') THEN
        ALTER TABLE message DROP CONSTRAINT message_sender_id_fkey;
    END IF;
    ALTER TABLE message ADD CONSTRAINT message_sender_id_fkey FOREIGN KEY (sender_id) REFERENCES "user" (id) ON DELETE CASCADE;

    -- Message Recipient
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE table_name = 'message' AND constraint_name = 'message_recipient_id_fkey') THEN
        ALTER TABLE message DROP CONSTRAINT message_recipient_id_fkey;
    END IF;
    ALTER TABLE message ADD CONSTRAINT message_recipient_id_fkey FOREIGN KEY (recipient_id) REFERENCES "user" (id) ON DELETE CASCADE;

    -- Notification
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE table_name = 'notification' AND constraint_name = 'notification_user_id_fkey') THEN
        ALTER TABLE notification DROP CONSTRAINT notification_user_id_fkey;
    END IF;
    ALTER TABLE notification ADD CONSTRAINT notification_user_id_fkey FOREIGN KEY (user_id) REFERENCES "user" (id) ON DELETE CASCADE;
END $$;
"""

async def apply_database_fixes(conn):
    """Executes SQL to align user table and constraints if on PostgreSQL"""
    # Check if we are on PostgreSQL
    try:
        # Use connection's dialect to check
        if conn.dialect.name == 'postgresql':
            logger.info("Applying PostgreSQL schema fixes...")
            await conn.execute(text(FIX_SQL))
            logger.info("Database schema fixes applied successfully.")
        else:
            logger.info(f"Skipping database fixes for dialect: {conn.dialect.name}")
    except Exception as e:
        logger.error(f"Error applying database fixes: {e}")
        # We don't want to crash the whole app if this fails, 
        # but the error will be in the logs.
