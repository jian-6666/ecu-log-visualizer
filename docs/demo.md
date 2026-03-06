# ECU Log Visualizer - Engineering Toolchain Demo

## Overview

This document provides a complete demonstration workflow for the ECU Log Visualizer engineering toolchain. The demo showcases modern software engineering practices including version control, continuous integration, containerization, and automated deployment.

**Time Required:** 15 minutes  
**Audience:** Technical and non-technical stakeholders  
**Prerequisites:** Docker installed, Git installed, Python 3.12+

## Demo Workflow

### Phase 1: Setup and Initialization (3 minutes)

#### Step 1.1: Clone the Repository
```bash
git clone <repository-url>
cd ecu-log-visualizer
```

**Expected Outcome:** Repository cloned successfully

#### Step 1.2: Run Development Setup
```bash
./scripts/dev.sh
```

**Expected Outcome:**
- Python dependencies installed
- Necessary directories created
- Git repository initialized (if needed)
- Setup completion message displayed

**Talking Points:**
- Automated setup reduces onboarding time
- Script handles all environment configuration
- Consistent development environment across team

### Phase 2: Local Development and Testing (4 minutes)

#### Step 2.1: Run Automated Tests
```bash
./scripts/test.sh
```

**Expected Outcome:**
- All tests pass
- Coverage report generated
- Test summary displayed

**Talking Points:**
- Comprehensive test suite ensures code quality
- Property-based testing validates universal correctness
- Coverage metrics track test completeness

#### Step 2.2: Start the Application Locally
```bash
python run_server.py
```

**Expected Outcome:**
- Server starts on http://localhost:8000
- Application accessible in browser
- Health check endpoint responds

**Talking Points:**
- Fast local development iteration
- Immediate feedback on changes
- Health monitoring built-in

### Phase 3: Containerization (3 minutes)

#### Step 3.1: Build Docker Image
```bash
./scripts/build.sh
```

**Expected Outcome:**
- Multi-stage Docker build completes
- Image tagged with timestamp and 'latest'
- Build completes within 5 minutes
- Image size optimized through multi-stage build

**Talking Points:**
- Docker ensures consistent deployment environments
- Multi-stage builds minimize image size
- Automated tagging for version tracking

#### Step 3.2: Deploy Container
```bash
./scripts/deploy.sh
```

**Expected Outcome:**
- Existing container stopped (if running)
- New container started successfully
- Application accessible at http://localhost:8000
- Container health check passes

**Talking Points:**
- Zero-downtime deployment strategy
- Health checks ensure service availability
- Volume mounting preserves uploaded data

### Phase 4: Engineering Dashboard (3 minutes)

#### Step 4.1: Access Engineering Dashboard
Open browser to: http://localhost:8000/engineering-dashboard.html

**Expected Outcome:**
- Dashboard loads within 2 seconds
- All panels display status information
- Auto-refresh every 30 seconds

**Talking Points:**
- Real-time visibility into engineering workflow
- Accessible to non-technical stakeholders
- Color-coded status indicators for quick assessment

#### Step 4.2: Explore Dashboard Sections

**Git Activity Panel:**
- Shows recent commits
- Displays repository statistics
- Tracks contributor activity

**CI/CD Status Panel:**
- GitHub Actions workflow status
- Jenkins pipeline status
- Success rate metrics

**Docker Status Panel:**
- Container running status
- Image information
- Port mappings and health

**Test Results Panel:**
- Test execution results
- Pass/fail counts
- Coverage metrics

**API Health Panel:**
- Service health status
- Response time monitoring

**Talking Points:**
- Comprehensive view of engineering process
- Identifies bottlenecks quickly
- Facilitates stakeholder communication

### Phase 5: Continuous Integration (2 minutes)

#### Step 5.1: Make a Code Change
```bash
# Edit a file (e.g., add a comment to README.md)
echo "# Demo change" >> README.md

# Commit the change
git add README.md
git commit -m "Demo: Add comment to README"
```

**Expected Outcome:**
- Commit created successfully
- Commit appears in Git history

#### Step 5.2: Push to GitHub (if configured)
```bash
git push origin main
```

**Expected Outcome:**
- Code pushed to GitHub
- GitHub Actions CI pipeline triggers automatically
- Pipeline runs tests, linting, and build verification

