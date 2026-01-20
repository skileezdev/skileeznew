@echo off
echo 🚀 Starting Google Meet Migration...
echo.

REM Check if we're in the right directory
if not exist "app.py" (
    echo ❌ Error: app.py not found. Please run this script from the SKILEEZ_GOL directory.
    pause
    exit /b 1
)

REM Try to find Python
set PYTHON_PATH=

REM Check common Python locations
where python.exe >nul 2>&1
if %ERRORLEVEL% == 0 (
    set PYTHON_PATH=python.exe
    echo ✅ Found Python in PATH
) else (
    where python3.exe >nul 2>&1
    if %ERRORLEVEL% == 0 (
        set PYTHON_PATH=python3.exe
        echo ✅ Found Python3 in PATH
    ) else (
        echo ❌ Python not found in PATH
        echo 💡 Please install Python or ensure it's in your PATH
        echo 💡 You can download Python from: https://www.python.org/downloads/
        pause
        exit /b 1
    )
)

echo 🔧 Running Google Meet migration...
echo.

REM Try to run the original script
echo 📋 Attempting to run add_google_meet_columns.py...
%PYTHON_PATH% add_google_meet_columns.py

if %ERRORLEVEL% == 0 (
    echo ✅ Google Meet migration completed successfully!
) else (
    echo ⚠️  Original script failed, trying alternative approach...
    echo.
    
    REM Try to run through the deployment script
    echo 📋 Running deployment script with Google Meet columns...
    %PYTHON_PATH% deploy_simple.py
    
    if %ERRORLEVEL% == 0 (
        echo ✅ Google Meet migration completed through deployment script!
    ) else (
        echo ❌ Migration failed. Please check the error messages above.
        pause
        exit /b 1
    )
)

echo.
echo 🎉 Google Meet migration process completed!
echo 📋 Check the output above for any errors or success messages.
pause
