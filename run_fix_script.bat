@echo off
echo 🚀 Running Database Fix Script...
echo.

REM Try to find Python in common locations
set PYTHON_FOUND=0

REM Check if python is in PATH
where python.exe >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo ✅ Found Python in PATH
    set PYTHON_CMD=python.exe
    set PYTHON_FOUND=1
) else (
    echo ❌ Python not found in PATH
    echo 🔍 Searching for Python installations...
    
    REM Check common Python installation locations
    if exist "C:\Python*\python.exe" (
        for /d %%i in (C:\Python*) do (
            if exist "%%i\python.exe" (
                echo ✅ Found Python at: %%i\python.exe
                set PYTHON_CMD="%%i\python.exe"
                set PYTHON_FOUND=1
                goto :found_python
            )
        )
    )
    
    if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python*\python.exe" (
        for /d %%i in (C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python*) do (
            if exist "%%i\python.exe" (
                echo ✅ Found Python at: %%i\python.exe
                set PYTHON_CMD="%%i\python.exe"
                set PYTHON_FOUND=1
                goto :found_python
            )
        )
    )
    
    if exist "C:\Program Files\Python*\python.exe" (
        for /d %%i in (C:\Program Files\Python*) do (
            if exist "%%i\python.exe" (
                echo ✅ Found Python at: %%i\python.exe
                set PYTHON_CMD="%%i\python.exe"
                set PYTHON_FOUND=1
                goto :found_python
            )
        )
    )
)

:found_python

if %PYTHON_FOUND% == 0 (
    echo ❌ No Python installation found
    echo 💡 Please install Python from https://www.python.org/downloads/
    echo 💡 Make sure to check "Add to PATH" during installation
    pause
    exit /b 1
)

echo.
echo 🔧 Running database fix script...
echo.

REM Run the Python script
%PYTHON_CMD% fix_database_columns.py

if %ERRORLEVEL% == 0 (
    echo ✅ Script completed successfully!
) else (
    echo ❌ Script failed with error code: %ERRORLEVEL%
    echo 💡 Check the error messages above for details
)

echo.
echo 📋 Script execution completed
pause
