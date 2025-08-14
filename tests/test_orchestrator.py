"""
Tests for the automate_dev.py orchestrator script.

This file contains TDD tests for the automated development workflow orchestrator.
Following the red-green-refactor cycle, these tests are written before implementation.
"""

import pytest
import sys
import os
from unittest.mock import patch

class TestOrchestratorScriptExecution:
    """Test suite for basic orchestrator script functionality."""
    
    def test_main_function_import_and_executable(self):
        """
        Test that the main function can be imported from automate_dev.py
        and that the script is executable.
        
        This test will initially fail because automate_dev.py doesn't exist yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Attempt to import the main function from automate_dev.py
        try:
            from automate_dev import main
            
            # Verify that main is callable (a function)
            assert callable(main), "main should be a callable function"
            
            # Verify that the main function can be called without error
            # (for now, we just check it exists and is callable)
            assert hasattr(main, '__call__'), "main should have __call__ attribute"
            
        except ImportError as e:
            # This is expected to fail initially - automate_dev.py doesn't exist yet
            pytest.fail(f"Cannot import main function from automate_dev.py: {e}")
        
    def test_automate_dev_script_exists(self):
        """
        Test that the automate_dev.py script file exists in the root directory.
        
        This test ensures the orchestrator script is present and readable.
        """
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "automate_dev.py")
        
        assert os.path.exists(script_path), f"automate_dev.py should exist at {script_path}"
        assert os.path.isfile(script_path), "automate_dev.py should be a file"
        assert os.access(script_path, os.R_OK), "automate_dev.py should be readable"


class TestOrchestratorPrerequisiteFileChecks:
    """Test suite for prerequisite file validation in the orchestrator."""
    
    def test_orchestrator_exits_gracefully_when_implementation_plan_missing(self, tmp_path, monkeypatch):
        """
        Test that the orchestrator exits gracefully with an error if Implementation Plan.md is missing.
        
        This test creates a temporary directory without the Implementation Plan.md file,
        changes to that directory, and verifies that the orchestrator exits with the
        appropriate error code and message.
        
        This test will initially fail because main() doesn't implement these checks yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Change to temporary directory where Implementation Plan.md doesn't exist
        monkeypatch.chdir(tmp_path)
        
        # Import main function to test
        from automate_dev import main
        
        # Mock sys.exit to capture exit calls and prevent actual exit
        with patch('sys.exit') as mock_exit:
            # Mock print to capture error messages
            with patch('builtins.print') as mock_print:
                # Call main function - it should detect missing Implementation Plan.md
                main()
                
                # Verify that sys.exit was called with error code (non-zero)
                mock_exit.assert_called_once()
                exit_code = mock_exit.call_args[0][0] if mock_exit.call_args[0] else 1
                assert exit_code != 0, "Expected non-zero exit code when Implementation Plan.md is missing"
                
                # Verify that an appropriate error message was printed
                mock_print.assert_called()
                printed_messages = [str(call.args[0]) for call in mock_print.call_args_list]
                error_message_found = any(
                    "Implementation Plan.md" in msg or "implementation plan" in msg.lower()
                    for msg in printed_messages
                )
                assert error_message_found, f"Expected error message about missing Implementation Plan.md, got: {printed_messages}"
    
    def test_orchestrator_prints_warning_when_prd_md_missing(self, tmp_path, monkeypatch):
        """
        Test that the orchestrator prints a warning if PRD.md is missing.
        
        This test creates a temporary directory with Implementation Plan.md present
        but PRD.md missing, and verifies that a warning is printed.
        
        This test will initially fail because main() doesn't implement these checks yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Change to temporary directory
        monkeypatch.chdir(tmp_path)
        
        # Create Implementation Plan.md to avoid the exit condition
        implementation_plan = tmp_path / "Implementation Plan.md"
        implementation_plan.write_text("# Implementation Plan\n\n- [ ] Task 1", encoding="utf-8")
        
        # Ensure PRD.md does NOT exist
        prd_file = tmp_path / "PRD.md"
        if prd_file.exists():
            prd_file.unlink()
        
        # Import main function to test
        from automate_dev import main
        
        # Mock sys.exit to prevent actual exit
        with patch('sys.exit') as mock_exit:
            # Mock print to capture warning messages
            with patch('builtins.print') as mock_print:
                # Call main function - it should detect missing PRD.md and print warning
                main()
                
                # Verify that an appropriate warning message was printed
                mock_print.assert_called()
                printed_messages = [str(call.args[0]) for call in mock_print.call_args_list]
                warning_message_found = any(
                    ("PRD.md" in msg and ("missing" in msg.lower() or "warning" in msg.lower()))
                    for msg in printed_messages
                )
                assert warning_message_found, f"Expected warning message about missing PRD.md, got: {printed_messages}"
    
    def test_orchestrator_prints_warning_when_claude_md_missing(self, tmp_path, monkeypatch):
        """
        Test that the orchestrator prints a warning if CLAUDE.md is missing.
        
        This test creates a temporary directory with Implementation Plan.md present
        but CLAUDE.md missing, and verifies that a warning is printed.
        
        This test will initially fail because main() doesn't implement these checks yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Change to temporary directory
        monkeypatch.chdir(tmp_path)
        
        # Create Implementation Plan.md to avoid the exit condition
        implementation_plan = tmp_path / "Implementation Plan.md"
        implementation_plan.write_text("# Implementation Plan\n\n- [ ] Task 1", encoding="utf-8")
        
        # Ensure CLAUDE.md does NOT exist
        claude_file = tmp_path / "CLAUDE.md"
        if claude_file.exists():
            claude_file.unlink()
        
        # Import main function to test
        from automate_dev import main
        
        # Mock sys.exit to prevent actual exit
        with patch('sys.exit') as mock_exit:
            # Mock print to capture warning messages
            with patch('builtins.print') as mock_print:
                # Call main function - it should detect missing CLAUDE.md and print warning
                main()
                
                # Verify that an appropriate warning message was printed
                mock_print.assert_called()
                printed_messages = [str(call.args[0]) for call in mock_print.call_args_list]
                warning_message_found = any(
                    ("CLAUDE.md" in msg and ("missing" in msg.lower() or "warning" in msg.lower()))
                    for msg in printed_messages
                )
                assert warning_message_found, f"Expected warning message about missing CLAUDE.md, got: {printed_messages}"
    
    def test_orchestrator_continues_when_all_prerequisite_files_present(self, tmp_path, monkeypatch):
        """
        Test that the orchestrator continues normally when all prerequisite files are present.
        
        This test creates a temporary directory with all required files present
        and verifies that no error or warning messages are printed.
        
        This test will initially fail because main() doesn't implement these checks yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Change to temporary directory
        monkeypatch.chdir(tmp_path)
        
        # Create all prerequisite files
        implementation_plan = tmp_path / "Implementation Plan.md"
        implementation_plan.write_text("# Implementation Plan\n\n- [ ] Task 1", encoding="utf-8")
        
        prd_file = tmp_path / "PRD.md"
        prd_file.write_text("# Product Requirements Document", encoding="utf-8")
        
        claude_file = tmp_path / "CLAUDE.md"
        claude_file.write_text("# CLAUDE.md\n\nProject instructions for Claude Code.", encoding="utf-8")
        
        # Import main function to test
        from automate_dev import main
        
        # Mock sys.exit to prevent actual exit and capture exit calls
        with patch('sys.exit') as mock_exit:
            # Mock print to capture any messages
            with patch('builtins.print') as mock_print:
                # Call main function - it should not exit or print warnings
                main()
                
                # Verify that sys.exit was NOT called due to missing files
                # (it might be called for other reasons once more functionality is implemented)
                if mock_exit.called:
                    # If exit was called, ensure it wasn't due to missing files
                    printed_messages = [str(call.args[0]) for call in mock_print.call_args_list]
                    file_error_found = any(
                        any(filename in msg for filename in ["Implementation Plan.md", "PRD.md", "CLAUDE.md"])
                        and ("missing" in msg.lower() or "not found" in msg.lower())
                        for msg in printed_messages
                    )
                    assert not file_error_found, f"No file-related errors should be printed when all files are present, got: {printed_messages}"


class TestTaskTracker:
    """Test suite for the TaskTracker class and its state management functionality."""
    
    def test_get_next_task_identifies_first_incomplete_task(self, tmp_path, monkeypatch):
        """
        Test that TaskTracker.get_next_task correctly identifies the first incomplete task.
        
        Given an Implementation Plan.md file with multiple tasks where some are complete
        and some are incomplete, the get_next_task method should return the first task
        marked with [ ] (incomplete).
        
        This test will initially fail because the TaskTracker class doesn't exist yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Change to temporary directory
        monkeypatch.chdir(tmp_path)
        
        # Create Implementation Plan.md with mixed complete/incomplete tasks
        implementation_plan = tmp_path / "Implementation Plan.md"
        implementation_plan_content = """# Implementation Plan

## Phase 1: Setup
- [X] Create project structure
- [X] Set up basic configuration

## Phase 2: Core Development
- [ ] Implement TaskTracker class
- [ ] Add error handling
- [X] Write documentation

## Phase 3: Testing
- [ ] Add integration tests
- [ ] Performance testing
"""
        implementation_plan.write_text(implementation_plan_content, encoding="utf-8")
        
        # Import TaskTracker class to test
        from automate_dev import TaskTracker
        
        # Create TaskTracker instance
        tracker = TaskTracker()
        
        # Call get_next_task method
        result = tracker.get_next_task()
        
        # Verify that it returns a tuple with the task and completion status
        assert isinstance(result, tuple), "get_next_task should return a tuple"
        assert len(result) == 2, "get_next_task should return a tuple with 2 elements"
        
        task, all_complete = result
        
        # Verify that all_complete is False (since there are incomplete tasks)
        assert all_complete is False, "all_complete should be False when there are incomplete tasks"
        
        # Verify that the first incomplete task is returned
        assert task is not None, "task should not be None when there are incomplete tasks"
        assert "Implement TaskTracker class" in task, f"Expected first incomplete task 'Implement TaskTracker class', got: {task}"
    
    def test_get_next_task_returns_none_true_when_all_tasks_complete(self, tmp_path, monkeypatch):
        """
        Test that TaskTracker.get_next_task returns (None, True) when all tasks are complete.
        
        Given an Implementation Plan.md file where all tasks are marked with [X] (complete),
        the get_next_task method should return (None, True) indicating no more work to do.
        
        This test will initially fail because the TaskTracker class doesn't exist yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Change to temporary directory
        monkeypatch.chdir(tmp_path)
        
        # Create Implementation Plan.md with all tasks complete
        implementation_plan = tmp_path / "Implementation Plan.md"
        implementation_plan_content = """# Implementation Plan

