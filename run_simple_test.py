#!/usr/bin/env python3
"""Simple test runner to verify get_latest_status tests are working before refactoring."""

import sys
import subprocess
import os

def run_specific_tests():
    """Run only the get_latest_status tests to verify current functionality."""
    os.chdir('/Users/jbbrack03/Claude_Development_Loop')
    
    # Try running the specific test class
    test_command = [
        sys.executable, '-m', 'pytest', 
        'tests/test_orchestrator.py::TestGetLatestStatus', 
        '-v', '--tb=short'
    ]
    
    print("Running get_latest_status tests...")
    print(f"Command: {' '.join(test_command)}")
    
    try:
        result = subprocess.run(test_command, capture_output=True, text=True, timeout=30)
        print("STDOUT:")
        print(result.stdout)
        print("\nSTDERR:")
        print(result.stderr)
        print(f"\nReturn code: {result.returncode}")
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("Tests timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"Error running tests: {e}")
        return False

if __name__ == "__main__":
    success = run_specific_tests()
    if success:
        print("\n✅ Tests passed - ready for refactoring!")
    else:
        print("\n❌ Tests failed - need to fix before refactoring")
        sys.exit(1)