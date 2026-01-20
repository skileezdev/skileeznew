-- Immediate fix for missing message_type column in production database
-- Run this script directly on the production PostgreSQL database

-- Check if message_type column exists, if not add it
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'message' AND column_name = 'message_type'
    ) THEN
        ALTER TABLE message ADD COLUMN message_type VARCHAR(20) DEFAULT 'TEXT';
        RAISE NOTICE 'Added message_type column to message table';
    ELSE
        RAISE NOTICE 'message_type column already exists in message table';
    END IF;
END $$;

-- Check if sender_role column exists, if not add it
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'message' AND column_name = 'sender_role'
    ) THEN
        ALTER TABLE message ADD COLUMN sender_role VARCHAR(20);
        RAISE NOTICE 'Added sender_role column to message table';
    ELSE
        RAISE NOTICE 'sender_role column already exists in message table';
    END IF;
END $$;

-- Check if recipient_role column exists, if not add it
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'message' AND column_name = 'recipient_role'
    ) THEN
        ALTER TABLE message ADD COLUMN recipient_role VARCHAR(20);
        RAISE NOTICE 'Added recipient_role column to message table';
    ELSE
        RAISE NOTICE 'recipient_role column already exists in message table';
    END IF;
END $$;

-- Verify the fix
SELECT 
    column_name,
    data_type,
    column_default,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'message' 
AND column_name IN ('message_type', 'sender_role', 'recipient_role')
ORDER BY column_name;
