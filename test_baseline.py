#!/usr/bin/env python3
"""Run baseline tests before refactoring to ensure all tests pass."""

import subprocess
import sys
import os

def run_tests():
    """Run pytest to establish baseline before refactoring."""
    try:
        # Change to project directory
        os.chdir('/Users/jbbrack03/Claude_Development_Loop')
        
        # Run pytest on the tests directory
        result = subprocess.run(['pytest', 'tests/', '-v'], 
                              capture_output=True, text=True)
        
        print("PYTEST OUTPUT:")
        print("=" * 50)
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        print("=" * 50)
        print(f"Return code: {result.returncode}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error running tests: {e}")
        return False

if __name__ == "__main__":
    success = run_tests()
    if success:
        print("✅ All tests pass - ready for refactoring!")
    else:
        print("❌ Tests failing - cannot proceed with refactoring")
        sys.exit(1)