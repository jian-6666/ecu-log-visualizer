"""
CI/CD Status Monitoring Module

This module provides functionality to monitor CI/CD pipeline status from
GitHub Actions and Jenkins.
"""

import time
from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime
import urllib.request
import urllib.error
import json


@dataclass
class WorkflowRun:
    """GitHub Actions workflow run information"""
    id: int
    name: str
    status: str  # queued, in_progress, completed
    conclusion: Optional[str]  # success, failure, cancelled, skipped
    created_at: datetime
    updated_at: datetime
    html_url: str


@dataclass
class WorkflowStatus:
    """Current GitHub Actions workflow status"""
    latest_run: Optional[WorkflowRun]
    recent_runs: List[WorkflowRun]
    success_rate: float


@dataclass
class BuildInfo:
    """Jenkins build information"""
    number: int
    status: str  # SUCCESS, FAILURE, UNSTABLE, ABORTED, IN_PROGRESS
    timestamp: datetime
    duration: int  # milliseconds
    url: str


@dataclass
class BuildStatus:
    """Current Jenkins build status"""
    latest_build: Optional[BuildInfo]
    recent_builds: List[BuildInfo]
    success_rate: float


class GitHubActionsMonitor:
    """Monitor GitHub Actions workflow status"""
    
    def __init__(self, repo_owner: str, repo_name: str, token: Optional[str] = None):
        """
        Initialize GitHub Actions monitor
        
        Args:
            repo_owner: GitHub repository owner/organization
            repo_name: GitHub repository name
            token: Optional GitHub personal access token for authentication
        """
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.token = token
        self.base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        
        # Cache with 30-second TTL
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._cache_ttl = 30
    
    def _get_cached(self, key: str) -> Optional[Any]:
        """Get cached value if not expired"""
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < self._cache_ttl:
                return value
        return None
    
    def _set_cache(self, key: str, value: Any):
        """Set cached value with current timestamp"""
        self._cache[key] = (value, time.time())
    
    def _make_request(self, url: str) -> Optional[Dict]:
        """
        Make HTTP request to GitHub API
        
        Args:
            url: API endpoint URL
            
        Returns:
            Parsed JSON response or None on error
        """
        try:
            headers = {
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'ECU-Log-Visualizer'
            }
            
            if self.token:
                headers['Authorization'] = f'token {self.token}'
            
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode())
                
        except urllib.error.HTTPError as e:
            if e.code == 403:
                # Rate limit exceeded
                return None
            elif e.code == 404:
                # Repository or workflow not found
                return None
            return None
        except (urllib.error.URLError, json.JSONDecodeError, Exception):
            return None
    
    def get_workflow_runs(self, limit: int = 10) -> List[WorkflowRun]:
        """
        Get recent workflow run history
        
        Args:
            limit: Maximum number of runs to retrieve
            
        Returns:
            List of WorkflowRun objects
        """
        cache_key = f"workflow_runs_{limit}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached
        
        url = f"{self.base_url}/actions/runs?per_page={limit}"
        data = self._make_request(url)
        
        if not data or 'workflow_runs' not in data:
            return []
        
        runs = []
        for run_data in data['workflow_runs'][:limit]:
            try:
                run = WorkflowRun(
                    id=run_data['id'],
                    name=run_data['name'],
                    status=run_data['status'],
                    conclusion=run_data.get('conclusion'),
                    created_at=datetime.fromisoformat(run_data['created_at'].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(run_data['updated_at'].replace('Z', '+00:00')),
                    html_url=run_data['html_url']
                )
                runs.append(run)
            except (KeyError, ValueError):
                continue
        
        self._set_cache(cache_key, runs)
        return runs
    
    def get_latest_run_status(self) -> WorkflowStatus:
        """
        Get status of most recent workflow run
        
        Returns:
            WorkflowStatus object with latest run and statistics
        """
        runs = self.get_workflow_runs(limit=20)
        
        if not runs:
            return WorkflowStatus(
                latest_run=None,
                recent_runs=[],
                success_rate=0.0
            )
        
        # Calculate success rate from completed runs
        completed_runs = [r for r in runs if r.status == 'completed']
        if completed_runs:
            successful = sum(1 for r in completed_runs if r.conclusion == 'success')
            success_rate = successful / len(completed_runs)
        else:
            success_rate = 0.0
        
        return WorkflowStatus(
            latest_run=runs[0],
            recent_runs=runs[:10],
            success_rate=success_rate
        )


class JenkinsMonitor:
    """Monitor Jenkins pipeline status"""
    
    def __init__(self, jenkins_url: str, job_name: str, auth: Optional[Tuple[str, str]] = None):
        """
        Initialize Jenkins monitor
        
        Args:
            jenkins_url: Jenkins server URL (e.g., http://jenkins.example.com)
            job_name: Jenkins job/pipeline name
            auth: Optional tuple of (username, api_token) for authentication
        """
        self.jenkins_url = jenkins_url.rstrip('/')
        self.job_name = job_name
        self.auth = auth
        
        # Cache with 30-second TTL
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._cache_ttl = 30
    
    def _get_cached(self, key: str) -> Optional[Any]:
        """Get cached value if not expired"""
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < self._cache_ttl:
                return value
        return None
    
    def _set_cache(self, key: str, value: Any):
        """Set cached value with current timestamp"""
        self._cache[key] = (value, time.time())
    
    def _make_request(self, url: str) -> Optional[Dict]:
        """
        Make HTTP request to Jenkins API
        
        Args:
            url: API endpoint URL
            
        Returns:
            Parsed JSON response or None on error
        """
        try:
            headers = {
                'Accept': 'application/json',
                'User-Agent': 'ECU-Log-Visualizer'
            }
            
            req = urllib.request.Request(url, headers=headers)
            
            if self.auth:
                import base64
                credentials = base64.b64encode(f"{self.auth[0]}:{self.auth[1]}".encode()).decode()
                req.add_header('Authorization', f'Basic {credentials}')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode())
                
        except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError, Exception):
            return None
    
    def get_build_history(self, limit: int = 10) -> List[BuildInfo]:
        """
        Get recent build history
        
        Args:
            limit: Maximum number of builds to retrieve
            
        Returns:
            List of BuildInfo objects
        """
        cache_key = f"build_history_{limit}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached
        
        url = f"{self.jenkins_url}/job/{self.job_name}/api/json?tree=builds[number,result,timestamp,duration,url]{{0,{limit}}}"
        data = self._make_request(url)
        
        if not data or 'builds' not in data:
            return []
        
        builds = []
        for build_data in data['builds'][:limit]:
            try:
                # Determine status
                result = build_data.get('result')
                if result is None:
                    status = 'IN_PROGRESS'
                else:
                    status = result
                
                build = BuildInfo(
                    number=build_data['number'],
                    status=status,
                    timestamp=datetime.fromtimestamp(build_data['timestamp'] / 1000),
                    duration=build_data.get('duration', 0),
                    url=build_data['url']
                )
                builds.append(build)
            except (KeyError, ValueError):
                continue
        
        self._set_cache(cache_key, builds)
        return builds
    
    def get_latest_build_status(self) -> BuildStatus:
        """
        Get status of most recent build
        
        Returns:
            BuildStatus object with latest build and statistics
        """
        builds = self.get_build_history(limit=20)
        
        if not builds:
            return BuildStatus(
                latest_build=None,
                recent_builds=[],
                success_rate=0.0
            )
        
        # Calculate success rate from completed builds
        completed_builds = [b for b in builds if b.status != 'IN_PROGRESS']
        if completed_builds:
            successful = sum(1 for b in completed_builds if b.status == 'SUCCESS')
            success_rate = successful / len(completed_builds)
        else:
            success_rate = 0.0
        
        return BuildStatus(
            latest_build=builds[0],
            recent_builds=builds[:10],
            success_rate=success_rate
        )
