-- Production migration script to add reschedule_proposed_time column to session table
-- This fixes the error: column session.reschedule_proposed_time does not exist

-- Check if column exists and add it if it doesn't
DO $$
BEGIN
    -- Check if the column exists
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'session' 
        AND column_name = 'reschedule_proposed_time'
    ) THEN
        -- Add the column
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