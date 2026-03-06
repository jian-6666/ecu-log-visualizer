# ECU Log Visualizer - Simple Operation Guide

## 📖 Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation Steps](#installation-steps)
3. [Starting the Application](#starting-the-application)
4. [Using the Main Application](#using-the-main-application)
5. [Viewing the Engineering Dashboard](#viewing-the-engineering-dashboard)
6. [Demo Presentation Steps](#demo-presentation-steps)
7. [Troubleshooting](#troubleshooting)

---

## System Requirements

Before starting, ensure you have:

- ✅ **Python 3.9 or higher**
  - Check: Open terminal and type `python --version`
  - Download from: https://www.python.org/downloads/

- ✅ **Git** (optional, for version control)
  - Check: Open terminal and type `git --version`
  - Download from: https://git-scm.com/downloads

- ✅ **Docker** (optional, for containerized deployment)
  - Check: Open terminal and type `docker --version`
  - Download from: https://www.docker.com/get-started

---

## Installation Steps

### Method 1: Clone from GitHub (Recommended)

#### Step 1: Open Terminal
- **Windows**: Press `Win + R`, type `cmd`, press Enter
- **Mac/Linux**: Open Terminal

#### Step 2: Clone the Project
```bash
git clone https://github.com/jian-6666/ecu-log-visualizer.git
cd ecu-log-visualizer
```

#### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

Wait for installation to complete (may take 1-2 minutes).

---

### Method 2: Download ZIP File

#### Step 1: Download Project
1. Visit: https://github.com/jian-6666/ecu-log-visualizer
2. Click the green "Code" button
3. Click "Download ZIP"
4. Extract the downloaded file to your desired location

#### Step 2: Open Terminal and Navigate to Project Directory
```bash
cd path/to/ecu-log-visualizer
```

#### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Starting the Application

### Method 1: Run with Python (Simplest)

#### Step 1: Run in Project Directory
```bash
python run_server.py
```

#### Step 2: Success Output
```
============================================================
ECU Log Visualizer - Backend Server
============================================================
Starting server on http://127.0.0.1:8000
API Documentation: http://127.0.0.1:8000/docs
Alternative Docs: http://127.0.0.1:8000/redoc
Health Check: http://127.0.0.1:8000/health
============================================================
Press CTRL+C to stop the server
============================================================
```

#### Step 3: Keep Terminal Window Open
**Important**: Don't close this window - the server needs to keep running.

---

### Method 2: Run with Docker (Optional)

#### Step 1: Build Docker Image
```bash
docker build -t ecu-log-visualizer:latest .
```

Wait for build to complete (first time may take 3-5 minutes).

#### Step 2: Run Container
```bash
docker run -d --name ecu-log-visualizer -p 8000:8000 ecu-log-visualizer:latest
```

#### Step 3: Check Container Status
```bash
docker ps
```

You should see the `ecu-log-visualizer` container running.

---

## Using the Main Application

### Step 1: Open Browser

Open your preferred browser (Chrome, Firefox, Edge, etc.) and visit:
```
http://localhost:8000
```

### Step 2: Upload ECU Log File

#### 2.1 Click "Choose File" Button
Find the file upload area at the top of the page.

#### 2.2 Select Sample File
The project includes a sample file at:
```
examples/sample_ecu_log.csv
```

Or use your own ECU log file (supports CSV and JSON formats).

#### 2.3 Click "Upload" Button
Wait a few seconds for the file to upload.

### Step 3: View Data Analysis

After successful upload, the page automatically displays:

#### 3.1 Statistics Table
Shows for each sensor:
- **Minimum** - Lowest reading
- **Maximum** - Highest reading
- **Mean** - Average reading
- **Standard Deviation** - Data fluctuation

#### 3.2 Interactive Chart
- **Zoom**: Use mouse wheel to zoom in/out
- **Pan**: Hold left mouse button and drag
- **Hover**: Move mouse over data points to see exact values

### Step 4: Use Filter Features

#### 4.1 Select Time Range
Find the "Time Range" selector on the right:
- Click start time to select beginning
- Click end time to select end

#### 4.2 Select Sensors
In the "Sensor Selection" area:
- Check sensors you want to view
- Uncheck sensors you want to hide

#### 4.3 Apply Filter
Click "Apply Filter" button - chart and statistics update immediately.

### Step 5: Export Data

#### 5.1 Click "Export CSV" Button
Find the export button on the right side of the page.

#### 5.2 Save File
Browser automatically downloads filtered data as CSV file.

---

## Viewing the Engineering Dashboard

### Step 1: Open Engineering Dashboard

Visit in your browser:
```
http://localhost:8000/engineering-dashboard.html
```

### Step 2: Understand Dashboard Layout

#### Top: DevOps Pipeline Flow
Shows complete development process, left to right:

1. **👨‍💻 Developer Commit** - Developer commits code
2. **📊 Git** - Local version control
3. **🐙 GitHub** - Remote code repository
4. **🔄 CI/CD Build** - Automated testing and building
5. **🐳 Docker Image** - Container image
6. **🔧 Jenkins Test** - Automated testing
7. **🚀 Running Service** - Running service

**Status Indicators**:
- ✓ Green = Success
- ✗ Red = Failure
- ⚠ Yellow = In Progress/Warning
- ● Gray = Pending/Not Configured

#### Bottom: Detailed Panels

**1. Git Activity**
- Shows recent code commits
- Shows repository statistics (total commits, branches, contributors)

**2. CI/CD Pipelines**
- GitHub Actions status
- Jenkins build status
- Success rate statistics

**3. Docker Status**
- Container running status
- Image information
- Port mappings

**4. Test Results**
- Test execution results
- Code coverage

**5. API Health**
- Service health status
- Response time

### Step 3: Refresh Data

#### Auto Refresh
Dashboard automatically refreshes every 30 seconds.

#### Manual Refresh
Click the "↻ Refresh" button in the top right corner.

---

## Demo Presentation Steps

### Preparation (5 Minutes Before Demo)

#### 1. Start Server
```bash
python run_server.py
```

#### 2. Open Browser Tabs
Prepare 3 tabs:
- **Tab 1**: http://localhost:8000 (Main App)
- **Tab 2**: http://localhost:8000/engineering-dashboard.html (Dashboard)
- **Tab 3**: https://github.com/jian-6666/ecu-log-visualizer (GitHub)

#### 3. Prepare Sample File
Ensure `examples/sample_ecu_log.csv` file exists.

---

### Demo Flow (15 Minutes)

#### Part 1: Introduction (2 Minutes)

**What to Say**:
> "Hello everyone! Today I'll demonstrate the ECU Log Visualizer system. This is a complete DevOps demonstration project with data analysis features and a full engineering toolchain."

**What to Do**:
- Stand in front of the screen, face the audience
- Show a confident smile

---

#### Part 2: Main Application Demo (5 Minutes)

##### 2.1 Show Interface (1 Minute)

**Switch to Tab 1** (Main App)

**What to Say**:
> "This is the main application interface. At the top is the file upload area, in the middle is the data statistics table, and below is the interactive chart."

**What to Do**:
- Point to each area with your mouse
- Let the audience see the layout clearly

##### 2.2 Upload File (1 Minute)

**What to Say**:
> "Now I'll demonstrate uploading an ECU log file. The system supports both CSV and JSON formats."

**What to Do**:
1. Click "Choose File"
2. Select `examples/sample_ecu_log.csv`
3. Click "Upload"
4. Wait for upload to complete

**What to Say**:
> "Upload successful! The system automatically generates a unique ID for the file and validates the format."

##### 2.3 Show Statistics (1 Minute)

**What to Say**:
> "After upload, the system immediately analyzes the data. Here you can see statistics for each sensor: minimum, maximum, mean, and standard deviation."

**What to Do**:
- Point to the statistics table
- Highlight a few key data points

##### 2.4 Show Chart (1 Minute)

**What to Say**:
> "More intuitively, here's the interactive time series chart. I can zoom, pan, and view specific values."

**What to Do**:
1. Use mouse wheel to zoom the chart
2. Drag the chart to pan
3. Hover mouse to show values

##### 2.5 Demonstrate Filtering (1 Minute)

**What to Say**:
> "The system also provides powerful filtering features. I can select specific time ranges and sensors."

**What to Do**:
1. Select a time range
2. Uncheck some sensors
3. Click "Apply Filter"
4. Show chart updating

---

#### Part 3: Engineering Dashboard Demo (6 Minutes)

##### 3.1 Introduce Dashboard (1 Minute)

**Switch to Tab 2** (Engineering Dashboard)

**What to Say**:
> "This is the engineering dashboard - the most valuable part of the entire system. It provides complete DevOps process visibility."

**What to Do**:
- Pause for 2 seconds to let audience see the interface
- Point to the entire page

##### 3.2 Explain Pipeline Flow (3 Minutes)

**What to Say**:
> "The flow chart at the top shows the complete DevOps process, from developer commit to running service."

**What to Do**:
Point to each stage and explain:

1. **Developer Commit**
   > "Developer commits code - this is the starting point."

2. **Git**
   > "Code is saved in local Git repository for version control."

3. **GitHub**
   > "Code is pushed to GitHub remote repository, the center of team collaboration."

4. **CI/CD Build**
   > "GitHub Actions automatically triggers, running tests and builds."

5. **Docker Image**
   > "Docker image is built, ensuring environment consistency."

6. **Jenkins Test**
   > "Jenkins runs additional automated tests."

7. **Running Service**
   > "Finally, the service is deployed and running."

**What to Say**:
> "Notice the status indicators for each stage: green means success, red means failure, yellow means in progress. Each stage also shows the last update time."

##### 3.3 Show Detailed Panels (2 Minutes)

**What to Say**:
> "The panels below provide more detailed information."

**What to Do**:
Quickly review each panel:

1. **Git Activity**
   > "Here you see recent commit records and repository statistics."

2. **CI/CD Pipelines**
   > "Here you see GitHub Actions and Jenkins status."

3. **Docker Status**
   > "Here you see container running status."

4. **Test Results**
   > "Here you see test results and coverage."

5. **API Health**
   > "Here you see service health status."

---

#### Part 4: GitHub Integration Demo (2 Minutes)

##### 4.1 Show GitHub Repository

**Switch to Tab 3** (GitHub)

**What to Say**:
> "This is our GitHub repository. All code is hosted here."

**What to Do**:
- Show repository homepage
- Point out file structure

##### 4.2 Show GitHub Actions

**Click "Actions" Tab**

**What to Say**:
> "Here are the GitHub Actions CI/CD pipelines. Every time code is pushed, tests and builds run automatically."

**What to Do**:
- Show recent workflow runs
- Click a workflow to show detailed steps
- Point out green checkmarks for passed tests

---

#### Part 5: Live Demo (Optional, 2 Minutes)

##### 5.1 Make a Code Change

**Open Terminal**

**What to Say**:
> "Now I'll demonstrate a complete workflow. I'll make a small change and commit it."

**What to Do**:
```bash
echo "# Demo change - $(date)" >> README.md
git add README.md
git commit -m "demo: Live demonstration change"
git push origin main
```

##### 5.2 Show Process Triggering

**Switch back to Tab 3** (GitHub Actions)

**What to Say**:
> "Look, GitHub Actions has automatically triggered. It's running tests and builds now."

**What to Do**:
- Refresh page
- Show new workflow run
- Point out "in progress" status

**Switch back to Tab 2** (Engineering Dashboard)

**What to Say**:
> "On the dashboard, we can also see the new commit and CI/CD status updates."

**What to Do**:
- Click "Refresh" button
- Show new commit appearing in Git Activity
- Show CI/CD status updating

---

#### Part 6: Summary (2 Minutes)

**Face the Audience**

**What to Say**:
> "Let me summarize the core value of this system:"

> "First, **complete visibility**. From code commit to running service, every step is clearly visible. Management doesn't need to ask 'what's the status' - just open the dashboard."

> "Second, **full automation**. Testing, building, deployment - all automated. No manual steps means no human error."

> "Third, **fast delivery**. From code change to deployment takes only minutes. Traditional methods might take days."

> "Fourth, **high quality assurance**. Tests run automatically on every change. Problems are found in minutes, not when deploying."

> "Most importantly, these engineering practices are reusable. We can apply this standard to other projects, establishing a unified engineering culture."

**Pause for 2 seconds**

**What to Say**:
> "That concludes my demonstration. I'm happy to answer any questions."

**Smile and wait for questions**

---

### Presentation Tips

#### Pace and Rhythm
- ✅ Normal pace, not too fast
- ✅ Slow down for key points
- ✅ Pause 2-3 seconds between sections
- ✅ Watch audience reactions, adjust pace

#### Body Language
- ✅ Point to screen when discussing specific content
- ✅ Face audience when summarizing
- ✅ Maintain smile, show confidence
- ✅ Make eye contact with different audience members

#### Handling Unexpected Situations

**If system lags**:
> "The system is processing data, which demonstrates our performance monitoring features..."

**If error occurs**:
> "This demonstrates our error handling mechanism - the system provides clear error messages..."

**If you forget next step**:
> "Let me address some questions you might have..."(then check notes)

**If running out of time**:
> "Due to time constraints, let me quickly show the most important parts..."(skip to dashboard)

---

## Troubleshooting

### Q1: Server Fails to Start - "Port Already in Use"

**Problem**:
```
OSError: [Errno 48] Address already in use
```

**Solution**:

**Windows**:
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Note the PID (last column), then kill process
taskkill /PID <PID> /F

# Restart server
python run_server.py
```

**Mac/Linux**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill process (replace <PID> with actual process ID)
kill -9 <PID>

# Restart server
python run_server.py
```

---

### Q2: File Upload Fails

**Possible Causes**:
1. Incorrect file format (only CSV and JSON supported)
2. File too large (50MB limit)
3. File content format doesn't meet requirements

**Solutions**:
1. Test with sample file: `examples/sample_ecu_log.csv`
2. Check file size: Right-click file → Properties → Check size
3. Check file format: Ensure it's CSV or JSON

**CSV Format Requirements**:
```csv
timestamp,sensor_name,value
2024-01-01 10:00:00,temperature,25.5
2024-01-01 10:00:01,pressure,101.3
```

**JSON Format Requirements**:
```json
[
  {
    "timestamp": "2024-01-01 10:00:00",
    "sensor_name": "temperature",
    "value": 25.5
  }
]
```

---

### Q3: Dashboard Shows "Loading..." Indefinitely

**Possible Causes**:
1. Server not started
2. Network connection issue
3. API response timeout

**Solutions**:

**Step 1**: Check if server is running
```bash
curl http://localhost:8000/health
```

Should return:
```json
{"status":"healthy","service":"ECU Log Visualizer","max_upload_size_mb":50.0}
```

**Step 2**: Check browser console
1. Press F12 to open developer tools
2. Click "Console" tab
3. Check for error messages

**Step 3**: Refresh page
Press Ctrl+F5 (Windows) or Cmd+Shift+R (Mac) to force refresh.

---

### Q4: GitHub Actions Not Triggering

**Possible Causes**:
1. GitHub Actions not enabled
2. Workflow file has syntax errors
3. Not pushing to correct branch

**Solutions**:

**Step 1**: Check if GitHub Actions is enabled
1. Visit: https://github.com/jian-6666/ecu-log-visualizer
2. Click "Settings"
3. Click "Actions" → "General" on left
4. Ensure "Allow all actions and reusable workflows" is selected

**Step 2**: Check workflow file
Ensure `.github/workflows/ci.yml` exists and format is correct.

**Step 3**: Check branch
Ensure pushing to main or master branch:
```bash
git branch  # View current branch
git push origin main  # Push to main branch
```

---

### Q5: Docker Build Fails

**Possible Causes**:
1. Docker not started
2. Insufficient disk space
3. Network connection issue

**Solutions**:

**Step 1**: Check if Docker is running
```bash
docker info
```

If error shown, start Docker Desktop.

**Step 2**: Check disk space
```bash
docker system df
```

If insufficient space, clean up:
```bash
docker system prune -a
```

**Step 3**: Rebuild
```bash
docker build -t ecu-log-visualizer:latest .
```

---

### Q6: Chart Not Displaying or Displaying Incorrectly

**Possible Causes**:
1. Incorrect data format
2. Browser compatibility issue
3. JavaScript error

**Solutions**:

**Step 1**: Check data
Ensure uploaded file contains valid data.

**Step 2**: Try different browser
Use latest version of Chrome or Firefox.

**Step 3**: Clear cache
Press Ctrl+Shift+Delete (Windows) or Cmd+Shift+Delete (Mac) to clear browser cache.

---

### Q7: How to Stop the Server?

**Method 1**: In terminal running server
Press `Ctrl + C`

**Method 2**: If using Docker
```bash
docker stop ecu-log-visualizer
docker rm ecu-log-visualizer
```

---

### Q8: How to Update Code?

**If using Git**:
```bash
git pull origin main
pip install -r requirements.txt
python run_server.py
```

**If downloaded ZIP**:
1. Re-download latest ZIP file
2. Extract and replace old files
3. Reinstall dependencies: `pip install -r requirements.txt`
4. Start server: `python run_server.py`

---

## Quick Command Reference

### Start and Stop

```bash
# Start server
python run_server.py

# Stop server
# Press Ctrl+C

# Start with Docker
docker run -d --name ecu-log-visualizer -p 8000:8000 ecu-log-visualizer:latest

# Stop with Docker
docker stop ecu-log-visualizer
docker rm ecu-log-visualizer
```

### Testing

```bash
# Run all tests
pytest tests/ -v

# Run unit tests
pytest tests/unit/ -v

# Run tests with coverage
pytest tests/ -v --cov=src --cov-report=term-missing
```

### Git Operations

```bash
# Check status
git status

# View recent commits
git log --oneline -5

# Commit changes
git add .
git commit -m "Your commit message"
git push origin main
```

### Docker Operations

```bash
# Build image
docker build -t ecu-log-visualizer:latest .

# View images
docker images

# View running containers
docker ps

# View container logs
docker logs ecu-log-visualizer

# Enter container
docker exec -it ecu-log-visualizer bash
```

---

## Important Links

- **Main App**: http://localhost:8000
- **Engineering Dashboard**: http://localhost:8000/engineering-dashboard.html
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **GitHub Repository**: https://github.com/jian-6666/ecu-log-visualizer
- **GitHub Actions**: https://github.com/jian-6666/ecu-log-visualizer/actions

---

## Getting Help

If you encounter problems:

1. **Check Documentation**
   - `DEVOPS_DEMO_GUIDE.md` - Complete DevOps guide
   - `QUICK_DEMO_STEPS.md` - Quick demo steps
   - Other docs in `docs/` directory

2. **Check Logs**
   - Server logs: Terminal window output
   - Browser logs: Press F12, check Console

3. **GitHub Issues**
   - Visit: https://github.com/jian-6666/ecu-log-visualizer/issues
   - Search for similar issues or create new one

---

## Summary

This guide covers:

✅ System requirements and installation steps
✅ Multiple methods to start the application
✅ Detailed main application usage
✅ Complete engineering dashboard introduction
✅ 15-minute complete demo presentation flow
✅ Common problems and solutions
✅ Quick command reference

**Remember**:
- Stay confident
- Speak clearly
- Pause appropriately
- Enjoy the presentation

**Good luck!** 🎉

---

**Document Version**: 1.0  
**Last Updated**: 2026-03-06  
**Maintainer**: Jian Ma  
**GitHub**: https://github.com/jian-6666/ecu-log-visualizer
