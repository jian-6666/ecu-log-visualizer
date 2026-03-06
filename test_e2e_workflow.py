"""
End-to-end workflow test for ECU Log Visualizer
Tests the complete workflow: upload, parse, statistics, visualization, and export
"""

import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_complete_workflow():
    """Test complete workflow using sample data"""
    print("=" * 80)
    print("ECU Log Visualizer - End-to-End Workflow Test")
    print("=" * 80)
    
    # 1. Test server health
    print("\n1. Testing server health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        print("   ✓ Server is healthy")
    except Exception as e:
        print(f"   ✗ Server health check failed: {e}")
        return False
    
    # 2. Upload CSV file
    print("\n2. Testing file upload (CSV)...")
    csv_file = Path("examples/sample_ecu_log.csv")
    if not csv_file.exists():
        print(f"   ✗ Sample file not found: {csv_file}")
        return False
    
    try:
        with open(csv_file, 'rb') as f:
            files = {'file': ('sample_ecu_log.csv', f, 'text/csv')}
            response = requests.post(f"{BASE_URL}/api/upload", files=files)
        
        assert response.status_code == 200, f"Upload failed: {response.status_code}"
        upload_data = response.json()
        file_id = upload_data['file_id']
        print(f"   ✓ File uploaded successfully (ID: {file_id})")
        print(f"     - Filename: {upload_data['filename']}")
        print(f"     - Size: {upload_data['size']} bytes")
    except Exception as e:
        print(f"   ✗ File upload failed: {e}")
        return False
    
    # 3. Get statistics
    print("\n3. Testing statistics calculation...")
    try:
        response = requests.get(f"{BASE_URL}/api/stats/{file_id}")
        assert response.status_code == 200, f"Stats request failed: {response.status_code}"
        stats_data = response.json()
        
        print(f"   ✓ Statistics calculated successfully")
        print(f"     - Sensors found: {len(stats_data['sensors'])}")
        for sensor_name, sensor_stats in list(stats_data['sensors'].items())[:3]:
            print(f"     - {sensor_name}:")
            print(f"       min={sensor_stats['min']:.2f}, max={sensor_stats['max']:.2f}, "
                  f"mean={sensor_stats['mean']:.2f}, std={sensor_stats['std']:.2f}")
    except Exception as e:
        print(f"   ✗ Statistics calculation failed: {e}")
        return False
    
    # 4. Get chart data
    print("\n4. Testing chart generation...")
    try:
        response = requests.get(f"{BASE_URL}/api/chart/{file_id}")
        assert response.status_code == 200, f"Chart request failed: {response.status_code}"
        chart_data = response.json()
        
        assert 'data' in chart_data, "Chart data missing 'data' field"
        assert 'layout' in chart_data, "Chart data missing 'layout' field"
        
        print(f"   ✓ Chart generated successfully")
        print(f"     - Number of traces: {len(chart_data['data'])}")
        print(f"     - Chart title: {chart_data['layout'].get('title', {}).get('text', 'N/A')}")
    except Exception as e:
        print(f"   ✗ Chart generation failed: {e}")
        return False
    
    # 5. Test filtering
    print("\n5. Testing data filtering...")
    try:
        # Get first sensor name
        sensor_names = list(stats_data['sensors'].keys())
        if len(sensor_names) > 0:
            test_sensor = sensor_names[0]
            response = requests.get(
                f"{BASE_URL}/api/stats/{file_id}",
                params={'sensors': test_sensor}
            )
            assert response.status_code == 200, f"Filtered stats failed: {response.status_code}"
            filtered_stats = response.json()
            
            assert test_sensor in filtered_stats['sensors'], f"Sensor {test_sensor} not in filtered results"
            print(f"   ✓ Filtering works correctly")
            print(f"     - Filtered by sensor: {test_sensor}")
    except Exception as e:
        print(f"   ✗ Filtering test failed: {e}")
        return False
    
    # 6. Test CSV export
    print("\n6. Testing CSV export...")
    try:
        response = requests.get(f"{BASE_URL}/api/export/{file_id}", params={'format': 'csv'})
        assert response.status_code == 200, f"CSV export failed: {response.status_code}"
        assert 'text/csv' in response.headers.get('content-type', ''), "Wrong content type for CSV"
        
        csv_content = response.text
        lines = csv_content.strip().split('\n')
        print(f"   ✓ CSV export successful")
        print(f"     - Exported {len(lines)} lines (including header)")
    except Exception as e:
        print(f"   ✗ CSV export failed: {e}")
        return False
    
    # 7. Test JSON export
    print("\n7. Testing JSON export...")
    try:
        response = requests.get(f"{BASE_URL}/api/export/{file_id}", params={'format': 'json'})
        assert response.status_code == 200, f"JSON export failed: {response.status_code}"
        
        export_data = response.json()
        assert 'data' in export_data, "JSON export missing 'data' field"
        assert 'metadata' in export_data, "JSON export missing 'metadata' field"
        
        print(f"   ✓ JSON export successful")
        print(f"     - Exported {len(export_data['data'])} records")
        print(f"     - Metadata includes: {', '.join(export_data['metadata'].keys())}")
    except Exception as e:
        print(f"   ✗ JSON export failed: {e}")
        return False
    
    # 8. Test error handling
    print("\n8. Testing error handling...")
    try:
        # Test with non-existent file ID
        response = requests.get(f"{BASE_URL}/api/stats/nonexistent-id")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        error_data = response.json()
        assert 'error_code' in error_data, "Error response missing 'error_code'"
        assert 'message' in error_data, "Error response missing 'message'"
        
        print(f"   ✓ Error handling works correctly")
        print(f"     - 404 error properly returned for non-existent file")
        print(f"     - Error code: {error_data['error_code']}")
    except Exception as e:
        print(f"   ✗ Error handling test failed: {e}")
        return False
    
    # 9. Test with JSON file
    print("\n9. Testing with JSON file...")
    json_file = Path("examples/sample_ecu_log.json")
    if json_file.exists():
        try:
            with open(json_file, 'rb') as f:
                files = {'file': ('sample_ecu_log.json', f, 'application/json')}
                response = requests.post(f"{BASE_URL}/api/upload", files=files)
            
            assert response.status_code == 200, f"JSON upload failed: {response.status_code}"
            json_file_id = response.json()['file_id']
            
            # Get stats for JSON file
            response = requests.get(f"{BASE_URL}/api/stats/{json_file_id}")
            assert response.status_code == 200, f"JSON stats failed: {response.status_code}"
            
            print(f"   ✓ JSON file processing works correctly")
            print(f"     - File ID: {json_file_id}")
        except Exception as e:
            print(f"   ✗ JSON file test failed: {e}")
            return False
    else:
        print(f"   ⊘ JSON sample file not found, skipping")
    
    print("\n" + "=" * 80)
    print("✓ All end-to-end tests passed successfully!")
    print("=" * 80)
    return True

if __name__ == "__main__":
    try:
        success = test_complete_workflow()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
