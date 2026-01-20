-- PostgreSQL Script to Add Google Meet Columns
-- Run this script directly against your PostgreSQL database

-- Add Google Meet columns to scheduled_session table
ALTER TABLE scheduled_session 
ADD COLUMN IF NOT EXISTS google_meet_url TEXT;

ALTER TABLE scheduled_session 
ADD COLUMN IF NOT EXISTS meeting_status VARCHAR(50) DEFAULT 'pending';

ALTER TABLE scheduled_session 
ADD COLUMN IF NOT EXISTS meeting_created_at TIMESTAMP;

ALTER TABLE scheduled_session 
ADD COLUMN IF NOT EXISTS meeting_created_by INTEGER;

ALTER TABLE scheduled_session 
ADD COLUMN IF NOT EXISTS meeting_notes TEXT;

-- Add Google Meet columns to scheduled_call table
ALTER TABLE scheduled_call 
ADD COLUMN IF NOT EXISTS google_meet_url TEXT;

ALTER TABLE scheduled_call 
ADD COLUMN IF NOT EXISTS meeting_status VARCHAR(50) DEFAULT 'pending';

ALTER TABLE scheduled_call 
ADD COLUMN IF NOT EXISTS meeting_created_at TIMESTAMP;

ALTER TABLE scheduled_call 
ADD COLUMN IF NOT EXISTS meeting_created_by INTEGER;

ALTER TABLE scheduled_call 
ADD COLUMN IF NOT EXISTS meeting_notes TEXT;

-- Verify the columns were added
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name IN ('scheduled_session', 'scheduled_call')
AND column_name IN ('google_meet_url', 'meeting_status', 'meeting_created_at', 'meeting_created_by', 'meeting_notes')
ORDER BY table_name, column_name;

-- Show success message
DO $$
BEGIN
    RAISE NOTICE 'Google Meet columns added successfully!';
    RAISE NOTICE 'Check the results above to verify all columns were created.';
END $$;
