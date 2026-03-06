#!/bin/bash
# Application Deployment Script
# This script deploys the ECU Log Visualizer in a Docker container

set -e  # Exit on error

echo "========================================="
echo "ECU Log Visualizer - Deploying Application"
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

CONTAINER_NAME="ecu-log-visualizer"
IMAGE_NAME="ecu-log-visualizer:latest"
HOST_PORT=8000
CONTAINER_PORT=8000

# Check if image exists
if ! docker images "${IMAGE_NAME}" | grep -q "ecu-log-visualizer"; then
    echo "ERROR: Docker image '${IMAGE_NAME}' not found"
    echo "Please build the image first: ./scripts/build.sh"
    exit 1
fi

# Stop existing container if running
echo "[1/3] Checking for existing container..."
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Stopping and removing existing container..."
    docker stop "${CONTAINER_NAME}" &> /dev/null || true
    docker rm "${CONTAINER_NAME}" &> /dev/null || true
    echo "Existing container removed"
else
    echo "No existing container found"
fi
echo ""

# Start new container
echo "[2/3] Starting new container..."
docker run -d \
    --name "${CONTAINER_NAME}" \
    -p "${HOST_PORT}:${CONTAINER_PORT}" \
    -v "$(pwd)/uploads:/app/uploads" \
    "${IMAGE_NAME}"

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to start container"
    exit 1
fi

echo "Container started successfully"
echo ""

# Verify container health
echo "[3/3] Verifying container health..."
sleep 3

if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    CONTAINER_STATUS=$(docker inspect --format='{{.State.Status}}' "${CONTAINER_NAME}")
    echo "Container status: ${CONTAINER_STATUS}"
    
    if [ "${CONTAINER_STATUS}" = "running" ]; then
        echo ""
        echo "========================================="
        echo "✓ Application deployed successfully!"
        echo "========================================="
        echo ""
        echo "Access the application at:"
        echo "  http://localhost:${HOST_PORT}"
        echo ""
        echo "View logs:"
        echo "  docker logs ${CONTAINER_NAME}"
        echo ""
        echo "Stop container:"
        echo "  docker stop ${CONTAINER_NAME}"
        echo ""
        exit 0
    else
        echo ""
        echo "========================================="
        echo "✗ Container is not running"
        echo "========================================="
        echo ""
        echo "Check logs for errors:"
        echo "  docker logs ${CONTAINER_NAME}"
        exit 1
    fi
else
    echo ""
    echo "========================================="
    echo "✗ Container failed to start"
    echo "========================================="
    echo ""
    echo "Check Docker logs for details"
    exit 1
fi
