# Production Database Fix

## Issue
The production database is missing the `message_type` column in the `message` table, which is causing errors when the application tries to access this field.

## Error Message
```
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedColumn) column message.message_type does not exist
```

## Solution

### Option 1: Run the Python Script (Recommended)
1. SSH into your production server
2. Navigate to your application directory
3. Run the deployment script:
   ```bash
   python deploy_database_fix.py
   ```

### Option 2: Run SQL Script Directly
1. Connect to your PostgreSQL database
2. Run the SQL script:
   ```bash
   psql -d your_database_name -f production_database_fix.sql
   ```

### Option 3: Manual SQL Commands
Connect to your PostgreSQL database and run these commands:

```sql
-- Add message_type column to message table
ALTER TABLE message ADD COLUMN message_type VARCHAR(20) DEFAULT 'TEXT';

-- Add contract acceptance columns
ALTER TABLE contract ADD COLUMN accepted_at TIMESTAMP;
ALTER TABLE contract ADD COLUMN declined_at TIMESTAMP;
ALTER TABLE contract ADD COLUMN payment_completed_at TIMESTAMP;

-- Update existing contracts to have 'pending' status
UPDATE contract SET status = 'pending' WHERE status = 'active';
```

## What This Fix Does

1. **Adds `message_type` column** to the `message` table with default value 'TEXT'
2. **Adds contract acceptance tracking columns** to the `contract` table:
   - `accepted_at`: When the coach accepts the contract
   - `declined_at`: When the coach declines the contract  
   - `payment_completed_at`: When the student completes payment
3. **Updates existing contracts** to have 'pending' status instead of 'active'

## Verification

After running the fix, you can verify the changes by checking if the columns exist:

```sql
-- Check if message_type column exists
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'message' AND column_name = 'message_type';

-- Check if contract columns exist
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'contract' AND column_name IN ('accepted_at', 'declined_at', 'payment_completed_at');
```

## Files Created

- `deploy_database_fix.py` - Python script to fix the database
- `production_database_fix.sql` - SQL script to fix the database
- `fix_production_database.py` - Local development database fix script

## Notes

- The scripts are designed to be safe and won't fail if columns already exist
- This fix is required for the enhanced contract system to work properly
- After applying this fix, the messaging system will support contract offers and system notifications
