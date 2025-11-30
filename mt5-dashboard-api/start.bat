@echo off
REM Startup script for MT5 Dashboard API (Windows)

echo Starting MT5 Dashboard API...

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Create necessary directories
if not exist logs mkdir logs
if not exist data mkdir data

REM Start the application
echo Starting uvicorn server...
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2

pause
