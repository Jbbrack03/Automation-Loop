#!/usr/bin/env python3
"""Test the refactored get_latest_status function to ensure all functionality preserved."""

import tempfile
import json
import os
import sys

def test_refactored_get_latest_status():
    """Test all scenarios to ensure refactoring preserved behavior."""
    
    # Import the refactored function
    sys.path.insert(0, '/Users/jbbrack03/Claude_Development_Loop')
    from automate_dev import get_latest_status
    
    # Save current directory
    original_dir = os.getcwd()
    
    try:
        # Create temporary directory and change to it
        with tempfile.TemporaryDirectory() as tmp_dir:
            os.chdir(tmp_dir)
            
            # Test 1: No .claude directory - should return None
            result = get_latest_status()
            assert result is None, f"Expected None when .claude directory missing, got {result}"
            print("✓ Test 1 passed: Returns None when .claude directory missing")
            
            # Create .claude directory
            claude_dir = os.path.join(tmp_dir, '.claude')
            os.makedirs(claude_dir)
            
            # Test 2: No status files - should return None
            result = get_latest_status()
            assert result is None, f"Expected None when no files exist, got {result}"
            print("✓ Test 2 passed: Returns None when no status files exist")
            
            # Test 3: Create status files and verify newest is read
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
            print("✓ Test 3 passed: Returns status from newest file")
            
            # Test 4: Verify all files are deleted
            remaining_files = [f for f in os.listdir(claude_dir) if f.startswith('status_')]
            assert len(remaining_files) == 0, f"Expected no status files remaining, found {remaining_files}"
            print("✓ Test 4 passed: All status files deleted after reading")
            
            # Test 5: Test with debug logging
            for filename, data in status_files.items():
                filepath = os.path.join(claude_dir, filename)
                with open(filepath, 'w') as f:
                    json.dump(data, f)
            
            print("\n--- Testing debug mode ---")
            result = get_latest_status(debug=True)
            assert result == 'newest_status', f"Expected 'newest_status' in debug mode, got {result}"
            print("✓ Test 5 passed: Debug mode works correctly")
            
            # Test 6: Test malformed JSON handling
            with open(os.path.join(claude_dir, 'status_20240101_150000.json'), 'w') as f:
                f.write('{"invalid": json}')  # Invalid JSON
            
            result = get_latest_status()
            assert result is None, f"Expected None for malformed JSON, got {result}"
            print("✓ Test 6 passed: Handles malformed JSON gracefully")
            
            print("\n✅ All refactored function tests passed!")
            return True
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        os.chdir(original_dir)

if __name__ == "__main__":
    success = test_refactored_get_latest_status()
    sys.exit(0 if success else 1)