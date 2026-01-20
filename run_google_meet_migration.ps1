# PowerShell script to run Google Meet migration
# This script will execute the migration through the Flask application

Write-Host "🚀 Starting Google Meet Migration..." -ForegroundColor Green

# Check if we're in the right directory
if (-not (Test-Path "app.py")) {
    Write-Host "❌ Error: app.py not found. Please run this script from the SKILEEZ_GOL directory." -ForegroundColor Red
    exit 1
}

# Try to find Python
$pythonPath = $null

# Check common Python locations
$pythonLocations = @(
    "python.exe",
    "python3.exe",
    "C:\Python*\python.exe",
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python*\python.exe",
    "C:\Program Files\Python*\python.exe"
)

foreach ($location in $pythonLocations) {
    try {
        $found = Get-Command $location -ErrorAction SilentlyContinue
        if ($found) {
            $pythonPath = $found.Source
            Write-Host "✅ Found Python at: $pythonPath" -ForegroundColor Green
            break
        }
    } catch {
        # Continue searching
    }
}

if (-not $pythonPath) {
    Write-Host "❌ Python not found. Please install Python or ensure it's in your PATH." -ForegroundColor Red
    Write-Host "💡 You can download Python from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Try to run the migration
Write-Host "🔧 Running Google Meet migration..." -ForegroundColor Yellow

try {
    # First try to run the original script
    Write-Host "📋 Attempting to run add_google_meet_columns.py..." -ForegroundColor Yellow
    & $pythonPath add_google_meet_columns.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Google Meet migration completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Original script failed, trying alternative approach..." -ForegroundColor Yellow
        
        # Try to run through the deployment script
        Write-Host "📋 Running deployment script with Google Meet columns..." -ForegroundColor Yellow
        & $pythonPath deploy_simple.py
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Google Meet migration completed through deployment script!" -ForegroundColor Green
        } else {
            Write-Host "❌ Migration failed. Please check the error messages above." -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "❌ Error running migration: $_" -ForegroundColor Red
    exit 1
}

Write-Host "🎉 Google Meet migration process completed!" -ForegroundColor Green
Write-Host "📋 Check the output above for any errors or success messages." -ForegroundColor Yellow
