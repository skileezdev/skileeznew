-- Fix reschedule_status column issue
-- Run this SQL script on the production database

-- Add reschedule_status column to session table if it doesn't exist
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

-- Add reschedule_status column to scheduled_session table if it doesn't exist
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

-- Verify the columns exist
SELECT 
    table_name, 
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns 
WHERE table_name IN ('session', 'scheduled_session') 
AND column_name = 'reschedule_status'
ORDER BY table_name;
