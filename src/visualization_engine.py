"""
可视化引擎模块

该模块负责生成 Plotly 图表配置，用于交互式数据可视化。
"""

import pandas as pd
from typing import Dict, List, Optional
import logging

# 配置日志
logger = logging.getLogger(__name__)


class VisualizationEngine:
    """可视化引擎类
    
    负责生成 Plotly 图表配置，支持时间序列折线图和多传感器叠加显示。
    """
    
    def __init__(self):
        """初始化可视化引擎"""
        pass
    
    def create_time_series_chart(
        self,
        df: pd.DataFrame,
        sensors: Optional[List[str]] = None,
        title: str = "ECU Sensor Data"
    ) -> Dict:
        """创建时间序列折线图
        
        生成 Plotly 格式的图表配置，包含数据轨迹（traces）、布局（layout）
        和配置选项（config）。支持多传感器在同一图表上叠加显示。
        
        Args:
            df: 数据框（必须包含 timestamp 列和传感器列）
            sensors: 可选的传感器名称列表，如果提供则只显示这些传感器
            title: 图表标题
            
        Returns:
            Dict: Plotly 图表配置，格式为：
                {
                    'data': [...],    # Plotly traces 列表
                    'layout': {...},  # Plotly layout 配置
                    'config': {...}   # Plotly config 选项
                }
                
        Raises:
            ValueError: 如果数据框为空或指定的传感器不存在
            
        Validates: Requirements 4.1, 4.2, 4.3, 4.4
        """
        if df.empty:
            raise ValueError("Cannot create chart from empty DataFrame")
        
        # 验证 timestamp 列存在
        if 'timestamp' not in df.columns:
            raise ValueError("DataFrame must contain 'timestamp' column")
        
        # 获取所有可用的传感器名称
        available_sensors = [col for col in df.columns if col != 'timestamp']
        
        if not available_sensors:
            raise ValueError("DataFrame contains no sensor columns")
        
        # 如果指定了传感器列表，验证它们是否存在
        if sensors is not None:
            if not sensors:
                raise ValueError("Sensor list cannot be empty")
            
            # 检查所有指定的传感器是否存在
            invalid_sensors = [s for s in sensors if s not in available_sensors]
            if invalid_sensors:
                raise ValueError(
                    f"Sensors not found in data: {', '.join(invalid_sensors)}. "
                    f"Available sensors: {', '.join(available_sensors)}"
                )
            
            # 使用指定的传感器列表
            sensors_to_plot = sensors
        else:
            # 使用所有可用的传感器
            sensors_to_plot = available_sensors
        
        # 创建数据轨迹（traces）
        traces = []
        for sensor in sensors_to_plot:
            trace = self._create_trace(df, sensor)
            traces.append(trace)
        
        # 创建布局配置
        layout = {
            'title': {
                'text': title,
                'x': 0.5,
                'xanchor': 'center'
            },
            'xaxis': {
                'title': 'Time',
                'type': 'date',
                'showgrid': True,
                'gridcolor': '#E5E5E5'
            },
            'yaxis': {
                'title': 'Sensor Value',
                'showgrid': True,
                'gridcolor': '#E5E5E5'
            },
            'hovermode': 'closest',
            'showlegend': True,
            'legend': {
                'x': 1.02,
                'y': 1,
                'xanchor': 'left',
                'yanchor': 'top'
            },
            'margin': {
                'l': 60,
                'r': 150,
                't': 80,
                'b': 60
            },
            'plot_bgcolor': '#FFFFFF',
            'paper_bgcolor': '#FFFFFF'
        }
        
        # 创建配置选项（启用交互功能）
        config = {
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToAdd': ['pan2d', 'zoom2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d'],
            'modeBarButtonsToRemove': [],
            'scrollZoom': True,
            'responsive': True
        }
        
        return {
            'data': traces,
            'layout': layout,
            'config': config
        }
    
    def _create_trace(
        self,
        df: pd.DataFrame,
        sensor: str
    ) -> Dict:
        """为单个传感器创建 Plotly trace
        
        创建折线图轨迹，包含时间戳和传感器值，以及悬停工具提示配置。
        
        Args:
            df: 数据框（必须包含 timestamp 列和指定的传感器列）
            sensor: 传感器名称
            
        Returns:
            Dict: Plotly trace 配置
            
        Raises:
            ValueError: 如果传感器列不存在
            
        Validates: Requirements 4.1, 4.2
        """
        if sensor not in df.columns:
            raise ValueError(f"Sensor '{sensor}' not found in DataFrame")
        
        # 提取时间戳和传感器值
        timestamps = df['timestamp'].tolist()
        values = df[sensor].tolist()
        
        # 创建 trace
        trace = {
            'type': 'scatter',
            'mode': 'lines+markers',
            'name': sensor,
            'x': timestamps,
            'y': values,
            'line': {
                'width': 2
            },
            'marker': {
                'size': 4
            },
            'hovertemplate': (
                f'<b>{sensor}</b><br>'
                'Time: %{x}<br>'
                'Value: %{y:.2f}<br>'
                '<extra></extra>'
            )
        }
        
        return trace
