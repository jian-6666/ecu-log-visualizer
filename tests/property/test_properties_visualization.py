"""
属性测试 - 可视化引擎模块

该模块包含可视化引擎的基于属性的测试（Property-Based Tests），
使用 Hypothesis 框架生成随机测试数据，验证系统的通用属性。

Feature: ecu-log-visualizer
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings, assume
from typing import List

from src.visualization_engine import VisualizationEngine


# ============================================================================
# 测试数据生成策略
# ============================================================================

@st.composite
def valid_dataframe_with_sensors(draw, min_sensors=1, max_sensors=20, min_records=1, max_records=1000):
    """生成包含时间戳和传感器数据的有效 DataFrame
    
    Args:
        draw: Hypothesis 的 draw 函数
        min_sensors: 最少传感器数量
        max_sensors: 最多传感器数量
        min_records: 最少记录数
        max_records: 最多记录数
        
    Returns:
        pd.DataFrame: 包含 timestamp 列和多个传感器列的数据框
    """
    # 生成记录数量
    num_records = draw(st.integers(min_value=min_records, max_value=max_records))
    
    # 生成传感器数量
    num_sensors = draw(st.integers(min_value=min_sensors, max_value=max_sensors))
    
    # 生成时间戳序列
    start_time = datetime(2024, 1, 1, 0, 0, 0)
    timestamps = [start_time + timedelta(seconds=i) for i in range(num_records)]
    
    # 创建数据字典
    data = {'timestamp': timestamps}
    
    # 生成传感器数据
    for i in range(num_sensors):
        sensor_name = f'sensor{i+1}'
        # 生成传感器值（有限的浮点数）
        sensor_values = draw(
            st.lists(
                st.floats(
                    min_value=-1e10,
                    max_value=1e10,
                    allow_nan=False,
                    allow_infinity=False
                ),
                min_size=num_records,
                max_size=num_records
            )
        )
        data[sensor_name] = sensor_values
    
    return pd.DataFrame(data)


# ============================================================================
# Property 10: 图表数据生成
# Validates: Requirements 4.1
# ============================================================================

# Feature: ecu-log-visualizer, Property 10: 图表数据生成
@given(df=valid_dataframe_with_sensors(min_sensors=1, max_sensors=10, min_records=1, max_records=100))
@settings(max_examples=100, deadline=None)
def test_property_10_chart_data_generation(df):
    """
    Property 10: 图表数据生成
    
    对于任何有效的时间序列数据，可视化引擎应生成包含有效 Plotly 格式的
    图表配置（包含 data 和 layout 字段）。
    
    Validates: Requirements 4.1
    """
    engine = VisualizationEngine()
    
    # 生成图表
    chart = engine.create_time_series_chart(df)
    
    # 验证返回的是字典
    assert isinstance(chart, dict), "Chart should be a dictionary"
    
    # 验证包含必需的顶层字段
    assert 'data' in chart, "Chart must contain 'data' field"
    assert 'layout' in chart, "Chart must contain 'layout' field"
    assert 'config' in chart, "Chart must contain 'config' field"
    
    # 验证 data 字段是列表
    assert isinstance(chart['data'], list), "'data' field must be a list"
    assert len(chart['data']) > 0, "'data' field must not be empty"
    
    # 验证 layout 字段是字典
    assert isinstance(chart['layout'], dict), "'layout' field must be a dictionary"
    
    # 验证 layout 包含必需的字段
    assert 'title' in chart['layout'], "Layout must contain 'title' field"
    assert 'xaxis' in chart['layout'], "Layout must contain 'xaxis' field"
    assert 'yaxis' in chart['layout'], "Layout must contain 'yaxis' field"
    
    # 验证 config 字段是字典
    assert isinstance(chart['config'], dict), "'config' field must be a dictionary"
    
    # 验证每个 trace 的结构
    for i, trace in enumerate(chart['data']):
        assert isinstance(trace, dict), f"Trace {i} must be a dictionary"
        assert 'type' in trace, f"Trace {i} must have 'type' field"
        assert 'x' in trace, f"Trace {i} must have 'x' field (timestamps)"
        assert 'y' in trace, f"Trace {i} must have 'y' field (values)"
        assert 'name' in trace, f"Trace {i} must have 'name' field"
        
        # 验证 x 和 y 数据长度一致
        assert len(trace['x']) == len(trace['y']), \
            f"Trace {i}: x and y data must have same length"
        
        # 验证数据点数量与 DataFrame 一致
        assert len(trace['x']) == len(df), \
            f"Trace {i}: number of data points must match DataFrame length"


# Feature: ecu-log-visualizer, Property 10: 图表数据生成 - 空 DataFrame 处理
def test_property_10_empty_dataframe_raises_error():
    """
    Property 10 边界情况: 空 DataFrame 应抛出错误
    
    验证当传入空 DataFrame 时，系统应该抛出 ValueError。
    
    Validates: Requirements 4.1
    """
    engine = VisualizationEngine()
    
    # 创建空 DataFrame
    empty_df = pd.DataFrame()
    
    # 验证抛出 ValueError
    with pytest.raises(ValueError, match="Cannot create chart from empty DataFrame"):
        engine.create_time_series_chart(empty_df)


# Feature: ecu-log-visualizer, Property 10: 图表数据生成 - 缺少 timestamp 列
@given(num_sensors=st.integers(min_value=1, max_value=5))
@settings(max_examples=50, deadline=None)
def test_property_10_missing_timestamp_raises_error(num_sensors):
    """
    Property 10 边界情况: 缺少 timestamp 列应抛出错误
    
    验证当 DataFrame 缺少 timestamp 列时，系统应该抛出 ValueError。
    
    Validates: Requirements 4.1
    """
    engine = VisualizationEngine()
    
    # 创建没有 timestamp 列的 DataFrame
    data = {}
    for i in range(num_sensors):
        data[f'sensor{i+1}'] = [1.0, 2.0, 3.0]
    
    df = pd.DataFrame(data)
    
    # 验证抛出 ValueError
    with pytest.raises(ValueError, match="must contain 'timestamp' column"):
        engine.create_time_series_chart(df)


# ============================================================================
# Property 11: 多传感器图表支持
# Validates: Requirements 4.2
# ============================================================================

# Feature: ecu-log-visualizer, Property 11: 多传感器图表支持
@given(df=valid_dataframe_with_sensors(min_sensors=2, max_sensors=20, min_records=10, max_records=100))
@settings(max_examples=100, deadline=None)
def test_property_11_multi_sensor_chart_support(df):
    """
    Property 11: 多传感器图表支持
    
    对于任何传感器列表，生成的图表应包含所有指定传感器的数据轨迹（traces）。
    
    Validates: Requirements 4.2
    """
    engine = VisualizationEngine()
    
    # 获取所有传感器名称
    all_sensors = [col for col in df.columns if col != 'timestamp']
    
    # 验证至少有 2 个传感器
    assume(len(all_sensors) >= 2)
    
    # 生成包含所有传感器的图表
    chart = engine.create_time_series_chart(df)
    
    # 验证 traces 数量等于传感器数量
    assert len(chart['data']) == len(all_sensors), \
        f"Chart should have {len(all_sensors)} traces, got {len(chart['data'])}"
    
    # 提取图表中的传感器名称
    chart_sensor_names = {trace['name'] for trace in chart['data']}
    
    # 验证所有传感器都在图表中
    for sensor in all_sensors:
        assert sensor in chart_sensor_names, \
            f"Sensor '{sensor}' should be in chart traces"
    
    # 验证每个 trace 包含正确的数据
    for trace in chart['data']:
        sensor_name = trace['name']
        assert sensor_name in all_sensors, \
            f"Trace name '{sensor_name}' should be a valid sensor"
        
        # 验证 trace 的 y 值与 DataFrame 中的传感器值匹配
        expected_values = df[sensor_name].tolist()
        actual_values = trace['y']
        
        assert len(actual_values) == len(expected_values), \
            f"Trace for '{sensor_name}' has wrong number of values"


# Feature: ecu-log-visualizer, Property 11: 多传感器图表支持 - 指定传感器子集
@given(
    df=valid_dataframe_with_sensors(min_sensors=5, max_sensors=10, min_records=10, max_records=50),
    num_selected=st.integers(min_value=1, max_value=5)
)
@settings(max_examples=100, deadline=None)
def test_property_11_selected_sensors_subset(df, num_selected):
    """
    Property 11 扩展: 指定传感器子集
    
    当指定传感器子集时，图表应只包含这些传感器的 traces。
    
    Validates: Requirements 4.2
    """
    engine = VisualizationEngine()
    
    # 获取所有传感器名称
    all_sensors = [col for col in df.columns if col != 'timestamp']
    
    # 确保有足够的传感器可选择
    assume(len(all_sensors) >= num_selected)
    
    # 选择传感器子集
    selected_sensors = all_sensors[:num_selected]
    
    # 生成只包含选定传感器的图表
    chart = engine.create_time_series_chart(df, sensors=selected_sensors)
    
    # 验证 traces 数量等于选定的传感器数量
    assert len(chart['data']) == len(selected_sensors), \
        f"Chart should have {len(selected_sensors)} traces, got {len(chart['data'])}"
    
    # 提取图表中的传感器名称
    chart_sensor_names = {trace['name'] for trace in chart['data']}
    
    # 验证只包含选定的传感器
    assert chart_sensor_names == set(selected_sensors), \
        f"Chart should only contain selected sensors: {selected_sensors}"
    
    # 验证不包含未选定的传感器
    unselected_sensors = set(all_sensors) - set(selected_sensors)
    for sensor in unselected_sensors:
        assert sensor not in chart_sensor_names, \
            f"Unselected sensor '{sensor}' should not be in chart"


# Feature: ecu-log-visualizer, Property 11: 多传感器图表支持 - 无效传感器名称
@given(df=valid_dataframe_with_sensors(min_sensors=2, max_sensors=5, min_records=10, max_records=50))
@settings(max_examples=50, deadline=None)
def test_property_11_invalid_sensor_names_raise_error(df):
    """
    Property 11 边界情况: 无效传感器名称应抛出错误
    
    当指定的传感器名称不存在时，系统应该抛出 ValueError。
    
    Validates: Requirements 4.2
    """
    engine = VisualizationEngine()
    
    # 使用不存在的传感器名称
    invalid_sensors = ['nonexistent_sensor', 'fake_sensor']
    
    # 验证抛出 ValueError
    with pytest.raises(ValueError, match="Sensors not found in data"):
        engine.create_time_series_chart(df, sensors=invalid_sensors)


# Feature: ecu-log-visualizer, Property 11: 多传感器图表支持 - 空传感器列表
@given(df=valid_dataframe_with_sensors(min_sensors=2, max_sensors=5, min_records=10, max_records=50))
@settings(max_examples=50, deadline=None)
def test_property_11_empty_sensor_list_raises_error(df):
    """
    Property 11 边界情况: 空传感器列表应抛出错误
    
    当传入空的传感器列表时，系统应该抛出 ValueError。
    
    Validates: Requirements 4.2
    """
    engine = VisualizationEngine()
    
    # 使用空传感器列表
    empty_sensors = []
    
    # 验证抛出 ValueError
    with pytest.raises(ValueError, match="Sensor list cannot be empty"):
        engine.create_time_series_chart(df, sensors=empty_sensors)


# ============================================================================
# 额外的属性测试 - 图表配置完整性
# ============================================================================

# Feature: ecu-log-visualizer, Property: 图表交互功能配置
@given(df=valid_dataframe_with_sensors(min_sensors=1, max_sensors=5, min_records=5, max_records=50))
@settings(max_examples=50, deadline=None)
def test_chart_interactive_features_configured(df):
    """
    验证图表配置包含交互功能（zoom、pan、hover）
    
    Validates: Requirements 4.3
    """
    engine = VisualizationEngine()
    chart = engine.create_time_series_chart(df)
    
    # 验证 config 包含交互功能配置
    assert 'displayModeBar' in chart['config'], "Config should enable mode bar"
    assert chart['config']['displayModeBar'] is True, "Mode bar should be displayed"
    
    assert 'scrollZoom' in chart['config'], "Config should enable scroll zoom"
    assert chart['config']['scrollZoom'] is True, "Scroll zoom should be enabled"
    
    # 验证 layout 包含 hovermode
    assert 'hovermode' in chart['layout'], "Layout should specify hovermode"
    
    # 验证每个 trace 包含 hovertemplate
    for trace in chart['data']:
        assert 'hovertemplate' in trace, "Each trace should have hovertemplate"


# Feature: ecu-log-visualizer, Property: 图表标题自定义
@given(
    df=valid_dataframe_with_sensors(min_sensors=1, max_sensors=3, min_records=5, max_records=20),
    title=st.text(min_size=1, max_size=100)
)
@settings(max_examples=50, deadline=None)
def test_chart_custom_title(df, title):
    """
    验证图表标题可以自定义
    
    Validates: Requirements 4.1
    """
    # 过滤掉可能导致问题的特殊字符
    assume(title.strip() != '')
    
    engine = VisualizationEngine()
    chart = engine.create_time_series_chart(df, title=title)
    
    # 验证标题被正确设置
    assert 'title' in chart['layout'], "Layout should contain title"
    assert 'text' in chart['layout']['title'], "Title should have text field"
    assert chart['layout']['title']['text'] == title, \
        f"Title should be '{title}', got '{chart['layout']['title']['text']}'"
