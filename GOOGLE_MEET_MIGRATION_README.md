# Google Meet Migration Guide

This guide explains how to add Google Meet columns to your database for video call functionality.

## What This Migration Adds

The migration adds the following columns to your database tables:

### For `scheduled_call` table:
- `google_meet_url` - Stores the Google Meet meeting link
- `meeting_status` - Tracks meeting status (pending, created, active, completed)
- `meeting_created_at` - Timestamp when the meeting was created
- `meeting_created_by` - User ID who created the meeting
- `meeting_notes` - Any notes about the meeting

### For `scheduled_session` table (if it exists):
- Same columns as above

## How to Run the Migration

### Option 1: Python Script (Recommended)
If you have Python available, run:
```bash
python add_google_meet_columns.py
```

### Option 2: Modified Deployment Script
The `deploy_simple.py` script has been updated to include Google Meet columns. Run:
```bash
python deploy_simple.py
```

### Option 3: Manual SQL Execution
If you can't run Python, execute the SQL script manually:

#### For SQLite databases:
1. Open your database file (e.g., `skileez.db`) with a SQLite browser
2. Execute the SQL commands from `add_google_meet_columns.sql`
3. Focus on the SQLite section (uncomment the SQLite commands)

#### For PostgreSQL databases:
1. Connect to your database using psql or a database management tool
2. Execute the PostgreSQL section from `add_google_meet_columns.sql`
3. Uncomment the PostgreSQL section

## Verification

After running the migration, verify the columns were added:

### SQLite:
```sql
PRAGMA table_info(scheduled_call);
```

### PostgreSQL:
```sql
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'scheduled_call' 
AND column_name IN ('google_meet_url', 'meeting_status', 'meeting_created_at', 'meeting_created_by', 'meeting_notes');
```

## Troubleshooting

### "Column already exists" errors
This is normal if the columns were already added. The migration is idempotent.

### "Table doesn't exist" errors
Some tables like `scheduled_session` might not exist in your database. This is normal.

### Python not found
If you can't run Python:
1. Install Python from https://www.python.org/downloads/
2. Ensure Python is in your PATH
3. Or use the manual SQL approach

## What Happens After Migration

Once the columns are added:
1. Your existing consultation cards will work normally
2. New consultations can include Google Meet integration
3. The system can track meeting creation and status
4. Video call functionality will be available

## Support

If you encounter issues:
1. Check the error messages for specific details
2. Verify your database connection
3. Ensure you have the necessary permissions to modify tables
4. Check that the tables exist before adding columns