## Phase 1: Setup
- [X] Create project structure
- [X] Set up basic configuration

## Phase 2: Core Development
- [X] Implement TaskTracker class
- [X] Add error handling
- [X] Write documentation

## Phase 3: Testing
- [X] Add integration tests
- [X] Performance testing
"""
        implementation_plan.write_text(implementation_plan_content, encoding="utf-8")
        
        # Import TaskTracker class to test
        from automate_dev import TaskTracker
        
        # Create TaskTracker instance
        tracker = TaskTracker()
        
        # Call get_next_task method
        result = tracker.get_next_task()
        
        # Verify that it returns a tuple with (None, True)
        assert isinstance(result, tuple), "get_next_task should return a tuple"
        assert len(result) == 2, "get_next_task should return a tuple with 2 elements"
        
        task, all_complete = result
        
        # Verify that all_complete is True and task is None
        assert all_complete is True, "all_complete should be True when all tasks are complete"
        assert task is None, f"task should be None when all tasks are complete, got: {task}"
    
    def test_get_next_task_returns_none_true_when_implementation_plan_missing(self, tmp_path, monkeypatch):
        """
        Test that TaskTracker.get_next_task returns (None, True) when Implementation Plan.md doesn't exist.
        
        Given a directory where Implementation Plan.md file does not exist,
        the get_next_task method should return (None, True) indicating no work can be done.
        
        This test will initially fail because the TaskTracker class doesn't exist yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Change to temporary directory where Implementation Plan.md doesn't exist
        monkeypatch.chdir(tmp_path)
        
        # Ensure Implementation Plan.md does NOT exist
        implementation_plan = tmp_path / "Implementation Plan.md"
        if implementation_plan.exists():
            implementation_plan.unlink()
        
        # Import TaskTracker class to test
        from automate_dev import TaskTracker
        
        # Create TaskTracker instance
        tracker = TaskTracker()
        
        # Call get_next_task method
        result = tracker.get_next_task()
        
        # Verify that it returns a tuple with (None, True)
        assert isinstance(result, tuple), "get_next_task should return a tuple"
        assert len(result) == 2, "get_next_task should return a tuple with 2 elements"
        
        task, all_complete = result
        
        # Verify that all_complete is True and task is None when file doesn't exist
        assert all_complete is True, "all_complete should be True when Implementation Plan.md doesn't exist"
        assert task is None, f"task should be None when Implementation Plan.md doesn't exist, got: {task}"


