#!/usr/bin/env python3
"""
Jenkins Simulation Script

This script simulates a Jenkins build by running tests and reporting results.
It can be used for demonstration purposes when Jenkins is not available.
"""

import sys
import subprocess
import time
from datetime import datetime
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")

def print_step(step_num, total_steps, description):
    """Print step information"""
    print(f"[{step_num}/{total_steps}] {description}...")

def run_command(command, description):
    """Run a command and return success status"""
    print(f"  → {description}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode == 0:
            print(f"  ✓ {description} - SUCCESS")
            return True
        else:
            print(f"  ✗ {description} - FAILED")
            if result.stderr:
                print(f"    Error: {result.stderr[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"  ✗ {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"  ✗ {description} - ERROR: {str(e)}")
        return False

def main():
    """Main Jenkins simulation workflow"""
    start_time = time.time()
    
    print_header("JENKINS BUILD SIMULATION")
    print(f"Build Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Job: ecu-log-visualizer")
    print(f"Build #: {int(time.time())}")
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    
    results = []
    total_steps = 5
    
    # Step 1: Checkout
    print_step(1, total_steps, "Checkout Source Code")
    results.append(run_command("git status", "Verify Git repository"))
    time.sleep(1)
    
    # Step 2: Install Dependencies
    print_step(2, total_steps, "Install Dependencies")
    results.append(run_command("pip install -q -r requirements.txt", "Install Python packages"))
    time.sleep(2)
    
    # Step 3: Lint
    print_step(3, total_steps, "Code Quality Check")
    # Linting is optional, don't fail build on lint errors
    run_command("pip install -q flake8", "Install flake8")
    run_command("flake8 src/ --max-line-length=120 --exclude=__pycache__ || true", "Run linter")
    results.append(True)  # Don't fail on lint
    time.sleep(1)
    
    # Step 4: Run Tests
    print_step(4, total_steps, "Run Automated Tests")
    test_result = run_command(
        "pytest tests/unit/ -v --tb=short",
        "Execute unit tests"
    )
    results.append(test_result)
    time.sleep(2)
    
    # Step 5: Build Verification
    print_step(5, total_steps, "Build Verification")
    results.append(run_command(
        'python -c "from src.main import app; print(\'Application imports successfully\')"',
        "Verify application imports"
    ))
    time.sleep(1)
    
    # Calculate results
    duration = time.time() - start_time
    success_count = sum(results)
    total_count = len(results)
    
    # Print summary
    print_header("BUILD SUMMARY")
    print(f"Total Steps: {total_count}")
    print(f"Successful: {success_count}")
    print(f"Failed: {total_count - success_count}")
    print(f"Duration: {duration:.1f} seconds")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if all(results):
        print("\n✓ BUILD SUCCESSFUL")
        print("=" * 70 + "\n")
        return 0
    else:
        print("\n✗ BUILD FAILED")
        print("=" * 70 + "\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
