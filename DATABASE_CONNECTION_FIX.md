# Database Connection Error - Fix Guide

## Problem
You're seeing this error:
```
could not translate host name "dpg-d3ikjck9c44c73askgs0-a" to address: Name or service not known
```

This means your `DATABASE_URL` environment variable is incomplete or malformed. The hostname is missing the domain part.

## Root Cause
The DATABASE_URL should look like:
```
postgresql://user:password@dpg-d3ikjck9c44c73askgs0-a.oregon-postgres.render.com/database
```

But it appears to be:
```
postgresql://user:password@dpg-d3ikjck9c44c73askgs0-a/database
```

## Solution

### For Render Deployments:

1. **Check Database Link in Render Dashboard:**
   - Go to your Render dashboard
   - Click on your web service (skileez)
   - Go to the "Environment" tab
   - Verify that `DATABASE_URL` is set and linked to your database
   - The database should be listed under "Linked Databases"

2. **If DATABASE_URL is not linked:**
   - Go to your database service in Render
   - Copy the "Internal Database URL" or "Connection String"
   - Go back to your web service
   - Add or update the `DATABASE_URL` environment variable
   - Make sure it includes the full hostname with domain (e.g., `.oregon-postgres.render.com`)

3. **Verify the Connection String Format:**
   The DATABASE_URL should be in this format:
   ```
   postgresql://[user]:[password]@[host]:[port]/[database]
   ```
   
   For Render, it typically looks like:
   ```
   postgresql://user:password@dpg-xxxxx.oregon-postgres.render.com:5432/dbname
   ```

4. **Restart Your Service:**
   After updating the DATABASE_URL, restart your Render service to apply the changes.

### Alternative: Check Render Database Settings

1. Go to your Render dashboard
2. Navigate to your PostgreSQL database
3. Go to the "Info" tab
4. Look for "Internal Database URL" or "Connection String"
5. Copy the full connection string (it should include the full hostname)
6. Update the DATABASE_URL environment variable in your web service

## Verification

After fixing the DATABASE_URL, you should see in your logs:
- ✅ Database connection successful
- ✅ Tables created/migrated successfully
- ✅ No more "could not translate host name" errors

## Note
This is a deployment configuration issue, not a code issue. The application code is correct, but the DATABASE_URL environment variable needs to be properly configured in your Render dashboard.

