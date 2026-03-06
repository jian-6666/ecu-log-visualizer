#!/bin/bash
# ECU Log Visualizer - Backend Server Startup Script (Shell version)
# 
# This script starts the FastAPI backend server using uvicorn.
# It displays the server URL and API documentation URL upon startup.
#
# Requirements: 13.1, 13.3, 13.4, 13.5

# Configuration
HOST="127.0.0.1"
PORT=8000

# Display startup information
echo "============================================================"
echo "ECU Log Visualizer - Backend Server"
echo "============================================================"
echo "Starting server on http://${HOST}:${PORT}"
echo "API Documentation: http://${HOST}:${PORT}/docs"
echo "Alternative Docs: http://${HOST}:${PORT}/redoc"
echo "Health Check: http://${HOST}:${PORT}/health"
echo "============================================================"
echo "Press CTRL+C to stop the server"
echo "============================================================"
echo ""

# Check if uvicorn is installed
if ! python -c "import uvicorn" 2>/dev/null; then
    echo "ERROR: uvicorn is not installed."
    echo "Please install dependencies: pip install -r requirements.txt"
    exit 1
fi

# Start the server
python -m uvicorn src.main:app \
    --host "${HOST}" \
    --port "${PORT}" \
    --log-level info \
    --no-reload \
    --timeout-keep-alive 5
