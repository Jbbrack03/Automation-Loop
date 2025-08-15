#!/usr/bin/env python3
"""Quick test runner to establish baseline before refactoring."""
import subprocess
import sys
import os

def main():
    """Run pytest to establish baseline before refactoring."""
    os.chdir("/Users/jbbrack03/Claude_Development_Loop")
    
    print("Running baseline test suite...")
    
    try:
        # Run pytest on the tests directory
        result = subprocess.run(['python', '-m', 'pytest', 'tests/', '-v'],
                              capture_output=True, text=True, timeout=60)
        
        print("=" * 60)
        print("PYTEST OUTPUT:")
        print("=" * 60)
        print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
            
        print(f"\nExit code: {result.returncode}")
        
        if result.returncode == 0:
            print("\n✅ All tests PASSED - Ready to refactor!")
        else:
            print("\n❌ Tests FAILED - Cannot proceed with refactoring")
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Tests timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
