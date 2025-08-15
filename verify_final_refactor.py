#!/usr/bin/env python3
"""Final verification that all refactoring changes work correctly."""
import subprocess
import sys
import os

def run_tests():
    """Run both original and new tests to verify refactoring."""
    os.chdir('/Users/jbbrack03/Claude_Development_Loop')
    
    tests = [
        ('test_refactor_validation.py', 'Original validation test'),
        ('test_refactored_function.py', 'New refactored function test')
    ]
    
    all_passed = True
    
    for test_file, description in tests:
        print(f"\n{'='*60}")
        print(f"Running: {description}")
        print(f"File: {test_file}")
        print('='*60)
        
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
        if result.returncode != 0:
            print(f"\n❌ {description} FAILED (exit code: {result.returncode})")
            all_passed = False
        else:
            print(f"\n✅ {description} PASSED")
    
    return all_passed

if __name__ == "__main__":
    print("Verifying refactored calculate_wait_time function...")
    
    success = run_tests()
    
    if success:
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED - REFACTORING SUCCESSFUL!")
        print("\nRefactoring Summary:")
        print("- Extracted helper functions for better separation of concerns")
        print("- Added constants for magic values (12-hour conversion)")
        print("- Moved imports to top of file")
        print("- Improved error messages with more specific descriptions")
        print("- Reduced complexity of main function")
        print("- All tests remain green - behavior preserved")
        print("="*60)
    else:
        print("\n❌ SOME TESTS FAILED - REFACTORING NEEDS ATTENTION")
        sys.exit(1)