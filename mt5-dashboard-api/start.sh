#!/bin/bash
# Startup script for MT5 Dashboard API

echo "Starting MT5 Dashboard API..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Create necessary directories
mkdir -p logs
mkdir -p data

# Start the application
echo "Starting uvicorn server..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
