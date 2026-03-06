#!/usr/bin/env python3
"""
ECU Log Visualizer - Backend Server Startup Script

This script starts the FastAPI backend server using uvicorn.
It displays the server URL and API documentation URL upon startup.

Requirements: 13.1, 13.3, 13.4, 13.5
"""

import sys
import os
from pathlib import Path

def main():
    """Start the FastAPI backend server"""
    
    # Ensure we're in the project root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Configuration
    HOST = "127.0.0.1"
    PORT = 8000
    
    # Display startup information
    print("=" * 60)
    print("ECU Log Visualizer - Backend Server")
    print("=" * 60)
    print(f"Starting server on http://{HOST}:{PORT}")
    print(f"API Documentation: http://{HOST}:{PORT}/docs")
    print(f"Alternative Docs: http://{HOST}:{PORT}/redoc")
    print(f"Health Check: http://{HOST}:{PORT}/health")
    print("=" * 60)
    print("Press CTRL+C to stop the server")
    print("=" * 60)
    print()
    
    # Import uvicorn here to ensure proper error handling
    try:
        import uvicorn
    except ImportError:
        print("ERROR: uvicorn is not installed.")
        print("Please install dependencies: pip install -r requirements.txt")
        sys.exit(1)
    
    # Start the server
    # Note: reload=False for production, set to True for development
    uvicorn.run(
        "src.main:app",
        host=HOST,
        port=PORT,
        reload=False,
        log_level="info",
        access_log=True,
        limit_max_requests=None,
        timeout_keep_alive=5
    )

if __name__ == "__main__":
    main()
