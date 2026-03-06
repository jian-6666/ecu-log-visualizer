# Engineering Toolchain Architecture

## Overview

The ECU Log Visualizer engineering toolchain demonstrates modern software engineering practices through an integrated system of version control, continuous integration, containerization, and real-time monitoring. This document describes the architecture, component interactions, and data flow.

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Developer                                │
└────────────┬────────────────────────────────────────────────────┘
             │
             ├─── Code Changes
             │
┌────────────▼────────────────────────────────────────────────────┐
│                      Git Repository                              │
│  - Version Control                                               │
│  - Commit History                                                │
│  - Branch Management                                             │
└────────────┬────────────────────────────────────────────────────┘
             │
             ├─── Push to GitHub
             │
┌────────────▼────────────────────────────────────────────────────┐
│                    GitHub Remote                                 │
│  - Remote Repository                                             │
│  - Collaboration                                                 │
│  - Webhook Triggers                                              │
└────────┬───────────────────────────────────────┬────────────────┘
         │                                       │
         │ Trigger                               │ Trigger
         │                                       │
┌────────▼──────────────┐            ┌──────────▼─────────────────┐
│  GitHub Actions CI    │            │   Jenkins Pipeline         │
│  - Automated Testing  │            │   - Automated Testing      │
│  - Code Linting       │            │   - Code Linting           │
│  - Build Verification │            │   - Build Verification     │
│  - Docker Build       │            │   - Docker Build           │
└────────┬──────────────┘            └──────────┬─────────────────┘
         │                                       │
         └───────────────┬───────────────────────┘
                         │
                         │ Build Artifacts
                         │
                ┌────────▼────────────┐
                │   Docker Image      │
                │   - Multi-stage     │
                │   - Optimized       │
                │   - Tagged          │
                └────────┬────────────┘
                         │
                         │ Deploy
                         │
                ┌────────▼────────────┐
                │  Docker Container   │
                │  - Running App      │
                │  - Health Checks    │
                │  - Port Mapping     │
                └────────┬────────────┘
                         │
                         │ Serves
                         │
        ┌────────────────┴────────────────┐
        │                                  │
┌───────▼──────────┐          ┌───────────▼──────────┐
│  FastAPI App     │          │  Engineering         │
│  - REST API      │◄─────────┤  Dashboard           │
│  - File Upload   │  Queries │  - Real-time Status  │
│  - Data Analysis │          │  - Visualization     │
└──────────────────┘          └──────────────────────┘
```

## Core Components

### 1. Version Control Layer

**Technology:** Git + GitHub

**Purpose:** Track code changes, enable collaboration, maintain history

**Key Features:**
- Local Git repository for version control
- GitHub remote for collaboration and backup
- Commit history tracking
- Branch management
- Contributor tracking

**Implementation:**
- `src/git_integration.py` - Python interface to Git commands
- Uses subprocess to execute Git CLI commands
- Parses Git output for commit history and statistics

**Data Models:**
```python
CommitInfo:
  - hash: Full commit hash
  - short_hash: Abbreviated hash
  - author: Commit author name
  - email: Author email
  - timestamp: Commit timestamp
  - message: Commit message
  - branch: Branch name

RepositoryStats:
  - total_commits: Total number of commits
  - branches: List of branch names
  - current_branch: Active branch
  - remote_url: GitHub repository URL
  - contributors: Number of unique contributors
