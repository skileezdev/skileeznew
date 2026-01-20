-- Production Migration Script for Render PostgreSQL Database
-- Adds reschedule_proposed_time column to Session table

-- Check if column already exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'session' 
        AND column_name = 'reschedule_proposed_time'
    ) THEN
        -- Add the new column
        ALTER TABLE session ADD COLUMN reschedule_proposed_time TIMESTAMP;
        
        -- Log the change
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
