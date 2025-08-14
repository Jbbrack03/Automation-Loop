#!/usr/bin/env python3
"""Test the current get_latest_status function to establish baseline before refactoring."""

import tempfile
import json
import os
import sys

def test_get_latest_status_basic():
    """Basic test to verify get_latest_status works before refactoring."""
    
    # Import the function
    sys.path.insert(0, '/Users/jbbrack03/Claude_Development_Loop')
    from automate_dev import get_latest_status
    
    # Save current directory
    original_dir = os.getcwd()
    
    try:
        # Create temporary directory and change to it
        with tempfile.TemporaryDirectory() as tmp_dir:
            os.chdir(tmp_dir)
            
            # Create .claude directory
            claude_dir = os.path.join(tmp_dir, '.claude')
            os.makedirs(claude_dir)
            
            # Test 1: No status files - should return None
            result = get_latest_status()
            assert result is None, f"Expected None when no files exist, got {result}"
            print("✓ Test 1 passed: Returns None when no status files exist")
            
            # Test 2: Create status files and verify newest is read
            status_files = {
                'status_20240101_120000.json': {'status': 'old_status'},
                'status_20240101_140000.json': {'status': 'newest_status'},
                'status_20240101_130000.json': {'status': 'middle_status'}
            }
            
            for filename, data in status_files.items():
                filepath = os.path.join(claude_dir, filename)
                with open(filepath, 'w') as f:
                    json.dump(data, f)
            
            # Call function
            result = get_latest_status()
            assert result == 'newest_status', f"Expected 'newest_status', got {result}"
            print("✓ Test 2 passed: Returns status from newest file")
            
            # Test 3: Verify all files are deleted
            remaining_files = [f for f in os.listdir(claude_dir) if f.startswith('status_')]
            assert len(remaining_files) == 0, f"Expected no status files remaining, found {remaining_files}"
            print("✓ Test 3 passed: All status files deleted after reading")
            
            print("\n✅ All baseline tests passed! Ready for refactoring.")
            return True
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        os.chdir(original_dir)

if __name__ == "__main__":
    success = test_get_latest_status_basic()
    sys.exit(0 if success else 1)