```

### 2. Continuous Integration Layer

**Technologies:** GitHub Actions + Jenkins

**Purpose:** Automated testing, linting, and build verification on every commit

#### GitHub Actions Pipeline

**Configuration:** `.github/workflows/ci.yml`

**Stages:**
1. **Checkout** - Clone repository code
2. **Setup Python** - Install Python 3.12
3. **Install Dependencies** - Install from requirements.txt
4. **Lint** - Run flake8 for code quality
5. **Test** - Execute pytest with coverage
6. **Build Verification** - Verify application imports
7. **Docker Build** - Build Docker image (main branch only)

**Triggers:**
- Push to any branch
- Pull request to main/master
- Manual workflow dispatch

#### Jenkins Pipeline

**Configuration:** `Jenkinsfile`

**Stages:**
1. **Checkout** - Retrieve source code
2. **Dependencies** - Install Python packages
3. **Lint** - Run code quality checks
4. **Test** - Execute automated tests with JUnit XML output
5. **Build** - Create Docker image with build number tag

**Post Actions:**
- Archive test results
- Generate build artifacts

**Implementation:**
- `src/cicd_status.py` - Monitors CI/CD pipeline status
- GitHub Actions: Uses GitHub REST API v3
- Jenkins: Uses Jenkins REST API
- Caching with 30-second TTL to avoid rate limiting

**Data Models:**
```python
WorkflowRun (GitHub Actions):
  - id: Workflow run ID
  - name: Workflow name
  - status: queued, in_progress, completed
  - conclusion: success, failure, cancelled
  - created_at: Creation timestamp
  - updated_at: Last update timestamp
  - html_url: GitHub URL

BuildInfo (Jenkins):
  - number: Build number
  - status: SUCCESS, FAILURE, UNSTABLE, ABORTED, IN_PROGRESS
  - timestamp: Build timestamp
  - duration: Build duration (milliseconds)
  - url: Jenkins build URL
```

### 3. Containerization Layer

**Technology:** Docker

**Purpose:** Consistent deployment environments, isolation, portability

#### Multi-Stage Dockerfile

**Stage 1: Builder**
- Base: `python:3.12-slim`
- Install dependencies to user directory
- Minimize build context

**Stage 2: Runtime**
- Base: `python:3.12-slim`
- Copy Python packages from builder
- Copy application code
- Create uploads directory
- Expose port 8000
- Configure health check
- Set startup command

**Benefits:**
- Reduced image size (only runtime dependencies)
- Faster builds (cached layers)
- Security (minimal attack surface)

**Configuration Files:**
- `Dockerfile` - Multi-stage build definition
- `.dockerignore` - Exclude unnecessary files from build context

**Implementation:**
- `src/docker_status.py` - Monitors Docker container status
- Uses subprocess to execute Docker CLI commands
- Parses JSON output from `docker inspect` and `docker ps`

**Data Models:**
```python
ContainerStatus:
  - name: Container name
  - status: running, stopped, paused, restarting, error
  - image: Image name
  - created: Creation timestamp
  - ports: Port mappings (dict)
  - health: healthy, unhealthy, starting

ImageInfo:
  - id: Image ID
  - tags: List of image tags
  - created: Creation timestamp
  - size: Image size (bytes)
