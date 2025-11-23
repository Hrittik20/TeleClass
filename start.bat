@echo off
REM Noētica LMS - Startup Script for Windows
REM This script starts both the API server and the Telegram bot

echo ========================================
echo Starting Noētica LMS
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo ERROR: .env file not found
    echo Please copy .env.example to .env and configure it
    pause
    exit /b 1
)

REM Check if data directory exists
if not exist data mkdir data
if not exist data\files mkdir data\files

REM Start the API server in a new window
echo Starting API Server...
start "Noētica LMS - API Server" cmd /k "echo API Server Starting... && uvicorn server.app:app --host 0.0.0.0 --port 8000 --reload"

REM Wait a bit for the server to start
timeout /t 3 /nobreak >nul

REM Start the Telegram bot in a new window
echo Starting Telegram Bot...
start "Noētica LMS - Telegram Bot" cmd /k "echo Telegram Bot Starting... && python bot\bot.py"

echo.
echo ========================================
echo Both services started!
echo ========================================
echo.
echo API Server: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to stop all services...
pause >nul

REM Close both windows
taskkill /FI "WindowTitle eq Noētica LMS - API Server*" /F >nul 2>&1
taskkill /FI "WindowTitle eq Noētica LMS - Telegram Bot*" /F >nul 2>&1

echo All services stopped.
pause

