-- Production Database Schema Fix
-- Run this script on the production PostgreSQL database to add missing columns

-- Add message_type column to message table
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

-- Add contract acceptance columns
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'contract' AND column_name = 'accepted_at'
    ) THEN
        ALTER TABLE contract ADD COLUMN accepted_at TIMESTAMP;
        RAISE NOTICE 'Added accepted_at column to contract table';
    ELSE
        RAISE NOTICE 'accepted_at column already exists in contract table';
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'contract' AND column_name = 'declined_at'
    ) THEN
        ALTER TABLE contract ADD COLUMN declined_at TIMESTAMP;
        RAISE NOTICE 'Added declined_at column to contract table';
    ELSE
        RAISE NOTICE 'declined_at column already exists in contract table';
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'contract' AND column_name = 'payment_completed_at'
    ) THEN
        ALTER TABLE contract ADD COLUMN payment_completed_at TIMESTAMP;
        RAISE NOTICE 'Added payment_completed_at column to contract table';
    ELSE
        RAISE NOTICE 'payment_completed_at column already exists in contract table';
    END IF;
END $$;

-- Update existing contracts to have 'pending' status
UPDATE contract SET status = 'pending' WHERE status = 'active';

-- Verify the changes
SELECT 'message_type' as column_name, 
       EXISTS(SELECT 1 FROM information_schema.columns 
              WHERE table_name = 'message' AND column_name = 'message_type') as exists
UNION ALL
SELECT 'accepted_at' as column_name,
       EXISTS(SELECT 1 FROM information_schema.columns 
              WHERE table_name = 'contract' AND column_name = 'accepted_at') as exists
UNION ALL
SELECT 'declined_at' as column_name,
       EXISTS(SELECT 1 FROM information_schema.columns 
              WHERE table_name = 'contract' AND column_name = 'declined_at') as exists
UNION ALL
SELECT 'payment_completed_at' as column_name,
       EXISTS(SELECT 1 FROM information_schema.columns 
              WHERE table_name = 'contract' AND column_name = 'payment_completed_at') as exists;
