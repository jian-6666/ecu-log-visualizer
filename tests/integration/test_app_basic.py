"""
Integration tests for basic FastAPI application functionality
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns API information"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs" in data
    assert data["message"] == "ECU Log Visualizer API"


def test_health_check_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ECU Log Visualizer"
    assert "max_upload_size_mb" in data
    assert data["max_upload_size_mb"] == 50


def test_docs_endpoint_exists():
    """Test that API documentation endpoint exists"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_cors_headers():
    """Test that CORS headers are properly configured"""
    response = client.get("/health", headers={"Origin": "http://localhost:3000"})
    assert response.status_code == 200
    # CORS headers should be present
    assert "access-control-allow-origin" in response.headers
