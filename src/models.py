"""
Pydantic 数据模型定义

该模块定义了 ECU Log Visualizer 系统中使用的所有数据模型。
"""

from pydantic import BaseModel, Field, ConfigDict, field_serializer
from datetime import datetime
from typing import Dict, List, Optional


class FileMetadata(BaseModel):
    """文件元数据模型"""
    model_config = ConfigDict()
    
    file_id: str = Field(..., description="唯一文件标识符")
    filename: str = Field(..., description="存储的文件名")
    original_filename: str = Field(..., description="原始上传文件名")
    file_size: int = Field(..., description="文件大小（字节）")
    upload_time: datetime = Field(..., description="上传时间")
    file_format: str = Field(..., description="文件格式 (csv 或 json)")
    status: str = Field(..., description="文件状态 (uploaded, parsed, error)")
    
    @field_serializer('upload_time')
    def serialize_upload_time(self, dt: datetime, _info):
        return dt.isoformat()


class SensorStatistics(BaseModel):
    """传感器统计信息模型"""
    min: float = Field(..., description="最小值")
    max: float = Field(..., description="最大值")
    mean: float = Field(..., description="平均值")
    std: float = Field(..., description="标准差")
    count: int = Field(..., description="数据点数量")


class StatisticsResponse(BaseModel):
    """统计信息响应模型"""
    file_id: str = Field(..., description="文件标识符")
    sensors: Dict[str, SensorStatistics] = Field(..., description="各传感器的统计信息")
    time_range: Dict[str, str] = Field(..., description="时间范围 (start, end)")
    total_records: int = Field(..., description="总记录数")
    filtered_records: int = Field(..., description="过滤后的记录数")
    warnings: Optional[List[str]] = Field(default=None, description="数据验证警告列表")
    skipped_entries: Optional[int] = Field(default=None, description="跳过的条目数量")


class ChartResponse(BaseModel):
    """图表响应模型"""
    data: List[Dict] = Field(..., description="Plotly 数据轨迹")
    layout: Dict = Field(..., description="Plotly 布局配置")
    config: Dict = Field(..., description="Plotly 配置选项")
    warnings: Optional[List[str]] = Field(default=None, description="数据验证警告列表")
    skipped_entries: Optional[int] = Field(default=None, description="跳过的条目数量")


class FilterParams(BaseModel):
    """过滤参数模型"""
    model_config = ConfigDict()
    
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    sensors: Optional[List[str]] = Field(None, description="传感器名称列表")
    
    @field_serializer('start_time', 'end_time')
    def serialize_datetime(self, dt: Optional[datetime], _info):
        return dt.isoformat() if dt else None


class ExportRequest(BaseModel):
    """导出请求模型"""
    file_id: str = Field(..., description="文件标识符")
    format: str = Field(..., description="导出格式 (csv 或 json)")
    filters: Optional[FilterParams] = Field(None, description="过滤条件")
    include_metadata: bool = Field(True, description="是否包含元数据")


class FileListResponse(BaseModel):
    """文件列表响应模型"""
    files: List[FileMetadata] = Field(..., description="文件元数据列表")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    model_config = ConfigDict()
    
    error_code: str = Field(..., description="错误代码")
    message: str = Field(..., description="错误消息")
    details: Optional[Dict] = Field(None, description="错误详情")
    timestamp: datetime = Field(..., description="错误发生时间")
    
    @field_serializer('timestamp')
    def serialize_timestamp(self, dt: datetime, _info):
        return dt.isoformat()


# Engineering Dashboard Models

class CommitInfo(BaseModel):
    """Git commit information model"""
    hash: str = Field(..., description="Full commit hash")
    short_hash: str = Field(..., description="Short commit hash")
    author: str = Field(..., description="Commit author name")
    email: str = Field(..., description="Commit author email")
    timestamp: datetime = Field(..., description="Commit timestamp")
    message: str = Field(..., description="Commit message")
    branch: str = Field(..., description="Branch name")
    
    @field_serializer('timestamp')
    def serialize_timestamp(self, dt: datetime, _info):
        return dt.isoformat()


