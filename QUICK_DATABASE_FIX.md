# Quick Database Fix Guide

Since we can't run Python directly due to the Microsoft Store Python alias issue, here's how to add the Google Meet columns manually:

## Option 1: Run SQL Script Directly

1. **Connect to your PostgreSQL database** using:
   - pgAdmin (GUI tool)
   - psql command line
   - Any database management tool

2. **Execute the SQL script**:
   ```sql
   -- Copy and paste the contents of add_google_meet_columns_postgres.sql
   ```

## Option 2: Use Database Management Tool

1. **Open your database** in pgAdmin, DBeaver, or similar tool
2. **Run these commands** one by one:

### For scheduled_session table:
```sql
ALTER TABLE scheduled_session ADD COLUMN IF NOT EXISTS google_meet_url TEXT;
ALTER TABLE scheduled_session ADD COLUMN IF NOT EXISTS meeting_status VARCHAR(50) DEFAULT 'pending';
ALTER TABLE scheduled_session ADD COLUMN IF NOT EXISTS meeting_created_at TIMESTAMP;
ALTER TABLE scheduled_session ADD COLUMN IF NOT EXISTS meeting_created_by INTEGER;
ALTER TABLE scheduled_session ADD COLUMN IF NOT EXISTS meeting_notes TEXT;
```

### For scheduled_call table:
```sql
ALTER TABLE scheduled_call ADD COLUMN IF NOT EXISTS google_meet_url TEXT;
ALTER TABLE scheduled_call ADD COLUMN IF NOT EXISTS meeting_status VARCHAR(50) DEFAULT 'pending';
ALTER TABLE scheduled_call ADD COLUMN IF NOT EXISTS meeting_created_at TIMESTAMP;
ALTER TABLE scheduled_call ADD COLUMN IF NOT EXISTS meeting_created_by INTEGER;
ALTER TABLE scheduled_call ADD COLUMN IF NOT EXISTS meeting_notes TEXT;
```

## Option 3: Fix Python Installation

To run the Python script in the future:

1. **Download Python** from https://www.python.org/downloads/
2. **Install with "Add to PATH" checked**
3. **Disable Microsoft Store Python alias**:
   - Go to Windows Settings > Apps > Advanced app settings > App execution aliases
   - Turn OFF "python.exe" and "python3.exe"

## Verification

After running the SQL, verify the columns were added:

```sql
SELECT 
    table_name,
    column_name,
    data_type
FROM information_schema.columns 
WHERE table_name IN ('scheduled_session', 'scheduled_call')
AND column_name IN ('google_meet_url', 'meeting_status', 'meeting_created_at', 'meeting_created_by', 'meeting_notes')
ORDER BY table_name, column_name;
```

## What This Adds

- ✅ `google_meet_url` - For storing meeting links
- ✅ `meeting_status` - For tracking meeting state
- ✅ `meeting_created_at` - For creation timestamps
- ✅ `meeting_created_by` - For tracking who created meetings
- ✅ `meeting_notes` - For meeting-related notes

The `IF NOT EXISTS` clause ensures this won't break if columns already exist.
