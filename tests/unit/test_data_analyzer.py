"""
DataAnalyzer 模块的单元测试
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import os
from src.data_analyzer import DataAnalyzer


class TestDataAnalyzer:
    """DataAnalyzer 类的测试套件"""
    
    @pytest.fixture
    def analyzer(self):
        """创建 DataAnalyzer 实例"""
        return DataAnalyzer()
    
    @pytest.fixture
    def valid_csv_file(self):
        """创建有效的 CSV 测试文件"""
        content = """timestamp,sensor1,sensor2,sensor3,status
2024-01-01T00:00:00,23.5,45.2,67.8,OK
2024-01-01T00:00:01,23.6,45.3,67.9,OK
2024-01-01T00:00:02,23.7,45.4,68.0,OK
2024-01-01T00:00:03,23.8,45.5,68.1,OK
2024-01-01T00:00:04,23.9,45.6,68.2,OK"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        yield Path(temp_path)
        
        # 清理
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @pytest.fixture
    def csv_with_non_numeric(self):
        """创建包含非数值数据的 CSV 文件"""
        content = """timestamp,sensor1,sensor2
2024-01-01T00:00:00,23.5,45.2
2024-01-01T00:00:01,N/A,45.3
2024-01-01T00:00:02,23.7,invalid
2024-01-01T00:00:03,23.8,45.5"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        yield Path(temp_path)
        
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @pytest.fixture
    def csv_with_unordered_timestamps(self):
        """创建时间戳乱序的 CSV 文件"""
        content = """timestamp,sensor1,sensor2
2024-01-01T00:00:02,23.7,45.4
2024-01-01T00:00:00,23.5,45.2
2024-01-01T00:00:03,23.8,45.5
2024-01-01T00:00:01,23.6,45.3"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        yield Path(temp_path)
        
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    # ===== parse_csv 测试 =====
    
    def test_parse_csv_valid_file(self, analyzer, valid_csv_file):
        """测试解析有效的 CSV 文件"""
        df = analyzer.parse_csv(valid_csv_file)
        
        # 验证数据框结构
        assert 'timestamp' in df.columns
        assert 'sensor1' in df.columns
        assert 'sensor2' in df.columns
        assert 'sensor3' in df.columns
        
        # 验证 status 列被排除（非数值列）
        assert 'status' not in df.columns
        
        # 验证数据类型
        assert pd.api.types.is_datetime64_any_dtype(df['timestamp'])
        assert pd.api.types.is_numeric_dtype(df['sensor1'])
        
        # 验证数据行数
        assert len(df) == 5
    
    def test_parse_csv_file_not_found(self, analyzer):
        """测试文件不存在的情况"""
        with pytest.raises(FileNotFoundError):
            analyzer.parse_csv(Path("nonexistent.csv"))
    
    def test_parse_csv_missing_timestamp_column(self, analyzer):
        """测试缺少 timestamp 列的情况"""
        content = """sensor1,sensor2
23.5,45.2
23.6,45.3"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="must contain 'timestamp' column"):
                analyzer.parse_csv(Path(temp_path))
        finally:
            os.unlink(temp_path)
    
    def test_parse_csv_invalid_timestamp_format(self, analyzer):
        """测试无效的时间戳格式"""
        content = """timestamp,sensor1
