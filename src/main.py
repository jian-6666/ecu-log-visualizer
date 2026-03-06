"""
ECU Log Visualizer - FastAPI Application

This module creates the FastAPI application instance and configures:
- CORS middleware for frontend access
- Static file serving for frontend
- File upload size limits
- Basic health check endpoint
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional
import pandas as pd
import io
import json

from src.models import (
    FileMetadata, ErrorResponse, StatisticsResponse, SensorStatistics, 
    ChartResponse, FileListResponse, DashboardData, CommitInfo, RepositoryStats,
    WorkflowStatus, BuildStatus, ContainerStatus
)
from src.file_handler import FileHandler
from src.data_analyzer import DataAnalyzer
from src.visualization_engine import VisualizationEngine
from src.error_handler import setup_exception_handlers
from src.git_integration import GitRepository
from src.cicd_status import GitHubActionsMonitor, JenkinsMonitor
from src.docker_status import DockerMonitor

# Create FastAPI application instance
app = FastAPI(
    title="ECU Log Visualizer API",
    description="API for analyzing and visualizing ECU log data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup global exception handlers
setup_exception_handlers(app)

# Ensure frontend directory exists
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists() and any(frontend_path.iterdir()):
    # Mount static files for frontend (only if frontend has files)
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

# Configure file upload size limit (50MB)
# This is handled by the server configuration (uvicorn/gunicorn)
# For uvicorn, use: --limit-max-requests 52428800
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB in bytes

# Initialize FileHandler
file_handler = FileHandler(storage_path="uploads")

# Initialize DataAnalyzer
data_analyzer = DataAnalyzer()

# Initialize VisualizationEngine
visualization_engine = VisualizationEngine()


@app.get("/")
async def root():
    """Root endpoint - serves the frontend HTML page"""
    frontend_path = Path(__file__).parent.parent / "frontend" / "index.html"
    if frontend_path.exists():
        return FileResponse(frontend_path)
    else:
        # Fallback to API information if frontend not found
        return {
            "message": "ECU Log Visualizer API",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health",
            "note": "Frontend files not found. Please ensure frontend/index.html exists."
        }


@app.get("/styles.css")
async def get_styles():
    """Serve CSS file"""
    css_path = Path(__file__).parent.parent / "frontend" / "styles.css"
    if css_path.exists():
        return FileResponse(css_path, media_type="text/css")
    raise HTTPException(status_code=404, detail="CSS file not found")


@app.get("/app.js")
async def get_app_js():
    """Serve JavaScript file"""
    js_path = Path(__file__).parent.parent / "frontend" / "app.js"
    if js_path.exists():
        return FileResponse(js_path, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="JavaScript file not found")


@app.get("/engineering-dashboard.html")
async def get_engineering_dashboard():
    """Serve Engineering Dashboard HTML"""
    dashboard_path = Path(__file__).parent.parent / "frontend" / "engineering-dashboard.html"
    if dashboard_path.exists():
        return FileResponse(dashboard_path, media_type="text/html")
    raise HTTPException(status_code=404, detail="Engineering Dashboard not found")


@app.get("/engineering-dashboard.css")
async def get_engineering_dashboard_css():
    """Serve Engineering Dashboard CSS"""
    css_path = Path(__file__).parent.parent / "frontend" / "engineering-dashboard.css"
    if css_path.exists():
        return FileResponse(css_path, media_type="text/css")
    raise HTTPException(status_code=404, detail="Engineering Dashboard CSS not found")


@app.get("/engineering-dashboard.js")
async def get_engineering_dashboard_js():
    """Serve Engineering Dashboard JavaScript"""
    js_path = Path(__file__).parent.parent / "frontend" / "engineering-dashboard.js"
    if js_path.exists():
        return FileResponse(js_path, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="Engineering Dashboard JS not found")



@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ECU Log Visualizer",
        "max_upload_size_mb": MAX_UPLOAD_SIZE / (1024 * 1024)
    }


@app.post("/api/upload", response_model=FileMetadata)
async def upload_file(file: UploadFile = File(...)):
    """
    上传 ECU 日志文件
    
    接受 CSV 或 JSON 格式的日志文件，验证格式和大小，
    保存文件并返回文件元数据。
    
    Args:
        file: 上传的文件（multipart/form-data）
        
    Returns:
        FileMetadata: 包含 file_id、filename、size、upload_time 等信息
        
    Raises:
        HTTPException 400: 文件格式无效或参数错误
        HTTPException 413: 文件大小超过限制
        HTTPException 500: 内部服务器错误
        
    Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 8.1, 8.2, 8.3, 8.5
    """
    try:
        # 验证文件格式
        if not file_handler.validate_file(file):
            # 检查具体的验证失败原因
            if not file.filename:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error_code": "INVALID_FILE",
                        "message": "No filename provided",
                        "details": {
                            "parameter": "file",
                            "expected": "File with valid filename"
                        },
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )
            
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in file_handler.ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error_code": "INVALID_FORMAT",
                        "message": f"Invalid file format. Only CSV and JSON files are supported.",
                        "details": {
                            "provided_format": file_ext,
                            "allowed_formats": list(file_handler.ALLOWED_EXTENSIONS),
                            "filename": file.filename
                        },
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )
        
        # 保存文件
        try:
            file_id = file_handler.save_file(file)
        except ValueError as e:
            # 文件大小超过限制
            error_msg = str(e)
            if "exceeds maximum limit" in error_msg:
                raise HTTPException(
                    status_code=413,
                    detail={
                        "error_code": "FILE_TOO_LARGE",
                        "message": f"File size exceeds maximum limit of {MAX_UPLOAD_SIZE / (1024 * 1024)}MB",
                        "details": {
                            "max_size_mb": MAX_UPLOAD_SIZE / (1024 * 1024),
                            "filename": file.filename
                        },
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error_code": "INVALID_FILE",
                        "message": error_msg,
                        "details": {
                            "filename": file.filename
                        },
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )
        
        # 获取文件信息
        file_path = file_handler.get_file_path(file_id)
        file_size = file_path.stat().st_size
        file_format = file_path.suffix.lower().lstrip('.')
        
        # 构建响应
        metadata = FileMetadata(
            file_id=file_id,
            filename=file_path.name,
            original_filename=file.filename,
            file_size=file_size,
            upload_time=datetime.now(timezone.utc),
            file_format=file_format,
            status="uploaded"
        )
        
        return metadata
        
    except HTTPException:
        # 重新抛出 HTTP 异常
        raise
    except Exception as e:
        # 内部服务器错误
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "INTERNAL_ERROR",
                "message": "An internal error occurred while processing your request",
                "details": {
                    "request_id": f"req-{datetime.now(timezone.utc).timestamp()}"
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )


@app.get("/api/stats/{file_id}", response_model=StatisticsResponse)
async def get_statistics(
    file_id: str,
    start_time: Optional[str] = Query(None, description="开始时间 (ISO 8601 格式)"),
    end_time: Optional[str] = Query(None, description="结束时间 (ISO 8601 格式)"),
    sensors: Optional[str] = Query(None, description="传感器名称列表（逗号分隔）")
):
    """
    获取文件的统计信息
    
    解析指定的日志文件并计算统计信息（最小值、最大值、平均值、标准差）。
    支持可选的过滤参数来限制分析的时间范围和传感器。
    
    Args:
        file_id: 文件唯一标识符
        start_time: 可选的开始时间（ISO 8601 格式）
        end_time: 可选的结束时间（ISO 8601 格式）
        sensors: 可选的传感器名称列表（逗号分隔，例如 "sensor1,sensor2"）
        
    Returns:
        StatisticsResponse: 包含传感器统计信息、时间范围、记录数等
        
    Raises:
        HTTPException 404: 文件不存在
        HTTPException 400: 参数无效或文件解析失败
        HTTPException 500: 内部服务器错误
        
    Validates: Requirements 3.5, 3.6, 5.1, 5.2, 5.3, 8.1, 8.4
    """
    try:
        # 1. 验证文件是否存在
        try:
            file_path = file_handler.get_file_path(file_id)
            if not file_path.exists():
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error_code": "FILE_NOT_FOUND",
                        "message": f"File with ID '{file_id}' does not exist",
                        "details": {
                            "file_id": file_id
                        },
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )
        except FileNotFoundError:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "FILE_NOT_FOUND",
                    "message": f"File with ID '{file_id}' does not exist",
                    "details": {
                        "file_id": file_id
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        # 2. 解析文件
        try:
            df = data_analyzer.parse_file(file_path)
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail={
                    "error_code": "PARSE_ERROR",
                    "message": f"Failed to parse file: {str(e)}",
                    "details": {
                        "file_id": file_id
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        # 3. 验证和清洗数据
        try:
            df, warnings, skipped_count = data_analyzer.validate_data(df)
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail={
                    "error_code": "VALIDATION_ERROR",
                    "message": f"Data validation failed: {str(e)}",
                    "details": {
                        "file_id": file_id
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        # 记录原始记录数
        total_records = len(df)
        
        # 4. 解析过滤参数
        filter_start_time = None
        filter_end_time = None
        filter_sensors = None
        
        # 解析开始时间
        if start_time:
            try:
                filter_start_time = pd.to_datetime(start_time)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error_code": "INVALID_PARAMETER",
                        "message": "Invalid time format for start_time parameter",
                        "details": {
                            "parameter": "start_time",
                            "provided_value": start_time,
                            "expected_format": "ISO 8601 (YYYY-MM-DDTHH:MM:SS)"
                        },
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )
        
        # 解析结束时间
        if end_time:
            try:
                filter_end_time = pd.to_datetime(end_time)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error_code": "INVALID_PARAMETER",
                        "message": "Invalid time format for end_time parameter",
                        "details": {
                            "parameter": "end_time",
                            "provided_value": end_time,
                            "expected_format": "ISO 8601 (YYYY-MM-DDTHH:MM:SS)"
                        },
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )
        
        # 解析传感器列表
        if sensors:
            filter_sensors = [s.strip() for s in sensors.split(',') if s.strip()]
            if not filter_sensors:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error_code": "INVALID_PARAMETER",
                        "message": "Sensor list cannot be empty",
                        "details": {
                            "parameter": "sensors",
                            "provided_value": sensors
                        },
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )
        
        # 5. 应用过滤
        try:
            filtered_df = data_analyzer.filter_data(
                df,
                start_time=filter_start_time,
                end_time=filter_end_time,
                sensors=filter_sensors
            )
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail={
                    "error_code": "FILTER_ERROR",
                    "message": f"Failed to apply filters: {str(e)}",
                    "details": {
                        "file_id": file_id
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        filtered_records = len(filtered_df)
        
        # 6. 计算统计信息
        try:
            stats = data_analyzer.calculate_statistics(
                filtered_df,
                sensors=filter_sensors
            )
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail={
                    "error_code": "CALCULATION_ERROR",
                    "message": f"Failed to calculate statistics: {str(e)}",
                    "details": {
                        "file_id": file_id
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        # 7. 构建响应
        # 转换统计信息为 SensorStatistics 模型
        sensor_stats = {
            sensor_name: SensorStatistics(**sensor_data)
            for sensor_name, sensor_data in stats.items()
        }
        
        # 获取时间范围
        time_range = {
            "start": filtered_df['timestamp'].min().isoformat(),
            "end": filtered_df['timestamp'].max().isoformat()
        }
        
        response = StatisticsResponse(
            file_id=file_id,
            sensors=sensor_stats,
            time_range=time_range,
            total_records=total_records,
            filtered_records=filtered_records,
            warnings=warnings if warnings else None,
            skipped_entries=skipped_count if skipped_count > 0 else None
        )
        
        return response
        
    except HTTPException:
        # 重新抛出 HTTP 异常
        raise
    except Exception as e:
        # 内部服务器错误
        import traceback
        traceback.print_exc()  # 打印堆栈跟踪用于调试
        
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "INTERNAL_ERROR",
                "message": "An internal error occurred while processing your request",
                "details": {
                    "request_id": f"req-{datetime.now(timezone.utc).timestamp()}"
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )


@app.get("/api/chart/{file_id}", response_model=ChartResponse)
async def get_chart(
    file_id: str,
    start_time: Optional[str] = Query(None, description="开始时间 (ISO 8601 格式)"),
    end_time: Optional[str] = Query(None, description="结束时间 (ISO 8601 格式)"),
    sensors: Optional[str] = Query(None, description="传感器名称列表（逗号分隔）")
):
    """
    获取图表数据
    
    解析指定的日志文件并生成 Plotly 格式的交互式图表配置。
    支持可选的过滤参数来限制显示的时间范围和传感器。
    
    Args:
        file_id: 文件唯一标识符
        start_time: 可选的开始时间（ISO 8601 格式）
        end_time: 可选的结束时间（ISO 8601 格式）
        sensors: 可选的传感器名称列表（逗号分隔，例如 "sensor1,sensor2"）
        
    Returns:
        ChartResponse: 包含 Plotly 图表配置（data、layout、config）
        
    Raises:
        HTTPException 404: 文件不存在
        HTTPException 400: 参数无效或文件解析失败
        HTTPException 500: 内部服务器错误
        
    Validates: Requirements 4.4, 4.5, 5.1, 5.2, 5.3
    """
    try:
        # 1. 验证文件是否存在
        try:
            file_path = file_handler.get_file_path(file_id)
            if not file_path.exists():
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error_code": "FILE_NOT_FOUND",
                        "message": f"File with ID '{file_id}' does not exist",
                        "details": {
                            "file_id": file_id
                        },
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )
        except FileNotFoundError:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "FILE_NOT_FOUND",
                    "message": f"File with ID '{file_id}' does not exist",
                    "details": {
                        "file_id": file_id
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        # 2. 解析文件
        try:
            df = data_analyzer.parse_file(file_path)
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail={
                    "error_code": "PARSE_ERROR",
                    "message": f"Failed to parse file: {str(e)}",
                    "details": {
                        "file_id": file_id
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        # 3. 验证和清洗数据
        try:
            df, warnings, skipped_count = data_analyzer.validate_data(df)
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail={
                    "error_code": "VALIDATION_ERROR",
                    "message": f"Data validation failed: {str(e)}",
                    "details": {
                        "file_id": file_id
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        # 4. 解析过滤参数
        filter_start_time = None
        filter_end_time = None
        filter_sensors = None
        
        # 解析开始时间
        if start_time:
            try:
                filter_start_time = pd.to_datetime(start_time)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error_code": "INVALID_PARAMETER",
                        "message": "Invalid time format for start_time parameter",
                        "details": {
                            "parameter": "start_time",
                            "provided_value": start_time,
                            "expected_format": "ISO 8601 (YYYY-MM-DDTHH:MM:SS)"
                        },
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )
        
        # 解析结束时间
        if end_time:
            try:
                filter_end_time = pd.to_datetime(end_time)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error_code": "INVALID_PARAMETER",
                        "message": "Invalid time format for end_time parameter",
                        "details": {
                            "parameter": "end_time",
                            "provided_value": end_time,
                            "expected_format": "ISO 8601 (YYYY-MM-DDTHH:MM:SS)"
                        },
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )
        
        # 解析传感器列表
        if sensors:
            filter_sensors = [s.strip() for s in sensors.split(',') if s.strip()]
            if not filter_sensors:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error_code": "INVALID_PARAMETER",
                        "message": "Sensor list cannot be empty",
                        "details": {
                            "parameter": "sensors",
                            "provided_value": sensors
                        },
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )
        
        # 5. 应用过滤
        try:
            filtered_df = data_analyzer.filter_data(
                df,
                start_time=filter_start_time,
                end_time=filter_end_time,
                sensors=filter_sensors
            )
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail={
                    "error_code": "FILTER_ERROR",
                    "message": f"Failed to apply filters: {str(e)}",
                    "details": {
                        "file_id": file_id
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        # 6. 生成图表配置
        try:
            chart_config = visualization_engine.create_time_series_chart(
                filtered_df,
                sensors=filter_sensors,
                title="ECU Sensor Data"
            )
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail={
                    "error_code": "CHART_GENERATION_ERROR",
                    "message": f"Failed to generate chart: {str(e)}",
                    "details": {
                        "file_id": file_id
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        # 7. 构建响应
        response = ChartResponse(
            data=chart_config['data'],
            layout=chart_config['layout'],
            config=chart_config['config'],
            warnings=warnings if warnings else None,
            skipped_entries=skipped_count if skipped_count > 0 else None
        )
        
        return response
        
    except HTTPException:
        # 重新抛出 HTTP 异常
        raise
    except Exception as e:
        # 内部服务器错误
        import traceback
        traceback.print_exc()  # 打印堆栈跟踪用于调试
        
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "INTERNAL_ERROR",
                "message": "An internal error occurred while processing your request",
                "details": {
                    "request_id": f"req-{datetime.now(timezone.utc).timestamp()}"
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )


@app.get("/api/export/{file_id}")
async def export_data(
    file_id: str,
    format: str = Query(..., description="导出格式 (csv 或 json)"),
    start_time: Optional[str] = Query(None, description="开始时间 (ISO 8601 格式)"),
    end_time: Optional[str] = Query(None, description="结束时间 (ISO 8601 格式)"),
    sensors: Optional[str] = Query(None, description="传感器名称列表（逗号分隔）")
):
    """
    导出数据
    
    导出指定文件的数据为 CSV 或 JSON 格式。
    支持可选的过滤参数来限制导出的时间范围和传感器。
    导出结果包含元数据（导出时间戳、应用的过滤参数）。
    
    Args:
        file_id: 文件唯一标识符
        format: 导出格式 ("csv" 或 "json")
        start_time: 可选的开始时间（ISO 8601 格式）
        end_time: 可选的结束时间（ISO 8601 格式）
        sensors: 可选的传感器名称列表（逗号分隔，例如 "sensor1,sensor2"）
        
    Returns:
        StreamingResponse: CSV 文件下载或 JSON 响应
        
    Raises:
        HTTPException 404: 文件不存在
        HTTPException 400: 参数无效或文件解析失败
        HTTPException 500: 内部服务器错误
        
    Validates: Requirements 15.1, 15.2, 15.3, 15.4
    """
    try:
        # 1. 验证导出格式
        format_lower = format.lower()
        if format_lower not in ['csv', 'json']:
            raise HTTPException(
                status_code=400,
                detail={
                    "error_code": "INVALID_PARAMETER",
                    "message": "Invalid export format. Only 'csv' and 'json' are supported.",
                    "details": {
                        "parameter": "format",
                        "provided_value": format,
                        "allowed_values": ["csv", "json"]
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        # 2. 验证文件是否存在
        try:
            file_path = file_handler.get_file_path(file_id)
            if not file_path.exists():
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error_code": "FILE_NOT_FOUND",
                        "message": f"File with ID '{file_id}' does not exist",
                        "details": {
                            "file_id": file_id
                        },
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )
        except FileNotFoundError:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "FILE_NOT_FOUND",
                    "message": f"File with ID '{file_id}' does not exist",
                    "details": {
                        "file_id": file_id
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        # 3. 解析文件
        try:
            df = data_analyzer.parse_file(file_path)
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail={
                    "error_code": "PARSE_ERROR",
                    "message": f"Failed to parse file: {str(e)}",
                    "details": {
                        "file_id": file_id
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        # 4. 验证和清洗数据
        try:
            df, warnings, skipped_count = data_analyzer.validate_data(df)
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail={
                    "error_code": "VALIDATION_ERROR",
                    "message": f"Data validation failed: {str(e)}",
                    "details": {
                        "file_id": file_id
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        # 5. 解析过滤参数
        filter_start_time = None
        filter_end_time = None
        filter_sensors = None
        
        # 解析开始时间
        if start_time:
            try:
                filter_start_time = pd.to_datetime(start_time)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error_code": "INVALID_PARAMETER",
                        "message": "Invalid time format for start_time parameter",
                        "details": {
                            "parameter": "start_time",
                            "provided_value": start_time,
                            "expected_format": "ISO 8601 (YYYY-MM-DDTHH:MM:SS)"
                        },
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )
        
        # 解析结束时间
        if end_time:
            try:
                filter_end_time = pd.to_datetime(end_time)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error_code": "INVALID_PARAMETER",
                        "message": "Invalid time format for end_time parameter",
                        "details": {
                            "parameter": "end_time",
                            "provided_value": end_time,
                            "expected_format": "ISO 8601 (YYYY-MM-DDTHH:MM:SS)"
                        },
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )
        
        # 解析传感器列表
        if sensors:
            filter_sensors = [s.strip() for s in sensors.split(',') if s.strip()]
            if not filter_sensors:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error_code": "INVALID_PARAMETER",
                        "message": "Sensor list cannot be empty",
                        "details": {
                            "parameter": "sensors",
                            "provided_value": sensors
                        },
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )
        
        # 6. 应用过滤
        try:
            filtered_df = data_analyzer.filter_data(
                df,
                start_time=filter_start_time,
                end_time=filter_end_time,
                sensors=filter_sensors
            )
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail={
                    "error_code": "FILTER_ERROR",
                    "message": f"Failed to apply filters: {str(e)}",
                    "details": {
                        "file_id": file_id
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        # 7. 准备导出元数据
        export_timestamp = datetime.now(timezone.utc).isoformat()
        metadata = {
            "export_timestamp": export_timestamp,
            "file_id": file_id,
            "filters": {
                "start_time": start_time,
                "end_time": end_time,
                "sensors": filter_sensors
            },
            "record_count": len(filtered_df)
        }
        
        # 8. 根据格式导出数据
        if format_lower == 'csv':
            # 导出为 CSV
            # 创建内存缓冲区
            output = io.StringIO()
            
            # 写入元数据作为注释
            output.write(f"# Export Timestamp: {export_timestamp}\n")
            output.write(f"# File ID: {file_id}\n")
            output.write(f"# Filters Applied:\n")
            output.write(f"#   Start Time: {start_time or 'None'}\n")
            output.write(f"#   End Time: {end_time or 'None'}\n")
            output.write(f"#   Sensors: {', '.join(filter_sensors) if filter_sensors else 'All'}\n")
            output.write(f"# Record Count: {len(filtered_df)}\n")
            output.write("#\n")
            
            # 写入数据
            filtered_df.to_csv(output, index=False)
            
            # 获取 CSV 内容
            csv_content = output.getvalue()
            output.close()
            
            # 返回文件下载响应
            return StreamingResponse(
                io.BytesIO(csv_content.encode('utf-8')),
                media_type='text/csv',
                headers={
                    'Content-Disposition': f'attachment; filename="export_{file_id}_{datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")}.csv"'
                }
            )
        
        else:  # format_lower == 'json'
            # 导出为 JSON
            # 转换 DataFrame 为字典列表
            records = filtered_df.to_dict(orient='records')
            
            # 转换时间戳为 ISO 格式字符串
            for record in records:
                if 'timestamp' in record and pd.notna(record['timestamp']):
                    record['timestamp'] = pd.to_datetime(record['timestamp']).isoformat()
            
            # 构建完整的 JSON 响应
            json_response = {
                "metadata": metadata,
                "data": records
            }
            
            # 返回 JSON 响应
            return JSONResponse(
                content=json_response,
                headers={
                    'Content-Disposition': f'attachment; filename="export_{file_id}_{datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")}.json"'
                }
            )
        
    except HTTPException:
        # 重新抛出 HTTP 异常
        raise
    except Exception as e:
        # 内部服务器错误
        import traceback
        traceback.print_exc()  # 打印堆栈跟踪用于调试
        
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "INTERNAL_ERROR",
                "message": "An internal error occurred while processing your request",
                "details": {
                    "request_id": f"req-{datetime.now(timezone.utc).timestamp()}"
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )


@app.get("/api/files", response_model=FileListResponse)
async def get_files():
    """
    获取所有已上传文件的列表
    
    返回所有已上传文件的元数据列表，包括文件 ID、文件名、大小、上传时间等信息。
    
    Returns:
        FileListResponse: 包含所有文件元数据的列表
        
    Raises:
        HTTPException 500: 内部服务器错误
        
    Validates: Requirements 1.3
    """
    try:
        # 获取 uploads 目录中的所有文件
        files_metadata = []
        
        # 遍历存储目录中的所有文件
        for file_path in file_handler.storage_path.iterdir():
            if file_path.is_file():
                # 检查文件扩展名是否有效
                file_ext = file_path.suffix.lower()
                if file_ext in file_handler.ALLOWED_EXTENSIONS:
                    # 提取文件 ID（文件名去掉扩展名）
                    file_id = file_path.stem
                    
                    # 获取文件信息
                    file_size = file_path.stat().st_size
                    file_format = file_ext.lstrip('.')
                    
                    # 获取文件修改时间作为上传时间
                    upload_time = datetime.fromtimestamp(
                        file_path.stat().st_mtime,
                        tz=timezone.utc
                    )
                    
                    # 创建文件元数据
                    metadata = FileMetadata(
                        file_id=file_id,
                        filename=file_path.name,
                        original_filename=file_path.name,  # 我们没有存储原始文件名，使用当前文件名
                        file_size=file_size,
                        upload_time=upload_time,
                        file_format=file_format,
                        status="uploaded"
                    )
                    
                    files_metadata.append(metadata)
        
        # 按上传时间降序排序（最新的在前）
        files_metadata.sort(key=lambda x: x.upload_time, reverse=True)
        
        # 构建响应
        response = FileListResponse(files=files_metadata)
        
        return response
        
    except Exception as e:
        # 内部服务器错误
        import traceback
        traceback.print_exc()  # 打印堆栈跟踪用于调试
        
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "INTERNAL_ERROR",
                "message": "An internal error occurred while processing your request",
                "details": {
                    "request_id": f"req-{datetime.now(timezone.utc).timestamp()}"
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )


# Engineering Dashboard API Endpoints

@app.get("/api/engineering/git/commits")
async def get_git_commits(limit: int = Query(50, description="Maximum number of commits to retrieve")):
    """
    Get recent Git commit history
    
    Args:
        limit: Maximum number of commits to retrieve (default: 50)
        
    Returns:
        List of CommitInfo objects
        
    Validates: Requirements 1.4, 6.2
    """
    try:
        git_repo = GitRepository()
        commits = git_repo.get_commit_history(limit=limit)
        return commits
    except Exception as e:
        return []


@app.get("/api/engineering/git/stats")
async def get_git_stats():
    """
    Get repository statistics
    
    Returns:
        RepositoryStats object
        
    Validates: Requirements 1.4, 6.2
    """
    try:
        git_repo = GitRepository()
        stats = git_repo.get_repository_stats()
        return stats
    except Exception as e:
        return {
            "total_commits": 0,
            "branches": [],
            "current_branch": "unknown",
            "remote_url": None,
            "contributors": 0
        }


@app.get("/api/engineering/cicd/github")
async def get_github_actions_status(
    repo_owner: str = Query("owner", description="GitHub repository owner"),
    repo_name: str = Query("repo", description="GitHub repository name"),
    token: Optional[str] = Query(None, description="GitHub personal access token")
):
    """
    Get GitHub Actions workflow status
    
    Args:
        repo_owner: GitHub repository owner/organization
        repo_name: GitHub repository name
        token: Optional GitHub personal access token
        
    Returns:
        WorkflowStatus object
        
    Validates: Requirements 3.7, 6.3
    """
    try:
        monitor = GitHubActionsMonitor(repo_owner, repo_name, token)
        status = monitor.get_latest_run_status()
        return status
    except Exception as e:
        return {
            "latest_run": None,
            "recent_runs": [],
            "success_rate": 0.0
        }


@app.get("/api/engineering/cicd/jenkins")
async def get_jenkins_status(
    jenkins_url: str = Query("http://localhost:8080", description="Jenkins server URL"),
    job_name: str = Query("ecu-log-visualizer", description="Jenkins job name"),
    username: Optional[str] = Query(None, description="Jenkins username"),
    api_token: Optional[str] = Query(None, description="Jenkins API token")
):
    """
    Get Jenkins pipeline status
    
    Args:
        jenkins_url: Jenkins server URL
        job_name: Jenkins job/pipeline name
        username: Optional Jenkins username
        api_token: Optional Jenkins API token
        
    Returns:
        BuildStatus object
        
    Validates: Requirements 5.6, 6.5
    """
    try:
        auth = (username, api_token) if username and api_token else None
        monitor = JenkinsMonitor(jenkins_url, job_name, auth)
        status = monitor.get_latest_build_status()
        return status
    except Exception as e:
        return {
            "latest_build": None,
            "recent_builds": [],
            "success_rate": 0.0
        }


@app.get("/api/engineering/docker/status")
async def get_docker_status(
    container_name: str = Query("ecu-log-visualizer", description="Container name to check")
):
    """
    Get Docker container status
    
    Args:
        container_name: Name of the container to check
        
    Returns:
        ContainerStatus object or None if container doesn't exist
        
    Validates: Requirements 4.5, 6.4
    """
    try:
        monitor = DockerMonitor()
        status = monitor.get_container_status(container_name)
        return status
    except Exception as e:
        return None


@app.get("/api/engineering/dashboard", response_model=DashboardData)
async def get_dashboard_data(
    repo_owner: str = Query("owner", description="GitHub repository owner"),
    repo_name: str = Query("repo", description="GitHub repository name"),
    github_token: Optional[str] = Query(None, description="GitHub personal access token"),
    jenkins_url: str = Query("http://localhost:8080", description="Jenkins server URL"),
    jenkins_job: str = Query("ecu-log-visualizer", description="Jenkins job name"),
    jenkins_username: Optional[str] = Query(None, description="Jenkins username"),
    jenkins_token: Optional[str] = Query(None, description="Jenkins API token"),
    container_name: str = Query("ecu-log-visualizer", description="Docker container name")
):
    """
    Get all dashboard data in a single request
    
    This endpoint aggregates data from all engineering tools with timeout handling.
    Returns partial data if some components fail or timeout.
    
    Args:
        repo_owner: GitHub repository owner
        repo_name: GitHub repository name
        github_token: Optional GitHub token
        jenkins_url: Jenkins server URL
        jenkins_job: Jenkins job name
        jenkins_username: Optional Jenkins username
        jenkins_token: Optional Jenkins API token
        container_name: Docker container name
        
    Returns:
        DashboardData object with all available information
        
    Validates: Requirements 6.2, 6.3, 6.4, 6.5, 6.6, 6.7
    """
    import asyncio
    from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
    
    dashboard_data = {
        "git_stats": None,
        "recent_commits": [],
        "github_status": None,
        "jenkins_status": None,
        "docker_status": None,
        "api_health": {
            "status": "healthy",
            "service": "ECU Log Visualizer"
        },
        "test_results": None,
        "timestamp": datetime.now(timezone.utc)
    }
    
    # Use ThreadPoolExecutor for parallel execution with timeout
    executor = ThreadPoolExecutor(max_workers=5)
    
    def get_git_data():
        try:
            git_repo = GitRepository()
            return {
                "stats": git_repo.get_repository_stats(),
                "commits": git_repo.get_commit_history(limit=10)
            }
        except Exception:
            return {"stats": None, "commits": []}
    
    def get_github_data():
        try:
            monitor = GitHubActionsMonitor(repo_owner, repo_name, github_token)
            return monitor.get_latest_run_status()
        except Exception:
            return None
    
    def get_jenkins_data():
        try:
            auth = (jenkins_username, jenkins_token) if jenkins_username and jenkins_token else None
            monitor = JenkinsMonitor(jenkins_url, jenkins_job, auth)
            return monitor.get_latest_build_status()
        except Exception:
            return None
    
    def get_docker_data():
        try:
            monitor = DockerMonitor()
            return monitor.get_container_status(container_name)
        except Exception:
            return None
    
    # Submit all tasks
    git_future = executor.submit(get_git_data)
    github_future = executor.submit(get_github_data)
    jenkins_future = executor.submit(get_jenkins_data)
    docker_future = executor.submit(get_docker_data)
    
    # Collect results with timeout (5 seconds total)
    try:
        git_data = git_future.result(timeout=2)
        dashboard_data["git_stats"] = git_data["stats"].model_dump() if git_data["stats"] else None
        dashboard_data["recent_commits"] = [c.model_dump() for c in git_data["commits"]]
    except (FuturesTimeoutError, Exception):
        pass
    
    try:
        github_status = github_future.result(timeout=2)
        dashboard_data["github_status"] = github_status.model_dump() if github_status else None
    except (FuturesTimeoutError, Exception):
        pass
    
    try:
        jenkins_status = jenkins_future.result(timeout=2)
        dashboard_data["jenkins_status"] = jenkins_status.model_dump() if jenkins_status else None
    except (FuturesTimeoutError, Exception):
        pass
    
    try:
        docker_status = docker_future.result(timeout=2)
        dashboard_data["docker_status"] = docker_status.model_dump() if docker_status else None
    except (FuturesTimeoutError, Exception):
        pass
    
    executor.shutdown(wait=False)
    
    return DashboardData(**dashboard_data)


if __name__ == "__main__":
    import uvicorn
    
    # Display startup information
    print("=" * 60)
    print("ECU Log Visualizer - Starting Server")
    print("=" * 60)
    print(f"Server URL: http://localhost:8000")
    print(f"API Documentation: http://localhost:8000/docs")
    print(f"Health Check: http://localhost:8000/health")
    print(f"Max Upload Size: {MAX_UPLOAD_SIZE / (1024 * 1024)}MB")
    print("=" * 60)
    
    # Start the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        limit_max_requests=MAX_UPLOAD_SIZE
    )
