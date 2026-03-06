# GitHub Setup Guide

This guide explains how to set up GitHub integration for the ECU Log Visualizer project.

## Prerequisites

- Git installed on your system
- GitHub account (https://github.com/jian-6666)
- Repository initialized locally

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `ecu-log-visualizer`
3. Description: "ECU Log Visualizer with Engineering Delivery Toolchain"
4. Choose visibility: Public or Private
5. **Do NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

## Step 2: Configure Git Remote

Add the GitHub repository as a remote:

```bash
git remote add origin https://github.com/jian-6666/ecu-log-visualizer.git
```

Verify the remote was added:

```bash
git remote -v
```

You should see:
```
origin  https://github.com/jian-6666/ecu-log-visualizer.git (fetch)
origin  https://github.com/jian-6666/ecu-log-visualizer.git (push)
```

## Step 3: Initial Commit and Push

### Stage all files

```bash
git add .
```

### Create initial commit

```bash
git commit -m "Initial commit: ECU Log Visualizer with Engineering Toolchain"
```

### Push to GitHub

For the first push, use:

```bash
git push -u origin master
```

Or if your default branch is `main`:

```bash
git branch -M main
git push -u origin main
```

### Subsequent pushes

After the initial push, you can simply use:

```bash
git push
```

## Step 4: Verify CI Pipeline

After pushing code to GitHub, the CI pipeline will automatically run.

### View CI Pipeline Status

1. Go to your repository: https://github.com/jian-6666/ecu-log-visualizer
2. Click on the "Actions" tab
3. You should see the "CI Pipeline" workflow running or completed

### CI Pipeline Steps

The pipeline automatically:
- ✅ Checks out code
- ✅ Sets up Python 3.12
- ✅ Installs dependencies
- ✅ Runs linting (flake8)
- ✅ Executes tests with coverage
- ✅ Verifies application builds
- ✅ Builds Docker image (on main/master branch)

### Troubleshooting CI Failures

If the CI pipeline fails:

1. Click on the failed workflow run
2. Click on the failed job
3. Expand the failed step to see error details
4. Fix the issue locally
5. Commit and push the fix:
   ```bash
   git add .
   git commit -m "Fix: [description of fix]"
   git push
   ```

## Step 5: Configure GitHub Actions Secrets (Optional)

If you need to add secrets for deployment or external services:

1. Go to repository Settings
2. Click "Secrets and variables" → "Actions"
3. Click "New repository secret"
4. Add your secrets (e.g., DOCKER_HUB_TOKEN, API_KEYS)

## Step 6: Set Up Branch Protection (Recommended)

Protect your main branch to require CI checks before merging:

1. Go to repository Settings
2. Click "Branches"
3. Click "Add branch protection rule"
4. Branch name pattern: `main` or `master`
5. Enable:
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
6. Select status checks: "test"
7. Click "Create"

## Step 7: Configure Webhooks for Jenkins (Optional)

If you're using Jenkins for CI/CD:

1. Go to repository Settings
2. Click "Webhooks"
3. Click "Add webhook"
4. Payload URL: `http://your-jenkins-server/github-webhook/`
5. Content type: `application/json`
6. Select events: "Just the push event"
7. Click "Add webhook"

## Common Git Commands

### Check repository status
```bash
git status
```

### View commit history
```bash
git log --oneline
```

### Create a new branch
```bash
git checkout -b feature/new-feature
```

### Switch branches
```bash
git checkout main
```

### Pull latest changes
```bash
git pull origin main
```

### View remote information
```bash
git remote show origin
```

## Authentication

### HTTPS Authentication

When pushing via HTTPS, you'll need to authenticate:

**Option 1: Personal Access Token (Recommended)**
1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with `repo` scope
3. Use token as password when prompted

**Option 2: GitHub CLI**
```bash
gh auth login
```

### SSH Authentication (Alternative)

If you prefer SSH:

1. Generate SSH key:
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```

2. Add SSH key to GitHub:
   - Copy public key: `cat ~/.ssh/id_ed25519.pub`
   - Go to GitHub Settings → SSH and GPG keys → New SSH key
   - Paste and save

3. Change remote to SSH:
   ```bash
   git remote set-url origin git@github.com:jian-6666/ecu-log-visualizer.git
   ```

## Viewing CI Results

### In GitHub UI

1. Repository page shows CI status badge
2. Actions tab shows all workflow runs
3. Each commit shows CI status (✅ or ❌)

### In Engineering Dashboard

Once deployed, the Engineering Dashboard will display:
- Recent commits
- CI/CD pipeline status
- Build history
- Test results

Access at: `http://localhost:8000/engineering-dashboard.html`

## Next Steps

After GitHub setup:

1. ✅ Configure branch protection rules
2. ✅ Set up automated deployments
3. ✅ Configure monitoring and alerts
4. ✅ Document contribution guidelines
5. ✅ Set up issue templates

## Support

For issues or questions:
- Check GitHub Actions logs
- Review this documentation
- Consult the Engineering Toolchain documentation: `docs/engineering-toolchain.md`
