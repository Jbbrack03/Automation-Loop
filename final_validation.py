#!/usr/bin/env python3
"""Final validation that refactoring maintained green tests."""
import subprocess
import sys
import os

def main():
    os.chdir("/Users/jbbrack03/Claude_Development_Loop")
    
    print("\n" + "=" * 80)
    print("FINAL REFACTORING VALIDATION")
    print("=" * 80)
    print("\nValidating that all refactoring maintained green tests...")
    
    # Run the full test suite with detailed output
    result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"], 
                          capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    print("\n" + "=" * 80)
    
    if result.returncode == 0:
        print("✅ SUCCESS: All tests remain green after refactoring!")
        
        # Import and show the summary
        try:
            from refactoring_summary import show_refactoring_summary
            show_refactoring_summary()
        except ImportError:
            print("Summary module not available")
        
        print("\n🎉 TDD REFACTOR PHASE COMPLETED SUCCESSFULLY")
        print("\nOrchestrator can be notified that this TDD cycle is complete.")
        return True
    else:
        print(f"❌ FAILED: Tests are failing (exit code: {result.returncode})")
        print("Refactoring may have introduced issues that need to be addressed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