invalid-date,23.5
2024-01-01T00:00:01,23.6"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Invalid timestamp format"):
                analyzer.parse_csv(Path(temp_path))
        finally:
            os.unlink(temp_path)
    
    def test_parse_csv_no_numeric_columns(self, analyzer):
        """测试没有数值列的情况"""
        content = """timestamp,status
2024-01-01T00:00:00,OK
2024-01-01T00:00:01,OK"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="must contain at least one numeric sensor column"):
                analyzer.parse_csv(Path(temp_path))
        finally:
            os.unlink(temp_path)
    
    def test_parse_csv_empty_file(self, analyzer):
        """测试空文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="CSV file is empty"):
                analyzer.parse_csv(Path(temp_path))
        finally:
            os.unlink(temp_path)
    
    # ===== validate_data 测试 =====
    
    def test_validate_data_clean_data(self, analyzer):
        """测试验证干净的数据"""
        df = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=5, freq='s'),
            'sensor1': [23.5, 23.6, 23.7, 23.8, 23.9],
            'sensor2': [45.2, 45.3, 45.4, 45.5, 45.6]
        })
        
        validated_df, warnings, skipped_count = analyzer.validate_data(df)
        
        # 验证没有警告
        assert len(warnings) == 0
        assert skipped_count == 0
        
        # 验证数据未被修改
        assert len(validated_df) == 5
        pd.testing.assert_frame_equal(validated_df, df)
    
    def test_validate_data_unordered_timestamps(self, analyzer):
        """测试乱序时间戳的自动排序"""
        df = pd.DataFrame({
            'timestamp': pd.to_datetime([
                '2024-01-01T00:00:02',
                '2024-01-01T00:00:00',
                '2024-01-01T00:00:03',
                '2024-01-01T00:00:01'
            ]),
            'sensor1': [23.7, 23.5, 23.8, 23.6]
        })
        
        validated_df, warnings, skipped_count = analyzer.validate_data(df)
        
        # 验证有排序警告
        assert any('not in chronological order' in w for w in warnings)
        
        # 验证数据已排序
        assert validated_df['timestamp'].is_monotonic_increasing
        assert validated_df['sensor1'].tolist() == [23.5, 23.6, 23.7, 23.8]
    
    def test_validate_data_non_numeric_values(self, analyzer, csv_with_non_numeric):
        """测试非数值数据的处理"""
        df = analyzer.parse_csv(csv_with_non_numeric)
        validated_df, warnings, skipped_count = analyzer.validate_data(df)
        
        # 验证有警告
        assert len(warnings) > 0
        assert any('non-numeric' in w.lower() for w in warnings)
        assert skipped_count > 0
        
        # 验证无效行被删除
        assert len(validated_df) < len(df)
        
        # 验证剩余数据都是有效的（只检查存在的列）
        for col in validated_df.columns:
            if col != 'timestamp':
                assert not validated_df[col].isna().any()
    
    def test_validate_data_out_of_range_values(self, analyzer):
        """测试超出范围的数值"""
        df = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=5, freq='s'),
            'sensor1': [23.5, 2e10, 23.7, -2e10, 23.9]  # 超出范围
        })
        
        validated_df, warnings, skipped_count = analyzer.validate_data(df)
        
        # 验证有范围警告
        assert any('outside valid range' in w for w in warnings)
        assert skipped_count == 2
        
        # 验证超出范围的行被删除
        assert len(validated_df) == 3
        assert all((validated_df['sensor1'] >= -1e10) & (validated_df['sensor1'] <= 1e10))
    
    def test_validate_data_all_invalid(self, analyzer):
        """测试所有数据都无效的情况"""
        df = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=3, freq='s'),
            'sensor1': [np.nan, np.nan, np.nan]
        })
        
        with pytest.raises(ValueError, match="No valid data remaining"):
            analyzer.validate_data(df)
    
    # ===== get_sensor_names 测试 =====
    
    def test_get_sensor_names(self, analyzer):
        """测试获取传感器名称"""
        df = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=3, freq='s'),
            'sensor1': [23.5, 23.6, 23.7],
            'sensor2': [45.2, 45.3, 45.4],
            'sensor3': [67.8, 67.9, 68.0]
        })
        
        sensor_names = analyzer.get_sensor_names(df)
        
        assert 'timestamp' not in sensor_names
        assert 'sensor1' in sensor_names
        assert 'sensor2' in sensor_names
        assert 'sensor3' in sensor_names
        assert len(sensor_names) == 3
    
    def test_get_sensor_names_empty_dataframe(self, analyzer):
        """测试空数据框"""
        df = pd.DataFrame({'timestamp': []})
        sensor_names = analyzer.get_sensor_names(df)
        assert len(sensor_names) == 0
    
    # ===== 集成测试 =====
    
    def test_parse_and_validate_integration(self, analyzer, valid_csv_file):
        """测试解析和验证的完整流程"""
        # 解析文件
        df = analyzer.parse_csv(valid_csv_file)
        
        # 验证数据
        validated_df, warnings, skipped_count = analyzer.validate_data(df)
        
        # 获取传感器名称
        sensor_names = analyzer.get_sensor_names(validated_df)
        
        # 验证结果
        assert len(validated_df) == 5
        assert len(sensor_names) == 3
        assert 'sensor1' in sensor_names
        assert len(warnings) == 0
    
    def test_parse_and_validate_with_issues(self, analyzer, csv_with_unordered_timestamps):
        """测试解析和验证包含问题的数据"""
        # 解析文件
        df = analyzer.parse_csv(csv_with_unordered_timestamps)
        
        # 验证数据
        validated_df, warnings, skipped_count = analyzer.validate_data(df)
        
        # 验证警告存在
        assert len(warnings) > 0
        
        # 验证数据已排序
        assert validated_df['timestamp'].is_monotonic_increasing

    # ===== calculate_statistics 测试 =====
    
    def test_calculate_statistics_all_sensors(self, analyzer):
        """测试计算所有传感器的统计信息"""
        df = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=5, freq='s'),
            'sensor1': [10.0, 20.0, 30.0, 40.0, 50.0],
            'sensor2': [5.0, 10.0, 15.0, 20.0, 25.0]
        })
        
        stats = analyzer.calculate_statistics(df)
        
        # 验证返回了所有传感器的统计信息
        assert 'sensor1' in stats
        assert 'sensor2' in stats
        
        # 验证 sensor1 的统计信息
        assert stats['sensor1']['min'] == 10.0
        assert stats['sensor1']['max'] == 50.0
        assert stats['sensor1']['mean'] == 30.0
        assert stats['sensor1']['count'] == 5
        
        # 验证 sensor2 的统计信息
        assert stats['sensor2']['min'] == 5.0
        assert stats['sensor2']['max'] == 25.0
        assert stats['sensor2']['mean'] == 15.0
        assert stats['sensor2']['count'] == 5
    
    def test_calculate_statistics_specific_sensors(self, analyzer):
        """测试计算指定传感器的统计信息"""
        df = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=5, freq='s'),
            'sensor1': [10.0, 20.0, 30.0, 40.0, 50.0],
            'sensor2': [5.0, 10.0, 15.0, 20.0, 25.0],
            'sensor3': [1.0, 2.0, 3.0, 4.0, 5.0]
        })
        
        # 只计算 sensor1 和 sensor3 的统计信息
        stats = analyzer.calculate_statistics(df, sensors=['sensor1', 'sensor3'])
        
        # 验证只返回了指定传感器的统计信息
        assert 'sensor1' in stats
        assert 'sensor3' in stats
        assert 'sensor2' not in stats
        
        # 验证统计信息正确
        assert stats['sensor1']['min'] == 10.0
        assert stats['sensor3']['max'] == 5.0
    
    def test_calculate_statistics_empty_dataframe(self, analyzer):
        """测试空数据框"""
        df = pd.DataFrame({'timestamp': [], 'sensor1': []})
        
        with pytest.raises(ValueError, match="Cannot calculate statistics on empty DataFrame"):
            analyzer.calculate_statistics(df)
    
    def test_calculate_statistics_no_sensor_columns(self, analyzer):
        """测试没有传感器列的数据框"""
        df = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=5, freq='s')
        })
        
        with pytest.raises(ValueError, match="contains no sensor columns"):
            analyzer.calculate_statistics(df)
    
    def test_calculate_statistics_invalid_sensor_name(self, analyzer):
        """测试指定不存在的传感器"""
        df = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=5, freq='s'),
            'sensor1': [10.0, 20.0, 30.0, 40.0, 50.0]
        })
        
        with pytest.raises(ValueError, match="Sensors not found in data"):
            analyzer.calculate_statistics(df, sensors=['sensor1', 'nonexistent'])
    
    def test_calculate_statistics_empty_sensor_list(self, analyzer):
        """测试空的传感器列表"""
        df = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=5, freq='s'),
            'sensor1': [10.0, 20.0, 30.0, 40.0, 50.0]
        })
        
        with pytest.raises(ValueError, match="Sensor list cannot be empty"):
            analyzer.calculate_statistics(df, sensors=[])
    
    def test_calculate_statistics_standard_deviation(self, analyzer):
        """测试标准差计算"""
        df = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=4, freq='s'),
            'sensor1': [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0][:4]  # 简化数据
        })
        
        stats = analyzer.calculate_statistics(df)
        
        # 验证标准差存在且为正数（对于非常量数据）
        assert 'std' in stats['sensor1']
        assert stats['sensor1']['std'] >= 0
    
    def test_calculate_statistics_single_value(self, analyzer):
        """测试单个数据点的统计"""
        df = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=1, freq='s'),
            'sensor1': [42.0]
        })
        
        stats = analyzer.calculate_statistics(df)
        
        # 验证单个值的统计信息
        assert stats['sensor1']['min'] == 42.0
        assert stats['sensor1']['max'] == 42.0
        assert stats['sensor1']['mean'] == 42.0
        assert stats['sensor1']['count'] == 1
        # 单个值的标准差应该是 NaN 或 0
        assert np.isnan(stats['sensor1']['std']) or stats['sensor1']['std'] == 0.0
    
    # ===== filter_data 测试 =====
    
    def test_filter_data_by_start_time(self, analyzer):
        """测试按开始时间过滤"""
        timestamps = pd.date_range('2024-01-01', periods=5, freq='s')
        df = pd.DataFrame({
            'timestamp': timestamps,
            'sensor1': [10.0, 20.0, 30.0, 40.0, 50.0]
        })
        
        # 过滤：从第3个时间点开始
        start_time = timestamps[2]
        filtered = analyzer.filter_data(df, start_time=start_time)
        
        # 验证过滤结果
        assert len(filtered) == 3
        assert all(filtered['timestamp'] >= start_time)
    
    def test_filter_data_by_end_time(self, analyzer):
        """测试按结束时间过滤"""
        timestamps = pd.date_range('2024-01-01', periods=5, freq='s')
        df = pd.DataFrame({
            'timestamp': timestamps,
            'sensor1': [10.0, 20.0, 30.0, 40.0, 50.0]
        })
        
        # 过滤：到第3个时间点结束
        end_time = timestamps[2]
        filtered = analyzer.filter_data(df, end_time=end_time)
        
        # 验证过滤结果
        assert len(filtered) == 3
        assert all(filtered['timestamp'] <= end_time)
    
    def test_filter_data_by_time_range(self, analyzer):
        """测试按时间范围过滤"""
        timestamps = pd.date_range('2024-01-01', periods=10, freq='s')
        df = pd.DataFrame({
            'timestamp': timestamps,
            'sensor1': list(range(10))
        })
        
        # 过滤：从第3个到第7个时间点
        start_time = timestamps[2]
        end_time = timestamps[6]
        filtered = analyzer.filter_data(df, start_time=start_time, end_time=end_time)
        
        # 验证过滤结果
        assert len(filtered) == 5
        assert all(filtered['timestamp'] >= start_time)
        assert all(filtered['timestamp'] <= end_time)
    
    def test_filter_data_by_sensors(self, analyzer):
        """测试按传感器过滤"""
        df = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=5, freq='s'),
            'sensor1': [10.0, 20.0, 30.0, 40.0, 50.0],
            'sensor2': [5.0, 10.0, 15.0, 20.0, 25.0],
            'sensor3': [1.0, 2.0, 3.0, 4.0, 5.0]
        })
        
        # 只保留 sensor1 和 sensor3
        filtered = analyzer.filter_data(df, sensors=['sensor1', 'sensor3'])
        
        # 验证过滤结果
        assert 'timestamp' in filtered.columns
        assert 'sensor1' in filtered.columns
        assert 'sensor3' in filtered.columns
        assert 'sensor2' not in filtered.columns
        assert len(filtered) == 5
    
    def test_filter_data_combined_filters(self, analyzer):
        """测试组合过滤条件"""
        timestamps = pd.date_range('2024-01-01', periods=10, freq='s')
        df = pd.DataFrame({
            'timestamp': timestamps,
            'sensor1': list(range(10)),
            'sensor2': list(range(10, 20)),
            'sensor3': list(range(20, 30))
        })
        
        # 组合过滤：时间范围 + 传感器选择
        start_time = timestamps[2]
        end_time = timestamps[7]
        filtered = analyzer.filter_data(
            df, 
            start_time=start_time, 
            end_time=end_time,
            sensors=['sensor1', 'sensor3']
        )
        
        # 验证过滤结果
        assert len(filtered) == 6
        assert 'sensor1' in filtered.columns
        assert 'sensor3' in filtered.columns
        assert 'sensor2' not in filtered.columns
        assert all(filtered['timestamp'] >= start_time)
        assert all(filtered['timestamp'] <= end_time)
    
    def test_filter_data_no_filters(self, analyzer):
        """测试不应用任何过滤条件"""
        df = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=5, freq='s'),
            'sensor1': [10.0, 20.0, 30.0, 40.0, 50.0]
        })
        
        filtered = analyzer.filter_data(df)
        
        # 验证返回的是副本，内容相同
        assert len(filtered) == len(df)
        pd.testing.assert_frame_equal(filtered, df)
    
    def test_filter_data_empty_dataframe(self, analyzer):
        """测试过滤空数据框"""
        df = pd.DataFrame({'timestamp': [], 'sensor1': []})
        
        filtered = analyzer.filter_data(df)
        
        # 验证返回空数据框
        assert len(filtered) == 0
    
    def test_filter_data_no_matching_results(self, analyzer):
        """测试过滤条件不匹配任何数据"""
        timestamps = pd.date_range('2024-01-01', periods=5, freq='s')
        df = pd.DataFrame({
            'timestamp': timestamps,
            'sensor1': [10.0, 20.0, 30.0, 40.0, 50.0]
        })
        
        # 使用不匹配的时间范围
        start_time = timestamps[4] + pd.Timedelta(seconds=10)
        filtered = analyzer.filter_data(df, start_time=start_time)
        
        # 验证返回空结果
        assert len(filtered) == 0
    
    def test_filter_data_invalid_sensor(self, analyzer):
        """测试指定不存在的传感器"""
        df = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=5, freq='s'),
            'sensor1': [10.0, 20.0, 30.0, 40.0, 50.0]
        })
        
        with pytest.raises(ValueError, match="Sensors not found in data"):
            analyzer.filter_data(df, sensors=['sensor1', 'nonexistent'])
    
    def test_filter_data_empty_sensor_list(self, analyzer):
        """测试空的传感器列表"""
        df = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=5, freq='s'),
            'sensor1': [10.0, 20.0, 30.0, 40.0, 50.0]
        })
        
        with pytest.raises(ValueError, match="Sensor list cannot be empty"):
            analyzer.filter_data(df, sensors=[])