```

### 4. Automation Layer

**Technology:** Bash scripts

**Purpose:** Simplify common development tasks, ensure consistency

**Scripts:**

#### `scripts/dev.sh` - Development Setup
- Checks Python installation
- Installs dependencies from requirements.txt
- Creates necessary directories
- Initializes Git repository if needed
- Displays setup completion status

#### `scripts/test.sh` - Test Execution
- Runs pytest with coverage
- Generates coverage reports (terminal and HTML)
- Displays test results summary
- Exits with appropriate status code

#### `scripts/build.sh` - Docker Build
- Checks Docker availability
- Builds Docker image with timestamp tag
- Tags image as 'latest'
- Verifies image creation
- Displays build status

#### `scripts/deploy.sh` - Application Deployment
- Checks Docker availability
- Stops existing container if running
- Starts new container from latest image
- Mounts uploads directory
- Verifies container health
- Displays access URL

### 5. Visualization Layer

**Technology:** HTML5 + JavaScript + CSS3

**Purpose:** Real-time visibility into engineering workflow for all stakeholders

#### Engineering Dashboard

**Components:**

**Frontend Files:**
- `frontend/engineering-dashboard.html` - Dashboard structure
- `frontend/engineering-dashboard.js` - Data fetching and rendering
- `frontend/engineering-dashboard.css` - Styling and layout

**Dashboard Panels:**

1. **Git Activity Panel**
   - Recent commits (last 5)
   - Repository statistics
   - Contributor count
   - Current branch

2. **CI/CD Status Panel**
   - GitHub Actions workflow status
   - Jenkins pipeline status
   - Success rate metrics
   - Latest run information

3. **Docker Status Panel**
   - Container running status
   - Image information
   - Port mappings
   - Health check status

4. **Test Results Panel**
   - Test execution results
   - Pass/fail counts
   - Coverage metrics

5. **API Health Panel**
   - Service health status
   - Response time monitoring

**Features:**
- Auto-refresh every 30 seconds
- Manual refresh button
- Color-coded status indicators
- Responsive design
- Error handling and display

**API Endpoints:**
```
GET /api/engineering/git/commits - Recent commit history
GET /api/engineering/git/stats - Repository statistics
GET /api/engineering/cicd/github - GitHub Actions status
GET /api/engineering/cicd/jenkins - Jenkins pipeline status
GET /api/engineering/docker/status - Docker container status
GET /api/engineering/dashboard - Aggregated dashboard data
```

## Data Flow

### Commit to Deployment Flow

```
1. Developer makes code changes
   ↓
2. Developer commits changes to Git
   ↓
3. Developer pushes to GitHub
   ↓
4. GitHub triggers CI pipelines
   ├─→ GitHub Actions workflow starts
   └─→ Jenkins pipeline starts (via webhook)
   ↓
5. CI pipelines execute
   ├─→ Install dependencies
   ├─→ Run linting
   ├─→ Execute tests
   └─→ Build Docker image
   ↓
6. Docker image created and tagged
   ↓
7. Image deployed to container
   ↓
8. Application serves requests
   ↓
9. Dashboard displays status
```

### Dashboard Data Flow

```
1. User opens Engineering Dashboard
   ↓
2. JavaScript fetches data from API
   ├─→ GET /api/engineering/dashboard
   ↓
3. API aggregates data from sources
   ├─→ Git integration module
   ├─→ GitHub Actions monitor
   ├─→ Jenkins monitor
   └─→ Docker monitor
   ↓
4. Data returned to frontend
   ↓
5. JavaScript renders panels
   ├─→ Git Activity
   ├─→ CI/CD Status
   ├─→ Docker Status
   ├─→ Test Results
   └─→ API Health
   ↓
