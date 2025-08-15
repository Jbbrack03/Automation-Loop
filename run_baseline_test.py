#!/usr/bin/env python3
"""Run baseline tests before refactoring."""
import subprocess
import sys
import os

def main():
    os.chdir("/Users/jbbrack03/Claude_Development_Loop")
    
    print("Running baseline test suite before refactoring...")
    print("=" * 60)
    
    result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"], 
                          text=True)
    
    if result.returncode == 0:
        print("\n✅ All tests PASSED - Proceeding with refactoring!")
        return True
    else:
        print("\n❌ Tests FAILED - Cannot proceed with refactoring")
        return False

if __name__ == "__main__":
    success = main()
    print(f"\nBaseline test result: {'PASS' if success else 'FAIL'}")
    sys.exit(0 if success else 1)
