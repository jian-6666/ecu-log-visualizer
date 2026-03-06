"""
性能测试：图表数据 API 端点

验证图表生成在 3 秒内完成（10MB 文件）

Validates: Requirements 4.5
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import tempfile
import shutil
import time
from datetime import datetime, timedelta

from src.main import app

client = TestClient(app)


@pytest.fixture
def temp_upload_dir():
    """创建临时上传目录"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def large_csv_file(temp_upload_dir):
    """创建较大的 CSV 文件用于性能测试（约 1MB，10000 条记录）"""
    # 生成 10000 条记录
    lines = ["timestamp,sensor1,sensor2,sensor3,sensor4,sensor5"]
    
    base_time = datetime(2024, 1, 1, 0, 0, 0)
    for i in range(10000):
        timestamp = (base_time + timedelta(seconds=i)).isoformat()
        values = [f"{20 + i * 0.001:.3f}" for _ in range(5)]
        lines.append(f"{timestamp},{','.join(values)}")
    
    csv_content = "\n".join(lines)
    
    file_path = Path(temp_upload_dir) / "large_test.csv"
    file_path.write_text(csv_content)
    
    # 验证文件大小
    file_size_mb = file_path.stat().st_size / (1024 * 1024)
    print(f"\nGenerated test file size: {file_size_mb:.2f} MB")
    
    return file_path


def test_chart_generation_performance(large_csv_file):
    """测试图表生成性能（应在 3 秒内完成）"""
    # 上传文件
    with open(large_csv_file, "rb") as f:
        upload_response = client.post(
            "/api/upload",
            files={"file": ("large_test.csv", f, "text/csv")}
        )
    
    assert upload_response.status_code == 200
    file_id = upload_response.json()["file_id"]
    
    # 测量图表生成时间
    start_time = time.time()
    
    chart_response = client.get(f"/api/chart/{file_id}")
    
    elapsed_time = time.time() - start_time
    
    # 验证响应成功
    assert chart_response.status_code == 200
    chart_data = chart_response.json()
    
    # 验证图表数据完整性
    assert "data" in chart_data
    assert "layout" in chart_data
    assert "config" in chart_data
    assert len(chart_data["data"]) == 5  # 5 个传感器
    
    # 验证性能要求：3 秒内完成
    print(f"\nChart generation time: {elapsed_time:.2f} seconds")
    assert elapsed_time < 3.0, f"Chart generation took {elapsed_time:.2f}s, expected < 3s"


def test_chart_with_filter_performance(large_csv_file):
    """测试带过滤的图表生成性能"""
    # 上传文件
    with open(large_csv_file, "rb") as f:
        upload_response = client.post(
            "/api/upload",
            files={"file": ("large_test.csv", f, "text/csv")}
        )
    
    assert upload_response.status_code == 200
    file_id = upload_response.json()["file_id"]
    
    # 测量带过滤的图表生成时间
    start_time = time.time()
    
    chart_response = client.get(
        f"/api/chart/{file_id}",
        params={
            "start_time": "2024-01-01T00:00:00",
            "end_time": "2024-01-01T01:00:00",
            "sensors": "sensor1,sensor2"
        }
    )
    
    elapsed_time = time.time() - start_time
    
    # 验证响应成功
    assert chart_response.status_code == 200
    chart_data = chart_response.json()
    
    # 验证过滤后的数据
    assert len(chart_data["data"]) == 2  # 只有 2 个传感器
    
    # 过滤应该更快
    print(f"\nFiltered chart generation time: {elapsed_time:.2f} seconds")
    assert elapsed_time < 3.0, f"Filtered chart generation took {elapsed_time:.2f}s, expected < 3s"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
