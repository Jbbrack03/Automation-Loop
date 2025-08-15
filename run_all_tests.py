#!/usr/bin/env python3
"""Comprehensive test runner to verify refactoring didn't break anything."""
import subprocess
import sys
import os

def run_pytest_tests():
    """Run the full pytest suite."""
    print("\n" + "="*60)
    print("RUNNING PYTEST SUITE")
    print("="*60)
    
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v"],
        cwd="/Users/jbbrack03/Claude_Development_Loop",
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
        
    return result.returncode == 0

def run_refactoring_tests():
    """Run our specific refactoring tests."""
    print("\n" + "="*60)
    print("RUNNING REFACTORING TESTS")
    print("="*60)
    
    test_files = [
        "test_refactor_validation.py",
        "test_refactored_function.py",
        "check_code_quality.py"
    ]
    
    all_passed = True
    
    for test_file in test_files:
        if os.path.exists(f"/Users/jbbrack03/Claude_Development_Loop/{test_file}"):
            print(f"\n--- Running {test_file} ---")
            result = subprocess.run(
                [sys.executable, test_file],
                cwd="/Users/jbbrack03/Claude_Development_Loop",
                capture_output=True,
                text=True
            )
            
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
                
            if result.returncode != 0:
                all_passed = False
                print(f"\n❌ {test_file} FAILED")
            else:
                print(f"\n✅ {test_file} PASSED")
    
    return all_passed

if __name__ == "__main__":
    print("Running comprehensive test suite to verify refactoring...")
    
    os.chdir("/Users/jbbrack03/Claude_Development_Loop")
    
    # Run pytest tests first
    pytest_passed = run_pytest_tests()
    
    # Run refactoring specific tests
    refactor_passed = run_refactoring_tests()
    
    # Final summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    if pytest_passed and refactor_passed:
        print("✅ ALL TESTS PASSED - REFACTORING SUCCESSFUL!")
        print("\nRefactoring completed successfully:")
        print("- calculate_wait_time function refactored")
        print("- Helper functions extracted")
        print("- Constants added for magic values")
        print("- Imports moved to top of file")
        print("- All tests remain green")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        if not pytest_passed:
            print("- Pytest suite failed")
        if not refactor_passed:
            print("- Refactoring tests failed")
        sys.exit(1)