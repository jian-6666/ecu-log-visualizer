"""
集成测试：图表数据 API 端点

测试 GET /api/chart/{file_id} 端点的功能，包括：
- 获取图表数据
- 多传感器图表
- 带过滤的图表
- 响应格式符合 Plotly 规范
- 错误处理（文件不存在、无效参数）

Validates: Requirements 4.4, 4.5, 5.1, 5.2, 5.3, 10.2
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import tempfile
import shutil
from datetime import datetime

from src.main import app
from src.file_handler import FileHandler

client = TestClient(app)


@pytest.fixture
def temp_upload_dir():
    """创建临时上传目录"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_csv_file(temp_upload_dir):
    """创建示例 CSV 文件用于测试"""
    csv_content = """timestamp,sensor1,sensor2,sensor3
2024-01-01T00:00:00,23.5,45.2,67.8
2024-01-01T00:00:01,23.6,45.3,67.9
2024-01-01T00:00:02,23.7,45.4,68.0
2024-01-01T00:00:03,23.8,45.5,68.1
2024-01-01T00:00:04,23.9,45.6,68.2
"""
    
    file_path = Path(temp_upload_dir) / "test_chart.csv"
    file_path.write_text(csv_content)
    
    return file_path


def test_get_chart_success(sample_csv_file, monkeypatch):
    """测试成功获取图表数据"""
    # 上传文件
    with open(sample_csv_file, "rb") as f:
        upload_response = client.post(
            "/api/upload",
            files={"file": ("test_chart.csv", f, "text/csv")}
        )
    
    assert upload_response.status_code == 200
    file_id = upload_response.json()["file_id"]
    
    # 获取图表数据
    chart_response = client.get(f"/api/chart/{file_id}")
    
    assert chart_response.status_code == 200
    chart_data = chart_response.json()
    
    # 验证响应结构
    assert "data" in chart_data
    assert "layout" in chart_data
    assert "config" in chart_data
    
    # 验证 data 字段（Plotly traces）
    assert isinstance(chart_data["data"], list)
    assert len(chart_data["data"]) == 3  # 3 个传感器
    
    # 验证每个 trace 的结构
    for trace in chart_data["data"]:
        assert "type" in trace
        assert trace["type"] == "scatter"
        assert "x" in trace  # 时间戳
        assert "y" in trace  # 传感器值
        assert "name" in trace  # 传感器名称
        assert isinstance(trace["x"], list)
        assert isinstance(trace["y"], list)
        assert len(trace["x"]) == 5  # 5 个数据点
        assert len(trace["y"]) == 5
    
    # 验证 layout 字段
    assert isinstance(chart_data["layout"], dict)
    assert "title" in chart_data["layout"]
    assert "xaxis" in chart_data["layout"]
    assert "yaxis" in chart_data["layout"]
    
    # 验证 config 字段
    assert isinstance(chart_data["config"], dict)


def test_get_chart_with_sensor_filter(sample_csv_file):
    """测试带传感器过滤的图表"""
    # 上传文件
    with open(sample_csv_file, "rb") as f:
        upload_response = client.post(
            "/api/upload",
            files={"file": ("test_chart.csv", f, "text/csv")}
        )
    
    assert upload_response.status_code == 200
    file_id = upload_response.json()["file_id"]
    
    # 获取图表数据，只显示 sensor1 和 sensor2
    chart_response = client.get(
        f"/api/chart/{file_id}",
        params={"sensors": "sensor1,sensor2"}
    )
    
    assert chart_response.status_code == 200
    chart_data = chart_response.json()
    
    # 验证只有 2 个传感器的 traces
    assert len(chart_data["data"]) == 2
    
    # 验证传感器名称
    sensor_names = [trace["name"] for trace in chart_data["data"]]
    assert "sensor1" in sensor_names
    assert "sensor2" in sensor_names
    assert "sensor3" not in sensor_names


def test_get_chart_with_time_filter(sample_csv_file):
    """测试带时间范围过滤的图表"""
    # 上传文件
    with open(sample_csv_file, "rb") as f:
        upload_response = client.post(
            "/api/upload",
            files={"file": ("test_chart.csv", f, "text/csv")}
        )
    
    assert upload_response.status_code == 200
    file_id = upload_response.json()["file_id"]
    
    # 获取图表数据，只显示前 3 个数据点
    chart_response = client.get(
        f"/api/chart/{file_id}",
        params={
            "start_time": "2024-01-01T00:00:00",
            "end_time": "2024-01-01T00:00:02"
        }
    )
    
    assert chart_response.status_code == 200
    chart_data = chart_response.json()
    
    # 验证每个 trace 只有 3 个数据点
    for trace in chart_data["data"]:
        assert len(trace["x"]) == 3
        assert len(trace["y"]) == 3


