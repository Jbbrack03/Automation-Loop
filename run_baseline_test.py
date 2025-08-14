#!/usr/bin/env python3
"""Simple baseline test for get_latest_status before refactoring."""

import tempfile
import json
import os
import sys

# Test 1: Basic functionality
sys.path.insert(0, '/Users/jbbrack03/Claude_Development_Loop')
from automate_dev import get_latest_status

original_dir = os.getcwd()

try:
    with tempfile.TemporaryDirectory() as tmp_dir:
        os.chdir(tmp_dir)
        
        # Create .claude directory
        claude_dir = os.path.join(tmp_dir, '.claude')
        os.makedirs(claude_dir)
        
        # Test: No status files - should return None
        result = get_latest_status()
        assert result is None
        print("✓ Baseline test 1 passed: Returns None when no files exist")
        
        # Create test files
        status_files = {
            'status_20240101_120000.json': {'status': 'old_status'},
            'status_20240101_140000.json': {'status': 'newest_status'},
            'status_20240101_130000.json': {'status': 'middle_status'}
        }
        
        for filename, data in status_files.items():
            filepath = os.path.join(claude_dir, filename)
            with open(filepath, 'w') as f:
                json.dump(data, f)
        
        # Test newest file read
        result = get_latest_status()
        assert result == 'newest_status'
        print("✓ Baseline test 2 passed: Returns newest status")
        
        # Test files cleaned up
        remaining_files = [f for f in os.listdir(claude_dir) if f.startswith('status_')]
        assert len(remaining_files) == 0
        print("✓ Baseline test 3 passed: Files cleaned up")
        
        print("\n✅ Baseline established - all tests passed!")
        
except Exception as e:
    print(f"❌ Baseline test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    os.chdir(original_dir)