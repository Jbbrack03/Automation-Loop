"""
Tests for file I/O optimization in TaskTracker module.

This test file verifies that TaskTracker implements file caching for Implementation_Plan.md
to avoid repeated file I/O operations during frequent get_next_task() calls.

Phase 13, Task 13.1: Optimize file I/O operations by implementing caching for frequently read files.
"""

import sys
import os
import time
import logging
from unittest.mock import patch, mock_open, Mock
from pathlib import Path

# Add parent directory to path so we can import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from task_tracker import TaskTracker
from config import IMPLEMENTATION_PLAN_FILE, LOGGERS


class TestFileIOOptimization:
    """Test suite for file I/O optimization through caching."""
    
    def setup_method(self):
        """Set up mock logger for each test method."""
        # Store original logger state for cleanup
        self.original_logger = LOGGERS['task_tracker']
        # Mock the logger to avoid AttributeError on None
        mock_logger = Mock()
        LOGGERS['task_tracker'] = mock_logger
    
    def teardown_method(self):
        """Clean up after each test method."""
        # Restore original logger state
        LOGGERS['task_tracker'] = self.original_logger
    
    def test_implementation_plan_file_caching_behavior(self, tmp_path, monkeypatch):
        """
        Test that TaskTracker caches Implementation_Plan.md content to minimize file I/O operations.
        
        This test verifies the caching optimization for Task 13.1:
        1. File is read only once when get_next_task() is called multiple times
        2. Cache is invalidated when the file is modified (mtime changes)
        3. Multiple calls to get_next_task() without file changes use cached content
        4. File modification triggers cache invalidation and re-reading
        
        This test follows the FIRST principles:
        - Fast: Uses in-memory mocking for file operations
        - Independent: Creates isolated temporary environment
        - Repeatable: Deterministic file mocking with controlled content
        - Self-validating: Clear assertions on file read count and cache behavior
        - Timely: Written before cache implementation exists (red phase of TDD)
        
        The test will fail initially because TaskTracker currently reads the file
        on every get_next_task() call without any caching mechanism.
        """
        # Change to temporary directory
        monkeypatch.chdir(tmp_path)
        
        # Create test Implementation Plan content
        test_plan_content = """# Implementation Plan

## Phase 1: Development
- [ ] Implement user authentication
- [ ] Create database schema
- [X] Completed task

## Phase 2: Testing
- [ ] Write integration tests
"""
        
        # Create the Implementation Plan file
        plan_file = tmp_path / IMPLEMENTATION_PLAN_FILE
        plan_file.write_text(test_plan_content, encoding='utf-8')
        
        # Track file reads using mock
        original_open = open
        file_read_count = 0
        
        def mock_file_open(*args, **kwargs):
            nonlocal file_read_count
            # Only count reads of the Implementation Plan file
            if len(args) > 0 and IMPLEMENTATION_PLAN_FILE in str(args[0]):
                file_read_count += 1
            return original_open(*args, **kwargs)
        
        # Initialize TaskTracker instance
        tracker = TaskTracker()
        
        with patch('builtins.open', side_effect=mock_file_open):
            # First call to get_next_task() - should read file and cache content
            first_task, first_complete = tracker.get_next_task()
            assert first_task == "Implement user authentication", "First task should be the first incomplete task"
            assert not first_complete, "Project should not be complete yet"
            initial_read_count = file_read_count
            assert initial_read_count == 1, f"File should be read exactly once on first call, but was read {initial_read_count} times"
            
            # Second call to get_next_task() - should use cached content, no additional file read
            second_task, second_complete = tracker.get_next_task()
            assert second_task == "Implement user authentication", "Second task should be same as first (cached)"
            assert not second_complete, "Project should still not be complete"
            after_second_call_count = file_read_count
            assert after_second_call_count == initial_read_count, f"File should not be read again on second call (cache hit), but read count increased from {initial_read_count} to {after_second_call_count}"
            
            # Third call to get_next_task() - should still use cached content
            third_task, third_complete = tracker.get_next_task()
            assert third_task == "Implement user authentication", "Third task should be same as previous (cached)"
            assert not third_complete, "Project should still not be complete"
            after_third_call_count = file_read_count
            assert after_third_call_count == initial_read_count, f"File should not be read again on third call (cache hit), but read count increased from {initial_read_count} to {after_third_call_count}"
        
        # Now modify the file to simulate external changes (e.g., task completion)
        modified_content = """# Implementation Plan

## Phase 1: Development
- [X] Implement user authentication
- [ ] Create database schema
- [X] Completed task

## Phase 2: Testing
- [ ] Write integration tests
"""
        plan_file.write_text(modified_content, encoding='utf-8')
        
        # Add a small delay to ensure mtime difference is detectable
        time.sleep(0.01)
        
        with patch('builtins.open', side_effect=mock_file_open):
            # Reset file read counter for this part of the test
            pre_modification_count = file_read_count
            
            # Call get_next_task() after file modification - should invalidate cache and re-read
            post_mod_task, post_mod_complete = tracker.get_next_task()
            assert post_mod_task == "Create database schema", "Task should change after file modification (cache invalidated)"
            assert not post_mod_complete, "Project should still not be complete"
            post_modification_count = file_read_count
            assert post_modification_count > pre_modification_count, f"File should be re-read after modification (cache miss), but read count remained {post_modification_count}"
            
            # Subsequent call should use the new cached content
            final_task, final_complete = tracker.get_next_task()
            assert final_task == "Create database schema", "Final task should be same as post-modification (cached)"
            assert not final_complete, "Project should still not be complete"
            final_count = file_read_count
            assert final_count == post_modification_count, f"File should not be read again after cache refresh (cache hit), but read count increased from {post_modification_count} to {final_count}"
        
        # Summary assertions for the complete caching behavior
        # This test will fail initially because current TaskTracker implementation
        # reads the file on every get_next_task() call without any caching
        expected_total_reads = 2  # Once initially, once after modification
        actual_total_reads = file_read_count
        assert actual_total_reads == expected_total_reads, (
            f"Total file reads should be minimized through caching. "
            f"Expected {expected_total_reads} reads (initial + after modification), "
            f"but got {actual_total_reads} reads. "
            f"This indicates caching is not implemented yet."
        )