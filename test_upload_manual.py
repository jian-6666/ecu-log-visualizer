"""
Manual test script to verify the upload endpoint works

Run this after starting the server with: python src/main.py
"""

import requests
import io

# Server URL
BASE_URL = "http://localhost:8000"

def test_upload_csv():
    """Test uploading a CSV file"""
    print("Testing CSV upload...")
    
    # Create a simple CSV file
    csv_content = """timestamp,sensor1,sensor2,status
2024-01-01T00:00:00,23.5,45.2,OK
2024-01-01T00:00:01,23.6,45.3,OK
2024-01-01T00:00:02,23.7,45.4,OK
"""
    
    # Upload the file
    files = {'file': ('test_log.csv', csv_content, 'text/csv')}
    response = requests.post(f"{BASE_URL}/api/upload", files=files)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("✓ CSV upload successful!")
        return response.json()['file_id']
    else:
        print("✗ CSV upload failed!")
        return None

def test_upload_json():
    """Test uploading a JSON file"""
    print("\nTesting JSON upload...")
    
    # Create a simple JSON file
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
    
    # Upload the file
    files = {'file': ('test_log.json', json_content, 'application/json')}
    response = requests.post(f"{BASE_URL}/api/upload", files=files)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("✓ JSON upload successful!")
        return response.json()['file_id']
    else:
        print("✗ JSON upload failed!")
        return None

def test_invalid_format():
    """Test uploading an invalid file format"""
    print("\nTesting invalid format upload...")
    
    # Try to upload a text file
    files = {'file': ('test.txt', 'This is a text file', 'text/plain')}
    response = requests.post(f"{BASE_URL}/api/upload", files=files)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 400:
        print("✓ Invalid format correctly rejected!")
    else:
        print("✗ Invalid format not rejected properly!")

if __name__ == "__main__":
    print("=" * 60)
    print("ECU Log Visualizer - Upload Endpoint Manual Test")
    print("=" * 60)
    print("\nMake sure the server is running: python src/main.py")
    print()
    
    try:
        # Test health check first
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✓ Server is running!")
            print()
            
            # Run tests
            test_upload_csv()
            test_upload_json()
            test_invalid_format()
            
            print("\n" + "=" * 60)
            print("All manual tests completed!")
            print("=" * 60)
        else:
            print("✗ Server is not responding properly!")
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to server. Please start it first:")
        print("   python src/main.py")
