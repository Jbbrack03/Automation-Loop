#!/usr/bin/env python3
"""Run comprehensive validation after calculate_wait_time refactoring."""

import subprocess
import sys
import os

def run_all_tests():
    """Run all tests to ensure refactoring didn't break anything."""
    os.chdir("/Users/jbbrack03/Claude_Development_Loop")
    
    print("Running ALL tests to validate refactoring...")
    cmd = [sys.executable, "-m", "pytest", "-v", "--tb=short"]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(f"Overall test result: {'PASSED' if result.returncode == 0 else 'FAILED'}")
    
    if result.stdout:
        print("\nTest Output:")
        print(result.stdout)
    
    if result.stderr:
        print("\nErrors/Warnings:")
        print(result.stderr)
    
    return result.returncode == 0

def check_syntax():
    """Check that the refactored file has no syntax errors."""
    print("Checking syntax of refactored automate_dev.py...")
    
    cmd = [sys.executable, "-m", "py_compile", "automate_dev.py"]
    result = subprocess.run(cmd, cwd="/Users/jbbrack03/Claude_Development_Loop", capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Syntax check PASSED")
        return True
    else:
        print("❌ Syntax check FAILED")
        if result.stderr:
            print(result.stderr)
        return False

def main():
    """Main validation routine."""
    print("=== Refactoring Validation Report ===\n")
    
    # Check syntax first
    syntax_ok = check_syntax()
    if not syntax_ok:
        print("\n❌ REFACTORING FAILED: Syntax errors detected")
        return False
    
    # Run all tests
    tests_ok = run_all_tests()
    
    if tests_ok:
        print("\n🎉 REFACTORING SUCCESSFUL!")
        print("✅ All tests still pass")
        print("✅ No syntax errors")
        print("✅ calculate_wait_time refactoring complete")
    else:
        print("\n❌ REFACTORING FAILED: Some tests are failing")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)