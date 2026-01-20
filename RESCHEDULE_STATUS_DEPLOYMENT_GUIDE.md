# Reschedule Status Column Deployment Guide

## Issue
The application is failing with the error: `column session.reschedule_status does not exist`

This happens because the new `reschedule_status` column was added to the models but not yet deployed to the production database.

## Quick Fix Options

### Option 1: Run Python Script (Recommended)
```bash
python run_reschedule_fix.py
```

### Option 2: Run SQL Script
Execute the SQL commands in `fix_reschedule_status.sql` directly on your PostgreSQL database.

### Option 3: Manual Database Commands
Connect to your PostgreSQL database and run:
```sql
ALTER TABLE session ADD COLUMN reschedule_status VARCHAR(20) DEFAULT NULL;
ALTER TABLE scheduled_session ADD COLUMN reschedule_status VARCHAR(20) DEFAULT NULL;
```

## What This Fix Does

1. **Adds `reschedule_status` column** to both `session` and `scheduled_session` tables
2. **Sets default value to NULL** so existing records are not affected
3. **Enables the reschedule notification system** to work properly

## Verification

After running the fix, verify it worked by checking:
```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name IN ('session', 'scheduled_session') 
AND column_name = 'reschedule_status';
```

## Expected Results

- ✅ Student dashboard loads without errors
- ✅ Contract pages load without errors  
- ✅ Session management works properly
- ✅ Reschedule notifications display correctly

## Files Modified

The following files were updated to add reschedule notification features:

### Backend Changes
- `models.py` - Added `reschedule_status` field to Session and ScheduledSession models
- `routes.py` - Added notification sending when reschedule is approved/declined
- `email_utils.py` - Added email templates for reschedule notifications
- `notification_utils.py` - Added notification creation functions

### Frontend Changes  
- `templates/contracts/manage_sessions.html` - Added reschedule status indicators
- `templates/sessions/sessions_list_enhanced.html` - Added reschedule status indicators

### Database Migration
- `run_reschedule_fix.py` - Python script to add the missing column
- `fix_reschedule_status.sql` - SQL script for direct database execution

## Features Added

1. **Email Notifications** - Students receive emails when reschedule is approved/declined
2. **Message Notifications** - Chat messages appear when reschedule status changes
3. **Visual Indicators** - Color-coded status badges on session pages
4. **Database Tracking** - `reschedule_status` field tracks approval/decline status

## Testing

After deployment, test the reschedule flow:
1. Student requests a reschedule
2. Coach approves or declines
3. Student should see:
   - Email notification
   - Message in chat
   - Visual indicator on session page

## Rollback (if needed)

If issues occur, you can remove the column:
```sql
ALTER TABLE session DROP COLUMN IF EXISTS reschedule_status;
ALTER TABLE scheduled_session DROP COLUMN IF EXISTS reschedule_status;
```

But this will disable the new reschedule notification features.
