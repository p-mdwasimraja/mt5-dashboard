@echo off
echo ================================================
echo   MT5 Auto Dashboard - FastAPI Setup
echo ================================================
echo.
cd /d "%~dp0"
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found. Install Python 3.9+.
    pause
    exit /b 1
)
echo [INFO] Creating virtual environment...
python -m venv venv
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
echo [INFO] Installing requirements...
pip install --upgrade pip
pip install -r requirements_fastapi.txt
echo.
echo ================================================
echo   Setup completed successfully!
echo   To start the server, run: start_fastapi.bat
echo ================================================
echo.
pause
