-- SQL Script to Add Google Meet Columns
-- This script adds the necessary columns for Google Meet integration
-- Run this script against your database to add the required columns

-- For PostgreSQL databases
-- Uncomment the following lines if using PostgreSQL:

/*
-- Add Google Meet columns to scheduled_call table
DO $$ 
BEGIN
    -- Add google_meet_url column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'scheduled_call' AND column_name = 'google_meet_url') THEN
        ALTER TABLE scheduled_call ADD COLUMN google_meet_url TEXT;
        RAISE NOTICE 'Added google_meet_url column to scheduled_call table';
    ELSE
        RAISE NOTICE 'google_meet_url column already exists in scheduled_call table';
    END IF;
    
    -- Add meeting_status column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'scheduled_call' AND column_name = 'meeting_status') THEN
        ALTER TABLE scheduled_call ADD COLUMN meeting_status VARCHAR(50) DEFAULT 'pending';
        RAISE NOTICE 'Added meeting_status column to scheduled_call table';
    ELSE
        RAISE NOTICE 'meeting_status column already exists in scheduled_call table';
    END IF;
    
    -- Add meeting_created_at column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'scheduled_call' AND column_name = 'meeting_created_at') THEN
        ALTER TABLE scheduled_call ADD COLUMN meeting_created_at TIMESTAMP;
        RAISE NOTICE 'Added meeting_created_at column to scheduled_call table';
    ELSE
        RAISE NOTICE 'meeting_created_at column already exists in scheduled_call table';
    END IF;
    
    -- Add meeting_created_by column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'scheduled_call' AND column_name = 'meeting_created_by') THEN
        ALTER TABLE scheduled_call ADD COLUMN meeting_created_by INTEGER;
        RAISE NOTICE 'Added meeting_created_by column to scheduled_call table';
    ELSE
        RAISE NOTICE 'meeting_created_by column already exists in scheduled_call table';
    END IF;
    
    -- Add meeting_notes column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'scheduled_call' AND column_name = 'meeting_notes') THEN
        ALTER TABLE scheduled_call ADD COLUMN meeting_notes TEXT;
        RAISE NOTICE 'Added meeting_notes column to scheduled_call table';
    ELSE
        RAISE NOTICE 'meeting_notes column already exists in scheduled_call table';
    END IF;
    
    -- Add Google Meet columns to scheduled_session table if it exists
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'scheduled_session') THEN
        -- Add google_meet_url column if it doesn't exist
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_name = 'scheduled_session' AND column_name = 'google_meet_url') THEN
            ALTER TABLE scheduled_session ADD COLUMN google_meet_url TEXT;
            RAISE NOTICE 'Added google_meet_url column to scheduled_session table';
        ELSE
            RAISE NOTICE 'google_meet_url column already exists in scheduled_session table';
        END IF;
        
        -- Add meeting_status column if it doesn't exist
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_name = 'scheduled_session' AND column_name = 'meeting_status') THEN
            ALTER TABLE scheduled_session ADD COLUMN meeting_status VARCHAR(50) DEFAULT 'pending';
            RAISE NOTICE 'Added meeting_status column to scheduled_session table';
        ELSE
            RAISE NOTICE 'meeting_status column already exists in scheduled_session table';
        END IF;
        
        -- Add meeting_created_at column if it doesn't exist
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_name = 'scheduled_session' AND column_name = 'meeting_created_at') THEN
            ALTER TABLE scheduled_session ADD COLUMN meeting_created_at TIMESTAMP;
            RAISE NOTICE 'Added meeting_created_at column to scheduled_session table';
        ELSE
            RAISE NOTICE 'meeting_created_at column already exists in scheduled_session table';
        END IF;
        
        -- Add meeting_created_by column if it doesn't exist
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_name = 'scheduled_session' AND column_name = 'meeting_created_by') THEN
            ALTER TABLE scheduled_session ADD COLUMN meeting_created_by INTEGER;
            RAISE NOTICE 'Added meeting_created_by column to scheduled_session table';
        ELSE
            RAISE NOTICE 'meeting_created_by column already exists in scheduled_session table';
        END IF;
        
        -- Add meeting_notes column if it doesn't exist
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_name = 'scheduled_session' AND column_name = 'meeting_notes') THEN
            ALTER TABLE scheduled_session ADD COLUMN meeting_notes TEXT;
            RAISE NOTICE 'Added meeting_notes column to scheduled_session table';
        ELSE
            RAISE NOTICE 'meeting_notes column already exists in scheduled_session table';
        END IF;
    ELSE
        RAISE NOTICE 'scheduled_session table does not exist, skipping';
    END IF;
END $$;
*/

-- For SQLite databases
-- Uncomment the following lines if using SQLite:

-- Add Google Meet columns to scheduled_call table
-- Note: SQLite doesn't support IF NOT EXISTS for ALTER TABLE, so these will fail if columns already exist

-- Add google_meet_url column
ALTER TABLE scheduled_call ADD COLUMN google_meet_url TEXT;

-- Add meeting_status column
ALTER TABLE scheduled_call ADD COLUMN meeting_status TEXT DEFAULT 'pending';

-- Add meeting_created_at column
ALTER TABLE scheduled_call ADD COLUMN meeting_created_at DATETIME;

-- Add meeting_created_by column
ALTER TABLE scheduled_call ADD COLUMN meeting_created_by INTEGER;

-- Add meeting_notes column
ALTER TABLE scheduled_call ADD COLUMN meeting_notes TEXT;

-- Note: If you get "duplicate column name" errors, it means the columns already exist
-- This is normal and expected behavior

-- For scheduled_session table (if it exists)
-- Uncomment these lines if you have a scheduled_session table:

/*
ALTER TABLE scheduled_session ADD COLUMN google_meet_url TEXT;
ALTER TABLE scheduled_session ADD COLUMN meeting_status TEXT DEFAULT 'pending';
ALTER TABLE scheduled_session ADD COLUMN meeting_created_at DATETIME;
ALTER TABLE scheduled_session ADD COLUMN meeting_created_by INTEGER;
ALTER TABLE scheduled_session ADD COLUMN meeting_notes TEXT;
*/

-- Verification queries
-- Run these to check if the columns were added successfully:

-- Check scheduled_call table structure
PRAGMA table_info(scheduled_call);

-- Check if Google Meet columns exist
SELECT name FROM pragma_table_info('scheduled_call') 
WHERE name IN ('google_meet_url', 'meeting_status', 'meeting_created_at', 'meeting_created_by', 'meeting_notes');
