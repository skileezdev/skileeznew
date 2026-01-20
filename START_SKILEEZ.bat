@echo off
echo Starting Skileez V2.0 - Local Production Mode...

start cmd /k "cd v2_rebuild\backend && python run.py"
start cmd /k "cd v2_rebuild\frontend && npx next dev -p 3000"

echo.
echo ==========================================
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo ==========================================
echo.
echo Keep these windows open to stay online!
pause
