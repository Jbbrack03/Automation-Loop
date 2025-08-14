#!/usr/bin/env python3
"""Quick test to verify TaskTracker refactoring maintains functionality."""

import sys
import os

# Test the basic functionality
try:
    from automate_dev import TaskTracker, MAX_FIX_ATTEMPTS
    
    def test_tasktracker():
        print("Testing refactored TaskTracker...")
        
        # Test 1: Basic initialization
        tracker = TaskTracker()
        assert hasattr(tracker, 'fix_attempts')
        assert isinstance(tracker.fix_attempts, dict)
        print("✓ Initialization successful")
        
        # Test 2: Failure tracking
        task = "Test task"
        
        # Should return True for attempts 1, 2, 3
        for i in range(1, 4):
            result = tracker.increment_fix_attempts(task)
            assert result is True, f"Expected True for attempt {i}"
            assert tracker.fix_attempts[task] == i, f"Expected count {i}"
        print("✓ increment_fix_attempts working correctly for attempts 1-3")
        
        # Should return False for attempt 4 (exceeds MAX_FIX_ATTEMPTS=3)
        result = tracker.increment_fix_attempts(task)
        assert result is False, "Expected False when exceeding MAX_FIX_ATTEMPTS"
        assert tracker.fix_attempts[task] == 4, "Expected count 4"
        print("✓ increment_fix_attempts correctly returns False when limit exceeded")
        
        # Test 3: Reset functionality
        tracker.reset_fix_attempts(task)
        assert task not in tracker.fix_attempts, "Task should be removed after reset"
        print("✓ reset_fix_attempts working correctly")
        
        # Test 4: get_next_task when file doesn't exist
        result = tracker.get_next_task()
        assert isinstance(result, tuple), "Should return tuple"
        assert len(result) == 2, "Should return 2-element tuple"
        task_result, all_complete = result
        assert task_result is None, "Should return None when no file exists"
        assert all_complete is True, "Should return True when no file exists"
        print("✓ get_next_task working correctly when file doesn't exist")
        
        print("\n🎉 ALL TESTS PASSED!")
        print("TaskTracker refactoring successful - all functionality preserved")
        return True
        
    # Run the test
    test_tasktracker()
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)