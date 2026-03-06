"""
Integration tests for file upload API endpoint

Tests the POST /api/upload endpoint functionality including:
- Valid file uploads (CSV and JSON)
- Invalid file format rejection
- File size limit enforcement
- Error response format validation

Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 8.1, 8.2, 8.3, 8.5, 10.2, 10.3
"""

import pytest
import io
from fastapi.testclient import TestClient
from src.main import app
from pathlib import Path

client = TestClient(app)


def test_upload_valid_csv_file():
    """
    Test uploading a valid CSV file
    
    Validates: Requirements 1.1, 1.2, 1.3, 1.5
    """
    # Create a simple CSV file content
    csv_content = """timestamp,sensor1,sensor2,status
2024-01-01T00:00:00,23.5,45.2,OK
2024-01-01T00:00:01,23.6,45.3,OK
2024-01-01T00:00:02,23.7,45.4,OK
"""
    
    # Create file-like object
    file = io.BytesIO(csv_content.encode('utf-8'))
    
    # Upload file
    response = client.post(
        "/api/upload",
        files={"file": ("test_log.csv", file, "text/csv")}
    )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "file_id" in data
    assert "filename" in data
    assert "original_filename" in data
    assert "file_size" in data
    assert "upload_time" in data
    assert "file_format" in data
    assert "status" in data
    
    # Check response values
    assert data["original_filename"] == "test_log.csv"
    assert data["file_format"] == "csv"
    assert data["status"] == "uploaded"
    assert data["file_size"] > 0
    assert len(data["file_id"]) > 0  # UUID should be non-empty


def test_upload_valid_json_file():
    """
    Test uploading a valid JSON file
    
    Validates: Requirements 1.1, 1.2, 1.3, 1.5
    """
    # Create a simple JSON file content
    json_content = """[
    {
        "timestamp": "2024-01-01T00:00:00",
        "sensors": {
            "sensor1": 23.5,
            "sensor2": 45.2
        },
        "status": "OK"
    }
]"""
    
    # Create file-like object
    file = io.BytesIO(json_content.encode('utf-8'))
    
    # Upload file
    response = client.post(
        "/api/upload",
        files={"file": ("test_log.json", file, "application/json")}
    )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    
    # Check response values
    assert data["original_filename"] == "test_log.json"
    assert data["file_format"] == "json"
    assert data["status"] == "uploaded"


def test_upload_invalid_file_format():
    """
    Test uploading a file with invalid format returns 400
    
    Validates: Requirements 1.2, 1.4, 8.1, 8.5
    """
    # Create a text file (not CSV or JSON)
    txt_content = "This is a plain text file"
    file = io.BytesIO(txt_content.encode('utf-8'))
    
    # Upload file
    response = client.post(
        "/api/upload",
        files={"file": ("test_log.txt", file, "text/plain")}
    )
    
    # Verify error response
    assert response.status_code == 400
    data = response.json()
    
    # Check error response structure (new standardized format)
    assert "error_code" in data
    assert "message" in data
    assert "timestamp" in data
    
    # Check error details
    assert data["error_code"] == "INVALID_FORMAT"
    assert "CSV and JSON" in data["message"]
    assert "details" in data
    assert data["details"]["provided_format"] == ".txt"


def test_upload_file_too_large():
    """
    Test uploading a file exceeding size limit returns error
    
    Validates: Requirements 1.2, 8.1, 8.2, 8.3
    """
    # Create a file larger than 50MB
    # We'll create a 51MB file
    large_content = b"x" * (51 * 1024 * 1024)
    file = io.BytesIO(large_content)
    
    # Upload file
    response = client.post(
        "/api/upload",
        files={"file": ("large_file.csv", file, "text/csv")}
    )
    
    # Verify error response (should be 400 or 413 for file too large)
    # Note: The actual status code depends on when the size check happens
    assert response.status_code in [400, 413]
    data = response.json()
    
    # Check error response structure (new standardized format)
    assert "error_code" in data
    assert data["error_code"] in ["FILE_TOO_LARGE", "INVALID_FILE"]
    assert "message" in data
    # Error message should indicate the problem
    assert len(data["message"]) > 0


def test_upload_multiple_files_generate_unique_ids():
    """
    Test that uploading the same file multiple times generates different IDs
    
    Validates: Requirements 1.3, 1.5
    """
    # Create a CSV file
    csv_content = """timestamp,sensor1
2024-01-01T00:00:00,23.5
"""
    
    # Upload the same file twice
    file1 = io.BytesIO(csv_content.encode('utf-8'))
    response1 = client.post(
        "/api/upload",
        files={"file": ("test.csv", file1, "text/csv")}
    )
    
    file2 = io.BytesIO(csv_content.encode('utf-8'))
    response2 = client.post(
        "/api/upload",
        files={"file": ("test.csv", file2, "text/csv")}
    )
    
    # Both uploads should succeed
    assert response1.status_code == 200
    assert response2.status_code == 200
    
    # File IDs should be different
    file_id1 = response1.json()["file_id"]
    file_id2 = response2.json()["file_id"]
    assert file_id1 != file_id2


def test_upload_without_file():
    """
    Test uploading without providing a file returns 422 (validation error)
    
    Validates: Requirements 8.5
    """
    # Try to upload without file
    response = client.post("/api/upload")
    
    # FastAPI returns 422 for missing required fields
    assert response.status_code == 422


def test_upload_empty_filename():
    """
    Test uploading a file with empty filename returns error
    
    Validates: Requirements 1.2, 8.5
    """
    # Create file with empty filename
    file = io.BytesIO(b"test content")
    
    response = client.post(
        "/api/upload",
        files={"file": ("", file, "text/csv")}
    )
    
    # Should return 422 for validation error
    assert response.status_code == 422
    data = response.json()
    # Check for standardized error response format
    assert "error_code" in data or "validation_errors" in data.get("details", {})


def test_upload_response_includes_timestamp():
    """
    Test that upload response includes a valid timestamp
    
    Validates: Requirements 1.5
    """
    csv_content = "timestamp,sensor1\n2024-01-01T00:00:00,23.5\n"
    file = io.BytesIO(csv_content.encode('utf-8'))
    
    response = client.post(
        "/api/upload",
        files={"file": ("test.csv", file, "text/csv")}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check timestamp format (ISO 8601)
    assert "upload_time" in data
    assert "T" in data["upload_time"]  # ISO format includes 'T'
    
    # Verify it's a valid ISO timestamp
    from datetime import datetime
    try:
        datetime.fromisoformat(data["upload_time"].replace('Z', '+00:00'))
    except ValueError:
        pytest.fail("upload_time is not a valid ISO 8601 timestamp")


def test_error_response_format():
    """
    Test that error responses follow the standard format
    
    Validates: Requirements 8.1, 8.2, 8.3
    """
    # Trigger an error by uploading invalid format
    file = io.BytesIO(b"test")
    response = client.post(
        "/api/upload",
        files={"file": ("test.txt", file, "text/plain")}
    )
    
    assert response.status_code == 400
    data = response.json()
    
    # Verify error response structure (new standardized format)
    # All error responses should have these fields at root level
    assert "error_code" in data
    assert "message" in data
    assert "timestamp" in data
    
    # error_code should be a string
    assert isinstance(data["error_code"], str)
    assert len(data["error_code"]) > 0
    
    # message should be descriptive
    assert isinstance(data["message"], str)
    assert len(data["message"]) > 0
