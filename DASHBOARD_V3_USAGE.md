# Dashboard V3 使用指南

## 🎯 概述

Dashboard V3 是一个完整的 DevOps 可视化仪表板，展示从代码提交到生产部署的完整 CI/CD 流程。

## 🚀 快速启动

### 1. 启动后端服务

```bash
# 方式 1: 直接运行
python run_server.py

# 方式 2: 使用 Docker
docker build -t ecu-log-visualizer .
docker run -d -p 8000:8000 --name ecu-log-visualizer ecu-log-visualizer
```

### 2. 访问 Dashboard

打开浏览器访问：
```
http://localhost:8000/engineering-dashboard-v3.html
```

## 📊 Dashboard 功能模块

### 1. 完整 CI/CD Pipeline 流程图（顶部）

展示从开发到部署的完整流程：

- **Developer Commit** → 开发者提交代码
- **Push to GitHub** → 推送到 GitHub
- **CI Trigger** → 触发 GitHub Actions
- **Install Dependencies** → 安装依赖
- **Lint** → 代码检查
- **Unit Tests** → 单元测试
- **Integration Tests** → 集成测试
- **Build Application** → 构建应用
- **Docker Build** → 构建 Docker 镜像
- **Deploy** → 部署到生产环境

每个步骤显示：
- ✅ 成功状态（绿色）
- ⏳ 运行中（紫色动画）
- ❌ 失败状态（红色）
- ⏸️ 等待中（灰色）

### 2. 关键指标卡片（第二行）

四个核心指标：
- **Build Success Rate**: 构建成功率
- **Latest Build**: 最新构建状态
- **Docker Status**: Docker 容器状态
- **Deployment**: 部署状态

### 3. 工程活动日志（左侧）

实时显示所有工程活动：
- 📝 代码提交记录（commit SHA, author, branch, message）
- ✅/❌ CI Pipeline 运行结果
- 🐳 Docker 容器事件
- 📦 部署事件

每条记录包含：
- 事件类型和图标
- 时间戳
- 详细信息
- 元数据标签（SHA, author, status 等）

### 4. 状态面板（右侧）

#### 🔨 Current Build Status
- Workflow 名称
- Run ID
- 开始/更新时间
- 成功率
- 最近运行次数

#### 🐳 Docker Container
- Image 名称和标签
- Container 名称
- 运行状态
- 创建时间
- 构建来源 commit
- 端口映射
- **Docker 的作用说明**：
  - Consistency: 环境一致性
  - Isolation: 依赖隔离
  - Portability: 跨平台运行
  - Reproducibility: 可重现构建
  - Efficiency: 高效启动

#### 🚀 Deployment Status
- 环境信息
- 服务名称
- 访问端点
- 健康检查路径
- 部署版本
- 部署时间

### 5. 仓库统计（底部）

- Total Commits: 总提交数
- Contributors: 贡献者数量
- Branches: 分支数量
- Current Branch: 当前分支

## 🔄 自动刷新

Dashboard 每 30 秒自动刷新一次数据，也可以点击右上角的 "Refresh" 按钮手动刷新。

## 🎨 设计特点

### 适合管理层演示
- **Pipeline 流程图在顶部最显眼位置**，一目了然
- **关键指标卡片**快速展示系统健康状况
- **活动日志**展示实时工程活动
- **状态面板**提供详细技术信息
- **深色主题**专业且现代

### 响应式设计
- 大屏幕：2列布局，所有信息一屏展示
- 中等屏幕：自动调整为单列
- 小屏幕：完全响应式，适配移动设备

## 🔧 技术架构

### 前端
- **HTML5**: 语义化结构
- **CSS3**: 现代样式，CSS Grid/Flexbox 布局
- **Vanilla JavaScript**: 无框架依赖，轻量高效

### 后端 API
Dashboard 调用以下 API 端点：

```
GET /api/engineering/git/commits?limit=10
GET /api/engineering/git/stats
GET /api/engineering/cicd/github?repo_owner=xxx&repo_name=xxx
GET /api/engineering/docker/status?container_name=xxx
```

### 数据流
```
Frontend (JS) → Backend API → Git/GitHub/Docker
     ↓
  Render UI
```

## 📈 演示场景

### 场景 1: 展示完整 DevOps 流程
1. 打开 Dashboard
2. 指向顶部 Pipeline 流程图
3. 从左到右讲解每个步骤
4. 展示当前运行状态

### 场景 2: 展示实时活动
1. 查看活动日志
2. 展示最近的 commit
3. 展示 CI 运行结果
4. 展示 Docker 容器状态

### 场景 3: 展示 Docker 价值
1. 打开 Docker Container 卡片
2. 展示容器信息
3. 讲解 Docker 的 5 大优势
4. 展示从哪个 commit 构建

### 场景 4: 展示部署状态
1. 查看 Deployment Status
2. 展示服务端点
3. 展示部署版本
4. 展示健康检查

## 🐛 故障排查

### Dashboard 显示 "Loading..."
- 检查后端服务是否运行：`curl http://localhost:8000/health`
- 检查浏览器控制台是否有错误
- 检查 API 端点是否可访问

### Pipeline 显示全部 "Pending"
- 检查是否有 Git commits
- 检查 GitHub Actions 是否配置
- 检查 Docker 容器是否运行

### 活动日志为空
- 确保有 Git 提交记录
- 确保 GitHub Actions 有运行记录
- 检查 API 返回数据

## 🎯 下一步

1. **实时演示**：进行一次完整的 commit → push → CI → deploy 流程
2. **性能监控**：添加构建时间、测试覆盖率等指标
3. **告警集成**：集成告警通知功能
4. **历史趋势**：添加历史数据图表

## 📞 支持

如有问题，请查看：
- [完整文档](./docs/)
- [演示指南](./DEVOPS_DEMO_GUIDE.md)
- [快速参考](./QUICK_DEMO_STEPS.md)
