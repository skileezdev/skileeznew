-- Fix for reschedule_proposed_time column missing error
-- This script adds the missing column to the session table

-- Check if column already exists
DO $$
BEGIN
    -- Check if the column exists
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'session' 
        AND column_name = 'reschedule_proposed_time'
    ) THEN
        -- Add the column if it doesn't exist
        ALTER TABLE session ADD COLUMN reschedule_proposed_time TIMESTAMP NULL;
        RAISE NOTICE 'Column reschedule_proposed_time added successfully';
    ELSE
        RAISE NOTICE 'Column reschedule_proposed_time already exists';
    END IF;
END $$;

-- Verify the column was added
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_name = 'session' 
AND column_name = 'reschedule_proposed_time';
