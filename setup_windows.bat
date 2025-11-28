@echo off
REM ============================================================
REM MT5 Auto Dashboard - Windows Setup Script
REM ============================================================

echo.
echo ============================================================
echo MT5 Auto Dashboard - Windows Setup
echo ============================================================
echo.

REM Get the script directory
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo [INFO] Python found:
python --version
echo.

REM Create virtual environment
if exist "venv" (
    echo [INFO] Virtual environment already exists. Skipping creation.
    echo.
) else (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [SUCCESS] Virtual environment created
    echo.
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install requirements
if exist "requirements.txt" (
    echo [INFO] Installing required packages...
    pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to install requirements
        pause
        exit /b 1
    )
    echo [SUCCESS] All packages installed
) else (
    echo [WARNING] requirements.txt not found
    echo Installing core packages manually...
    pip install dash dash-bootstrap-components plotly pandas pyyaml
)

echo.
echo ============================================================
echo Setup Complete!
echo ============================================================
echo.
echo Next steps:
echo 1. Configure your MT5 data paths in config\settings.yaml
echo 2. Double-click start_dashboard.bat to run the dashboard
echo 3. Open your browser to http://localhost:8050
echo.
echo ============================================================
pause
