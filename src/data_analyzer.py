"""
数据分析模块

该模块负责解析日志文件、验证数据、计算统计信息和过滤数据。
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, List, Optional, Dict
from datetime import datetime
import logging

# 配置日志
logger = logging.getLogger(__name__)


class DataAnalyzer:
    """数据分析器类
    
    负责解析日志文件（CSV/JSON）、验证数据完整性、计算统计信息和过滤数据。
    """
    
    # 数值范围限制
    MIN_VALUE = -1e10
    MAX_VALUE = 1e10
    
    def __init__(self):
        """初始化数据分析器"""
        pass
    
    def parse_csv(self, file_path: Path) -> pd.DataFrame:
        """解析 CSV 格式日志文件
        
        CSV 格式示例:
        timestamp,sensor1,sensor2,sensor3,status
        2024-01-01T00:00:00,23.5,45.2,67.8,OK
        2024-01-01T00:00:01,23.6,45.3,67.9,OK
        
        Args:
            file_path: CSV 文件路径
            
        Returns:
            pd.DataFrame: 解析后的数据框，包含 timestamp 列和传感器列
            
        Raises:
            ValueError: 如果文件格式无效或解析失败
            FileNotFoundError: 如果文件不存在
            
        Validates: Requirements 2.1, 2.2, 2.3, 2.6
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            # 读取 CSV 文件
            df = pd.read_csv(file_path)
            
            # 验证必需的 timestamp 列
            if 'timestamp' not in df.columns:
                raise ValueError("CSV file must contain 'timestamp' column")
            
            # 解析时间戳列
            try:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            except Exception as e:
                raise ValueError(f"Invalid timestamp format: {str(e)}")
            
            # 识别传感器列（数值列或可转换为数值的列，排除 timestamp 和非数值列如 status）
            sensor_columns = []
            for col in df.columns:
                if col != 'timestamp':
                    # 尝试转换为数值类型（允许部分失败）
                    numeric_series = pd.to_numeric(df[col], errors='coerce')
                    # 如果至少有一些有效的数值，认为这是传感器列
                    if numeric_series.notna().any():
                        sensor_columns.append(col)
                    else:
                        # 完全非数值列（如 status），跳过
                        logger.debug(f"Column '{col}' contains no numeric values, skipping")
            
            if not sensor_columns:
                raise ValueError("CSV file must contain at least one numeric sensor column")
            
            # 只保留 timestamp 和传感器列（保留原始值，稍后在 validate_data 中处理）
            columns_to_keep = ['timestamp'] + sensor_columns
            df = df[columns_to_keep].copy()
            
            return df
            
        except pd.errors.EmptyDataError:
            raise ValueError("CSV file is empty")
        except pd.errors.ParserError as e:
            raise ValueError(f"Failed to parse CSV file: {str(e)}")
        except Exception as e:
            if isinstance(e, (ValueError, FileNotFoundError)):
                raise
            raise ValueError(f"Unexpected error parsing CSV: {str(e)}")
    
    def validate_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str], int]:
        """验证和清洗数据
        
        验证规则：
        1. 时间戳必须是有效的 ISO 8601 格式（已在 parse_csv 中处理）
        2. 如果时间戳乱序，自动排序并记录警告
        3. 传感器值必须是数值类型
        4. 非数值条目跳过并记录警告（包含行号）
        5. 传感器值必须在有效范围内（-1e10 到 1e10）
        
        Args:
            df: 待验证的数据框
            
        Returns:
            Tuple[pd.DataFrame, List[str], int]: 
                - 清洗后的数据框
                - 警告信息列表（包含行号）
                - 跳过的条目数量
                
        Validates: Requirements 2.5, 9.1, 9.2, 9.3, 9.4, 9.5
        """
        warnings = []
        original_count = len(df)
        
        # 创建数据副本以避免修改原始数据
        df = df.copy()
        
        # 保存原始行号（用于警告消息，行号从1开始，加上CSV头行）
        df['_original_line'] = range(2, len(df) + 2)  # CSV文件行号从2开始（1是头行）
        
        # 1. 检查时间戳是否按顺序排列
        if not df['timestamp'].is_monotonic_increasing:
            warnings.append("Timestamps are not in chronological order, data has been sorted")
            df = df.sort_values('timestamp').reset_index(drop=True)
            logger.warning("Data was sorted by timestamp")
        
        # 2. 获取传感器列（除了 timestamp 和 _original_line 的所有列）
        sensor_columns = [col for col in df.columns if col not in ['timestamp', '_original_line']]
        
        # 3. 验证和清洗传感器数据
        rows_to_drop = set()
        rows_with_issues = {}  # 记录每行的问题
        
        for col in sensor_columns:
            # 保存原始值用于错误报告
            original_values = df[col].copy()
            
            # 转换为数值类型，非数值设为 NaN
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 找出非数值的行（包括原本就是NaN的和转换后变成NaN的）
            nan_mask = df[col].isna()
            if nan_mask.any():
                nan_indices = df[nan_mask].index.tolist()
                for idx in nan_indices:
                    line_num = df.loc[idx, '_original_line']
                    original_val = original_values.loc[idx]
                    # 只报告那些原本不是NaN但转换后变成NaN的
                    if pd.notna(original_val):
                        if idx not in rows_with_issues:
                            rows_with_issues[idx] = []
                        rows_with_issues[idx].append(
                            f"line {int(line_num)}, column '{col}': non-numeric value '{original_val}'"
                        )
                rows_to_drop.update(nan_indices)
            
            # 检查数值范围
            valid_mask = (df[col] >= self.MIN_VALUE) & (df[col] <= self.MAX_VALUE)
            invalid_mask = ~valid_mask & ~df[col].isna()
            if invalid_mask.any():
                invalid_indices = df[invalid_mask].index.tolist()
                for idx in invalid_indices:
                    line_num = df.loc[idx, '_original_line']
                    invalid_val = df.loc[idx, col]
                    if idx not in rows_with_issues:
                        rows_with_issues[idx] = []
                    rows_with_issues[idx].append(
                        f"line {int(line_num)}, column '{col}': value {invalid_val} outside valid range "
                        f"({self.MIN_VALUE} to {self.MAX_VALUE})"
                    )
                rows_to_drop.update(invalid_indices)
        
        # 4. 生成详细的警告消息
        if rows_with_issues:
            # 限制警告消息数量，避免过多输出
            max_warnings = 10
            issue_count = 0
            for idx in sorted(rows_with_issues.keys()):
                if issue_count >= max_warnings:
                    remaining = len(rows_with_issues) - max_warnings
                    warnings.append(f"... and {remaining} more entries with issues (not shown)")
                    break
                for issue in rows_with_issues[idx]:
                    warnings.append(issue)
                    issue_count += 1
                    if issue_count >= max_warnings:
                        break
        
        # 5. 删除包含无效数据的行
        skipped_count = 0
        if rows_to_drop:
            df = df.drop(index=list(rows_to_drop)).reset_index(drop=True)
            skipped_count = len(rows_to_drop)
            warnings.append(
                f"Total entries skipped: {skipped_count} out of {original_count}"
            )
            logger.warning(f"Skipped {skipped_count} entries due to invalid data")
        
        # 6. 删除临时的行号列
        df = df.drop(columns=['_original_line'])
        
        # 7. 验证清洗后还有数据
        if len(df) == 0:
            raise ValueError("No valid data remaining after validation")
        
        return df, warnings, skipped_count
    
    def parse_json(self, file_path: Path) -> pd.DataFrame:
        """解析 JSON 格式日志文件
        
        JSON 格式示例:
        [
            {
                "timestamp": "2024-01-01T00:00:00",
                "sensors": {
                    "sensor1": 23.5,
                    "sensor2": 45.2,
                    "sensor3": 67.8
                },
                "status": "OK"
            }
        ]
        
        Args:
            file_path: JSON 文件路径
            
        Returns:
            pd.DataFrame: 解析后的数据框，包含 timestamp 列和传感器列
            
        Raises:
            ValueError: 如果文件格式无效或解析失败
            FileNotFoundError: 如果文件不存在
            
        Validates: Requirements 2.1, 2.2, 2.3, 2.7
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            # 读取 JSON 文件
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 验证数据是列表
            if not isinstance(data, list):
                raise ValueError("JSON file must contain an array of log entries")
            
            if len(data) == 0:
                raise ValueError("JSON file is empty")
            
            # 解析 JSON 数据为扁平化的字典列表
            records = []
            for i, entry in enumerate(data):
                if not isinstance(entry, dict):
                    raise ValueError(f"Entry {i} is not a valid object")
                
                # 提取 timestamp
                if 'timestamp' not in entry:
                    raise ValueError(f"Entry {i} is missing 'timestamp' field")
                
                record = {'timestamp': entry['timestamp']}
                
                # 提取传感器数据
                if 'sensors' in entry and isinstance(entry['sensors'], dict):
                    # 嵌套格式：sensors 字段包含传感器数据
                    for sensor_name, sensor_value in entry['sensors'].items():
                        record[sensor_name] = sensor_value
                else:
                    # 扁平格式：传感器数据直接在顶层
                    for key, value in entry.items():
                        if key not in ['timestamp', 'status']:
                            # 尝试将值转换为数值
                            try:
                                float(value)
                                record[key] = value
                            except (ValueError, TypeError):
                                # 非数值字段，跳过
                                pass
                
                records.append(record)
            
            # 转换为 DataFrame
            df = pd.DataFrame(records)
            
            # 验证必需的 timestamp 列
            if 'timestamp' not in df.columns:
                raise ValueError("JSON data must contain 'timestamp' field")
            
            # 解析时间戳列
            try:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            except Exception as e:
                raise ValueError(f"Invalid timestamp format: {str(e)}")
            
            # 识别传感器列（数值列，排除 timestamp）
            sensor_columns = []
            for col in df.columns:
                if col != 'timestamp':
                    # 转换为数值类型
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    sensor_columns.append(col)
            
            if not sensor_columns:
                raise ValueError("JSON data must contain at least one numeric sensor field")
            
            # 只保留 timestamp 和传感器列
            columns_to_keep = ['timestamp'] + sensor_columns
            df = df[columns_to_keep].copy()
            
            return df
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            if isinstance(e, (ValueError, FileNotFoundError)):
                raise
            raise ValueError(f"Unexpected error parsing JSON: {str(e)}")
    
    def parse_file(self, file_path: Path) -> pd.DataFrame:
        """解析日志文件（根据文件扩展名自动选择解析器）
        
        支持的格式：
        - .csv: CSV 格式
        - .json: JSON 格式
        
        Args:
            file_path: 日志文件路径
            
        Returns:
            pd.DataFrame: 解析后的数据框
            
        Raises:
            ValueError: 如果文件格式不支持或解析失败
            FileNotFoundError: 如果文件不存在
            
        Validates: Requirements 2.6, 2.7
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # 获取文件扩展名
        file_extension = file_path.suffix.lower()
        
        # 根据扩展名选择解析器
        if file_extension == '.csv':
            return self.parse_csv(file_path)
        elif file_extension == '.json':
            return self.parse_json(file_path)
        else:
            raise ValueError(
                f"Unsupported file format: {file_extension}. "
                f"Supported formats: .csv, .json"
            )
    
    def get_sensor_names(self, df: pd.DataFrame) -> List[str]:
        """获取所有传感器名称
        
        Args:
            df: 数据框
            
        Returns:
            List[str]: 传感器名称列表（不包括 timestamp）
            
        Validates: Requirements 2.3
        """
        return [col for col in df.columns if col != 'timestamp']
    
    def calculate_statistics(
        self, 
        df: pd.DataFrame, 
        sensors: Optional[List[str]] = None
    ) -> Dict:
        """计算统计信息
        
        计算每个传感器的最小值、最大值、平均值和标准差。
        
        Args:
            df: 数据框（必须包含 timestamp 列和传感器列）
            sensors: 可选的传感器名称列表，如果提供则只计算这些传感器的统计信息
            
        Returns:
            Dict: 统计信息字典，格式为：
                {
                    'sensor_name': {
                        'min': float,
                        'max': float,
                        'mean': float,
                        'std': float,
                        'count': int
                    }
                }
                
        Raises:
            ValueError: 如果数据框为空或指定的传感器不存在
            
        Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5
        """
        if df.empty:
            raise ValueError("Cannot calculate statistics on empty DataFrame")
        
        # 获取所有可用的传感器名称
        available_sensors = self.get_sensor_names(df)
        
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
            sensors_to_calculate = sensors
        else:
            # 使用所有可用的传感器
            sensors_to_calculate = available_sensors
        
        # 计算每个传感器的统计信息
        statistics = {}
        
        for sensor in sensors_to_calculate:
            sensor_data = df[sensor]
            
            # 计算统计值
            statistics[sensor] = {
                'min': float(sensor_data.min()),
                'max': float(sensor_data.max()),
                'mean': float(sensor_data.mean()),
                'std': float(sensor_data.std()),
                'count': int(len(sensor_data))
            }
        
        return statistics
    
    def filter_data(
        self,
        df: pd.DataFrame,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        sensors: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """根据条件过滤数据
        
        支持按时间范围和传感器类型过滤数据。多个过滤条件同时应用。
        
        Args:
            df: 数据框
            start_time: 可选的开始时间（包含）
            end_time: 可选的结束时间（包含）
            sensors: 可选的传感器名称列表
            
        Returns:
            pd.DataFrame: 过滤后的数据框
            
        Raises:
            ValueError: 如果指定的传感器不存在
            
        Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5
        """
        if df.empty:
            return df.copy()
        
        # 创建数据副本以避免修改原始数据
        filtered_df = df.copy()
        
        # 1. 按开始时间过滤
        if start_time is not None:
            filtered_df = filtered_df[filtered_df['timestamp'] >= start_time]
        
        # 2. 按结束时间过滤
        if end_time is not None:
            filtered_df = filtered_df[filtered_df['timestamp'] <= end_time]
        
        # 3. 按传感器过滤
        if sensors is not None:
            if not sensors:
                raise ValueError("Sensor list cannot be empty")
            
            # 验证传感器是否存在
            available_sensors = self.get_sensor_names(df)
            invalid_sensors = [s for s in sensors if s not in available_sensors]
            if invalid_sensors:
                raise ValueError(
                    f"Sensors not found in data: {', '.join(invalid_sensors)}. "
                    f"Available sensors: {', '.join(available_sensors)}"
                )
            
            # 只保留 timestamp 和指定的传感器列
            columns_to_keep = ['timestamp'] + sensors
            filtered_df = filtered_df[columns_to_keep]
        
        return filtered_df


