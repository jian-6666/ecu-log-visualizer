# 🚀 开始使用 ECU Log Visualizer

## 👋 欢迎！

这是 **ECU Log Visualizer** - 一个完整的 DevOps 演示系统，包含数据分析功能和工程工具链可视化。

---

## 📚 文档导航

根据你的需求，选择合适的文档：

### 🎯 快速开始

**如果你想立即开始使用：**
- 📖 **[简易操作指南.md](简易操作指南.md)** - 中文完整操作指南
- 📖 **[SIMPLE_OPERATION_GUIDE.md](SIMPLE_OPERATION_GUIDE.md)** - English Complete Guide

这两个文档包含：
- ✅ 详细的安装步骤
- ✅ 启动应用的方法
- ✅ 使用主应用的说明
- ✅ 工程仪表板介绍
- ✅ 完整的 Demo 演示脚本
- ✅ 常见问题解决方法

---

### 🎬 Demo 演示

**如果你要做演示：**
- 🎯 **[QUICK_DEMO_STEPS.md](QUICK_DEMO_STEPS.md)** - 5 分钟快速演示步骤
- 📋 **[DEMO-READY-CHECKLIST.md](DEMO-READY-CHECKLIST.md)** - 演示前检查清单
- 📝 **[docs/detailed-demo-script.md](docs/detailed-demo-script.md)** - 详细演示脚本（逐字稿）

---

### 🔧 DevOps 系统

**如果你想了解 DevOps 功能：**
- 🚀 **[DEVOPS_DEMO_GUIDE.md](DEVOPS_DEMO_GUIDE.md)** - 完整的 DevOps 系统指南
- 📊 **[DEVOPS_UPGRADE_SUMMARY.md](DEVOPS_UPGRADE_SUMMARY.md)** - DevOps 升级总结

---

### 📖 详细文档

**如果你需要深入了解：**
- 📘 **[docs/system_manual.md](docs/system_manual.md)** - 系统手册
- 🔍 **[docs/quick-reference.md](docs/quick-reference.md)** - 快速参考
- 🎓 **[docs/learning-guide.md](docs/learning-guide.md)** - 学习指南
- 🛠️ **[docs/engineering-toolchain.md](docs/engineering-toolchain.md)** - 工程工具链详解

---

## ⚡ 3 分钟快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动服务器
```bash
python run_server.py
```

### 3. 打开浏览器
- **主应用**：http://localhost:8000
- **工程仪表板**：http://localhost:8000/engineering-dashboard.html

就这么简单！🎉

---

## 🎯 核心功能

### 1. ECU 日志分析
- 📊 上传 CSV/JSON 格式的 ECU 日志
- 📈 自动生成统计分析
- 🎨 交互式时间序列图表
- 🔍 强大的过滤功能
- 💾 导出分析结果

### 2. DevOps 工程仪表板
- 🔄 完整的 DevOps 流程可视化
- 📊 Git 活动监控
- 🐙 GitHub Actions CI/CD 状态
- 🐳 Docker 容器状态
- 🔧 Jenkins 测试状态
- 🚀 服务健康监控

---

## 🌟 DevOps 流程图

```
👨‍💻 Developer Commit
    ↓
📊 Git (本地版本控制)
    ↓
🐙 GitHub (远程仓库)
    ↓
🔄 CI/CD Build (自动化测试)
    ↓
🐳 Docker Image (容器化)
    ↓
🔧 Jenkins Test (自动化测试)
    ↓
🚀 Running Service (运行服务)
```

每个阶段都有：
- ✓ 状态指示器（成功/失败/警告/待处理）
- ⏰ 时间戳（最后更新时间）
- 🎨 颜色编码（绿色/红色/黄色/灰色）

---

## 🔗 重要链接

### 本地应用
- **主应用**：http://localhost:8000
- **工程仪表板**：http://localhost:8000/engineering-dashboard.html
- **API 文档**：http://localhost:8000/docs
- **健康检查**：http://localhost:8000/health

### GitHub
- **仓库**：https://github.com/jian-6666/ecu-log-visualizer
- **GitHub Actions**：https://github.com/jian-6666/ecu-log-visualizer/actions
- **Issues**：https://github.com/jian-6666/ecu-log-visualizer/issues

---

## 📦 项目结构

