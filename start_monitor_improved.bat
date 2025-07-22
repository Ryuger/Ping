@echo off
chcp 65001 >nul 2>&1
title Network Monitor - Local Server

echo.
echo ==========================================
echo     NETWORK MONITOR - LOCAL SERVER
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python from https://python.org
    echo Make sure to add Python to PATH during installation
    echo.
    pause
    exit /b 1
)

REM Check if pip is available
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pip is not available
    echo.
    echo Please reinstall Python with pip included
    echo.
    pause
    exit /b 1
)

echo [INFO] Python and pip are available
echo.

REM Install required dependencies
echo [INFO] Installing/updating dependencies...
pip install flask flask-sqlalchemy flask-login flask-socketio ping3 netifaces apscheduler flask-wtf werkzeug openpyxl flask-bcrypt pyjwt --quiet --upgrade

if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    echo.
    pause
    exit /b 1
)

echo [INFO] Dependencies installed successfully
echo.

REM Set environment variables
set DATABASE_URL=sqlite:///network_monitor.db
set SESSION_SECRET=NetMon_K7x9P2mQ8vL4nR6tY3uI1oE5wZ0sA7bG9dF2hJ4kM8pN6qV3xC1yB5nU
set FLASK_ENV=development
set FLASK_DEBUG=true

echo [INFO] Environment variables set
echo.

REM Create necessary directories
if not exist "config" mkdir config
if not exist "static" mkdir static
if not exist "templates" mkdir templates

echo [INFO] Directory structure verified
echo.

REM Start the application
echo ==========================================
echo     STARTING NETWORK MONITOR SERVER
echo ==========================================
echo.
echo [INFO] Starting application...
echo [INFO] Press Ctrl+C to stop the server
echo.

python start_local.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Application failed to start
    echo.
    pause
    exit /b 1
)

echo.
echo [INFO] Application stopped
pause