"""
Tests for the automate_dev.py orchestrator script.

This file contains TDD tests for the automated development workflow orchestrator.
Following the red-green-refactor cycle, these tests are written before implementation.
"""

import pytest
import sys
import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

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


class TestClaudeCommandExecution:
    """Test suite for Claude CLI command execution functionality."""
    
    @patch('os.remove')
    @patch('os.path.exists')
    def test_run_claude_command_waits_for_signal_file_and_cleans_up(self, mock_exists, mock_remove):
        """
        Test that run_claude_command waits for signal_task_complete file and cleans up after.
        
        This test verifies the signal file waiting logic that enables reliable completion detection.
        The function should:
        1. Execute the Claude command
        2. Wait for ".claude/signal_task_complete" file to exist before returning
        3. Clean up (remove) the signal file after the loop breaks
        
        This test will initially fail because the signal file waiting logic doesn't exist yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Mock subprocess.run to return a successful result with JSON output
        with patch('subprocess.run') as mock_subprocess_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = '{"status": "success", "output": "Command completed"}'
            mock_result.stderr = ""
            mock_subprocess_run.return_value = mock_result
            
            # Simulate signal file appearing after some iterations
            # First few calls return False (file doesn't exist), then True (file exists)
            mock_exists.side_effect = [False, False, True]
            
            # Import the function to test
            from automate_dev import run_claude_command
            
            # Call the function
            test_command = "/continue"
            result = run_claude_command(test_command)
            
            # Verify subprocess.run was called with correct command array
            mock_subprocess_run.assert_called_once()
            call_args = mock_subprocess_run.call_args
            command_array = call_args[0][0]
            expected_command = [
                "claude",
                "-p", test_command,
                "--output-format", "json",
                "--dangerously-skip-permissions"
            ]
            assert command_array == expected_command, f"Expected command array {expected_command}, got {command_array}"
            
            # Verify that os.path.exists was called multiple times to check for signal file
            expected_signal_path = ".claude/signal_task_complete"
            mock_exists.assert_called_with(expected_signal_path)
            assert mock_exists.call_count == 3, f"Expected 3 calls to os.path.exists, got {mock_exists.call_count}"
            
            # Verify that os.remove was called to clean up the signal file
            mock_remove.assert_called_once_with(expected_signal_path)
            
            # Verify the function returns parsed JSON
            assert isinstance(result, dict), "run_claude_command should return parsed JSON as dict"
            assert result["status"] == "success", "JSON should be correctly parsed"
            assert result["output"] == "Command completed", "JSON content should be preserved"
    
    @patch('os.remove')
    @patch('os.path.exists')
    @patch('subprocess.run')
    def test_run_claude_command_constructs_correct_command_array(self, mock_subprocess_run, mock_exists, mock_remove):
        """
        Test that run_claude_command constructs the correct Claude CLI command array.
        
        Given a command string to execute via Claude CLI,
        when run_claude_command is called,
        then it should construct the proper command array with required flags
        and call subprocess.run with the correct parameters.
        
        This test will initially fail because the run_claude_command function doesn't exist yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Mock subprocess.run to return a successful result with JSON output
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"status": "success", "output": "Command executed successfully"}'
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result
        
        # Mock signal file to exist immediately (no waiting)
        mock_exists.return_value = True
        
        # Import the function to test
        from automate_dev import run_claude_command
        
        # Define test command to execute
        test_command = "/continue"
        
        # Call the function
        result = run_claude_command(test_command)
        
        # Verify subprocess.run was called with correct command array
        mock_subprocess_run.assert_called_once()
        call_args = mock_subprocess_run.call_args
        
        # Check the command array (first positional argument)
        command_array = call_args[0][0]
        expected_command = [
            "claude",
            "-p", test_command,
            "--output-format", "json",
            "--dangerously-skip-permissions"
        ]
        
        assert command_array == expected_command, f"Expected command array {expected_command}, got {command_array}"
        
        # Verify subprocess.run was called with correct keyword arguments
        kwargs = call_args[1]
        assert kwargs.get('capture_output') is True, "capture_output should be True"
        assert kwargs.get('text') is True, "text should be True"
        assert kwargs.get('check') is False, "check should be False to handle errors manually"
        
        # Verify the function returns parsed JSON
        assert isinstance(result, dict), "run_claude_command should return parsed JSON as dict"
        assert result["status"] == "success", "JSON should be correctly parsed"
        assert result["output"] == "Command executed successfully", "JSON content should be preserved"
    
    @patch('os.remove')
    @patch('os.path.exists')
    @patch('subprocess.run')
    def test_run_claude_command_parses_json_output_correctly(self, mock_subprocess_run, mock_exists, mock_remove):
        """
        Test that run_claude_command correctly parses JSON output from Claude CLI.
        
        Given various JSON responses from Claude CLI,
        when run_claude_command is called,
        then it should correctly parse the JSON and return the parsed data structure.
        
        This test will initially fail because the run_claude_command function doesn't exist yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Test complex JSON response
        complex_json_response = {
            "command": "/validate",
            "status": "completed",
            "results": {
                "tests_passed": 15,
                "tests_failed": 2,
                "errors": ["TypeError in test_function", "AssertionError in test_validation"]
            },
            "metadata": {
                "execution_time": "2.3s",
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }
        
        # Mock subprocess.run to return complex JSON
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(complex_json_response)
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result
        
        # Mock signal file to exist immediately (no waiting)
        mock_exists.return_value = True
        
        # Import the function to test
        from automate_dev import run_claude_command
        
        # Call the function
        result = run_claude_command("/validate")
        
        # Verify the JSON was correctly parsed and all nested data is accessible
        assert isinstance(result, dict), "Result should be a dictionary"
        assert result["command"] == "/validate", "Top-level fields should be accessible"
        assert result["status"] == "completed", "Status should be correctly parsed"
        
        # Verify nested objects are correctly parsed
        assert isinstance(result["results"], dict), "Nested objects should remain as dicts"
        assert result["results"]["tests_passed"] == 15, "Nested integer values should be preserved"
        assert result["results"]["tests_failed"] == 2, "Nested integer values should be preserved"
        assert isinstance(result["results"]["errors"], list), "Nested arrays should remain as lists"
        assert len(result["results"]["errors"]) == 2, "Array length should be preserved"
        assert "TypeError in test_function" in result["results"]["errors"], "Array contents should be preserved"
        
        # Verify deeply nested objects
        assert isinstance(result["metadata"], dict), "Deeply nested objects should be accessible"
        assert result["metadata"]["execution_time"] == "2.3s", "Deeply nested values should be preserved"
    
    @patch('os.remove')
    @patch('os.path.exists')
    @patch('subprocess.run')
    def test_run_claude_command_handles_claude_cli_errors_gracefully(self, mock_subprocess_run, mock_exists, mock_remove):
        """
        Test that run_claude_command handles Claude CLI errors gracefully.
        
        Given a Claude CLI command that fails with non-zero exit code,
        when run_claude_command is called,
        then it should handle the error gracefully and return appropriate error information.
        
        This test will initially fail because the run_claude_command function doesn't exist yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Mock subprocess.run to return an error response
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = '{"error": "Command failed", "details": "Invalid command syntax"}'
        mock_result.stderr = "Claude CLI Error: Command not recognized"
        mock_subprocess_run.return_value = mock_result
        
        # Mock signal file to exist immediately (no waiting)
        mock_exists.return_value = True
        
        # Import the function to test
        from automate_dev import run_claude_command
        
        # Call the function with an invalid command
        result = run_claude_command("/invalid-command")
        
        # Verify subprocess.run was called
        mock_subprocess_run.assert_called_once()
        
        # Verify the function still attempts to parse JSON even on error
        # (Claude CLI might return structured error information as JSON)
        assert isinstance(result, dict), "Result should still be a dictionary even on error"
        assert result["error"] == "Command failed", "Error information should be parsed from JSON"
        assert result["details"] == "Invalid command syntax", "Error details should be accessible"


