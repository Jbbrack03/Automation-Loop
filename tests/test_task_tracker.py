"""
Tests for the TaskTracker module.

This test file verifies that TaskTracker can be imported from a separate task_tracker.py module
and that it maintains the expected interface and functionality when extracted from automate_dev.py.
"""

import sys
import os
# Add parent directory to path so we can import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest


class TestTaskTrackerModuleImport:
    """Test suite for TaskTracker module import and interface."""
    
    def test_task_tracker_import_and_interface(self):
        """
        Test that TaskTracker can be imported from task_tracker module and has expected interface.
        
        This test verifies:
        1. TaskTracker class can be imported from task_tracker module
        2. The class has all expected methods (get_next_task, increment_fix_attempts, reset_fix_attempts)
        3. The module has proper documentation (__doc__ attribute)
        4. The class can be instantiated successfully
        
        This test follows the FIRST principles:
        - Fast: Simple import and attribute checks
        - Independent: No external dependencies or state
        - Repeatable: Deterministic import behavior
        - Self-validating: Clear pass/fail criteria with descriptive assertions
        - Timely: Written before the module extraction is implemented
        """
        # Test that TaskTracker can be imported from separate module
        from task_tracker import TaskTracker
        
        # Verify the module has documentation
        import task_tracker
        assert task_tracker.__doc__ is not None, "task_tracker module should have documentation"
        assert len(task_tracker.__doc__.strip()) > 0, "task_tracker module documentation should not be empty"
        
        # Verify TaskTracker class can be instantiated
        tracker = TaskTracker()
        assert tracker is not None, "TaskTracker should be instantiable"
        
        # Verify TaskTracker has expected methods with correct signatures
        assert hasattr(tracker, 'get_next_task'), "TaskTracker should have get_next_task method"
        assert hasattr(tracker, 'increment_fix_attempts'), "TaskTracker should have increment_fix_attempts method"
        assert hasattr(tracker, 'reset_fix_attempts'), "TaskTracker should have reset_fix_attempts method"
        
        # Verify method callability (they should be methods, not just attributes)
        assert callable(getattr(tracker, 'get_next_task')), "get_next_task should be callable"
        assert callable(getattr(tracker, 'increment_fix_attempts')), "increment_fix_attempts should be callable"
        assert callable(getattr(tracker, 'reset_fix_attempts')), "reset_fix_attempts should be callable"
        
        # Verify TaskTracker has the fix_attempts attribute for failure tracking
        assert hasattr(tracker, 'fix_attempts'), "TaskTracker should have fix_attempts attribute"
        assert isinstance(tracker.fix_attempts, dict), "fix_attempts should be a dictionary"