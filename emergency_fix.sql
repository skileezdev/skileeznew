-- EMERGENCY DATABASE FIX
-- Run this SQL script to fix the InFailedSqlTransaction error

-- 1. Roll back any failed transactions
ROLLBACK;

-- 2. Add missing reschedule_status column to session table
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'session' AND column_name = 'reschedule_status'
    ) THEN
        ALTER TABLE session ADD COLUMN reschedule_status VARCHAR(20) DEFAULT NULL;
        RAISE NOTICE 'Added reschedule_status column to session table';
    ELSE
        RAISE NOTICE 'reschedule_status column already exists in session table';
    END IF;
END $$;

-- 3. Add missing reschedule_status column to scheduled_session table
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'scheduled_session' AND column_name = 'reschedule_status'
    ) THEN
        ALTER TABLE scheduled_session ADD COLUMN reschedule_status VARCHAR(20) DEFAULT NULL;
        RAISE NOTICE 'Added reschedule_status column to scheduled_session table';
    ELSE
        RAISE NOTICE 'reschedule_status column already exists in scheduled_session table';
    END IF;
END $$;

-- 4. Test database connectivity
SELECT 'Database fix completed successfully' as status;

-- 5. Test the previously failing queries
SELECT COUNT(*) as proposal_count 
FROM proposal 
JOIN learning_request ON learning_request.id = proposal.learning_request_id 
WHERE learning_request.student_id = 2;

SELECT COUNT(*) as request_count 
FROM learning_request 
WHERE student_id = 2 AND is_active = true;
