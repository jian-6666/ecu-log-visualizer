# ECU Log Visualizer

ECU Log Visualizer 是一个用于分析和可视化电子控制单元（ECU）日志数据的 Web 应用系统，集成了完整的现代软件工程工具链。

[![CI Pipeline](https://github.com/jian-6666/ecu-log-visualizer/actions/workflows/ci.yml/badge.svg)](https://github.com/jian-6666/ecu-log-visualizer/actions)

## 📚 快速导航

**🚀 新用户？从这里开始：**
- 📖 **[README_FIRST.md](README_FIRST.md)** - 文档导航和快速开始
- 📖 **[简易操作指南.md](简易操作指南.md)** - 中文完整操作指南
- 📖 **[SIMPLE_OPERATION_GUIDE.md](SIMPLE_OPERATION_GUIDE.md)** - English Complete Guide

**🎬 要做演示？**
- 🎯 **[QUICK_DEMO_STEPS.md](QUICK_DEMO_STEPS.md)** - 5 分钟快速演示
- 📋 **[DEMO-READY-CHECKLIST.md](DEMO-READY-CHECKLIST.md)** - 演示前检查清单

**🔧 了解 DevOps？**
- 🚀 **[DEVOPS_DEMO_GUIDE.md](DEVOPS_DEMO_GUIDE.md)** - DevOps 系统指南
- 📊 **[DEVOPS_UPGRADE_SUMMARY.md](DEVOPS_UPGRADE_SUMMARY.md)** - 升级总结

---

## 功能特性

### 核心功能
- 日志文件上传（支持 CSV 和 JSON 格式）
- 时间序列数据统计分析
- 交互式数据可视化（基于 Plotly）
- 灵活的数据过滤（按时间范围和传感器类型）
- 数据导出功能（CSV/JSON）
- 自动生成的 API 文档

### 工程工具链
- **版本控制**: Git + GitHub 集成
- **持续集成**: GitHub Actions 自动化测试和构建
- **容器化**: Docker 多阶段构建
- **CI/CD**: Jenkins 流水线支持
- **工程仪表板**: 实时可视化工程流程
- **自动化脚本**: 开发、测试、构建、部署自动化

### DevOps 流程可视化
```
👨‍💻 Developer Commit → 📊 Git → 🐙 GitHub → 🔄 CI/CD Build → 🐳 Docker Image → 🔧 Jenkins Test → 🚀 Running Service
```

## ⚡ 快速开始

### 3 分钟启动

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **启动服务器**
   ```bash
   python run_server.py
   ```

3. **打开浏览器**
   - 主应用：http://localhost:8000
   - **工程仪表板 V2** (新版，推荐): http://localhost:8000/engineering-dashboard-v2.html
   - 工程仪表板 V1: http://localhost:8000/engineering-dashboard.html

就这么简单！🎉

### 🎨 新版仪表板 V2 特性
- ✅ 专业企业级设计
- ✅ 高对比度状态指示
- ✅ 完整的流程可视化
- ✅ 适合管理层演示
- 📖 查看 [DASHBOARD_V2_QUICK_START.md](DASHBOARD_V2_QUICK_START.md) 了解更多

---

## 系统要求

- Python 3.9 或更高版本
- 现代 Web 浏览器（Chrome、Firefox、Safari、Edge）
- Docker（可选，用于容器化部署）
- Git（可选，用于版本控制）

## 详细安装说明

1. 克隆项目并进入目录：
   ```bash
   git clone https://github.com/jian-6666/ecu-log-visualizer.git
   cd ecu-log-visualizer
   ```

2. 创建虚拟环境（推荐）：
   ```bash
   python -m venv venv
   ```

3. 激活虚拟环境：
   - Linux/Mac: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate`

4. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 快速开始

### 方式 1: 使用自动化脚本（推荐）

```bash
# 设置开发环境
./scripts/dev.sh

# 运行测试
./scripts/test.sh

# 构建 Docker 镜像
./scripts/build.sh

# 部署应用
./scripts/deploy.sh
```

### 方式 2: 手动启动

使用启动脚本：
```bash
# Python 脚本（跨平台）
python run_server.py

# 或使用 Shell 脚本（Linux/Mac）
./run_server.sh
```

或直接使用 uvicorn：
```bash
uvicorn src.main:app --host 127.0.0.1 --port 8000
```

### 方式 3: 使用 Docker

```bash
# 构建镜像
docker build -t ecu-log-visualizer:latest .

# 运行容器
docker run -p 8000:8000 ecu-log-visualizer:latest
```

服务器启动后访问：
- Web 界面: http://localhost:8000
- API 文档: http://localhost:8000/docs
- 工程仪表板: http://localhost:8000/engineering-dashboard.html

### 使用示例数据

系统提供了示例数据文件用于快速体验：
- `examples/sample_ecu_log.csv` - CSV 格式示例（100+ 数据点）
- `examples/sample_ecu_log.json` - JSON 格式示例

通过 Web 界面上传这些文件即可查看分析结果。

## 项目结构

```
ecu-log-visualizer/
├── .github/workflows/      # GitHub Actions CI 配置
├── src/                    # 源代码
│   ├── main.py            # FastAPI 应用主文件
│   ├── models.py          # 数据模型
│   ├── file_handler.py    # 文件处理
│   ├── data_analyzer.py   # 数据分析
│   ├── visualization_engine.py  # 可视化引擎
│   ├── git_integration.py # Git 集成
│   ├── cicd_status.py     # CI/CD 状态监控
│   └── docker_status.py   # Docker 状态监控
├── frontend/              # 前端文件
│   ├── index.html         # 主界面
│   ├── engineering-dashboard.html  # 工程仪表板
│   ├── app.js             # 应用逻辑
│   └── styles.css         # 样式文件
├── tests/                 # 测试文件
│   ├── unit/             # 单元测试
│   ├── integration/      # 集成测试
│   └── property/         # 属性测试
├── scripts/              # 自动化脚本
│   ├── dev.sh           # 开发环境设置
│   ├── test.sh          # 运行测试
│   ├── build.sh         # 构建 Docker
│   └── deploy.sh        # 部署应用
├── docs/                 # 文档
│   ├── github-setup.md  # GitHub 设置指南
│   ├── engineering-toolchain.md  # 工具链架构
│   ├── demo.md          # 演示工作流
│   └── maintenance.md   # 维护指南
├── examples/             # 示例数据
├── uploads/              # 上传文件存储
├── Dockerfile            # Docker 配置
├── Jenkinsfile          # Jenkins 流水线
└── CHANGELOG.md         # 变更日志
```

## API 端点

### 应用 API
- `POST /api/upload` - 上传日志文件
- `GET /api/stats/{file_id}` - 获取统计信息
- `GET /api/chart/{file_id}` - 获取图表数据
- `GET /api/export/{file_id}` - 导出数据
- `GET /api/files` - 获取文件列表

### 工程 API
- `GET /api/engineering/git/commits` - Git 提交历史
- `GET /api/engineering/git/stats` - 仓库统计
- `GET /api/engineering/cicd/github` - GitHub Actions 状态
- `GET /api/engineering/cicd/jenkins` - Jenkins 构建状态
- `GET /api/engineering/docker/status` - Docker 容器状态
- `GET /api/engineering/dashboard` - 完整仪表板数据

## 日志文件格式

CSV 格式示例：
```
timestamp,sensor1,sensor2,sensor3,status
2024-01-01T00:00:00,23.5,45.2,67.8,OK
```

JSON 格式示例：
```json
[{"timestamp": "2024-01-01T00:00:00", "sensors": {"sensor1": 23.5}, "status": "OK"}]
```

详见 `docs/log_format.md`

## 开发

### 运行测试

运行所有测试：
```bash
pytest
# 或使用自动化脚本
./scripts/test.sh
```

运行特定测试类型：
```bash
pytest tests/unit          # 单元测试
pytest tests/integration   # 集成测试
pytest tests/property      # 属性测试
```

生成覆盖率报告：
```bash
pytest --cov=src --cov-report=html
```

### 开发模式

启动开发服务器（自动重载）：
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### GitHub 集成

查看 GitHub 设置指南：
```bash
cat docs/github-setup.md
```

配置 GitHub remote：
```bash
git remote add origin https://github.com/jian-6666/ecu-log-visualizer.git
```

推送代码：
```bash
git add .
git commit -m "Initial commit"
git push -u origin master
```

### CI/CD 流水线

GitHub Actions 会在每次推送时自动运行：
- ✅ 代码检查（flake8）
- ✅ 运行测试（pytest）
- ✅ 构建验证
- ✅ Docker 镜像构建（main/master 分支）

查看 CI 状态：https://github.com/jian-6666/ecu-log-visualizer/actions

## 故障排除

### 常见问题

**无法启动服务器**
- 检查 Python 版本（需要 3.9 或更高）：`python --version`
- 检查依赖是否正确安装：`pip list`
- 检查端口 8000 是否被占用

**文件上传失败**
- 确认文件格式为 .csv 或 .json
- 确认文件大小不超过 50MB
- 检查文件内容格式是否正确（参见 `docs/log_format.md`）

**图表无法显示**
- 检查浏览器控制台是否有错误信息
- 确认 Plotly.js 库已正确加载
- 尝试清除浏览器缓存

**统计计算缓慢**
- 对于大文件（>10MB），统计计算可能需要几秒钟
- 考虑使用过滤功能减少数据量

**API 错误**
- 查看 API 文档了解正确的请求格式：http://localhost:8000/docs
- 检查服务器日志获取详细错误信息

### 获取帮助

- 查看 API 文档：http://localhost:8000/docs
- 查看日志格式文档：`docs/log_format.md`
- 查看配置文档：`docs/configuration.md`
- 查看 GitHub 设置：`docs/github-setup.md`
- 查看工程工具链：`docs/engineering-toolchain.md`
- 查看演示工作流：`docs/demo.md`

## 文档

- [GitHub 设置指南](docs/github-setup.md) - GitHub 集成和 CI/CD 配置
- [工程工具链架构](docs/engineering-toolchain.md) - 系统架构和组件交互
- [演示工作流](docs/demo.md) - 完整演示流程（15 分钟）
- [维护指南](docs/maintenance.md) - 日常维护和故障排除
- [日志格式](docs/log_format.md) - 支持的日志文件格式
- [配置说明](docs/configuration.md) - 系统配置选项

## 贡献

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 LICENSE 文件

## 联系方式

- GitHub: [@jian-6666](https://github.com/jian-6666)
- 项目链接: [https://github.com/jian-6666/ecu-log-visualizer](https://github.com/jian-6666/ecu-log-visualizer)
