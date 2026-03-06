#!/bin/bash
# Development Environment Setup Script
# This script sets up the development environment for the ECU Log Visualizer

set -e  # Exit on error

echo "========================================="
echo "ECU Log Visualizer - Development Setup"
echo "========================================="
echo ""

# Check Python version
echo "[1/5] Checking Python version..."
if ! command -v python &> /dev/null; then
    echo "ERROR: Python is not installed or not in PATH"
    exit 1
fi

PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo "Found Python $PYTHON_VERSION"
echo ""

# Install Python dependencies
echo "[2/5] Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo "Dependencies installed successfully"
    else
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
else
    echo "ERROR: requirements.txt not found"
    exit 1
fi
echo ""

# Create necessary directories
echo "[3/5] Creating necessary directories..."
mkdir -p uploads
mkdir -p tests/unit
mkdir -p tests/integration
mkdir -p tests/property
mkdir -p docs
mkdir -p scripts
mkdir -p frontend
echo "Directories created successfully"
echo ""

# Initialize Git repository if needed
echo "[4/5] Checking Git repository..."
if [ ! -d ".git" ]; then
    echo "Initializing Git repository..."
    git init
    echo "Git repository initialized"
else
    echo "Git repository already initialized"
fi
echo ""

# Display setup completion status
echo "[5/5] Setup complete!"
echo ""
echo "========================================="
echo "Development environment is ready!"
echo "========================================="
echo ""
echo "Next steps:"
echo "  - Run tests: ./scripts/test.sh"
echo "  - Build Docker image: ./scripts/build.sh"
echo "  - Start application: python run_server.py"
echo ""

exit 0
