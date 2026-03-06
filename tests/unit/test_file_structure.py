"""
Unit Tests for File Structure Validation

This module tests that all required files and directories exist
and have the correct structure as specified in the engineering toolchain.

Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8
"""

import os
import pytest
from pathlib import Path


# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent


class TestFileStructure:
    """Test that all required files and directories exist"""
    
    def test_root_files_exist(self):
        """Test that required root-level files exist"""
        required_files = [
            'README.md',
            'CHANGELOG.md',
            'requirements.txt',
            'pytest.ini',
            'Dockerfile',
            'Jenkinsfile',
            '.gitignore',
            '.dockerignore',
            'run_server.py',
        ]
        
        for filename in required_files:
            file_path = PROJECT_ROOT / filename
            assert file_path.exists(), f"Required file '{filename}' does not exist"
            assert file_path.is_file(), f"'{filename}' exists but is not a file"
    
    def test_directory_structure(self):
        """Test that required directories exist"""
        required_dirs = [
            'src',
            'frontend',
            'tests',
            'tests/unit',
            'tests/integration',
            'tests/property',
            'scripts',
            'docs',
            'examples',
            'uploads',
            '.github',
            '.github/workflows',
        ]
        
        for dirname in required_dirs:
            dir_path = PROJECT_ROOT / dirname
            assert dir_path.exists(), f"Required directory '{dirname}' does not exist"
            assert dir_path.is_dir(), f"'{dirname}' exists but is not a directory"
    
    def test_source_files_exist(self):
        """Test that required source files exist"""
        required_source_files = [
            'src/main.py',
            'src/models.py',
            'src/file_handler.py',
            'src/data_analyzer.py',
            'src/visualization_engine.py',
            'src/error_handler.py',
            'src/git_integration.py',
            'src/cicd_status.py',
            'src/docker_status.py',
        ]
        
        for filename in required_source_files:
            file_path = PROJECT_ROOT / filename
            assert file_path.exists(), f"Required source file '{filename}' does not exist"
            assert file_path.is_file(), f"'{filename}' exists but is not a file"
    
    def test_frontend_files_exist(self):
        """Test that required frontend files exist"""
        required_frontend_files = [
            'frontend/index.html',
            'frontend/app.js',
            'frontend/styles.css',
            'frontend/engineering-dashboard.html',
            'frontend/engineering-dashboard.js',
            'frontend/engineering-dashboard.css',
        ]
        
        for filename in required_frontend_files:
            file_path = PROJECT_ROOT / filename
            assert file_path.exists(), f"Required frontend file '{filename}' does not exist"
            assert file_path.is_file(), f"'{filename}' exists but is not a file"
    
    def test_script_files_exist(self):
        """Test that required automation scripts exist"""
        required_scripts = [
            'scripts/dev.sh',
            'scripts/test.sh',
            'scripts/build.sh',
            'scripts/deploy.sh',
        ]
        
        for filename in required_scripts:
            file_path = PROJECT_ROOT / filename
            assert file_path.exists(), f"Required script '{filename}' does not exist"
            assert file_path.is_file(), f"'{filename}' exists but is not a file"
    
    def test_script_permissions(self):
        """Test that automation scripts have executable permissions (Unix-like systems only)"""
        if os.name == 'nt':  # Skip on Windows
            pytest.skip("Skipping permission test on Windows")
        
        required_scripts = [
            'scripts/dev.sh',
            'scripts/test.sh',
            'scripts/build.sh',
            'scripts/deploy.sh',
        ]
        
        for filename in required_scripts:
            file_path = PROJECT_ROOT / filename
            if file_path.exists():
                # Check if file has execute permission
                is_executable = os.access(file_path, os.X_OK)
                assert is_executable, f"Script '{filename}' is not executable"
    
    def test_documentation_files_exist(self):
        """Test that required documentation files exist"""
        required_docs = [
            'docs/demo.md',
            'docs/maintenance.md',
            'docs/github-setup.md',
            'docs/engineering-toolchain.md',
            'docs/log_format.md',
            'docs/configuration.md',
        ]
        
        for filename in required_docs:
            file_path = PROJECT_ROOT / filename
            assert file_path.exists(), f"Required documentation '{filename}' does not exist"
            assert file_path.is_file(), f"'{filename}' exists but is not a file"
    
    def test_example_files_exist(self):
        """Test that example data files exist"""
        required_examples = [
            'examples/sample_ecu_log.csv',
            'examples/sample_ecu_log.json',
        ]
        
        for filename in required_examples:
            file_path = PROJECT_ROOT / filename
            assert file_path.exists(), f"Required example file '{filename}' does not exist"
            assert file_path.is_file(), f"'{filename}' exists but is not a file"
    
    def test_github_workflow_exists(self):
        """Test that GitHub Actions workflow file exists"""
        workflow_file = PROJECT_ROOT / '.github' / 'workflows' / 'ci.yml'
        assert workflow_file.exists(), "GitHub Actions workflow file 'ci.yml' does not exist"
        assert workflow_file.is_file(), "ci.yml exists but is not a file"


