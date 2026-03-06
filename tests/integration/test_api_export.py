"""
Integration tests for data export API endpoint

Validates: Requirements 15.1, 15.2, 15.3, 15.4, 8.1, 8.4, 8.5, 10.2
"""

import pytest
import io
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


@pytest.fixture
def uploaded_csv_file():
    """Fixture that uploads a CSV file and returns its file_id"""
    csv_content = """timestamp,sensor1,sensor2,sensor3,status
2024-01-01T00:00:00,23.5,45.2,67.8,OK
2024-01-01T00:00:01,23.6,45.3,67.9,OK
2024-01-01T00:00:02,23.7,45.4,68.0,OK
2024-01-01T00:00:03,23.8,45.5,68.1,OK
2024-01-01T00:00:04,23.9,45.6,68.2,OK
2024-01-01T00:00:05,24.0,45.7,68.3,OK
2024-01-01T00:00:06,24.1,45.8,68.4,OK
2024-01-01T00:00:07,24.2,45.9,68.5,OK
2024-01-01T00:00:08,24.3,46.0,68.6,OK
2024-01-01T00:00:09,24.4,46.1,68.7,OK
"""
    file = io.BytesIO(csv_content.encode('utf-8'))
    response = client.post("/api/upload", files={"file": ("test_export.csv", file, "text/csv")})
    assert response.status_code == 200
    return response.json()["file_id"]


@pytest.fixture
def uploaded_json_file():
    """Fixture that uploads a JSON file and returns its file_id"""
    json_content = """[
    {"timestamp": "2024-01-01T00:00:00", "sensors": {"sensor1": 23.5, "sensor2": 45.2, "sensor3": 67.8}, "status": "OK"},
    {"timestamp": "2024-01-01T00:00:01", "sensors": {"sensor1": 23.6, "sensor2": 45.3, "sensor3": 67.9}, "status": "OK"},
    {"timestamp": "2024-01-01T00:00:02", "sensors": {"sensor1": 23.7, "sensor2": 45.4, "sensor3": 68.0}, "status": "OK"}
]"""
    file = io.BytesIO(json_content.encode('utf-8'))
    response = client.post("/api/upload", files={"file": ("test_export.json", file, "application/json")})
    assert response.status_code == 200
    return response.json()["file_id"]


def test_export_csv_without_filters(uploaded_csv_file):
    """Test exporting data as CSV without any filters - Validates: Requirements 15.1, 15.4"""
    file_id = uploaded_csv_file
    response = client.get(f"/api/export/{file_id}?format=csv")
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "Content-Disposition" in response.headers
    assert "attachment" in response.headers["Content-Disposition"]
    assert f"export_{file_id}" in response.headers["Content-Disposition"]
    
    content = response.text
    lines = content.strip().split('\n')
    assert lines[0].startswith("# Export Timestamp:")
    assert file_id in lines[1]
    
    header_idx = None
    for i, line in enumerate(lines):
        if not line.startswith('#') and 'timestamp' in line.lower():
            header_idx = i
            break
    assert header_idx is not None
    data_lines = [line for line in lines[header_idx+1:] if line.strip()]
    assert len(data_lines) == 10


def test_export_json_without_filters(uploaded_csv_file):
    """Test exporting data as JSON without any filters - Validates: Requirements 15.2, 15.4"""
    file_id = uploaded_csv_file
    response = client.get(f"/api/export/{file_id}?format=json")
    
    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]
    data = response.json()
    
    assert "metadata" in data and "data" in data
    metadata = data["metadata"]
    assert metadata["file_id"] == file_id
    assert metadata["record_count"] == 10
    assert metadata["filters"]["start_time"] is None
    assert len(data["data"]) == 10


def test_export_csv_with_time_filter(uploaded_csv_file):
    """Test exporting CSV with time range filter - Validates: Requirements 15.1, 15.3, 15.4"""
    file_id = uploaded_csv_file
    response = client.get(f"/api/export/{file_id}", params={
        "format": "csv",
        "start_time": "2024-01-01T00:00:00",
        "end_time": "2024-01-01T00:00:04"
    })
    
    assert response.status_code == 200
    content = response.text
    lines = content.strip().split('\n')
    filter_text = '\n'.join([line for line in lines if line.startswith('#')])
    assert "2024-01-01T00:00:00" in filter_text
    assert "2024-01-01T00:00:04" in filter_text
    
    data_lines = [line for line in lines if not line.startswith('#') and line.strip() and 'timestamp' not in line.lower()]
    assert len(data_lines) == 5


