# Timezone Column Deployment Fix

## Issue
The application is failing because the `timezone` column doesn't exist in the production database on Render, but the code is trying to query it.

## Temporary Fix Applied
I've temporarily commented out the timezone column in the User model and added error handling to prevent crashes. The application will now work with UTC timezone as default.

## Permanent Fix Required

### Option 1: Manual Database Update (Recommended)
1. Connect to your Render PostgreSQL database
2. Run the SQL script in `add_timezone_column.sql`:

```sql
ALTER TABLE "user" ADD COLUMN timezone VARCHAR(50) DEFAULT 'UTC';
UPDATE "user" SET timezone = 'UTC' WHERE timezone IS NULL;
COMMENT ON COLUMN "user".timezone IS 'User timezone preference for displaying dates and times';
```

### Option 2: Using Flask-Migrate (If you have shell access)
1. Uncomment the timezone column in `models.py`:
   ```python
   # timezone = db.Column(db.String(50), default='UTC')
   ```
2. Run the migration:
   ```bash
   python -m flask db upgrade
   ```

## After Applying the Fix

1. **Uncomment the timezone column** in `models.py`:
   ```python
   # Change this line:
   # timezone = db.Column(db.String(50), default='UTC')
   # To this:
   timezone = db.Column(db.String(50), default='UTC')
   ```

2. **Remove the error handling** from the template filters in `app.py` (optional, but cleaner)

3. **Update the templates** to use the actual timezone field:
   - In `templates/profile/account_settings.html`: Change `UTC` back to `{{ user.timezone or 'UTC' }}`
   - In `templates/messages/conversation.html`: Change `"UTC"` back to `"{{ get_current_user().timezone or 'UTC' }}"`

## Current Status
- ✅ Application works with UTC timezone as default
- ✅ All timezone utility functions work
- ✅ Template filters work with fallback to UTC
- ⏳ Waiting for database column to be added

## Testing
After applying the fix:
1. Users can log in successfully
2. All time displays work (using UTC)
3. Timezone settings page shows UTC as default
4. No database errors occur

## Next Steps
1. Apply the database fix (Option 1 or 2 above)
2. Uncomment the timezone column in models.py
3. Deploy the updated code
4. Test timezone functionality