class RepositoryStats(BaseModel):
    """Repository statistics model"""
    total_commits: int = Field(..., description="Total number of commits")
    branches: List[str] = Field(..., description="List of branch names")
    current_branch: str = Field(..., description="Current branch name")
    remote_url: Optional[str] = Field(None, description="Remote repository URL")
    contributors: int = Field(..., description="Number of contributors")


class WorkflowRun(BaseModel):
    """GitHub Actions workflow run model"""
    id: int = Field(..., description="Workflow run ID")
    name: str = Field(..., description="Workflow name")
    status: str = Field(..., description="Workflow status (queued, in_progress, completed)")
    conclusion: Optional[str] = Field(None, description="Workflow conclusion (success, failure, cancelled)")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    html_url: str = Field(..., description="GitHub URL for the workflow run")
    
    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime, _info):
        return dt.isoformat()


class WorkflowStatus(BaseModel):
    """GitHub Actions workflow status model"""
    latest_run: Optional[WorkflowRun] = Field(None, description="Latest workflow run")
    recent_runs: List[WorkflowRun] = Field(default_factory=list, description="Recent workflow runs")
    success_rate: float = Field(..., description="Success rate (0.0 to 1.0)")


class BuildInfo(BaseModel):
    """Jenkins build information model"""
    number: int = Field(..., description="Build number")
    status: str = Field(..., description="Build status (SUCCESS, FAILURE, UNSTABLE, ABORTED, IN_PROGRESS)")
    timestamp: datetime = Field(..., description="Build timestamp")
    duration: int = Field(..., description="Build duration in milliseconds")
    url: str = Field(..., description="Jenkins URL for the build")
    
    @field_serializer('timestamp')
    def serialize_timestamp(self, dt: datetime, _info):
        return dt.isoformat()


class BuildStatus(BaseModel):
    """Jenkins build status model"""
    latest_build: Optional[BuildInfo] = Field(None, description="Latest build")
    recent_builds: List[BuildInfo] = Field(default_factory=list, description="Recent builds")
    success_rate: float = Field(..., description="Success rate (0.0 to 1.0)")


class ContainerStatus(BaseModel):
    """Docker container status model"""
    name: str = Field(..., description="Container name")
    status: str = Field(..., description="Container status (running, stopped, paused, restarting, error)")
    image: str = Field(..., description="Image name")
    created: datetime = Field(..., description="Container creation timestamp")
    ports: Dict[str, str] = Field(default_factory=dict, description="Port mappings")
    health: Optional[str] = Field(None, description="Health status (healthy, unhealthy, starting)")
    
    @field_serializer('created')
    def serialize_created(self, dt: datetime, _info):
        return dt.isoformat()


class ImageInfo(BaseModel):
    """Docker image information model"""
    id: str = Field(..., description="Image ID")
    tags: List[str] = Field(default_factory=list, description="Image tags")
    created: datetime = Field(..., description="Image creation timestamp")
    size: int = Field(..., description="Image size in bytes")
    
    @field_serializer('created')
    def serialize_created(self, dt: datetime, _info):
        return dt.isoformat()


class DashboardData(BaseModel):
    """Complete dashboard data model"""
    git_stats: Optional[RepositoryStats] = Field(None, description="Git repository statistics")
    recent_commits: List[CommitInfo] = Field(default_factory=list, description="Recent commits")
    github_status: Optional[WorkflowStatus] = Field(None, description="GitHub Actions status")
    jenkins_status: Optional[BuildStatus] = Field(None, description="Jenkins pipeline status")
    docker_status: Optional[ContainerStatus] = Field(None, description="Docker container status")
    api_health: Dict = Field(default_factory=dict, description="API health information")
    test_results: Optional[Dict] = Field(None, description="Test execution results")
    timestamp: datetime = Field(..., description="Dashboard data timestamp")
    
    @field_serializer('timestamp')
    def serialize_timestamp(self, dt: datetime, _info):
        return dt.isoformat()
