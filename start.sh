#!/bin/bash
# Noētica LMS - Startup Script for Linux/Mac
# This script starts both the API server and the Telegram bot

echo "========================================"
echo "Starting Noētica LMS"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found"
    echo "Please copy .env.example to .env and configure it"
    exit 1
fi

# Check if data directory exists
mkdir -p data/files

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "========================================"
    echo "Stopping all services..."
    echo "========================================"
    kill $API_PID $BOT_PID 2>/dev/null
    echo "All services stopped."
    exit 0
}

# Set up trap for cleanup
trap cleanup INT TERM

# Start the API server in background
echo "Starting API Server..."
uvicorn server.app:app --host 0.0.0.0 --port 8000 --reload &
API_PID=$!

# Wait a bit for the server to start
sleep 3

# Start the Telegram bot in background
echo "Starting Telegram Bot..."
python3 bot/bot.py &
BOT_PID=$!

echo ""
echo "========================================"
echo "Both services started!"
echo "========================================"
echo ""
echo "API Server: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "API Server PID: $API_PID"
echo "Bot PID: $BOT_PID"
echo ""
echo "Press Ctrl+C to stop all services..."
echo ""

# Wait for processes
wait

