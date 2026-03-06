"""
单元测试：Pydantic 数据模型

测试所有数据模型的创建、验证和序列化功能。
"""

import pytest
from datetime import datetime
from src.models import (
    FileMetadata,
    SensorStatistics,
    StatisticsResponse,
    ChartResponse,
    FilterParams,
    ExportRequest,
    ErrorResponse
)


def test_file_metadata_creation():
    """测试 FileMetadata 模型创建"""
    metadata = FileMetadata(
        file_id="test-123",
        filename="stored_file.csv",
        original_filename="upload.csv",
        file_size=1024,
        upload_time=datetime(2024, 1, 1, 12, 0, 0),
        file_format="csv",
        status="uploaded"
    )
    
    assert metadata.file_id == "test-123"
    assert metadata.filename == "stored_file.csv"
    assert metadata.file_format == "csv"
    assert metadata.status == "uploaded"


def test_file_metadata_json_serialization():
    """测试 FileMetadata 的 JSON 序列化（datetime 处理）"""
    metadata = FileMetadata(
        file_id="test-123",
        filename="stored_file.csv",
        original_filename="upload.csv",
        file_size=1024,
        upload_time=datetime(2024, 1, 1, 12, 0, 0),
        file_format="csv",
        status="uploaded"
    )
    
    json_data = metadata.model_dump_json()
    assert "2024-01-01T12:00:00" in json_data


def test_sensor_statistics_creation():
    """测试 SensorStatistics 模型创建"""
    stats = SensorStatistics(
        min=10.5,
        max=99.8,
        mean=55.2,
        std=15.3,
        count=100
    )
    
    assert stats.min == 10.5
    assert stats.max == 99.8
    assert stats.count == 100


def test_statistics_response_creation():
    """测试 StatisticsResponse 模型创建"""
    response = StatisticsResponse(
        file_id="test-123",
        sensors={
            "sensor1": SensorStatistics(min=10.0, max=90.0, mean=50.0, std=20.0, count=100),
            "sensor2": SensorStatistics(min=5.0, max=95.0, mean=48.0, std=22.0, count=100)
        },
        time_range={"start": "2024-01-01T00:00:00", "end": "2024-01-01T01:00:00"},
        total_records=100,
        filtered_records=100
    )
    
    assert response.file_id == "test-123"
    assert len(response.sensors) == 2
    assert "sensor1" in response.sensors
    assert response.total_records == 100


def test_chart_response_creation():
    """测试 ChartResponse 模型创建"""
    response = ChartResponse(
        data=[
            {"x": [1, 2, 3], "y": [10, 20, 30], "type": "scatter", "name": "sensor1"}
        ],
        layout={"title": "ECU Sensor Data", "xaxis": {"title": "Time"}},
        config={"responsive": True}
    )
    
    assert len(response.data) == 1
    assert response.layout["title"] == "ECU Sensor Data"
    assert response.config["responsive"] is True


def test_filter_params_optional_fields():
    """测试 FilterParams 的可选字段"""
    # 所有字段为空
    params1 = FilterParams()
    assert params1.start_time is None
    assert params1.end_time is None
    assert params1.sensors is None
    
    # 部分字段有值
    params2 = FilterParams(
        start_time=datetime(2024, 1, 1, 0, 0, 0),
        sensors=["sensor1", "sensor2"]
    )
    assert params2.start_time is not None
    assert params2.end_time is None
    assert len(params2.sensors) == 2


def test_filter_params_json_serialization():
    """测试 FilterParams 的 JSON 序列化（datetime 处理）"""
    params = FilterParams(
        start_time=datetime(2024, 1, 1, 0, 0, 0),
        end_time=datetime(2024, 1, 1, 23, 59, 59),
        sensors=["sensor1"]
    )
    
    json_data = params.model_dump_json()
    assert "2024-01-01T00:00:00" in json_data
    assert "2024-01-01T23:59:59" in json_data


def test_export_request_creation():
    """测试 ExportRequest 模型创建"""
    request = ExportRequest(
        file_id="test-123",
        format="csv",
        filters=FilterParams(sensors=["sensor1"]),
        include_metadata=True
    )
    
    assert request.file_id == "test-123"
    assert request.format == "csv"
    assert request.include_metadata is True
    assert request.filters.sensors == ["sensor1"]


def test_export_request_default_metadata():
    """测试 ExportRequest 的默认 include_metadata 值"""
    request = ExportRequest(
        file_id="test-123",
        format="json"
    )
    
    assert request.include_metadata is True


def test_error_response_creation():
    """测试 ErrorResponse 模型创建"""
    error = ErrorResponse(
        error_code="FILE_NOT_FOUND",
        message="File with ID 'abc123' does not exist",
        details={"file_id": "abc123"},
        timestamp=datetime(2024, 1, 1, 12, 0, 0)
    )
    
    assert error.error_code == "FILE_NOT_FOUND"
    assert "abc123" in error.message
    assert error.details["file_id"] == "abc123"


def test_error_response_json_serialization():
    """测试 ErrorResponse 的 JSON 序列化（datetime 处理）"""
    error = ErrorResponse(
        error_code="INTERNAL_ERROR",
        message="An internal error occurred",
        timestamp=datetime(2024, 1, 1, 12, 0, 0)
    )
    
    json_data = error.model_dump_json()
    assert "2024-01-01T12:00:00" in json_data
    assert "INTERNAL_ERROR" in json_data


def test_error_response_optional_details():
    """测试 ErrorResponse 的可选 details 字段"""
    error = ErrorResponse(
        error_code="BAD_REQUEST",
        message="Invalid parameter",
        timestamp=datetime.now()
    )
    
    assert error.details is None
