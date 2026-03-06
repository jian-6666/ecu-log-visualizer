# 快速参考卡片

## 🚀 常用命令

```bash
# 设置环境
./scripts/dev.sh

# 运行测试
./scripts/test.sh

# 构建 Docker
./scripts/build.sh

# 部署应用
./scripts/deploy.sh

# 启动服务器（不用 Docker）
python run_server.py

# 查看容器状态
docker ps

# 查看容器日志
docker logs ecu-log-visualizer

# 停止容器
docker stop ecu-log-visualizer

# 重启容器
docker restart ecu-log-visualizer
```

## 🌐 重要 URL

| 功能 | URL |
|------|-----|
| 主应用 | http://localhost:8000 |
| 工程仪表板 | http://localhost:8000/engineering-dashboard.html |
| API 文档 | http://localhost:8000/docs |
| 健康检查 | http://localhost:8000/health |

## 📁 关键文件位置

| 文件 | 位置 | 作用 |
|------|------|------|
| API 入口 | `src/main.py` | 定义所有 API 端点 |
| 数据模型 | `src/models.py` | 数据结构定义 |
| Git 集成 | `src/git_integration.py` | Git 功能 |
| CI/CD 监控 | `src/cicd_status.py` | CI/CD 状态 |
| Docker 监控 | `src/docker_status.py` | Docker 状态 |
| 主界面 | `frontend/index.html` | 用户界面 |
| 仪表板 | `frontend/engineering-dashboard.html` | 工程仪表板 |
| Docker 配置 | `Dockerfile` | 容器构建 |
| CI 配置 | `.github/workflows/ci.yml` | GitHub Actions |
| Jenkins 配置 | `Jenkinsfile` | Jenkins 流水线 |

## 🎯 演示流程（15 分钟）

| 时间 | 步骤 | 命令/操作 | 讲解要点 |
|------|------|-----------|----------|
| 0-2分钟 | 介绍和设置 | `./scripts/dev.sh` | 自动化设置 |
| 2-5分钟 | 运行测试 | `./scripts/test.sh` | 质量保证 |
| 5-8分钟 | 容器化 | `./scripts/build.sh`<br>`./scripts/deploy.sh` | 一致性部署 |
| 8-13分钟 | 工程仪表板 | 打开浏览器 | 实时监控 |
| 13-14分钟 | 完整流程 | 提交代码改动 | 自动化流程 |
| 14-15分钟 | 总结和Q&A | - | 回答问题 |

## 💬 关键讲解点

### 设置阶段
> "这个自动化脚本确保团队成员都有相同的开发环境，减少'在我机器上能跑'的问题。"

### 测试阶段
> "我们有三种测试：单元测试验证单个功能，集成测试验证模块协作，属性测试验证通用规则。这些测试在每次提交时自动运行。"

### 容器化阶段
> "Docker 容器化确保应用在任何环境都能一致运行。多阶段构建优化了镜像大小，健康检查确保服务可用性。"

### 仪表板阶段
> "这个工程仪表板提供实时可见性，让技术和非技术人员都能理解开发进度。颜色编码让状态一目了然。"

### 完整流程阶段
> "现在我提交一个改动。在实际环境中，这会自动触发 CI 流水线，运行所有测试，构建 Docker 镜像。整个过程完全自动化。"

## 🎨 仪表板面板说明

| 面板 | 显示内容 | 价值 |
|------|----------|------|
| Git Activity | 提交历史、仓库统计 | 追踪代码变更 |
| CI/CD Status | GitHub Actions、Jenkins 状态 | 自动化质量检查 |
| Docker Status | 容器状态、镜像信息 | 部署状态监控 |
| Test Results | 测试结果、覆盖率 | 代码质量指标 |
| API Health | 服务健康状态 | 可用性监控 |

## ❓ 常见问题快速回答

**Q: 这个系统的主要优势是什么？**
> A: 三个关键词：自动化（减少人工错误）、可视化（提高透明度）、标准化（确保一致性）。

**Q: 部署到生产环境需要什么？**
> A: Docker 环境、配置 GitHub/Jenkins、设置环境变量。详细步骤在 docs/github-setup.md。

**Q: 如何添加新功能？**
> A: 标准流程：创建分支 → 开发 → 测试 → 提交 → CI 验证 → 代码审查 → 合并。

**Q: 出问题怎么办？**
> A: 工程仪表板会立即显示问题。可以查看日志定位原因，必要时回滚到之前的版本。

**Q: 这个工具链适合小团队吗？**
> A: 非常适合！自动化减少了重复工作，即使是小团队也能保持高质量标准。

**Q: 学习成本高吗？**
> A: 我们提供了完整的文档和自动化脚本。新成员只需运行 ./scripts/dev.sh 就能开始工作。

**Q: 可以集成其他工具吗？**
> A: 可以！系统设计是模块化的，可以轻松添加新的监控模块或 CI/CD 工具。

## 🚨 故障排除速查

| 问题 | 快速解决 |
|------|----------|
| 脚本无法执行 | `chmod +x scripts/*.sh` |
| Docker 无法连接 | 启动 Docker Desktop |
| 端口被占用 | `lsof -i :8000` 查找并杀死进程 |
| 测试失败 | `pip install -r requirements.txt` |
| 仪表板错误 | 检查 Git/Docker 是否可用 |

## 📊 系统架构速览

```
用户界面 (浏览器)
    ↓
FastAPI 服务器 (Docker 容器)
    ↓
核心模块 + 工程模块
    ↓
外部工具 (Git, Docker, GitHub, Jenkins)
```

## 🔑 关键技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.12, FastAPI, Uvicorn |
| 前端 | HTML5, JavaScript ES6+, CSS3 |
| 数据处理 | Pandas, Plotly |
| 测试 | pytest, hypothesis |
| 容器化 | Docker |
| CI/CD | GitHub Actions, Jenkins |
| 版本控制 | Git, GitHub |

## 📈 性能指标

| 指标 | 目标 | 实际 |
|------|------|------|
| 仪表板加载 | < 2秒 | ✅ |
| Docker 构建 | < 5分钟 | ✅ |
| 测试执行 | < 2分钟 | ✅ |
| API 响应 | < 1秒 | ✅ |
| 代码覆盖率 | > 80% | ✅ |

## 🎓 学习资源

| 资源 | 位置 | 用途 |
|------|------|------|
| 学习指南 | `docs/learning-guide.md` | 系统学习 |
| 可视化指南 | `docs/visual-guide.md` | 图形化理解 |
| 演示流程 | `docs/demo.md` | 完整演示 |
| 检查清单 | `docs/demo-checklist.md` | 演示准备 |
| 架构文档 | `docs/engineering-toolchain.md` | 深入理解 |
| 维护指南 | `docs/maintenance.md` | 日常维护 |

## 🎯 演示成功标准

- ✅ 15 分钟内完成
- ✅ 展示所有关键功能
- ✅ 观众理解系统价值
- ✅ 回答至少 3 个问题
- ✅ 收到正面反馈

## 💡 演示技巧

1. **保持节奏**：不要在某个步骤停留太久
2. **讲故事**：用实际场景说明价值
3. **互动**：适时询问观众是否有问题
4. **自信**：即使出错也保持冷静
5. **准备**：提前演练至少 2 次

## 📞 紧急联系

如果演示中遇到无法解决的问题：
1. 保持冷静，向观众说明情况
2. 使用备份方案（截图、视频）
3. 承诺会后跟进
4. 继续其他部分的演示

---

**打印这张卡片，演示时放在手边！** 📄

**文档版本：** 1.0  
**最后更新：** 2024  
**维护者：** ECU Log Visualizer Team