class TestFileContent:
    """Test that key files have required content"""
    
    def test_dockerfile_has_multistage_build(self):
        """Test that Dockerfile uses multi-stage build"""
        dockerfile = PROJECT_ROOT / 'Dockerfile'
        content = dockerfile.read_text()
        
        # Check for multi-stage build keywords
        assert 'FROM' in content, "Dockerfile missing FROM instruction"
        assert 'as builder' in content.lower() or 'AS builder' in content, \
            "Dockerfile missing builder stage"
    
    def test_dockerfile_exposes_port(self):
        """Test that Dockerfile exposes port 8000"""
        dockerfile = PROJECT_ROOT / 'Dockerfile'
        content = dockerfile.read_text()
        
        assert 'EXPOSE 8000' in content or 'EXPOSE  8000' in content, \
            "Dockerfile does not expose port 8000"
    
    def test_dockerfile_has_healthcheck(self):
        """Test that Dockerfile includes health check"""
        dockerfile = PROJECT_ROOT / 'Dockerfile'
        content = dockerfile.read_text()
        
        assert 'HEALTHCHECK' in content, "Dockerfile missing HEALTHCHECK instruction"
    
    def test_gitignore_excludes_build_artifacts(self):
        """Test that .gitignore excludes build artifacts"""
        gitignore = PROJECT_ROOT / '.gitignore'
        content = gitignore.read_text(encoding='utf-8')
        
        required_patterns = [
            '__pycache__',
            '*.py[cod]',  # Covers *.pyc, *.pyo, *.pyd
            '.pytest_cache',
        ]
        
        for pattern in required_patterns:
            assert pattern in content, f".gitignore missing pattern '{pattern}'"
    
    def test_dockerignore_excludes_unnecessary_files(self):
        """Test that .dockerignore excludes unnecessary files"""
        dockerignore = PROJECT_ROOT / '.dockerignore'
        content = dockerignore.read_text()
        
        required_patterns = [
            '__pycache__',
            '.git',
            'tests',
        ]
        
        for pattern in required_patterns:
            assert pattern in content, f".dockerignore missing pattern '{pattern}'"
    
    def test_github_workflow_has_required_stages(self):
        """Test that GitHub Actions workflow has required stages"""
        workflow_file = PROJECT_ROOT / '.github' / 'workflows' / 'ci.yml'
        content = workflow_file.read_text()
        
        required_stages = [
            'checkout',
            'python',
            'dependencies',
            'test',
        ]
        
        content_lower = content.lower()
        for stage in required_stages:
            assert stage in content_lower, \
                f"GitHub Actions workflow missing '{stage}' stage"
    
    def test_jenkinsfile_has_required_stages(self):
        """Test that Jenkinsfile has required stages"""
        jenkinsfile = PROJECT_ROOT / 'Jenkinsfile'
        content = jenkinsfile.read_text()
        
        required_stages = [
            'Checkout',
            'Dependencies',
            'Lint',
            'Test',
            'Build',
        ]
        
        for stage in required_stages:
            assert stage in content, f"Jenkinsfile missing '{stage}' stage"
    
    def test_scripts_have_shebang(self):
        """Test that shell scripts have proper shebang"""
        scripts = [
            'scripts/dev.sh',
            'scripts/test.sh',
            'scripts/build.sh',
            'scripts/deploy.sh',
        ]
        
        for script_path in scripts:
            file_path = PROJECT_ROOT / script_path
            if file_path.exists():
                content = file_path.read_text(encoding='utf-8')
                assert content.startswith('#!/bin/bash') or content.startswith('#!/bin/sh'), \
                    f"Script '{script_path}' missing proper shebang"
    
    def test_readme_has_toolchain_section(self):
        """Test that README includes engineering toolchain information"""
        readme = PROJECT_ROOT / 'README.md'
        content = readme.read_text(encoding='utf-8')
        
        required_keywords = [
            'toolchain',
            'docker',
            'dashboard',
        ]
        
        content_lower = content.lower()
        for keyword in required_keywords:
            assert keyword in content_lower, \
                f"README missing '{keyword}' information"
        
        # Check for CI/CD (can be "CI", "ci/cd", or similar)
        assert 'ci' in content_lower, "README missing CI/CD information"
    
    def test_changelog_has_version_entries(self):
        """Test that CHANGELOG has version entries"""
        changelog = PROJECT_ROOT / 'CHANGELOG.md'
        content = changelog.read_text()
        
        # Check for version format [X.Y.Z]
        assert '[' in content and ']' in content, \
            "CHANGELOG missing version entries"
        
        # Check for standard sections
        assert '### Added' in content or '### Changed' in content, \
            "CHANGELOG missing standard sections"


class TestProjectConfiguration:
    """Test project configuration files"""
    
    def test_pytest_ini_exists(self):
        """Test that pytest.ini configuration exists"""
        pytest_ini = PROJECT_ROOT / 'pytest.ini'
        assert pytest_ini.exists(), "pytest.ini configuration file does not exist"
    
    def test_requirements_txt_not_empty(self):
        """Test that requirements.txt is not empty"""
        requirements = PROJECT_ROOT / 'requirements.txt'
        content = requirements.read_text().strip()
        
        assert len(content) > 0, "requirements.txt is empty"
        assert 'fastapi' in content.lower(), "requirements.txt missing fastapi"
        assert 'pytest' in content.lower(), "requirements.txt missing pytest"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
