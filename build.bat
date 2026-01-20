@echo off
echo 🚀 Starting build process...

REM Install dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements.txt

REM Run database migration to add Google Meet columns
echo 🗄️ Running database migration...
python auto_migrate.py

REM Check if migration was successful
if %ERRORLEVEL% EQU 0 (
    echo ✅ Database migration completed successfully!
    echo 🎯 Google Meet columns are now available!
) else (
    echo ❌ Database migration failed!
    echo ⚠️ Build will continue but Google Meet functionality may not work
)

echo 🏗️ Build process completed!
pause