6. Auto-refresh after 30 seconds
```

## Component Interactions

### Git Integration ↔ Dashboard
- Dashboard queries Git integration module
- Module executes Git commands via subprocess
- Parses output and returns structured data
- Dashboard displays commit history and stats

### CI/CD Monitors ↔ Dashboard
- Dashboard queries CI/CD monitoring modules
- Modules call external APIs (GitHub, Jenkins)
- Results cached for 30 seconds
- Dashboard displays pipeline status

### Docker Monitor ↔ Dashboard
- Dashboard queries Docker monitoring module
- Module executes Docker commands via subprocess
- Parses JSON output from Docker
- Dashboard displays container status

### Automation Scripts ↔ System
- Scripts provide CLI interface
- Execute system commands (pip, docker, pytest)
- Display progress and results
- Exit with appropriate status codes

## Technology Stack

### Backend
- **Language:** Python 3.12
- **Framework:** FastAPI
- **Server:** Uvicorn
- **Testing:** pytest, hypothesis
- **Data Processing:** pandas, plotly

### Frontend
- **HTML5** - Structure
- **JavaScript (ES6+)** - Logic and API calls
- **CSS3** - Styling and layout
- **No frameworks** - Vanilla JavaScript for simplicity

### Infrastructure
- **Version Control:** Git 2.x
- **Remote Hosting:** GitHub
- **CI/CD:** GitHub Actions, Jenkins 2.x
- **Containerization:** Docker 24.x
- **Orchestration:** Docker CLI (manual deployment)

### Development Tools
- **Linting:** flake8
- **Testing:** pytest, pytest-cov
- **Property Testing:** hypothesis
- **Code Coverage:** coverage.py

## Security Considerations

### Authentication
- GitHub API: Optional personal access token
- Jenkins API: Optional username/API token
- Docker: Local daemon access

### Data Protection
- No sensitive data stored in repository
- Secrets managed via environment variables
- API tokens passed as query parameters (should use headers in production)

### Container Security
- Multi-stage builds minimize attack surface
- Non-root user (should be configured)
- Health checks ensure availability
- Regular base image updates

## Performance Characteristics

### Dashboard Load Time
- **Target:** < 2 seconds
- **Optimization:** Parallel API calls with timeout
- **Caching:** 30-second TTL on CI/CD data

### Docker Build Time
- **Target:** < 5 minutes
- **Optimization:** Multi-stage builds, layer caching
- **Size:** Optimized through minimal base image

### CI Pipeline Time
- **GitHub Actions:** ~2-3 minutes
- **Jenkins:** ~2-3 minutes
- **Parallel execution:** Tests run concurrently

## Scalability

### Current Limitations
- Single container deployment
- Local Docker daemon
- Manual deployment process

### Future Enhancements
- Kubernetes orchestration
- Automated deployment pipelines
- Load balancing
- Database integration
- Distributed caching

## Monitoring and Observability

### Current Monitoring
- Engineering Dashboard (real-time)
- Docker health checks
- CI/CD pipeline status
- Application logs

### Metrics Tracked
- Commit frequency
- CI success rate
- Build duration
- Container health
- API response time

### Logging
- Application logs (stdout/stderr)
- Docker container logs
- CI/CD pipeline logs

## Disaster Recovery

### Backup Strategy
- Code: Git repository (GitHub backup)
- Uploads: Manual backup of uploads/ directory
- Configuration: Version controlled

### Recovery Procedures
- Restore from Git repository
- Rebuild Docker image
- Redeploy container
- Restore uploaded files from backup

## Best Practices

### Development Workflow
1. Create feature branch
2. Make changes and commit
3. Run tests locally
4. Push to GitHub
5. Create pull request
6. Wait for CI checks
7. Merge after approval

### Deployment Workflow
1. Merge to main branch
2. CI builds Docker image
3. Pull latest image
4. Run deployment script
5. Verify health checks
6. Monitor dashboard

### Maintenance
- Regular dependency updates
- Security vulnerability scans
- Performance monitoring
- Log review
- Backup verification

## Troubleshooting

### Common Issues

**Git Integration Fails**
- Verify Git is installed
- Check repository is initialized
- Ensure .git directory exists

**CI Pipeline Fails**
- Review pipeline logs
- Check test failures
- Verify dependencies

**Docker Build Fails**
- Check Dockerfile syntax
- Verify base image availability
- Review build logs

**Dashboard Not Loading**
- Verify server is running
- Check frontend files exist
- Review browser console errors

## Additional Resources

- [Demo Workflow](demo.md) - Step-by-step demonstration
- [Maintenance Guide](maintenance.md) - Ongoing operations
- [GitHub Setup](github-setup.md) - GitHub integration
- [System Manual](system_manual.md) - Application usage

## Glossary

- **CI/CD:** Continuous Integration / Continuous Deployment
- **Container:** Isolated runtime environment
- **Image:** Template for creating containers
- **Pipeline:** Automated workflow for building and testing
- **Workflow:** GitHub Actions automation definition
- **Build:** Process of creating deployable artifacts
- **Health Check:** Automated verification of service availability

---

**Document Version:** 1.0  
**Last Updated:** 2024  
**Maintainer:** ECU Log Visualizer Team
