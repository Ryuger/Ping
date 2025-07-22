@echo off
chcp 65001 > nul 2>&1
echo ======================================
echo    NETWORK MONITOR - LOCAL START
echo ======================================
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found
    echo Install Python from https://python.org
    pause
    exit /b 1
)

:: Check pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip not found
    pause
    exit /b 1
)

:: Install dependencies
echo Checking dependencies...
pip install flask flask-sqlalchemy flask-login flask-socketio ping3 netifaces apscheduler flask-wtf werkzeug openpyxl flask-bcrypt pyjwt --quiet

:: Set environment variables
set DATABASE_URL=sqlite:///network_monitor.db
set SESSION_SECRET=NetMon_K7x9P2mQ8vL4nR6tY3uI1oE5wZ0sA7bG9dF2hJ4kM8pN6qV3xC1yB5nU
set FLASK_ENV=development
set FLASK_DEBUG=true

:: Start application
echo.
echo Starting application...
echo.
python start_local.py

pause