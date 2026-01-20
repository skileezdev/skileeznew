-- Fix Database Schema for Rescheduling System
-- Run this on your Render PostgreSQL database

-- Check if column exists first
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'session' 
        AND column_name = 'reschedule_proposed_time'
    ) THEN
        -- Add the missing column
        ALTER TABLE session ADD COLUMN reschedule_proposed_time TIMESTAMP;
        RAISE NOTICE 'Column reschedule_proposed_time added successfully';
    ELSE
        RAISE NOTICE 'Column reschedule_proposed_time already exists';
    END IF;
END $$;

-- Verify the column was added
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'session' 
AND column_name = 'reschedule_proposed_time';