```
ecu-log-visualizer/
├── src/                    # 后端源代码
│   ├── main.py            # FastAPI 应用
│   ├── data_analyzer.py   # 数据分析
│   ├── git_integration.py # Git 集成
│   ├── cicd_status.py     # CI/CD 监控
│   └── docker_status.py   # Docker 监控
├── frontend/              # 前端文件
│   ├── index.html         # 主应用界面
│   ├── engineering-dashboard.html  # 工程仪表板
│   └── *.js, *.css        # JavaScript 和样式
├── tests/                 # 测试文件
│   ├── unit/             # 单元测试
│   ├── integration/      # 集成测试
│   └── property/         # 属性测试
├── docs/                  # 文档
├── examples/              # 示例数据
├── scripts/               # 自动化脚本
├── .github/workflows/     # GitHub Actions
├── Dockerfile            # Docker 配置
├── Jenkinsfile           # Jenkins 配置
└── requirements.txt      # Python 依赖
```

---

## 🎓 学习路径

### 初学者
1. 阅读 **[简易操作指南.md](简易操作指南.md)**
2. 启动应用并上传示例文件
3. 浏览工程仪表板
4. 尝试过滤和导出功能

### 演示者
1. 阅读 **[QUICK_DEMO_STEPS.md](QUICK_DEMO_STEPS.md)**
2. 查看 **[DEMO-READY-CHECKLIST.md](DEMO-READY-CHECKLIST.md)**
3. 练习演示流程
4. 准备回答常见问题

### 开发者
1. 阅读 **[DEVOPS_DEMO_GUIDE.md](DEVOPS_DEMO_GUIDE.md)**
2. 了解 **[docs/engineering-toolchain.md](docs/engineering-toolchain.md)**
3. 查看源代码和测试
4. 尝试修改和扩展功能

---

## 🆘 需要帮助？

### 常见问题
查看文档中的"常见问题"部分：
- [简易操作指南.md - 常见问题](简易操作指南.md#常见问题)
- [SIMPLE_OPERATION_GUIDE.md - Troubleshooting](SIMPLE_OPERATION_GUIDE.md#troubleshooting)

### 获取支持
1. **查看文档** - 大多数问题都有文档说明
2. **检查日志** - 服务器日志和浏览器控制台
3. **GitHub Issues** - 搜索或创建新问题
4. **联系团队** - 通过 GitHub 联系维护者

---

## 🎯 快速命令

### 启动和停止
```bash
# 启动服务器
python run_server.py

# 停止服务器（在运行窗口按 Ctrl+C）

# 使用 Docker
docker build -t ecu-log-visualizer:latest .
docker run -d --name ecu-log-visualizer -p 8000:8000 ecu-log-visualizer:latest
docker stop ecu-log-visualizer
```

### 测试
```bash
# 运行所有测试
pytest tests/ -v

# 运行测试并查看覆盖率
pytest tests/ -v --cov=src --cov-report=term-missing
```

### Git 操作
```bash
# 查看状态
git status

# 提交改动
git add .
git commit -m "你的提交信息"
git push origin main
```

---

## ✨ 特色功能

### 🎨 交互式可视化
- 缩放、平移、悬停查看数据
- 实时图表更新
- 多传感器同时显示

### 🔄 自动化 CI/CD
- 每次推送自动运行测试
- 自动构建 Docker 镜像
- 自动部署流程

### 📊 实时监控
- 30 秒自动刷新
- 完整的 DevOps 流程可见性
- 状态指示器和时间戳

### 🐳 容器化部署
- Docker 多阶段构建
- 健康检查
- 一致的部署环境

---

## 🏆 成功标准

使用这个系统，你应该能够：

✅ 在 5 分钟内启动应用
✅ 上传和分析 ECU 日志数据
✅ 查看完整的 DevOps 流程
✅ 进行 15 分钟的专业演示
✅ 理解现代 DevOps 实践
✅ 自动化测试和部署

---

## 📝 版本信息

- **版本**：2.0 (DevOps Demo)
- **最后更新**：2026-03-06
- **维护者**：Jian Ma
- **GitHub**：https://github.com/jian-6666/ecu-log-visualizer
- **许可证**：MIT

---

## 🙏 致谢

感谢使用 ECU Log Visualizer！

如果这个项目对你有帮助，请：
- ⭐ 在 GitHub 上给项目加星
- 🐛 报告问题和建议
- 🤝 贡献代码和文档
- 📢 分享给其他人

---

## 🚀 下一步

现在你已经了解了基本信息，选择一个文档开始：

1. **想立即使用？** → [简易操作指南.md](简易操作指南.md)
2. **要做演示？** → [QUICK_DEMO_STEPS.md](QUICK_DEMO_STEPS.md)
3. **想深入了解？** → [DEVOPS_DEMO_GUIDE.md](DEVOPS_DEMO_GUIDE.md)

**祝你使用愉快！** 🎉

---

**记住**：如果遇到问题，先查看文档，大多数问题都有解决方案！