class TestTaskTrackerFailureTracking:
    """Test suite for TaskTracker failure tracking functionality."""
    
    def test_increment_fix_attempts_correctly_increments_count_for_task(self):
        """
        Test that increment_fix_attempts correctly increments the count for a task.
        
        Given a TaskTracker instance and a task identifier,
        when increment_fix_attempts is called multiple times for the same task,
        then the fix attempt count should increment correctly and the method should
        return True until MAX_FIX_ATTEMPTS (3) is reached.
        
        This test will initially fail because the increment_fix_attempts method doesn't exist yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Import TaskTracker class to test
        from automate_dev import TaskTracker
        
        # Create TaskTracker instance
        tracker = TaskTracker()
        
        # Define a test task
        test_task = "Implement test feature"
        
        # Call increment_fix_attempts for the first time
        result1 = tracker.increment_fix_attempts(test_task)
        
        # Verify that the method returns True (within limit)
        assert result1 is True, "increment_fix_attempts should return True for first attempt"
        
        # Verify that the fix_attempts dictionary has been initialized for this task
        assert hasattr(tracker, 'fix_attempts'), "TaskTracker should have fix_attempts attribute"
        assert test_task in tracker.fix_attempts, "Task should be tracked in fix_attempts dictionary"
        assert tracker.fix_attempts[test_task] == 1, "Fix attempts count should be 1 after first call"
        
        # Call increment_fix_attempts for the second time
        result2 = tracker.increment_fix_attempts(test_task)
        assert result2 is True, "increment_fix_attempts should return True for second attempt"
        assert tracker.fix_attempts[test_task] == 2, "Fix attempts count should be 2 after second call"
        
        # Call increment_fix_attempts for the third time (should still be True)
        result3 = tracker.increment_fix_attempts(test_task)
        assert result3 is True, "increment_fix_attempts should return True for third attempt (at MAX_FIX_ATTEMPTS)"
        assert tracker.fix_attempts[test_task] == 3, "Fix attempts count should be 3 after third call"
    
    def test_increment_fix_attempts_returns_false_when_max_attempts_reached(self):
        """
        Test that increment_fix_attempts returns False when MAX_FIX_ATTEMPTS is reached.
        
        Given a TaskTracker instance and a task that has already reached the maximum
        number of fix attempts (3), when increment_fix_attempts is called again,
        then it should return False indicating that no more attempts should be made.
        
        This test will initially fail because the increment_fix_attempts method doesn't exist yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Import TaskTracker class to test
        from automate_dev import TaskTracker
        
        # Create TaskTracker instance
        tracker = TaskTracker()
        
        # Define a test task
        test_task = "Failed implementation task"
        
        # Manually set the fix_attempts to simulate reaching the limit
        # First ensure the fix_attempts attribute exists
        if not hasattr(tracker, 'fix_attempts'):
            tracker.fix_attempts = {}
        
        # Set the task to maximum attempts (3)
        tracker.fix_attempts[test_task] = 3
        
        # Call increment_fix_attempts - this should increment to 4 and return False
        result = tracker.increment_fix_attempts(test_task)
        
        # Verify that the method returns False (exceeded limit)
        assert result is False, "increment_fix_attempts should return False when MAX_FIX_ATTEMPTS (3) is exceeded"
        
        # Verify that the count was still incremented to 4
        assert tracker.fix_attempts[test_task] == 4, "Fix attempts count should be incremented to 4 even when limit exceeded"
    
    def test_reset_fix_attempts_removes_task_from_tracking_dictionary(self):
        """
        Test that reset_fix_attempts removes a task from the tracking dictionary.
        
        Given a TaskTracker instance with a task that has recorded fix attempts,
        when reset_fix_attempts is called for that task,
        then the task should be removed from the fix_attempts dictionary.
        
        This test will initially fail because the reset_fix_attempts method doesn't exist yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Import TaskTracker class to test
        from automate_dev import TaskTracker
        
        # Create TaskTracker instance
        tracker = TaskTracker()
        
        # Define test tasks
        test_task_1 = "Task to be reset"
        test_task_2 = "Task to remain"
        
        # Manually set up the fix_attempts dictionary with some tasks
        if not hasattr(tracker, 'fix_attempts'):
            tracker.fix_attempts = {}
        
        tracker.fix_attempts[test_task_1] = 2
        tracker.fix_attempts[test_task_2] = 1
        
        # Verify initial state
        assert test_task_1 in tracker.fix_attempts, "Task 1 should be in fix_attempts before reset"
        assert test_task_2 in tracker.fix_attempts, "Task 2 should be in fix_attempts before reset"
        assert tracker.fix_attempts[test_task_1] == 2, "Task 1 should have 2 attempts before reset"
        assert tracker.fix_attempts[test_task_2] == 1, "Task 2 should have 1 attempt before reset"
        
        # Call reset_fix_attempts for test_task_1
        tracker.reset_fix_attempts(test_task_1)
        
        # Verify that test_task_1 was removed but test_task_2 remains
        assert test_task_1 not in tracker.fix_attempts, "Task 1 should be removed from fix_attempts after reset"
        assert test_task_2 in tracker.fix_attempts, "Task 2 should remain in fix_attempts after reset of Task 1"
        assert tracker.fix_attempts[test_task_2] == 1, "Task 2 should still have 1 attempt after reset of Task 1"
        
        # Test resetting a task that doesn't exist (should not raise an error)
        non_existent_task = "Non-existent task"
        tracker.reset_fix_attempts(non_existent_task)  # Should not raise an exception
        
        # Verify that the dictionary is still intact
        assert test_task_2 in tracker.fix_attempts, "Task 2 should still be in fix_attempts after attempting to reset non-existent task"