def test_get_chart_with_combined_filters(sample_csv_file):
    """测试组合过滤（时间 + 传感器）"""
    # 上传文件
    with open(sample_csv_file, "rb") as f:
        upload_response = client.post(
            "/api/upload",
            files={"file": ("test_chart.csv", f, "text/csv")}
        )
    
    assert upload_response.status_code == 200
    file_id = upload_response.json()["file_id"]
    
    # 获取图表数据，应用时间和传感器过滤
    chart_response = client.get(
        f"/api/chart/{file_id}",
        params={
            "start_time": "2024-01-01T00:00:01",
            "end_time": "2024-01-01T00:00:03",
            "sensors": "sensor1"
        }
    )
    
    assert chart_response.status_code == 200
    chart_data = chart_response.json()
    
    # 验证只有 1 个传感器
    assert len(chart_data["data"]) == 1
    assert chart_data["data"][0]["name"] == "sensor1"
    
    # 验证只有 3 个数据点（时间范围内）
    assert len(chart_data["data"][0]["x"]) == 3
    assert len(chart_data["data"][0]["y"]) == 3


def test_get_chart_file_not_found():
    """测试文件不存在时返回 404"""
    response = client.get("/api/chart/nonexistent-file-id")
    
    assert response.status_code == 404
    error_data = response.json()
    # New standardized error format
    assert "error_code" in error_data
    assert error_data["error_code"] == "FILE_NOT_FOUND"
    assert "nonexistent-file-id" in error_data["message"]


def test_get_chart_invalid_time_format(sample_csv_file):
    """测试无效的时间格式返回 400"""
    # 上传文件
    with open(sample_csv_file, "rb") as f:
        upload_response = client.post(
            "/api/upload",
            files={"file": ("test_chart.csv", f, "text/csv")}
        )
    
    assert upload_response.status_code == 200
    file_id = upload_response.json()["file_id"]
    
    # 使用无效的时间格式
    response = client.get(
        f"/api/chart/{file_id}",
        params={"start_time": "invalid-date"}
    )
    
    assert response.status_code == 400
    error_data = response.json()
    # New standardized error format
    assert "error_code" in error_data
    assert error_data["error_code"] == "INVALID_PARAMETER"
    assert "start_time" in error_data["message"]


def test_get_chart_invalid_sensor(sample_csv_file):
    """测试无效的传感器名称返回 400"""
    # 上传文件
    with open(sample_csv_file, "rb") as f:
        upload_response = client.post(
            "/api/upload",
            files={"file": ("test_chart.csv", f, "text/csv")}
        )
    
    assert upload_response.status_code == 200
    file_id = upload_response.json()["file_id"]
    
    # 使用不存在的传感器名称
    response = client.get(
        f"/api/chart/{file_id}",
        params={"sensors": "nonexistent_sensor"}
    )
    
    assert response.status_code == 400
    error_data = response.json()
    # New standardized error format
    assert "error_code" in error_data
    assert error_data["error_code"] == "FILTER_ERROR"


def test_get_chart_empty_sensor_list(sample_csv_file):
    """测试空的传感器列表返回 400"""
    # 上传文件
    with open(sample_csv_file, "rb") as f:
        upload_response = client.post(
            "/api/upload",
            files={"file": ("test_chart.csv", f, "text/csv")}
        )
    
    assert upload_response.status_code == 200
    file_id = upload_response.json()["file_id"]
    
    # 使用空的传感器列表 - empty string is treated as no filter, so we expect 200
    # To test empty list validation, we need to pass something that parses to empty list
    response = client.get(
        f"/api/chart/{file_id}",
        params={"sensors": ",,,"}  # This will parse to empty list after stripping
    )
    
    assert response.status_code == 400
    error_data = response.json()
    # New standardized error format
    assert "error_code" in error_data
    assert error_data["error_code"] == "INVALID_PARAMETER"


def test_chart_plotly_format_compliance(sample_csv_file):
    """测试图表格式符合 Plotly 规范"""
    # 上传文件
    with open(sample_csv_file, "rb") as f:
        upload_response = client.post(
            "/api/upload",
            files={"file": ("test_chart.csv", f, "text/csv")}
        )
    
    assert upload_response.status_code == 200
    file_id = upload_response.json()["file_id"]
    
    # 获取图表数据
    chart_response = client.get(f"/api/chart/{file_id}")
    
    assert chart_response.status_code == 200
    chart_data = chart_response.json()
    
    # 验证 Plotly trace 必需字段
    for trace in chart_data["data"]:
        assert "type" in trace
        assert "x" in trace
        assert "y" in trace
        assert "name" in trace
        
        # 验证 scatter 类型的特定字段
        if trace["type"] == "scatter":
            assert "mode" in trace
    
    # 验证 Plotly layout 必需字段
    layout = chart_data["layout"]
    assert "xaxis" in layout
    assert "yaxis" in layout
    assert "title" in layout
    
    # 验证 config 包含交互选项
    config = chart_data["config"]
    assert "displayModeBar" in config or "responsive" in config


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
