# ECU Log Visualizer 配置文档

本文档描述 ECU Log Visualizer 的所有配置选项。

## 环境变量

系统支持以下环境变量进行配置：

### 服务器配置

```bash
# 服务器主机地址
HOST=0.0.0.0

# 服务器端口
PORT=8000

# 是否启用调试模式
DEBUG=false

# 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO
```

### 文件存储配置

```bash
# 上传文件存储目录
UPLOAD_DIR=./uploads

# 最大文件大小（字节）
MAX_FILE_SIZE=52428800  # 50MB

# 允许的文件扩展名（逗号分隔）
ALLOWED_EXTENSIONS=.csv,.json
```

### 数据处理配置

```bash
# 最大传感器数量
MAX_SENSORS=100

# 图表最大显示传感器数
MAX_CHART_SENSORS=20

# 最大记录数
MAX_RECORDS=1000000

# 数值范围限制
MIN_SENSOR_VALUE=-1e10
MAX_SENSOR_VALUE=1e10
```

### CORS 配置

```bash
# 允许的源（逗号分隔，* 表示所有）
CORS_ORIGINS=*

# 允许的方法
CORS_METHODS=GET,POST,PUT,DELETE,OPTIONS

# 允许的请求头
CORS_HEADERS=*
```

## 配置文件

### 应用配置

可以在 `src/main.py` 中修改以下配置：

```python
# FastAPI 应用配置
app = FastAPI(
    title="ECU Log Visualizer",
    description="ECU 日志分析和可视化系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 文件处理配置

在 `src/file_handler.py` 中配置：

```python
class FileHandler:
    ALLOWED_EXTENSIONS = {'.csv', '.json'}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
```

### 数据分析配置

在 `src/data_analyzer.py` 中配置：

```python
class DataAnalyzer:
    MAX_SENSORS = 100
    MIN_VALUE = -1e10
    MAX_VALUE = 1e10
```

## 性能配置

### 响应时间目标

系统设计的性能目标：

- 文件上传：即时（取决于网络速度）
- 统计计算：< 2 秒（10MB 文件）
- 图表生成：< 3 秒（10MB 文件）
- 过滤更新：< 1 秒（前端）

### 优化建议

1. **大文件处理**：
   - 对于超过 10MB 的文件，考虑使用过滤功能减少数据量
   - 使用时间范围过滤可以显著提高性能

2. **传感器选择**：
   - 图表同时显示的传感器不要超过 20 个
   - 使用传感器过滤功能专注于关键传感器

3. **缓存**：
   - 系统会在内存中缓存解析后的数据
   - 重复请求相同文件的统计信息会更快

## 日志配置

### 日志级别

系统使用 Python 标准 logging 模块，支持以下级别：

- `DEBUG`: 详细的调试信息
- `INFO`: 一般信息（默认）
- `WARNING`: 警告信息
- `ERROR`: 错误信息
- `CRITICAL`: 严重错误

### 日志格式

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ecu_log_visualizer.log'),
        logging.StreamHandler()
    ]
)
```

### 日志文件

- 默认日志文件：`ecu_log_visualizer.log`
- 日志轮转：建议使用 `RotatingFileHandler` 进行日志轮转

## 安全配置

### 文件验证

系统会验证上传的文件：

1. **文件类型验证**：
   - 只允许 .csv 和 .json 文件
   - 基于文件扩展名和 MIME 类型

2. **文件大小验证**：
   - 最大 50MB
   - 可通过 `MAX_FILE_SIZE` 配置

3. **内容验证**：
   - 验证文件格式正确性
   - 验证数据类型和范围

### API 安全

1. **CORS 配置**：
   - 生产环境建议限制允许的源
   - 不要使用 `allow_origins=["*"]`

2. **错误处理**：
   - 不暴露内部实现细节
   - 返回标准化的错误响应

3. **输入验证**：
   - 所有 API 参数都经过 Pydantic 验证
   - 防止 SQL 注入和 XSS 攻击

## 部署配置

### 生产环境建议

1. **使用 Gunicorn 或 Uvicorn**：
   ```bash
   uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

2. **使用反向代理**：
   - 推荐使用 Nginx 或 Apache
   - 配置 SSL/TLS 证书

3. **环境变量**：
   ```bash
   export DEBUG=false
   export LOG_LEVEL=WARNING
   export CORS_ORIGINS=https://yourdomain.com
   ```

4. **文件存储**：
   - 确保 `uploads/` 目录有适当的权限
   - 考虑使用专用存储服务（如 S3）

### Docker 配置

示例 Dockerfile：

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

示例 docker-compose.yml：

```yaml
version: '3.8'

services:
  ecu-log-visualizer:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./uploads:/app/uploads
    environment:
      - DEBUG=false
      - LOG_LEVEL=INFO
```

## 故障排除

### 常见配置问题

1. **端口已被占用**：
   - 修改 `PORT` 环境变量
   - 或在启动命令中指定不同端口

2. **文件上传失败**：
   - 检查 `UPLOAD_DIR` 目录权限
   - 确认 `MAX_FILE_SIZE` 设置合理

3. **CORS 错误**：
   - 检查 `CORS_ORIGINS` 配置
   - 确保包含前端域名

4. **性能问题**：
   - 增加 worker 数量
   - 调整 `MAX_RECORDS` 限制
   - 使用缓存机制

## 配置检查清单

部署前检查：

- [ ] 设置适当的 `DEBUG` 值（生产环境为 false）
- [ ] 配置 `CORS_ORIGINS` 限制允许的源
- [ ] 设置合理的 `MAX_FILE_SIZE`
- [ ] 配置日志级别和日志文件
- [ ] 确保 `uploads/` 目录存在且有写权限
- [ ] 配置 SSL/TLS 证书（生产环境）
- [ ] 设置适当的 worker 数量
- [ ] 配置监控和告警
