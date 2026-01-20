# Message Type Column Fix

## Issue Description

The production database is missing the `message_type` column in the `message` table, which is causing errors when the application tries to access this field. The error occurs in the `/messages` route when trying to query messages.

**Error:**
```
psycopg2.errors.UndefinedColumn: column message.message_type does not exist
```

## Root Cause

The `Message` model in `models.py` includes a `message_type` field:
```python
message_type = db.Column(db.String(20), default='TEXT')  # TEXT, CONTRACT_OFFER, SYSTEM
```

However, the production database schema doesn't have this column, causing SQLAlchemy queries to fail.

## Solutions

### 1. Immediate Database Fix (Recommended)

Run the SQL script directly on the production database:

```sql
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
```

### 2. Automated Fix Scripts

The following scripts are available to automatically fix the database:

- `fix_production_database.py` - Main fix script
- `deploy_database_fix.py` - Deployment-specific fix script
- `render_deployment_fix.py` - Render deployment wrapper

### 3. Code Fallback (Already Implemented)

The `routes.py` file has been updated with a fallback mechanism that:
1. First tries the normal SQLAlchemy query
2. If it fails due to missing `message_type` column, falls back to a raw SQL query
3. Manually constructs Message objects with default values

## Files Modified

1. **render.yaml** - Updated build command to include database fix scripts
2. **render_deployment_fix.py** - Created new deployment fix script
3. **immediate_fix.sql** - Created immediate SQL fix script
4. **routes.py** - Added fallback mechanism for missing columns

## Verification

After applying the fix, verify that the columns exist:

```sql
SELECT 
    column_name,
    data_type,
    column_default,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'message' 
AND column_name IN ('message_type', 'sender_role', 'recipient_role')
ORDER BY column_name;
```

## Deployment

1. **Immediate Fix**: Run the SQL script directly on the production database
2. **Automatic Fix**: Deploy the updated code - the build process will automatically run the fix scripts
3. **Manual Fix**: Run `python fix_production_database.py` on the production server

## Prevention

To prevent this issue in the future:
1. Always run database migrations before deploying new code
2. Use Alembic migrations for schema changes
3. Test database schema compatibility in staging environment
4. Include database fix scripts in deployment process
