"""
VisualizationEngine 单元测试

测试可视化引擎的图表生成功能。
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from src.visualization_engine import VisualizationEngine


class TestVisualizationEngine:
    """VisualizationEngine 类的单元测试"""
    
    @pytest.fixture
    def engine(self):
        """创建 VisualizationEngine 实例"""
        return VisualizationEngine()
    
    @pytest.fixture
    def sample_data(self):
        """创建示例数据"""
        timestamps = [datetime(2024, 1, 1) + timedelta(seconds=i) for i in range(10)]
        data = {
            'timestamp': timestamps,
            'sensor1': [20.0 + i * 0.5 for i in range(10)],
            'sensor2': [30.0 + i * 0.3 for i in range(10)],
            'sensor3': [40.0 - i * 0.2 for i in range(10)]
        }
        return pd.DataFrame(data)
    
    def test_create_time_series_chart_all_sensors(self, engine, sample_data):
        """测试创建包含所有传感器的时间序列图表"""
        chart = engine.create_time_series_chart(sample_data)
        
        # 验证返回的结构
        assert 'data' in chart
        assert 'layout' in chart
        assert 'config' in chart
        
        # 验证包含所有传感器的 traces
        assert len(chart['data']) == 3
        assert chart['data'][0]['name'] == 'sensor1'
        assert chart['data'][1]['name'] == 'sensor2'
        assert chart['data'][2]['name'] == 'sensor3'
        
        # 验证每个 trace 包含正确的数据点数量
        for trace in chart['data']:
            assert len(trace['x']) == 10
            assert len(trace['y']) == 10
    
    def test_create_time_series_chart_selected_sensors(self, engine, sample_data):
        """测试创建只包含指定传感器的图表"""
        chart = engine.create_time_series_chart(sample_data, sensors=['sensor1', 'sensor3'])
        
        # 验证只包含指定的传感器
        assert len(chart['data']) == 2
        assert chart['data'][0]['name'] == 'sensor1'
        assert chart['data'][1]['name'] == 'sensor3'
    
    def test_create_time_series_chart_single_sensor(self, engine, sample_data):
        """测试创建单传感器图表"""
        chart = engine.create_time_series_chart(sample_data, sensors=['sensor2'])
        
        # 验证只包含一个传感器
        assert len(chart['data']) == 1
        assert chart['data'][0]['name'] == 'sensor2'
    
    def test_create_time_series_chart_custom_title(self, engine, sample_data):
        """测试自定义图表标题"""
        custom_title = "Custom ECU Data"
        chart = engine.create_time_series_chart(sample_data, title=custom_title)
        
        # 验证标题
        assert chart['layout']['title']['text'] == custom_title
    
    def test_create_time_series_chart_empty_dataframe(self, engine):
        """测试空数据框应抛出异常"""
        empty_df = pd.DataFrame()
        
        with pytest.raises(ValueError, match="Cannot create chart from empty DataFrame"):
            engine.create_time_series_chart(empty_df)
    
    def test_create_time_series_chart_missing_timestamp(self, engine):
        """测试缺少 timestamp 列应抛出异常"""
        df = pd.DataFrame({
            'sensor1': [1, 2, 3],
            'sensor2': [4, 5, 6]
        })
        
        with pytest.raises(ValueError, match="must contain 'timestamp' column"):
            engine.create_time_series_chart(df)
    
    def test_create_time_series_chart_no_sensor_columns(self, engine):
        """测试没有传感器列应抛出异常"""
        df = pd.DataFrame({
            'timestamp': [datetime(2024, 1, 1), datetime(2024, 1, 2)]
        })
        
        with pytest.raises(ValueError, match="contains no sensor columns"):
            engine.create_time_series_chart(df)
    
    def test_create_time_series_chart_invalid_sensor(self, engine, sample_data):
        """测试指定不存在的传感器应抛出异常"""
        with pytest.raises(ValueError, match="Sensors not found in data"):
            engine.create_time_series_chart(sample_data, sensors=['nonexistent_sensor'])
    
    def test_create_time_series_chart_empty_sensor_list(self, engine, sample_data):
        """测试空传感器列表应抛出异常"""
        with pytest.raises(ValueError, match="Sensor list cannot be empty"):
            engine.create_time_series_chart(sample_data, sensors=[])
    
    def test_create_trace(self, engine, sample_data):
        """测试创建单个 trace"""
        trace = engine._create_trace(sample_data, 'sensor1')
        
        # 验证 trace 结构
        assert trace['type'] == 'scatter'
        assert trace['mode'] == 'lines+markers'
        assert trace['name'] == 'sensor1'
        assert len(trace['x']) == 10
        assert len(trace['y']) == 10
        
        # 验证数据值
        assert trace['y'][0] == 20.0
        assert trace['y'][9] == 24.5
    
    def test_create_trace_invalid_sensor(self, engine, sample_data):
        """测试创建不存在的传感器 trace 应抛出异常"""
        with pytest.raises(ValueError, match="not found in DataFrame"):
            engine._create_trace(sample_data, 'nonexistent_sensor')
    
    def test_chart_has_interactive_features(self, engine, sample_data):
        """测试图表包含交互功能配置"""
        chart = engine.create_time_series_chart(sample_data)
        
        # 验证布局包含交互功能
        assert chart['layout']['hovermode'] == 'closest'
        assert chart['layout']['showlegend'] is True
        
        # 验证配置包含交互工具
        assert chart['config']['displayModeBar'] is True
        assert chart['config']['scrollZoom'] is True
        assert chart['config']['responsive'] is True
    
    def test_chart_trace_has_hover_template(self, engine, sample_data):
        """测试 trace 包含悬停工具提示配置"""
        chart = engine.create_time_series_chart(sample_data, sensors=['sensor1'])
        
        trace = chart['data'][0]
        assert 'hovertemplate' in trace
        assert 'sensor1' in trace['hovertemplate']
        assert 'Time' in trace['hovertemplate']
        assert 'Value' in trace['hovertemplate']
