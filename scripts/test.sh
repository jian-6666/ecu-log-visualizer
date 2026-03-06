#!/bin/bash
# Automated Testing Script
# This script runs all automated tests with coverage reporting

set -e  # Exit on error

echo "========================================="
echo "ECU Log Visualizer - Running Tests"
echo "========================================="
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "ERROR: pytest is not installed"
    echo "Run: pip install pytest pytest-cov"
    exit 1
fi

# Run pytest with coverage
echo "Running tests with coverage..."
echo ""

pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

TEST_EXIT_CODE=$?

echo ""
echo "========================================="

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✓ All tests passed!"
    echo "========================================="
    echo ""
    echo "Coverage report generated in htmlcov/"
    echo "Open htmlcov/index.html to view detailed coverage"
    exit 0
else
    echo "✗ Some tests failed"
    echo "========================================="
    echo ""
    echo "Please review the test output above"
    exit $TEST_EXIT_CODE
fi
