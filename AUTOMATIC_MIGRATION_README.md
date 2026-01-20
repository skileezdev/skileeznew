# Automatic Database Migration System

This system ensures that your database schema is automatically updated during every Render deployment, eliminating the need for manual database migrations.

## 🚀 How It Works

### 1. **Build Process Integration**
- **`build.sh`** (Linux/Mac) and **`build.bat`** (Windows) are executed during Render's build process
- These scripts automatically run the database migration before your app starts
- No manual intervention required - happens automatically on every deploy

### 2. **Migration Scripts**
- **`auto_migrate.py`** - Main migration script with database availability checking
- **`fix_render_database.py`** - Original migration script (backup)
- Both scripts add the required Google Meet columns to your database

### 3. **Render Configuration**
- **`render.yaml`** is configured to run the build script automatically
- Database migration happens before the app starts
- Ensures database is ready before users can access the app

## 📋 What Gets Added

### scheduled_session table:
- `google_meet_url` (TEXT)
- `meeting_status` (VARCHAR(50), default 'pending')
- `meeting_created_at` (TIMESTAMP)
- `meeting_created_by` (INTEGER)
- `meeting_notes` (TEXT)

### scheduled_call table:
- `google_meet_url` (TEXT)
- `meeting_status` (VARCHAR(50), default 'pending')
- `meeting_created_at` (TIMESTAMP)
- `meeting_created_by` (INTEGER)
- `meeting_notes` (TEXT)

## 🔧 Files Created/Modified

1. **`build.sh`** - Linux/Mac build script
2. **`build.bat`** - Windows build script  
3. **`auto_migrate.py`** - Enhanced migration script
4. **`render.yaml`** - Updated to use build script
5. **`AUTOMATIC_MIGRATION_README.md`** - This documentation

## ✅ Benefits

- **Automatic**: No manual database updates needed
- **Reliable**: Runs on every deployment
- **Safe**: Only adds missing columns, won't duplicate
- **Fast**: Database is ready before app starts
- **Transparent**: Clear logging of what's happening

## 🚀 Deployment Process

1. **Push code to your repository**
2. **Render automatically triggers build**
3. **Build script installs dependencies**
4. **Database migration runs automatically**
5. **App starts with updated database schema**
6. **Google Meet functionality works immediately**

## 🔍 Troubleshooting

### If migration fails:
- Check Render build logs for error messages
- Verify `DATABASE_URL` environment variable is set
- Ensure database is accessible during build
- Migration failure won't stop app deployment

### Manual override:
- You can still run `python auto_migrate.py` manually if needed
- Use `python fix_render_database.py` as backup option

## 📝 Build Logs

During deployment, you'll see logs like:
```
🚀 Starting Render build process...
📦 Installing Python dependencies...
🗄️ Running database migration...
⏳ Waiting for database to be available...
✅ Database is available!
🔗 Connecting to database...
✅ Connected to database successfully!
🔍 Checking existing columns...
➕ Adding columns to scheduled_session table...
✅ Added google_meet_url to scheduled_session
...
🎯 Database migration completed successfully!
✅ Database migration completed successfully!
🎯 Google Meet columns are now available!
🏗️ Build process completed!
```

## 🎯 Result

After deployment:
- ✅ "Schedule Free Meeting" button works
- ✅ "Setup Meeting" button works  
- ✅ Background system runs without crashes
- ✅ Google Meet integration fully functional
- ✅ No manual database intervention needed

## 🔄 Future Updates

To add more database columns in the future:
1. Update `auto_migrate.py` with new column definitions
2. Push to repository
3. Render automatically applies changes on next deployment

This system ensures your database is always up-to-date with your application requirements!
