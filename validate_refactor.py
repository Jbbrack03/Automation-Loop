#!/usr/bin/env python3
"""Validate refactored calculate_wait_time function."""

import subprocess
import sys
import os

def run_original_test():
    """Run the original pytest to ensure refactoring didn't break functionality."""
    os.chdir("/Users/jbbrack03/Claude_Development_Loop")
    
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/test_orchestrator.py::TestOrchestrator::test_calculate_wait_time_unix_timestamp_format_returns_correct_seconds",
        "-v", "--tb=short", "--no-header"
    ]
    
    print("Running original calculate_wait_time test after refactoring...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    success = result.returncode == 0
    print(f"Original test {'PASSED' if success else 'FAILED'}")
    
    if result.stdout:
        print("STDOUT:")
        print(result.stdout)
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    return success

def check_imports():
    """Check that our new constant is properly defined."""
    try:
        # Try importing to check syntax
        sys.path.insert(0, "/Users/jbbrack03/Claude_Development_Loop")
        from automate_dev import calculate_wait_time, MIN_WAIT_TIME
        print(f"✓ MIN_WAIT_TIME constant defined: {MIN_WAIT_TIME}")
        print(f"✓ calculate_wait_time function importable")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

if __name__ == "__main__":
    print("=== Refactoring Validation ===")
    
    imports_ok = check_imports()
    if not imports_ok:
        print("❌ Imports failed - refactoring has syntax errors")
        sys.exit(1)
    
    test_ok = run_original_test()
    if not test_ok:
        print("❌ Original test failed - refactoring broke functionality")
        sys.exit(1)
    
    print("🎉 Refactoring validation successful!")