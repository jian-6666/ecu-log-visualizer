"""
Performance verification for ECU Log Visualizer
Tests performance requirements for 10MB files:
- Statistics calculation: < 2 seconds
- Chart generation: < 3 seconds
- Frontend filter response: < 1 second

Validates: Requirements 3.6, 4.5, 6.7
"""

from fastapi.testclient import TestClient
from src.main import app
from pathlib import Path
import tempfile
import time
from datetime import datetime, timedelta

client = TestClient(app)

def create_large_test_file(target_size_mb=10):
    """Create a large CSV file for performance testing"""
    print(f"\nCreating test file (target size: {target_size_mb}MB)...")
    
    # Calculate number of records needed
    # Each record is approximately: timestamp (20 bytes) + 10 sensors * 6 bytes = ~80 bytes per line
    bytes_per_line = 80
    target_bytes = target_size_mb * 1024 * 1024
    num_records = int(target_bytes / bytes_per_line)
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
    
    # Write header
    sensors = [f"sensor{i}" for i in range(1, 11)]  # 10 sensors
    temp_file.write(f"timestamp,{','.join(sensors)}\n")
    
    # Write data
    base_time = datetime(2024, 1, 1, 0, 0, 0)
    for i in range(num_records):
        timestamp = (base_time + timedelta(seconds=i)).isoformat()
        values = [f"{20 + (i % 100) * 0.1:.2f}" for _ in range(10)]
        temp_file.write(f"{timestamp},{','.join(values)}\n")
    
    temp_file.close()
    
    # Verify file size
    file_path = Path(temp_file.name)
    actual_size_mb = file_path.stat().st_size / (1024 * 1024)
    print(f"Created test file: {file_path}")
    print(f"Actual size: {actual_size_mb:.2f} MB")
    print(f"Records: {num_records:,}")
    
    return file_path

def test_performance():
    """Test all performance requirements"""
    print("=" * 80)
    print("ECU Log Visualizer - Performance Verification")
    print("=" * 80)
    
    # Create large test file
    test_file = create_large_test_file(target_size_mb=10)
    
    try:
        # Upload file
        print("\n1. Uploading test file...")
        with open(test_file, 'rb') as f:
            upload_response = client.post(
                "/api/upload",
                files={"file": ("performance_test.csv", f, "text/csv")}
            )
        
        assert upload_response.status_code == 200, f"Upload failed: {upload_response.status_code}"
        file_id = upload_response.json()["file_id"]
        print(f"   ✓ File uploaded (ID: {file_id})")
        
        # Test 1: Statistics calculation performance (< 2 seconds)
        print("\n2. Testing statistics calculation performance...")
        print("   Requirement: < 2 seconds for 10MB file")
        
        start_time = time.time()
        stats_response = client.get(f"/api/stats/{file_id}")
        stats_elapsed = time.time() - start_time
        
        assert stats_response.status_code == 200, f"Stats request failed: {stats_response.status_code}"
        stats_data = stats_response.json()
        
        print(f"   ✓ Statistics calculated in {stats_elapsed:.3f} seconds")
        if stats_elapsed < 2.0:
            print(f"   ✓ PASS: Within 2 second requirement")
        else:
            print(f"   ✗ FAIL: Exceeded 2 second requirement")
        
        print(f"     - Sensors: {len(stats_data['sensors'])}")
        print(f"     - Records: {stats_data['total_records']:,}")
        
        # Test 2: Chart generation performance (< 3 seconds)
        print("\n3. Testing chart generation performance...")
        print("   Requirement: < 3 seconds for 10MB file")
        
        start_time = time.time()
        chart_response = client.get(f"/api/chart/{file_id}")
        chart_elapsed = time.time() - start_time
        
        assert chart_response.status_code == 200, f"Chart request failed: {chart_response.status_code}"
        chart_data = chart_response.json()
        
        print(f"   ✓ Chart generated in {chart_elapsed:.3f} seconds")
        if chart_elapsed < 3.0:
            print(f"   ✓ PASS: Within 3 second requirement")
        else:
            print(f"   ✗ FAIL: Exceeded 3 second requirement")
        
        print(f"     - Traces: {len(chart_data['data'])}")
        
        # Test 3: Frontend filter response time (< 1 second)
        print("\n4. Testing frontend filter response time...")
        print("   Requirement: < 1 second")
        
        # Test with sensor filter
        sensor_names = list(stats_data['sensors'].keys())
        test_sensors = sensor_names[:3] if len(sensor_names) >= 3 else sensor_names
        
        start_time = time.time()
        filter_response = client.get(
            f"/api/stats/{file_id}",
            params={'sensors': ','.join(test_sensors)}
        )
        filter_elapsed = time.time() - start_time
        
        assert filter_response.status_code == 200, f"Filter request failed: {filter_response.status_code}"
        
        print(f"   ✓ Filtered statistics in {filter_elapsed:.3f} seconds")
        if filter_elapsed < 1.0:
            print(f"   ✓ PASS: Within 1 second requirement")
        else:
            print(f"   ✗ FAIL: Exceeded 1 second requirement")
        
        print(f"     - Filtered sensors: {', '.join(test_sensors)}")
        
        # Test with time range filter
        start_time = time.time()
        time_filter_response = client.get(
            f"/api/chart/{file_id}",
            params={
                'start_time': '2024-01-01T00:00:00',
                'end_time': '2024-01-01T01:00:00'
            }
        )
        time_filter_elapsed = time.time() - start_time
        
        assert time_filter_response.status_code == 200, f"Time filter request failed: {time_filter_response.status_code}"
        
        print(f"   ✓ Time-filtered chart in {time_filter_elapsed:.3f} seconds")
        if time_filter_elapsed < 1.0:
            print(f"   ✓ PASS: Within 1 second requirement")
        else:
            print(f"   ✗ FAIL: Exceeded 1 second requirement")
        
        # Summary
        print("\n" + "=" * 80)
        print("Performance Test Summary")
        print("=" * 80)
        
        all_passed = True
        
        print(f"\n1. Statistics Calculation (Req 3.6):")
        print(f"   Time: {stats_elapsed:.3f}s / 2.00s limit")
        if stats_elapsed < 2.0:
            print(f"   Status: ✓ PASS")
        else:
            print(f"   Status: ✗ FAIL")
            all_passed = False
        
        print(f"\n2. Chart Generation (Req 4.5):")
        print(f"   Time: {chart_elapsed:.3f}s / 3.00s limit")
        if chart_elapsed < 3.0:
            print(f"   Status: ✓ PASS")
        else:
            print(f"   Status: ✗ FAIL")
            all_passed = False
        
        print(f"\n3. Frontend Filter Response (Req 6.7):")
        print(f"   Sensor filter: {filter_elapsed:.3f}s / 1.00s limit")
        print(f"   Time filter: {time_filter_elapsed:.3f}s / 1.00s limit")
        if filter_elapsed < 1.0 and time_filter_elapsed < 1.0:
            print(f"   Status: ✓ PASS")
        else:
            print(f"   Status: ✗ FAIL")
            all_passed = False
        
        print("\n" + "=" * 80)
        if all_passed:
            print("✓ All performance requirements met!")
        else:
            print("✗ Some performance requirements not met")
        print("=" * 80)
        
        return all_passed
        
    finally:
        # Cleanup
        test_file.unlink()
        print(f"\nCleaned up test file: {test_file}")

if __name__ == "__main__":
    try:
        success = test_performance()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Performance test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
