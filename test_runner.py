#!/usr/bin/env python3
"""Simple test runner to validate calculate_wait_time functionality."""

import subprocess
import sys
import os

def run_specific_test():
    """Run the calculate_wait_time test to ensure baseline is working."""
    os.chdir("/Users/jbbrack03/Claude_Development_Loop")
    
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/test_orchestrator.py::TestOrchestrator::test_calculate_wait_time_unix_timestamp_format_returns_correct_seconds",
        "-v", "--tb=short"
    ]
    
    print("Running calculate_wait_time test...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(f"Return code: {result.returncode}")
    print("STDOUT:")
    print(result.stdout)
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    return result.returncode == 0

if __name__ == "__main__":
    success = run_specific_test()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)