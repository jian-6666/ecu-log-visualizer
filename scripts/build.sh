#!/bin/bash
# Docker Image Build Script
# This script builds the Docker image for the ECU Log Visualizer

set -e  # Exit on error

echo "========================================="
echo "ECU Log Visualizer - Building Docker Image"
echo "========================================="
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed or not in PATH"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "ERROR: Docker daemon is not running"
    echo "Please start Docker and try again"
    exit 1
fi

# Generate timestamp tag
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
IMAGE_NAME="ecu-log-visualizer"
IMAGE_TAG_LATEST="${IMAGE_NAME}:latest"
IMAGE_TAG_TIMESTAMP="${IMAGE_NAME}:${TIMESTAMP}"

echo "Building Docker image..."
echo "  Image: ${IMAGE_TAG_LATEST}"
echo "  Tag: ${IMAGE_TAG_TIMESTAMP}"
echo ""

# Build Docker image
docker build -t "${IMAGE_TAG_LATEST}" -t "${IMAGE_TAG_TIMESTAMP}" .

BUILD_EXIT_CODE=$?

echo ""
echo "========================================="

if [ $BUILD_EXIT_CODE -eq 0 ]; then
    echo "✓ Docker image built successfully!"
    echo "========================================="
    echo ""
    echo "Image tags:"
    echo "  - ${IMAGE_TAG_LATEST}"
    echo "  - ${IMAGE_TAG_TIMESTAMP}"
    echo ""
    echo "Verify image:"
    docker images "${IMAGE_NAME}"
    echo ""
    echo "Next steps:"
    echo "  - Deploy: ./scripts/deploy.sh"
    echo "  - Run manually: docker run -p 8000:8000 ${IMAGE_TAG_LATEST}"
    exit 0
else
    echo "✗ Docker image build failed"
    echo "========================================="
    echo ""
    echo "Please review the build output above"
    exit $BUILD_EXIT_CODE
fi
