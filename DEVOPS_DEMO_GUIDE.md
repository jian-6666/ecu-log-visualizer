# DevOps Demonstration Guide

## 🎯 Overview

This ECU Log Visualizer project has been upgraded to a complete DevOps demonstration system. The engineering dashboard clearly shows the full DevOps pipeline from developer commit to running service.

## 📊 DevOps Pipeline Flow

The dashboard visualizes the following stages:

```
Developer Commit → Git → GitHub → CI/CD Build → Docker Image → Jenkins Test → Running Service
```

Each stage shows:
- ✓ Status indicator (success/failure/warning/pending)
- ⏰ Timestamp (when the stage last updated)

## 🚀 Quick Start

### 1. Push Code to GitHub

```bash
# Configure Git (already done)
git config user.name "Jian Ma"
git config user.email "78182069+jian-6666@users.noreply.github.com"

# Add all files
git add .

# Commit changes
git commit -m "feat: Upgrade to DevOps demonstration system"

# Push to GitHub
git push -u origin main
```

### 2. Start the Application

```bash
# Option A: Run with Python
python run_server.py

# Option B: Run with Docker
docker build -t ecu-log-visualizer:latest .
docker run -d --name ecu-log-visualizer -p 8000:8000 ecu-log-visualizer:latest
```

### 3. Access the Engineering Dashboard

Open your browser to: **http://localhost:8000/engineering-dashboard.html**

## 🔧 DevOps Components

### 1. Git Integration ✅

**Status**: Active
**Location**: Local repository
**Features**:
- Tracks all commits with author and timestamp
- Shows repository statistics (commits, branches, contributors)
- Displays recent commit history

### 2. GitHub Integration ✅

**Status**: Configured
**Repository**: https://github.com/jian-6666/ecu-log-visualizer
**Features**:
- Remote repository hosting
- Triggers CI/CD on every push
- Provides collaboration platform

### 3. GitHub Actions CI/CD ✅

**Status**: Configured
**Workflow File**: `.github/workflows/ci.yml`
**Triggers**: On push to main/master/develop branches
**Steps**:
1. Checkout code
2. Set up Python 3.12
3. Install dependencies
4. Run linter (flake8)
5. Run unit tests
6. Run integration tests
7. Build Docker image
8. Test Docker image

**View Workflow**: https://github.com/jian-6666/ecu-log-visualizer/actions

### 4. Docker Containerization ✅

**Status**: Active
**Dockerfile**: `Dockerfile` (multi-stage build)
**Features**:
- Multi-stage build for optimized image size
- Health check endpoint
- Automatic port mapping (8000:8000)
- Volume mounting for persistent data

**Commands**:
```bash
# Build image
docker build -t ecu-log-visualizer:latest .

# Run container
docker run -d --name ecu-log-visualizer -p 8000:8000 ecu-log-visualizer:latest

# Check status
docker ps

# View logs
docker logs ecu-log-visualizer

# Stop container
docker stop ecu-log-visualizer
```

### 5. Jenkins Simulation ✅

**Status**: Simulated (for demo purposes)
**Script**: `scripts/simulate_jenkins.py`
**Features**:
- Simulates Jenkins build pipeline
- Runs automated tests
- Reports build status

**Run Simulation**:
```bash
python scripts/simulate_jenkins.py
```

**Note**: For production, configure actual Jenkins server:
- Jenkins URL: http://your-jenkins-server:8080
- Job Name: ecu-log-visualizer
- Configure webhook from GitHub to Jenkins

### 6. Automated Testing ✅

**Status**: Active
**Test Suites**:
- Unit tests: `tests/unit/`
- Integration tests: `tests/integration/`
- Property-based tests: `tests/property/`

**Run Tests**:
```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v

# With coverage
pytest tests/ -v --cov=src --cov-report=term-missing
```

## 📈 Dashboard Features

### Pipeline Flow Visualization

The top section shows the complete DevOps pipeline with real-time status:

- **Developer Commit**: Shows latest commit information
- **Git**: Local repository status
- **GitHub**: Remote repository connection
- **CI/CD Build**: GitHub Actions workflow status
- **Docker Image**: Container image status
- **Jenkins Test**: Automated test results
- **Running Service**: Application health status

### Detailed Panels

1. **Git Activity Panel**
   - Recent commits (last 5)
   - Repository statistics
   - Current branch information

