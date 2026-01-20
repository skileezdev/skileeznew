@echo off
echo 🚨 EMERGENCY DATABASE FIX
echo ========================
echo.
echo This script will fix the database transaction error
echo.
echo Please run the following SQL commands on your PostgreSQL database:
echo.
echo 1. ROLLBACK;
echo 2. ALTER TABLE session ADD COLUMN IF NOT EXISTS reschedule_status VARCHAR(20) DEFAULT NULL;
echo 3. ALTER TABLE scheduled_session ADD COLUMN IF NOT EXISTS reschedule_status VARCHAR(20) DEFAULT NULL;
echo.
echo Or run the emergency_fix.sql file directly on your database.
echo.
echo After running the SQL commands, restart your application.
echo.
pause
