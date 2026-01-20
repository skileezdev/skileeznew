-- Manual SQL script to add missing columns to PostgreSQL database
-- Run this script directly in your PostgreSQL database

-- Reset any pending transactions
ROLLBACK;

-- Add Coach Profile Stripe columns
DO $$
BEGIN
    -- Add stripe_account_id if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'coach_profile' AND column_name = 'stripe_account_id'
    ) THEN
        ALTER TABLE coach_profile ADD COLUMN stripe_account_id VARCHAR(255);
        RAISE NOTICE 'Added stripe_account_id to coach_profile';
    ELSE
        RAISE NOTICE 'stripe_account_id already exists in coach_profile';
    END IF;
    
    -- Add stripe_account_status if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'coach_profile' AND column_name = 'stripe_account_status'
    ) THEN
        ALTER TABLE coach_profile ADD COLUMN stripe_account_status VARCHAR(50);
        RAISE NOTICE 'Added stripe_account_status to coach_profile';
    ELSE
        RAISE NOTICE 'stripe_account_status already exists in coach_profile';
    END IF;
END $$;

-- Add Contract Payment columns
DO $$
BEGIN
    -- Add stripe_payment_intent_id if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'contract' AND column_name = 'stripe_payment_intent_id'
    ) THEN
        ALTER TABLE contract ADD COLUMN stripe_payment_intent_id VARCHAR(255);
        RAISE NOTICE 'Added stripe_payment_intent_id to contract';
    ELSE
        RAISE NOTICE 'stripe_payment_intent_id already exists in contract';
    END IF;
    
    -- Add payment_date if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'contract' AND column_name = 'payment_date'
    ) THEN
        ALTER TABLE contract ADD COLUMN payment_date TIMESTAMP;
        RAISE NOTICE 'Added payment_date to contract';
    ELSE
        RAISE NOTICE 'payment_date already exists in contract';
    END IF;
END $$;

-- Add Session Payment columns
DO $$
BEGIN
    -- Add stripe_transfer_id if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'session_payment' AND column_name = 'stripe_transfer_id'
    ) THEN
        ALTER TABLE session_payment ADD COLUMN stripe_transfer_id VARCHAR(255);
        RAISE NOTICE 'Added stripe_transfer_id to session_payment';
    ELSE
        RAISE NOTICE 'stripe_transfer_id already exists in session_payment';
    END IF;
    
    -- Add transfer_date if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'session_payment' AND column_name = 'transfer_date'
    ) THEN
        ALTER TABLE session_payment ADD COLUMN transfer_date TIMESTAMP;
        RAISE NOTICE 'Added transfer_date to session_payment';
    ELSE
        RAISE NOTICE 'transfer_date already exists in session_payment';
    END IF;
END $$;

-- Verify all columns were added
SELECT 
    table_name,
    column_name,
    data_type
FROM information_schema.columns 
WHERE table_name IN ('coach_profile', 'contract', 'session_payment')
    AND column_name IN (
        'stripe_account_id', 'stripe_account_status',
        'stripe_payment_intent_id', 'payment_date',
        'stripe_transfer_id', 'transfer_date'
    )
ORDER BY table_name, column_name;