2. **CI/CD Pipelines Panel**
   - GitHub Actions status and success rate
   - Jenkins build status and success rate
   - Last run timestamps

3. **Docker Status Panel**
   - Container running status
   - Image information
   - Port mappings
   - Health check status

4. **Test Results Panel**
   - Test execution results
   - Coverage metrics
   - Pass/fail counts

5. **API Health Panel**
   - Service health status
   - Response time monitoring

## 🎬 Demo Workflow

### For Management Presentation

1. **Show the Dashboard**
   - Open http://localhost:8000/engineering-dashboard.html
   - Point out the pipeline flow at the top
   - Explain each stage

2. **Make a Code Change**
   ```bash
   echo "# Demo change - $(date)" >> README.md
   git add README.md
   git commit -m "demo: Update README"
   git push origin main
   ```

3. **Watch the Pipeline**
   - Refresh the dashboard
   - Show the new commit appearing in Git Activity
   - Show GitHub Actions triggering (if configured)
   - Show the pipeline flow updating

4. **Explain the Value**
   - **Visibility**: Everyone can see the project status
   - **Automation**: No manual steps required
   - **Quality**: Tests run automatically on every change
   - **Speed**: From commit to deployment in minutes
   - **Reliability**: Consistent process every time

### For Technical Audience

1. **Show the Code**
   - Dockerfile for containerization
   - `.github/workflows/ci.yml` for CI/CD
   - `src/git_integration.py` for Git monitoring
   - `src/cicd_status.py` for pipeline monitoring

2. **Run Tests**
   ```bash
   pytest tests/ -v --cov=src
   ```

3. **Build Docker Image**
   ```bash
   docker build -t ecu-log-visualizer:latest .
   ```

4. **Deploy Container**
   ```bash
   docker run -d --name ecu-log-visualizer -p 8000:8000 ecu-log-visualizer:latest
   ```

5. **Simulate Jenkins**
   ```bash
   python scripts/simulate_jenkins.py
   ```

## 🔍 Monitoring and Troubleshooting

### Check Git Status
```bash
git status
git log --oneline -5
```

### Check GitHub Actions
Visit: https://github.com/jian-6666/ecu-log-visualizer/actions

### Check Docker Status
```bash
docker ps
docker logs ecu-log-visualizer
docker inspect ecu-log-visualizer
```

### Check Application Health
```bash
curl http://localhost:8000/health
```

### Check Dashboard API
```bash
curl "http://localhost:8000/api/engineering/dashboard?repo_owner=jian-6666&repo_name=ecu-log-visualizer"
```

## 📝 Configuration

### GitHub Repository
- **Owner**: jian-6666
- **Repository**: ecu-log-visualizer
- **URL**: https://github.com/jian-6666/ecu-log-visualizer

### Dashboard Configuration
Edit `frontend/engineering-dashboard.js`:
```javascript
const CONFIG = {
    API_BASE_URL: window.location.origin,
    REFRESH_INTERVAL: 30000, // 30 seconds
    REPO_OWNER: 'jian-6666',
    REPO_NAME: 'ecu-log-visualizer',
};
```

### Jenkins Configuration (Optional)
For actual Jenkins integration:
1. Install Jenkins
2. Create job named "ecu-log-visualizer"
3. Configure GitHub webhook
4. Update dashboard API call with Jenkins URL

## 🎯 Success Criteria

✅ Git repository initialized and connected to GitHub
✅ GitHub Actions CI/CD pipeline configured
✅ Docker containerization working
✅ Jenkins simulation available
✅ Engineering dashboard shows complete pipeline
✅ All stages display status and timestamp
✅ Dashboard auto-refreshes every 30 seconds
✅ Management can clearly see DevOps workflow

## 📚 Additional Resources

- **System Manual**: `docs/system_manual.md`
- **Demo Script**: `docs/detailed-demo-script.md`
- **Demo Checklist**: `docs/demo-checklist.md`
- **GitHub Setup**: `docs/github-setup.md`
- **Engineering Toolchain**: `docs/engineering-toolchain.md`

## 🤝 Support

For questions or issues:
1. Check the documentation in `docs/`
2. Review GitHub Issues
3. Contact the development team

---

**Version**: 2.0 (DevOps Demo)
**Last Updated**: 2026-03-06
**Maintainer**: Jian Ma
