"""
Git Integration Module

Provides programmatic access to Git repository information using subprocess
to execute Git commands and parse output. Avoids external dependencies like
GitPython while maintaining full functionality.
"""

import subprocess
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import os


@dataclass
class CommitInfo:
    """Git commit information"""
    hash: str
    short_hash: str
    author: str
    email: str
    timestamp: datetime
    message: str
    branch: str


@dataclass
class RepositoryStats:
    """Repository statistics"""
    total_commits: int
    branches: List[str]
    current_branch: str
    remote_url: Optional[str]
    contributors: int


class GitRepository:
    """Interface to Git repository operations"""
    
    def __init__(self, repo_path: str = "."):
        """
        Initialize with repository path
        
        Args:
            repo_path: Path to the Git repository (default: current directory)
        """
        self.repo_path = repo_path
        self._git_available = None
        self._is_repo = None
    
    def _check_git_available(self) -> bool:
        """Check if Git is available on the system"""
        if self._git_available is None:
            try:
                result = subprocess.run(
                    ["git", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                self._git_available = result.returncode == 0
            except (subprocess.SubprocessError, FileNotFoundError):
                self._git_available = False
        return self._git_available
    
    def _check_is_repo(self) -> bool:
        """Check if the path is a Git repository"""
        if self._is_repo is None:
            git_dir = os.path.join(self.repo_path, ".git")
            self._is_repo = os.path.exists(git_dir)
        return self._is_repo
    
    def _run_git_command(self, args: List[str], check: bool = True) -> Optional[str]:
        """
        Execute a Git command and return output
        
        Args:
            args: Git command arguments (without 'git' prefix)
            check: Whether to raise exception on non-zero exit code
            
        Returns:
            Command output as string, or None if command failed
        """
        if not self._check_git_available():
            return None
        
        if not self._check_is_repo():
            return None
        
        try:
            # Disable pager and interactive prompts
            env = os.environ.copy()
            env['GIT_PAGER'] = 'cat'
            env['GIT_TERMINAL_PROMPT'] = '0'
            
            result = subprocess.run(
                ["git", "-C", self.repo_path, "--no-pager"] + args,
                capture_output=True,
                text=True,
                timeout=10,
                check=check,
                env=env
            )
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            return None
        except subprocess.SubprocessError:
            return None

    def get_commit_history(self, limit: int = 50) -> List[CommitInfo]:
        """
        Retrieve recent commit history
        
        Args:
            limit: Maximum number of commits to retrieve
            
        Returns:
            List of CommitInfo objects, empty list if Git unavailable
        """
        if not self._check_git_available() or not self._check_is_repo():
            return []
        
        # Format: hash|short_hash|author|email|timestamp|message
        format_str = "%H|%h|%an|%ae|%at|%s"
        output = self._run_git_command([
            "log",
            f"--max-count={limit}",
            f"--format={format_str}"
        ])
        
        if not output:
            return []
        
        commits = []
        current_branch = self.get_current_branch()
        
        for line in output.split("\n"):
            if not line.strip():
                continue
            
            parts = line.split("|", 5)
            if len(parts) != 6:
                continue
            
            hash_val, short_hash, author, email, timestamp_str, message = parts
            
            try:
                timestamp = datetime.fromtimestamp(int(timestamp_str))
            except (ValueError, OSError):
                continue
            
            commits.append(CommitInfo(
                hash=hash_val,
                short_hash=short_hash,
                author=author,
                email=email,
                timestamp=timestamp,
                message=message,
                branch=current_branch
            ))
        
        return commits
    
    def get_current_branch(self) -> str:
        """
        Get current branch name
        
        Returns:
            Current branch name, or "unknown" if unavailable
        """
        output = self._run_git_command(["branch", "--show-current"])
        return output if output else "unknown"
    
    def get_remote_url(self) -> Optional[str]:
        """
        Get GitHub remote URL if configured
        
        Returns:
            Remote URL string, or None if not configured
        """
        output = self._run_git_command(["remote", "get-url", "origin"], check=False)
        return output if output else None
    
    def get_repository_stats(self) -> RepositoryStats:
        """
        Get repository statistics (commits, branches, contributors)
        
        Returns:
            RepositoryStats object with repository information
        """
        if not self._check_git_available() or not self._check_is_repo():
            return RepositoryStats(
                total_commits=0,
                branches=[],
                current_branch="unknown",
                remote_url=None,
                contributors=0
            )
        
        # Get total commits (handle empty repository)
        commit_count_output = self._run_git_command(["rev-list", "--count", "HEAD"], check=False)
        total_commits = int(commit_count_output) if commit_count_output and commit_count_output.isdigit() else 0
        
        # Get all branches
        branches_output = self._run_git_command(["branch", "--format=%(refname:short)"])
        branches = branches_output.split("\n") if branches_output else []
        branches = [b.strip() for b in branches if b.strip()]
        
        # Get current branch
        current_branch = self.get_current_branch()
        
        # Get remote URL
        remote_url = self.get_remote_url()
        
        # Get unique contributors (handle empty repository)
        contributors = 0
        if total_commits > 0:
            contributors_output = self._run_git_command(["shortlog", "-sn", "--all"], check=False)
            contributors = len(contributors_output.split("\n")) if contributors_output else 0
        
        return RepositoryStats(
            total_commits=total_commits,
            branches=branches,
            current_branch=current_branch,
            remote_url=remote_url,
            contributors=contributors
        )
