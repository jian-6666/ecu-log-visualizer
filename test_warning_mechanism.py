"""
Test script to verify the warning mechanism implementation
"""

import pandas as pd
from pathlib import Path
import sys
import tempfile
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.data_analyzer import DataAnalyzer


def test_warning_with_line_numbers():
    """Test that warnings include line numbers for invalid data"""
    print("Testing warning mechanism with line numbers...")
    
    # Create a temporary CSV file with some invalid data
    csv_content = """timestamp,sensor1,sensor2,sensor3
2024-01-01T00:00:00,23.5,45.2,67.8
2024-01-01T00:00:01,23.6,invalid,67.9
2024-01-01T00:00:02,23.7,45.4,N/A
2024-01-01T00:00:03,1e11,45.5,68.1
2024-01-01T00:00:04,23.9,45.6,68.2
"""
    
    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        temp_file = f.name
    
    try:
        # Parse the file
        analyzer = DataAnalyzer()
        df = analyzer.parse_csv(Path(temp_file))
        
        print(f"✓ Parsed CSV file successfully")
        print(f"  Original records: {len(df)}")
        
        # Validate data
        cleaned_df, warnings, skipped_count = analyzer.validate_data(df)
        
        print(f"✓ Validated data successfully")
        print(f"  Records after validation: {len(cleaned_df)}")
        print(f"  Skipped entries: {skipped_count}")
        print(f"  Warnings generated: {len(warnings)}")
        
        # Display warnings
        if warnings:
            print("\nWarnings:")
            for i, warning in enumerate(warnings, 1):
                print(f"  {i}. {warning}")
        
        # Verify warnings contain line numbers
        has_line_numbers = any('line' in w.lower() for w in warnings)
        if has_line_numbers:
            print("\n✓ Warnings include line numbers")
        else:
            print("\n✗ Warnings do NOT include line numbers")
            return False
        
        # Verify skipped count is correct
        expected_skipped = 3  # Lines 3, 4, 5 have issues
        if skipped_count == expected_skipped:
            print(f"✓ Skipped count is correct: {skipped_count}")
        else:
            print(f"✗ Skipped count mismatch: expected {expected_skipped}, got {skipped_count}")
            return False
        
        # Verify remaining data is valid
        expected_remaining = 2  # Lines 2 and 6 are valid
        if len(cleaned_df) == expected_remaining:
            print(f"✓ Remaining records count is correct: {len(cleaned_df)}")
        else:
            print(f"✗ Remaining records mismatch: expected {expected_remaining}, got {len(cleaned_df)}")
            return False
        
        print("\n✓ All tests passed!")
        return True
        
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def test_api_response_includes_warnings():
    """Test that API responses include warnings"""
    print("\n" + "="*60)
    print("Testing API response structure...")
    
    from src.models import StatisticsResponse, SensorStatistics, ChartResponse
    
    # Test StatisticsResponse model
    stats_response = StatisticsResponse(
        file_id="test123",
        sensors={
            "sensor1": SensorStatistics(min=1.0, max=10.0, mean=5.5, std=2.5, count=100)
        },
        time_range={"start": "2024-01-01T00:00:00", "end": "2024-01-01T01:00:00"},
        total_records=105,
        filtered_records=100,
        warnings=["line 3, column 'sensor2': non-numeric value 'invalid'"],
        skipped_entries=5
    )
    
    print("✓ StatisticsResponse model accepts warnings and skipped_entries")
    
    # Test ChartResponse model
    chart_response = ChartResponse(
        data=[{"x": [1, 2, 3], "y": [4, 5, 6], "type": "scatter"}],
        layout={"title": "Test Chart"},
        config={"responsive": True},
        warnings=["line 4, column 'sensor3': value outside valid range"],
        skipped_entries=2
    )
    
    print("✓ ChartResponse model accepts warnings and skipped_entries")
    
    # Verify fields are optional
    stats_no_warnings = StatisticsResponse(
        file_id="test456",
        sensors={
            "sensor1": SensorStatistics(min=1.0, max=10.0, mean=5.5, std=2.5, count=100)
        },
        time_range={"start": "2024-01-01T00:00:00", "end": "2024-01-01T01:00:00"},
        total_records=100,
        filtered_records=100
    )
    
    print("✓ Warnings and skipped_entries are optional fields")
    
    print("\n✓ All API response tests passed!")
    return True


if __name__ == "__main__":
    print("="*60)
    print("Warning Mechanism Verification Tests")
    print("="*60)
    
    success = True
    
    # Run tests
    success = test_warning_with_line_numbers() and success
    success = test_api_response_includes_warnings() and success
    
    print("\n" + "="*60)
    if success:
        print("✓ ALL TESTS PASSED")
        print("="*60)
        sys.exit(0)
    else:
        print("✗ SOME TESTS FAILED")
        print("="*60)
        sys.exit(1)
