@echo off
REM ============================================================
REM MT5 Auto Dashboard - Windows Startup Script
REM ============================================================

echo.
echo ============================================================
echo MT5 Auto Dashboard - Starting...
echo ============================================================
echo.

REM Get the script directory
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [WARNING] Virtual environment not found. Using global Python.
    echo [TIP] Create venv with: python -m venv venv
    echo.
)

REM Check if requirements are installed
python -c "import dash" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Required packages not installed
    echo Please run: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Check if start_dashboard.py exists
if not exist "start_dashboard.py" (
    echo [ERROR] start_dashboard.py not found
    echo Please ensure you're in the correct directory
    echo.
    pause
    exit /b 1
)

REM Start the dashboard
echo [INFO] Starting dashboard...
echo.
python start_dashboard.py

REM If the script exits, pause so user can see any errors
echo.
echo ============================================================
echo Dashboard stopped.
echo ============================================================
echo.
pause