def test_export_json_with_sensor_filter(uploaded_csv_file):
    """Test exporting JSON with sensor filter - Validates: Requirements 15.2, 15.3, 15.4"""
    file_id = uploaded_csv_file
    response = client.get(f"/api/export/{file_id}", params={"format": "json", "sensors": "sensor1,sensor2"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["filters"]["sensors"] == ["sensor1", "sensor2"]
    
    records = data["data"]
    assert len(records) == 10
    assert "sensor1" in records[0]
    assert "sensor2" in records[0]
    assert "sensor3" not in records[0]


def test_export_with_combined_filters(uploaded_csv_file):
    """Test exporting with multiple filters - Validates: Requirements 15.3, 15.4"""
    file_id = uploaded_csv_file
    response = client.get(f"/api/export/{file_id}", params={
        "format": "json",
        "start_time": "2024-01-01T00:00:02",
        "end_time": "2024-01-01T00:00:06",
        "sensors": "sensor1"
    })
    
    assert response.status_code == 200
    data = response.json()
    metadata = data["metadata"]
    assert metadata["filters"]["start_time"] == "2024-01-01T00:00:02"
    assert metadata["filters"]["sensors"] == ["sensor1"]
    assert len(data["data"]) == 5
    assert "sensor1" in data["data"][0]
    assert "sensor2" not in data["data"][0]


def test_export_invalid_format(uploaded_csv_file):
    """Test invalid export format returns 400 - Validates: Requirements 8.5"""
    file_id = uploaded_csv_file
    response = client.get(f"/api/export/{file_id}?format=xml")
    
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == "INVALID_PARAMETER"
    assert data["details"]["parameter"] == "format"
    assert data["details"]["provided_value"] == "xml"


def test_export_nonexistent_file():
    """Test exporting non-existent file returns 404 - Validates: Requirements 8.4"""
    response = client.get("/api/export/nonexistent-file-id?format=csv")
    
    assert response.status_code == 404
    data = response.json()
    assert data["error_code"] == "FILE_NOT_FOUND"
    assert "nonexistent-file-id" in data["message"]


def test_export_invalid_time_format(uploaded_csv_file):
    """Test invalid time format returns 400 - Validates: Requirements 8.5"""
    file_id = uploaded_csv_file
    response = client.get(f"/api/export/{file_id}", params={"format": "csv", "start_time": "invalid-date"})
    
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == "INVALID_PARAMETER"
    assert "start_time" in data["message"]


def test_export_empty_sensor_list(uploaded_csv_file):
    """Test empty sensor list returns 400 - Validates: Requirements 8.5"""
    file_id = uploaded_csv_file
    response = client.get(f"/api/export/{file_id}", params={"format": "csv", "sensors": "   "})
    
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == "INVALID_PARAMETER"
    assert "sensor" in data["message"].lower()


def test_export_metadata_timestamp_format(uploaded_csv_file):
    """Test export metadata timestamp format - Validates: Requirements 15.4"""
    file_id = uploaded_csv_file
    response = client.get(f"/api/export/{file_id}?format=json")
    
    assert response.status_code == 200
    export_timestamp = response.json()["metadata"]["export_timestamp"]
    assert "T" in export_timestamp
    
    from datetime import datetime
    try:
        datetime.fromisoformat(export_timestamp.replace('Z', '+00:00'))
    except ValueError:
        pytest.fail("export_timestamp is not a valid ISO 8601 timestamp")


def test_export_csv_format_case_insensitive(uploaded_csv_file):
    """Test format parameter is case-insensitive - Validates: Requirements 15.1"""
    file_id = uploaded_csv_file
    
    response1 = client.get(f"/api/export/{file_id}?format=CSV")
    assert response1.status_code == 200
    assert "text/csv" in response1.headers["content-type"]
    
    response2 = client.get(f"/api/export/{file_id}?format=CsV")
    assert response2.status_code == 200
    assert "text/csv" in response2.headers["content-type"]


def test_export_json_from_json_file(uploaded_json_file):
    """Test exporting JSON from JSON source - Validates: Requirements 15.2"""
    file_id = uploaded_json_file
    response = client.get(f"/api/export/{file_id}?format=json")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 3
    assert "sensor1" in data["data"][0]


def test_export_csv_from_json_file(uploaded_json_file):
    """Test exporting CSV from JSON source - Validates: Requirements 15.1"""
    file_id = uploaded_json_file
    response = client.get(f"/api/export/{file_id}?format=csv")
    
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    content = response.text
    lines = content.strip().split('\n')
    data_lines = [line for line in lines if not line.startswith('#') and line.strip() and 'timestamp' not in line.lower()]
    assert len(data_lines) == 3


def test_export_with_no_matching_data(uploaded_csv_file):
    """Test exporting with no matching data - Validates: Requirements 15.3"""
    file_id = uploaded_csv_file
    response = client.get(f"/api/export/{file_id}", params={
        "format": "json",
        "start_time": "2025-01-01T00:00:00",
        "end_time": "2025-01-01T00:00:10"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["record_count"] == 0
    assert len(data["data"]) == 0


def test_export_missing_format_parameter():
    """Test missing format parameter returns 422 - Validates: Requirements 8.5"""
    response = client.get("/api/export/some-file-id")
    assert response.status_code == 422


def test_export_sensor_list_with_spaces(uploaded_csv_file):
    """Test sensor list handles spaces - Validates: Requirements 15.3"""
    file_id = uploaded_csv_file
    response = client.get(f"/api/export/{file_id}", params={"format": "json", "sensors": " sensor1 , sensor2 "})
    
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["filters"]["sensors"] == ["sensor1", "sensor2"]
    assert "sensor1" in data["data"][0]
    assert "sensor3" not in data["data"][0]


def test_export_csv_filename_format(uploaded_csv_file):
    """Test CSV export filename format - Validates: Requirements 15.1"""
    file_id = uploaded_csv_file
    response = client.get(f"/api/export/{file_id}?format=csv")
    
    assert response.status_code == 200
    content_disposition = response.headers["Content-Disposition"]
    assert "attachment" in content_disposition
    assert f"export_{file_id}" in content_disposition
    assert ".csv" in content_disposition


def test_export_json_filename_format(uploaded_csv_file):
    """Test JSON export filename format - Validates: Requirements 15.2"""
    file_id = uploaded_csv_file
    response = client.get(f"/api/export/{file_id}?format=json")
    
    assert response.status_code == 200
    content_disposition = response.headers["Content-Disposition"]
    assert "attachment" in content_disposition
    assert f"export_{file_id}" in content_disposition
    assert ".json" in content_disposition
