# ECU Log Visualizer - Maintenance Guide

## Overview

This document provides maintenance procedures for the ECU Log Visualizer and its engineering toolchain. Regular maintenance ensures system reliability, security, and optimal performance.

## Table of Contents

1. [Routine Maintenance Tasks](#routine-maintenance-tasks)
2. [Troubleshooting Procedures](#troubleshooting-procedures)
3. [Update Procedures](#update-procedures)
4. [Backup and Recovery](#backup-and-recovery)
5. [Performance Monitoring](#performance-monitoring)
6. [Security Maintenance](#security-maintenance)

## Routine Maintenance Tasks

### Daily Tasks

#### Monitor System Health
```bash
# Check API health
curl http://localhost:8000/health

# Check Docker container status
docker ps | grep ecu-log-visualizer

# View container logs
docker logs ecu-log-visualizer --tail 100
```

**Expected Results:**
- API returns `{"status": "healthy"}`
- Container status shows "Up"
- No error messages in logs

#### Review Dashboard
- Access Engineering Dashboard at http://localhost:8000/engineering-dashboard.html
- Verify all panels show green status indicators
- Check for any warnings or failures

### Weekly Tasks

#### Run Full Test Suite
```bash
./scripts/test.sh
```

**Actions if tests fail:**
1. Review test output for specific failures
2. Check recent code changes
3. Verify dependencies are up to date
4. Run tests individually to isolate issues

#### Clean Up Old Uploads
```bash
# List uploaded files older than 30 days
find uploads/ -type f -mtime +30

# Remove old files (review list first!)
find uploads/ -type f -mtime +30 -delete
```

#### Review Disk Usage
```bash
# Check disk usage
df -h

# Check Docker disk usage
docker system df

# Clean up unused Docker resources
docker system prune -a --volumes
```

### Monthly Tasks

#### Update Dependencies
```bash
# Update Python packages
pip list --outdated
pip install --upgrade <package-name>

# Update requirements.txt
pip freeze > requirements.txt

# Test after updates
./scripts/test.sh
```

#### Review and Rotate Logs
```bash
# Archive old logs
tar -czf logs-$(date +%Y%m).tar.gz logs/

# Clear old log files
> logs/application.log
```

#### Security Audit
```bash
# Check for security vulnerabilities in dependencies
pip install safety
safety check

# Update Docker base image
docker pull python:3.12-slim
./scripts/build.sh
```

## Troubleshooting Procedures

### Application Won't Start

**Symptoms:**
- Server fails to start
- Port binding errors
- Import errors

**Diagnosis:**
```bash
# Check if port is in use
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Verify Python version
python --version

# Check dependencies
pip check
```

**Solutions:**
1. **Port in use:** Kill existing process or change port
2. **Missing dependencies:** Run `pip install -r requirements.txt`
3. **Python version:** Ensure Python 3.12+ is installed

### Docker Container Issues

**Symptoms:**
- Container won't start
- Container exits immediately
- Health check failures

**Diagnosis:**
```bash
# Check container status
docker ps -a | grep ecu-log-visualizer

# View container logs
docker logs ecu-log-visualizer

# Inspect container
docker inspect ecu-log-visualizer
```

**Solutions:**

1. **Container won't start:**
```bash
# Remove old container
docker rm -f ecu-log-visualizer

# Rebuild image
./scripts/build.sh

# Redeploy
./scripts/deploy.sh
```

2. **Health check failures:**
```bash
# Check if application is responding
docker exec ecu-log-visualizer curl http://localhost:8000/health

# Review application logs
docker logs ecu-log-visualizer --tail 50
```

3. **Permission issues:**
```bash
# Fix uploads directory permissions
docker exec ecu-log-visualizer chmod 777 /app/uploads
```

### CI/CD Pipeline Failures

**Symptoms:**
- GitHub Actions workflow fails
- Jenkins build fails
- Tests fail in CI but pass locally

**Diagnosis:**
1. Review pipeline logs in GitHub Actions or Jenkins
2. Check for environment differences
3. Verify all dependencies are specified

**Solutions:**

1. **Dependency issues:**
```bash
# Ensure requirements.txt is up to date
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update dependencies"
git push
```

2. **Test failures:**
```bash
# Run tests locally with same environment
docker run --rm -v $(pwd):/app python:3.12-slim bash -c "cd /app && pip install -r requirements.txt && pytest tests/"
```

3. **Timeout issues:**
- Increase timeout in workflow configuration
- Optimize slow tests
- Check for network issues

### Dashboard Not Loading

**Symptoms:**
- Dashboard shows blank page
- JavaScript errors in console
- API endpoints return errors

**Diagnosis:**
```bash
# Check if frontend files exist
ls frontend/engineering-dashboard.*

# Test API endpoints
curl http://localhost:8000/api/engineering/dashboard

# Check browser console for errors
```

**Solutions:**

1. **Missing files:**
```bash
# Verify all frontend files are present
ls -la frontend/
```

2. **API errors:**
```bash
# Check server logs
docker logs ecu-log-visualizer

# Verify Git is available
git --version

# Verify Docker is available
docker --version
```

3. **CORS issues:**
- Check CORS configuration in `src/main.py`
- Ensure frontend is served from same origin

## Update Procedures

### Application Updates

#### Update Application Code
```bash
# Pull latest changes
git pull origin main

# Install new dependencies
pip install -r requirements.txt

# Run tests
./scripts/test.sh

# Rebuild Docker image
./scripts/build.sh

# Redeploy
./scripts/deploy.sh
```

#### Update Python Dependencies
```bash
# Update specific package
pip install --upgrade <package-name>

# Update all packages (use with caution)
pip list --outdated | cut -d ' ' -f1 | xargs -n1 pip install -U

# Update requirements.txt
pip freeze > requirements.txt

# Test thoroughly
./scripts/test.sh
```

#### Update Docker Base Image
```bash
# Edit Dockerfile to use newer Python version
# FROM python:3.12-slim -> FROM python:3.13-slim

# Rebuild image
./scripts/build.sh

# Test thoroughly
./scripts/test.sh

# Deploy
./scripts/deploy.sh
```

### Rollback Procedures

#### Rollback Application
```bash
# Revert to previous commit
git log --oneline  # Find commit hash
git revert <commit-hash>

# Or reset to previous version
git reset --hard <commit-hash>

# Rebuild and redeploy
./scripts/build.sh
./scripts/deploy.sh
```

#### Rollback Docker Image
```bash
# List available images
docker images ecu-log-visualizer

# Deploy specific version
docker stop ecu-log-visualizer
docker rm ecu-log-visualizer
docker run -d --name ecu-log-visualizer -p 8000:8000 ecu-log-visualizer:<timestamp>
```

## Backup and Recovery

### Backup Procedures

#### Backup Uploaded Files
```bash
# Create backup archive
tar -czf uploads-backup-$(date +%Y%m%d).tar.gz uploads/

# Move to backup location
mv uploads-backup-*.tar.gz /path/to/backup/location/
```

#### Backup Configuration
```bash
# Backup configuration files
tar -czf config-backup-$(date +%Y%m%d).tar.gz \
    .env \
    Dockerfile \
    docker-compose.yml \
    requirements.txt
```

#### Backup Database (if applicable)
```bash
# If using database, backup data
# Example for PostgreSQL:
pg_dump -U username dbname > backup-$(date +%Y%m%d).sql
```

### Recovery Procedures

#### Restore Uploaded Files
```bash
# Extract backup
tar -xzf uploads-backup-YYYYMMDD.tar.gz

# Verify files
ls -la uploads/
```

#### Restore Configuration
```bash
# Extract configuration backup
tar -xzf config-backup-YYYYMMDD.tar.gz

# Rebuild with restored configuration
./scripts/build.sh
./scripts/deploy.sh
```

## Performance Monitoring

### Monitor Application Performance

#### Check Response Times
```bash
# Test API response time
time curl http://localhost:8000/health

# Test dashboard load time
time curl http://localhost:8000/engineering-dashboard.html
```

**Expected Results:**
- Health check: < 100ms
- Dashboard load: < 2 seconds

#### Monitor Resource Usage
```bash
# Check container resource usage
docker stats ecu-log-visualizer

# Check system resources
top  # Linux/macOS
```

**Warning Signs:**
- CPU usage consistently > 80%
- Memory usage consistently > 80%
- Disk usage > 90%

### Optimize Performance

#### Clear Caches
```bash
# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Clear Docker build cache
docker builder prune
```

#### Optimize Docker Image
```bash
# Review image size
docker images ecu-log-visualizer

# If image is too large:
# 1. Review Dockerfile for unnecessary files
# 2. Use .dockerignore to exclude files
# 3. Combine RUN commands to reduce layers
```

## Security Maintenance

### Security Best Practices

#### Regular Security Updates
```bash
# Update system packages (in Docker)
docker exec ecu-log-visualizer apt-get update
docker exec ecu-log-visualizer apt-get upgrade -y

# Rebuild image with updates
./scripts/build.sh
```

#### Scan for Vulnerabilities
```bash
# Scan Python dependencies
pip install safety
safety check

# Scan Docker image
docker scan ecu-log-visualizer:latest
```

#### Review Access Logs
```bash
# Review application logs for suspicious activity
docker logs ecu-log-visualizer | grep -i "error\|warning\|unauthorized"

# Check for unusual access patterns
docker logs ecu-log-visualizer | grep "POST\|DELETE" | tail -50
```

### Security Incident Response

#### If Security Issue Detected

1. **Isolate:** Stop the affected container
```bash
docker stop ecu-log-visualizer
```

2. **Investigate:** Review logs and identify issue
```bash
docker logs ecu-log-visualizer > incident-logs.txt
```

3. **Remediate:** Apply security patches
```bash
pip install --upgrade <vulnerable-package>
./scripts/build.sh
```

4. **Verify:** Test thoroughly
```bash
./scripts/test.sh
safety check
```

5. **Redeploy:** Deploy patched version
```bash
./scripts/deploy.sh
```

6. **Document:** Record incident and resolution

## Maintenance Schedule

### Daily
- [ ] Check system health
- [ ] Review dashboard status
- [ ] Monitor error logs

### Weekly
- [ ] Run full test suite
- [ ] Clean up old uploads
- [ ] Review disk usage

### Monthly
- [ ] Update dependencies
- [ ] Security audit
- [ ] Review and rotate logs
- [ ] Backup configuration

### Quarterly
- [ ] Performance review
- [ ] Capacity planning
- [ ] Documentation review
- [ ] Disaster recovery test

## Contact and Escalation

### Support Contacts
- **Development Team:** dev-team@example.com
- **DevOps Team:** devops@example.com
- **Security Team:** security@example.com

### Escalation Procedure
1. **Level 1:** Check this maintenance guide
2. **Level 2:** Contact development team
3. **Level 3:** Escalate to DevOps team
4. **Level 4:** Involve security team (for security issues)

## Additional Resources

- [Demo Workflow](demo.md)
- [GitHub Setup Guide](github-setup.md)
- [Engineering Toolchain Architecture](engineering-toolchain.md)
- [System Manual](system_manual.md)

---

**Document Version:** 1.0  
**Last Updated:** 2024  
**Maintainer:** ECU Log Visualizer Team
