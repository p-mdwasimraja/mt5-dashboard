@echo off
REM MT5 Dashboard API - Setup Script for Windows
REM This script sets up the complete environment

setlocal enabledelayedexpansion

echo ==========================================
echo   MT5 Dashboard API Setup
echo ==========================================
echo.

REM Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Found Python %PYTHON_VERSION%
echo.

REM Check if virtual environment exists
if exist "venv\" (
    echo [WARNING] Virtual environment already exists. Skipping creation.
    echo.
) else (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --quiet
echo [OK] Pip upgraded
echo.

REM Install requirements
echo Installing dependencies...
echo This may take a few minutes...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

REM Create necessary directories
echo Creating directory structure...
if not exist "config" mkdir config
if not exist "data\raw" mkdir data\raw
if not exist "data\processed" mkdir data\processed
if not exist "data\backup" mkdir data\backup
if not exist "logs" mkdir logs
if not exist "app\static\css" mkdir app\static\css
if not exist "app\static\js" mkdir app\static\js
if not exist "app\static\images" mkdir app\static\images
echo [OK] Directories created
echo.

REM Copy example config if not exists
if exist "config\settings.yaml" (
    echo [WARNING] config\settings.yaml already exists. Skipping copy.
) else (
    if exist "config\settings.yaml.example" (
        copy config\settings.yaml.example config\settings.yaml >nul
        echo [OK] Created config\settings.yaml from example
        echo [WARNING] Please edit config\settings.yaml with your MT5 data paths!
    ) else (
        echo [WARNING] config\settings.yaml.example not found
    )
)
echo.

REM Copy .env if not exists
if exist ".env" (
    echo [WARNING] .env already exists. Skipping copy.
) else (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo [OK] Created .env from example
    ) else (
        echo [WARNING] .env.example not found
    )
)
echo.

REM Test import
echo Testing installation...
python -c "import fastapi; import uvicorn; import pandas; print('[OK] All core dependencies working')" 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] Some dependencies may not be properly installed
) else (
    echo [OK] Installation verified
)
echo.

REM Display success message
echo ==========================================
echo Setup completed successfully!
echo ==========================================
echo.
echo Next steps:
echo.
echo 1. Configure your MT5 data sources:
echo    notepad config\settings.yaml
echo.
echo 2. Start the server:
echo    start.bat
echo.
echo 3. Access the dashboard:
echo    http://localhost:8000
echo.
echo 4. View API documentation:
echo    http://localhost:8000/docs
echo.
echo For VPS deployment, see README.md
echo.
pause
