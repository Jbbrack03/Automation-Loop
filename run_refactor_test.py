#!/usr/bin/env python3
"""Test runner to validate refactoring maintains green tests."""
import subprocess
import sys

def run_test():
    result = subprocess.run(
        [sys.executable, "test_refactor_validation.py"],
        capture_output=True,
        text=True,
        cwd="/Users/jbbrack03/Claude_Development_Loop"
    )
    
    print("STDOUT:")
    print(result.stdout)
    if result.stderr:
        print("\nSTDERR:")
        print(result.stderr)
    
    print(f"\nReturn code: {result.returncode}")
    return result.returncode == 0

if __name__ == "__main__":
    success = run_test()
    if success:
        print("\n✅ All tests passed - ready for refactoring")
    else:
        print("\n❌ Tests failed - fix before refactoring")
    sys.exit(0 if success else 1)