**Talking Points:**
- Automated CI on every commit
- Catches issues before they reach production
- Consistent quality gates

#### Step 5.3: Monitor CI Pipeline
- View GitHub Actions tab in repository
- Watch pipeline execution in real-time
- Check Engineering Dashboard for updated status

**Expected Outcome:**
- Pipeline completes successfully
- Dashboard reflects latest status
- Build artifacts created

## Demo Script for Presenters

### Introduction (1 minute)
"Today I'll demonstrate our modern engineering toolchain for the ECU Log Visualizer. This system showcases industry best practices including automated testing, continuous integration, containerization, and real-time monitoring."

### Setup (1 minute)
"First, let's set up the development environment with a single command. Our automated setup script handles all dependencies and configuration."

[Run `./scripts/dev.sh`]

### Testing (2 minutes)
"Quality is paramount. Let's run our comprehensive test suite, which includes unit tests, integration tests, and property-based tests that validate correctness across all inputs."

[Run `./scripts/test.sh`]

"Notice the coverage report - we maintain high test coverage to ensure reliability."

### Containerization (3 minutes)
"Modern applications need consistent deployment environments. Let's build a Docker image using our multi-stage Dockerfile, which optimizes image size while including all dependencies."

[Run `./scripts/build.sh`]

"Now let's deploy the containerized application."

[Run `./scripts/deploy.sh`]

"The application is now running in a container with health monitoring."

### Engineering Dashboard (4 minutes)
"The Engineering Dashboard provides real-time visibility into our entire workflow. Let's explore each section."

[Open dashboard in browser]

"The Git Activity panel shows recent commits and repository statistics. The CI/CD Status panel displays pipeline health from both GitHub Actions and Jenkins. The Docker Status panel confirms our container is running healthy. Test Results show our quality metrics, and API Health monitors service availability."

"This dashboard is designed for both technical and non-technical stakeholders - notice the color-coded indicators and clear status messages."

### Continuous Integration (3 minutes)
"Let's see the CI pipeline in action. I'll make a small change and commit it."

[Make change, commit, push]

"The commit automatically triggers our CI pipeline, which runs all tests, performs linting, and verifies the build. You can watch the progress in GitHub Actions or on our Engineering Dashboard."

### Conclusion (1 minute)
"This toolchain demonstrates modern software engineering practices: automated testing ensures quality, containerization ensures consistency, continuous integration catches issues early, and the Engineering Dashboard provides transparency. The entire workflow is automated, repeatable, and accessible to all stakeholders."

## Troubleshooting

### Issue: Docker daemon not running
**Solution:** Start Docker Desktop or Docker service
```bash
# Linux
sudo systemctl start docker

# macOS/Windows
# Start Docker Desktop application
```

### Issue: Port 8000 already in use
**Solution:** Stop existing process or use different port
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or change port in run_server.py
```

### Issue: Permission denied on scripts
**Solution:** Make scripts executable
```bash
chmod +x scripts/*.sh
```

### Issue: Tests failing
**Solution:** Ensure all dependencies installed
```bash
pip install -r requirements.txt
```

### Issue: Dashboard not loading
**Solution:** Verify server is running and frontend files exist
```bash
# Check server status
curl http://localhost:8000/health

# Verify frontend files
ls frontend/engineering-dashboard.*
```

## Success Criteria

✅ Setup completes without errors  
✅ All tests pass  
✅ Docker image builds within 5 minutes  
✅ Container deploys successfully  
✅ Dashboard loads within 2 seconds  
✅ All dashboard panels show data  
✅ CI pipeline triggers on commit  
✅ Demo completes within 15 minutes  

## Next Steps

After the demo:
1. Review [maintenance.md](maintenance.md) for ongoing operations
2. Check [github-setup.md](github-setup.md) for GitHub integration
3. Explore [engineering-toolchain.md](engineering-toolchain.md) for architecture details
4. Read [system_manual.md](system_manual.md) for application usage

## Feedback and Questions

For questions or feedback about the demo:
- Review documentation in `docs/` directory
- Check GitHub Issues for known problems
- Contact the development team

---

**Document Version:** 1.0  
**Last Updated:** 2024  
**Maintainer:** ECU Log Visualizer Team