class TestGetLatestStatus:
    """Test suite for the get_latest_status function and MCP server status file processing."""
    
    def test_get_latest_status_reads_newest_file_and_deletes_all_status_files(self, tmp_path, monkeypatch):
        """
        Test that get_latest_status reads the newest status file and deletes all status files.
        
        This test verifies the complete lifecycle of the get_latest_status function:
        1. Create multiple dummy status_*.json files with different timestamps
        2. Verify that the function reads the content of the *newest* file
        3. Verify that *all* status files are deleted after reading
        4. Verify that the function returns the correct status value from the JSON
        
        The function should:
        - Find all status_*.json files in .claude/ directory using glob pattern
        - Sort them to identify the newest file (lexicographic sort works with timestamp format)
        - Read the newest file and parse its JSON content
        - Extract the 'status' field from the JSON
        - Delete all status files after successful reading
        - Return the status value
        
        This test will initially fail because the get_latest_status function doesn't exist yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Change to temporary directory
        monkeypatch.chdir(tmp_path)
        
        # Create .claude directory structure
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        
        # Create multiple status files with different timestamps (newest should be read)
        # Using timestamp format that sorts lexicographically (newer timestamps sort later)
        status_files_data = {
            "status_20240101_120000.json": {
                "status": "validation_failed",
                "details": "Old validation failure",
                "timestamp": "2024-01-01T12:00:00Z"
            },
            "status_20240101_130000.json": {
                "status": "project_incomplete",
                "details": "Middle status update",
                "timestamp": "2024-01-01T13:00:00Z"
            },
            "status_20240101_140000.json": {
                "status": "validation_passed",
                "details": "Latest validation success",
                "timestamp": "2024-01-01T14:00:00Z"
            },
            "status_20240101_135500.json": {
                "status": "project_complete",
                "details": "Another status file (not newest)",
                "timestamp": "2024-01-01T13:55:00Z"
            }
        }
        
        # Write all status files to .claude directory
        for filename, data in status_files_data.items():
            status_file = claude_dir / filename
            status_file.write_text(json.dumps(data), encoding="utf-8")
        
        # Verify all files were created
        created_files = list(claude_dir.glob("status_*.json"))
        assert len(created_files) == 4, f"Expected 4 status files, but found {len(created_files)}"
        
        # Import the function to test
        from automate_dev import get_latest_status
        
        # Call the function
        result = get_latest_status()
        
        # Verify that the newest file's content was read correctly
        # The newest file should be "status_20240101_140000.json" with status "validation_passed"
        assert result == "validation_passed", f"Expected status 'validation_passed' from newest file, got: {result}"
        
        # Verify that ALL status files were deleted after reading
        remaining_files = list(claude_dir.glob("status_*.json"))
        assert len(remaining_files) == 0, f"Expected all status files to be deleted, but found {len(remaining_files)} remaining: {[f.name for f in remaining_files]}"
        
        # Verify the .claude directory still exists (only status files should be deleted)
        assert claude_dir.exists(), ".claude directory should still exist after status file cleanup"
    
    def test_get_latest_status_returns_none_when_no_status_files_exist(self, tmp_path, monkeypatch):
        """
        Test that get_latest_status returns None when no status files exist.
        
        Given a .claude directory with no status_*.json files,
        when get_latest_status is called,
        then it should return None to indicate no status is available.
        
        This test will initially fail because the get_latest_status function doesn't exist yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Change to temporary directory
        monkeypatch.chdir(tmp_path)
        
        # Create .claude directory structure without any status files
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        
        # Create some other files that should be ignored
        (claude_dir / "other_file.txt").write_text("not a status file")
        (claude_dir / "config.json").write_text('{"setting": "value"}')
        
        # Verify no status files exist
        status_files = list(claude_dir.glob("status_*.json"))
        assert len(status_files) == 0, f"Expected no status files, but found {len(status_files)}"
        
        # Import the function to test
        from automate_dev import get_latest_status
        
        # Call the function
        result = get_latest_status()
        
        # Verify that None is returned when no status files exist
        assert result is None, f"Expected None when no status files exist, got: {result}"
        
        # Verify that other files were not affected
        assert (claude_dir / "other_file.txt").exists(), "Non-status files should not be affected"
        assert (claude_dir / "config.json").exists(), "Non-status files should not be affected"
    
    def test_get_latest_status_handles_claude_directory_missing(self, tmp_path, monkeypatch):
        """
        Test that get_latest_status handles gracefully when .claude directory is missing.
        
        Given a working directory without a .claude subdirectory,
        when get_latest_status is called,
        then it should return None without raising an exception.
        
        This test will initially fail because the get_latest_status function doesn't exist yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Change to temporary directory
        monkeypatch.chdir(tmp_path)
        
        # Ensure .claude directory does NOT exist
        claude_dir = tmp_path / ".claude"
        if claude_dir.exists():
            claude_dir.rmdir()
        
        assert not claude_dir.exists(), ".claude directory should not exist for this test"
        
        # Import the function to test
        from automate_dev import get_latest_status
        
        # Call the function - should not raise an exception
        result = get_latest_status()
        
        # Verify that None is returned when .claude directory doesn't exist
        assert result is None, f"Expected None when .claude directory doesn't exist, got: {result}"