"""
统计计算功能的集成测试

测试从文件解析到统计计算的完整工作流程。
"""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
import os
from src.data_analyzer import DataAnalyzer


class TestStatisticsWorkflow:
    """统计计算工作流程的集成测试"""
    
    @pytest.fixture
    def analyzer(self):
        """创建 DataAnalyzer 实例"""
        return DataAnalyzer()
    
    @pytest.fixture
    def sample_csv_file(self):
        """创建示例 CSV 文件"""
        content = """timestamp,temperature,pressure,voltage,status
2024-01-01T00:00:00,23.5,101.3,12.5,OK
2024-01-01T00:00:01,23.6,101.4,12.6,OK
2024-01-01T00:00:02,23.7,101.5,12.7,OK
2024-01-01T00:00:03,23.8,101.6,12.8,OK
2024-01-01T00:00:04,23.9,101.7,12.9,OK
2024-01-01T00:00:05,24.0,101.8,13.0,OK
2024-01-01T00:00:06,24.1,101.9,13.1,OK
2024-01-01T00:00:07,24.2,102.0,13.2,OK
2024-01-01T00:00:08,24.3,102.1,13.3,OK
2024-01-01T00:00:09,24.4,102.2,13.4,OK"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        yield Path(temp_path)
        
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    def test_complete_statistics_workflow(self, analyzer, sample_csv_file):
        """测试完整的统计计算工作流程"""
        # 1. 解析文件
        df = analyzer.parse_file(sample_csv_file)
        
        # 验证解析成功
        assert not df.empty
        assert 'timestamp' in df.columns
        assert 'temperature' in df.columns
        assert 'pressure' in df.columns
        assert 'voltage' in df.columns
        
        # 2. 验证数据
        validated_df, warnings, skipped_count = analyzer.validate_data(df)
        
        # 验证没有警告（数据是干净的）
        assert len(warnings) == 0
        assert len(validated_df) == 10
        
        # 3. 计算所有传感器的统计信息
        stats = analyzer.calculate_statistics(validated_df)
        
        # 验证统计信息
        assert 'temperature' in stats
        assert 'pressure' in stats
        assert 'voltage' in stats
        
        # 验证 temperature 的统计值
        assert stats['temperature']['min'] == 23.5
        assert stats['temperature']['max'] == 24.4
        assert stats['temperature']['count'] == 10
        
        # 验证 pressure 的统计值
        assert stats['pressure']['min'] == 101.3
        assert stats['pressure']['max'] == 102.2
        
        # 验证 voltage 的统计值
        assert stats['voltage']['min'] == 12.5
        assert stats['voltage']['max'] == 13.4
    
    def test_statistics_with_filtering(self, analyzer, sample_csv_file):
        """测试带过滤的统计计算"""
        # 1. 解析和验证
        df = analyzer.parse_file(sample_csv_file)
        validated_df, _, _ = analyzer.validate_data(df)
        
        # 2. 按时间范围过滤
        start_time = pd.Timestamp('2024-01-01T00:00:03')
        end_time = pd.Timestamp('2024-01-01T00:00:07')
        filtered_df = analyzer.filter_data(
            validated_df,
            start_time=start_time,
            end_time=end_time
        )
        
        # 验证过滤结果
        assert len(filtered_df) == 5
        
        # 3. 计算过滤后数据的统计信息
        stats = analyzer.calculate_statistics(filtered_df)
        
        # 验证统计信息反映了过滤后的数据
        assert stats['temperature']['min'] == 23.8
        assert stats['temperature']['max'] == 24.2
        assert stats['temperature']['count'] == 5
    
    def test_statistics_with_sensor_selection(self, analyzer, sample_csv_file):
        """测试选择特定传感器的统计计算"""
        # 1. 解析和验证
        df = analyzer.parse_file(sample_csv_file)
        validated_df, _, _ = analyzer.validate_data(df)
        
        # 2. 按传感器过滤
        filtered_df = analyzer.filter_data(
            validated_df,
            sensors=['temperature', 'voltage']
        )
        
        # 验证只保留了指定的传感器
        assert 'temperature' in filtered_df.columns
        assert 'voltage' in filtered_df.columns
        assert 'pressure' not in filtered_df.columns
        
        # 3. 计算指定传感器的统计信息
        stats = analyzer.calculate_statistics(filtered_df, sensors=['temperature'])
        
        # 验证只返回了指定传感器的统计信息
        assert 'temperature' in stats
        assert 'voltage' not in stats
        assert 'pressure' not in stats
    
    def test_statistics_with_combined_filters(self, analyzer, sample_csv_file):
        """测试组合过滤条件的统计计算"""
        # 1. 解析和验证
        df = analyzer.parse_file(sample_csv_file)
        validated_df, _, _ = analyzer.validate_data(df)
        
        # 2. 应用组合过滤：时间范围 + 传感器选择
        start_time = pd.Timestamp('2024-01-01T00:00:02')
        end_time = pd.Timestamp('2024-01-01T00:00:06')
        filtered_df = analyzer.filter_data(
            validated_df,
            start_time=start_time,
            end_time=end_time,
            sensors=['temperature', 'pressure']
        )
        
        # 验证过滤结果
        assert len(filtered_df) == 5
        assert 'temperature' in filtered_df.columns
        assert 'pressure' in filtered_df.columns
        assert 'voltage' not in filtered_df.columns
        
        # 3. 计算统计信息
        stats = analyzer.calculate_statistics(filtered_df)
        
        # 验证统计信息
        assert 'temperature' in stats
        assert 'pressure' in stats
        assert stats['temperature']['count'] == 5
        assert stats['temperature']['min'] == 23.7
        assert stats['temperature']['max'] == 24.1
    
    def test_statistics_mean_calculation(self, analyzer):
        """测试平均值计算的准确性"""
        # 创建已知平均值的数据
        df = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=5, freq='s'),
            'sensor1': [10.0, 20.0, 30.0, 40.0, 50.0]  # 平均值应该是 30.0
        })
        
        stats = analyzer.calculate_statistics(df)
        
        # 验证平均值计算正确
        assert stats['sensor1']['mean'] == 30.0
    
    def test_statistics_std_calculation(self, analyzer):
        """测试标准差计算"""
        # 创建数据
        df = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=5, freq='s'),
            'sensor1': [2.0, 4.0, 4.0, 4.0, 6.0]
        })
        
        stats = analyzer.calculate_statistics(df)
        
        # 验证标准差存在且为正数
        assert 'std' in stats['sensor1']
        assert stats['sensor1']['std'] > 0
        
        # 对于常量数据，标准差应该是 0
        df_constant = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=5, freq='s'),
            'sensor1': [5.0, 5.0, 5.0, 5.0, 5.0]
        })
        
        stats_constant = analyzer.calculate_statistics(df_constant)
        assert stats_constant['sensor1']['std'] == 0.0
