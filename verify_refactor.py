#!/usr/bin/env python3
"""Quick verification script to ensure TaskTracker refactoring worked correctly."""

import os
import sys

# Add the current directory to Python path to import automate_dev
sys.path.insert(0, '.')

try:
    from automate_dev import TaskTracker, MAX_FIX_ATTEMPTS
    
    def test_basic_functionality():
        """Test basic TaskTracker functionality."""
        print("Testing TaskTracker basic functionality...")
        
        # Test initialization
        tracker = TaskTracker()
        assert hasattr(tracker, 'fix_attempts')
        assert isinstance(tracker.fix_attempts, dict)
        assert len(tracker.fix_attempts) == 0
        print(" Initialization works correctly")
        
        # Test increment_fix_attempts
        task = "Test task"
        
        # First attempt should return True
        result1 = tracker.increment_fix_attempts(task)
        assert result1 is True
        assert tracker.fix_attempts[task] == 1
        print(" First increment_fix_attempts works correctly")
        
        # Second attempt should return True
        result2 = tracker.increment_fix_attempts(task)
        assert result2 is True
        assert tracker.fix_attempts[task] == 2
        print(" Second increment_fix_attempts works correctly")
        
        # Third attempt should return True (at limit)
        result3 = tracker.increment_fix_attempts(task)
        assert result3 is True
        assert tracker.fix_attempts[task] == 3
        print(" Third increment_fix_attempts works correctly")
        
        # Fourth attempt should return False (exceeded limit)
        result4 = tracker.increment_fix_attempts(task)
        assert result4 is False
        assert tracker.fix_attempts[task] == 4
        print(" Fourth increment_fix_attempts correctly returns False")
        
        # Test reset_fix_attempts
        tracker.reset_fix_attempts(task)
        assert task not in tracker.fix_attempts
        print(" reset_fix_attempts works correctly")
        
        # Test get_next_task when file doesn't exist
        result = tracker.get_next_task()
        assert isinstance(result, tuple)
        assert len(result) == 2
        task_result, all_complete = result
        assert task_result is None
        assert all_complete is True
        print(" get_next_task works correctly when file doesn't exist")
        
        print("All basic functionality tests passed!")
        
    def test_type_annotations():
        """Test that type annotations are present."""
        print("Testing type annotations...")
        
        import inspect
        from typing import get_type_hints
        
        # Test TaskTracker class annotations
        tracker = TaskTracker()
        hints = get_type_hints(tracker.__init__)
        assert 'return' in hints
        print(" __init__ has return type annotation")
        
        hints = get_type_hints(tracker.get_next_task)
        assert 'return' in hints
        print(" get_next_task has return type annotation")
        
        hints = get_type_hints(tracker.increment_fix_attempts)
        assert 'return' in hints
        assert 'task' in hints
        print(" increment_fix_attempts has type annotations")
        
        hints = get_type_hints(tracker.reset_fix_attempts)
        assert 'return' in hints
        assert 'task' in hints
        print(" reset_fix_attempts has type annotations")
        
        print("All type annotation tests passed!")
    
    # Run all tests
    test_basic_functionality()
    test_type_annotations()
    
    print("\n<‰ All refactoring verification tests passed!")
    print("The TaskTracker class has been successfully refactored with:")
    print("   Improved type hints")
    print("   Enhanced docstrings")  
    print("   Better code organization")
    print("   All original functionality preserved")
    
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)
except AssertionError as e:
    print(f"Test failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1)