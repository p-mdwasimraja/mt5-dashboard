@echo off
echo ================================================
echo      MT5 PORTFOLIO DASHBOARD - FASTAPI SERVER
echo ================================================
echo.

cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [WARN] No venv found. Create one with: python -m venv venv
)

echo [INFO] Starting FastAPI server on http://127.0.0.1:8010
echo Logs will be saved to logs_fastapi.txt
echo Press CTRL+C to stop.
echo.

uvicorn app.main:app --host 127.0.0.1 --port 8010 --workers 1 >> logs_fastapi.txt 2>&1
