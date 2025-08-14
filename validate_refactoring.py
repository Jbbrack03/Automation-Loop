#!/usr/bin/env python3
"""Validate that the get_latest_status refactoring maintains all functionality."""

import tempfile
import json
import os
import sys

def run_all_validation_tests():
    """Run comprehensive validation tests."""
    
    print("=== VALIDATING GET_LATEST_STATUS REFACTORING ===\n")
    
    # Import the refactored function
    sys.path.insert(0, '/Users/jbbrack03/Claude_Development_Loop')
    
    # Test 1: Import succeeds
    try:
        from automate_dev import get_latest_status, _cleanup_status_files
        print("✓ Import successful - function and helper exist")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Test 2: Function signature compatibility
    import inspect
    sig = inspect.signature(get_latest_status)
    if len(sig.parameters) == 1 and 'debug' in sig.parameters:
        default_value = sig.parameters['debug'].default
        if default_value is False:
            print("✓ Function signature compatible - debug parameter has default False")
        else:
            print(f"❌ Debug parameter default should be False, got {default_value}")
            return False
    else:
        print(f"❌ Function signature changed unexpectedly: {sig}")
        return False
    
    # Test 3: Basic functionality with existing calling pattern
    original_dir = os.getcwd()
    
    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            os.chdir(tmp_dir)
            
            # Test 3a: No .claude directory
            result = get_latest_status()
            assert result is None
            print("✓ Handles missing .claude directory correctly")
            
            # Create .claude directory
            claude_dir = os.path.join(tmp_dir, '.claude')
            os.makedirs(claude_dir)
            
            # Test 3b: No status files
            result = get_latest_status()
            assert result is None
            print("✓ Returns None when no status files exist")
            
            # Test 3c: Multiple status files - newest selected
            status_files = {
                'status_20240101_120000.json': {'status': 'old_status'},
                'status_20240101_140000.json': {'status': 'newest_status'},
                'status_20240101_130000.json': {'status': 'middle_status'}
            }
            
            for filename, data in status_files.items():
                filepath = os.path.join(claude_dir, filename)
                with open(filepath, 'w') as f:
                    json.dump(data, f)
            
            result = get_latest_status()
            assert result == 'newest_status'
            print("✓ Correctly reads newest status file")
            
            # Test 3d: All files cleaned up
            remaining_files = [f for f in os.listdir(claude_dir) if f.startswith('status_')]
            assert len(remaining_files) == 0
            print("✓ All status files cleaned up after reading")
            
            # Test 4: Debug mode functionality
            # Recreate files for debug test
            for filename, data in status_files.items():
                filepath = os.path.join(claude_dir, filename)
                with open(filepath, 'w') as f:
                    json.dump(data, f)
            
            print("\n--- Testing debug mode ---")
            result = get_latest_status(debug=True)
            assert result == 'newest_status'
            print("✓ Debug mode works correctly")
            
            # Test 5: Malformed JSON handling
            with open(os.path.join(claude_dir, 'status_20240101_150000.json'), 'w') as f:
                f.write('{invalid json}')
            
            result = get_latest_status()
            assert result is None
            print("✓ Handles malformed JSON gracefully")
            
            print("\n=== ALL VALIDATION TESTS PASSED ===")
            print("✅ Refactoring successful!")
            print("✅ All existing functionality preserved")
            print("✅ New debug capability added")
            print("✅ Better error handling implemented")
            print("✅ Code quality improved with helper function")
            return True
            
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        os.chdir(original_dir)

if __name__ == "__main__":
    success = run_all_validation_tests()
    sys.exit(0 if success else 1)