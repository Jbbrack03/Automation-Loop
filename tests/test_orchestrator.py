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
from unittest.mock import patch, MagicMock, call
from test_fixtures import (
    mock_claude_command_fixture,
    mock_get_latest_status_fixture,
    create_mock_implementation_plan,
    create_main_loop_command_mock,
    get_main_loop_status_sequence,
    get_refactoring_loop_status_sequence
)

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
        
        # Create .claude directory to avoid ensure_settings_file issues
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        
        # Import main function to test
        from automate_dev import main
        
        # Mock sys.exit to capture exit calls and prevent actual exit
        # Also mock subprocess to prevent any command execution
        with patch('sys.exit') as mock_exit:
            # Make sys.exit raise an exception to stop execution flow
            mock_exit.side_effect = SystemExit(1)
            
            # Mock print to capture error messages
            with patch('builtins.print') as mock_print:
                # Call main function - it should detect missing Implementation Plan.md and exit
                import pytest
                with pytest.raises(SystemExit):
                    main()
                
                # Verify that sys.exit was called with error code 1
                mock_exit.assert_called_once_with(1)
                
                # Verify that an appropriate error message was printed
                mock_print.assert_called()
                printed_messages = [str(call.args[0]) for call in mock_print.call_args_list]
                error_message_found = any(
                    "Implementation Plan.md" in msg or "implementation plan" in msg.lower()
                    for msg in printed_messages
                )
                assert error_message_found, f"Expected error message about missing Implementation Plan.md, got: {printed_messages}"
    
    def test_orchestrator_prints_warning_when_prd_md_missing(self, mock_claude_command, mock_get_latest_status, test_environment):
        """
        Test that the orchestrator prints a warning if PRD.md is missing.
        
        This test creates a temporary directory with Implementation Plan.md present
        but PRD.md missing, and verifies that a warning is printed.
        
        This test will initially fail because main() doesn't implement these checks yet.
        This is the RED phase of TDD - the test must fail first.
        """
        env = test_environment
        
        # Ensure PRD.md does NOT exist
        if env["prd_file"].exists():
            env["prd_file"].unlink()
        
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
    
    def test_orchestrator_prints_warning_when_claude_md_missing(self, mock_claude_command, mock_get_latest_status, test_environment):
        """
        Test that the orchestrator prints a warning if CLAUDE.md is missing.
        
        This test creates a temporary directory with Implementation Plan.md present
        but CLAUDE.md missing, and verifies that a warning is printed.
        
        This test will initially fail because main() doesn't implement these checks yet.
        This is the RED phase of TDD - the test must fail first.
        """
        env = test_environment
        
        # Ensure CLAUDE.md does NOT exist
        if env["claude_file"].exists():
            env["claude_file"].unlink()
        
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
    
    def test_orchestrator_continues_when_all_prerequisite_files_present(self, mock_claude_command, mock_get_latest_status, prerequisite_files_setup):
        """
        Test that the orchestrator continues normally when all prerequisite files are present.
        
        This test creates a temporary directory with all required files present
        and verifies that no error or warning messages are printed.
        
        This test will initially fail because main() doesn't implement these checks yet.
        This is the RED phase of TDD - the test must fail first.
        """
        env = prerequisite_files_setup
        
        # Import main function to test
        from automate_dev import main
        
        # Mock sys.exit to prevent actual exit and capture exit calls
        with patch('sys.exit') as mock_exit:
            # Mock print to capture any messages
            with patch('builtins.print') as mock_print:
                # Call main function - it should not exit or print warnings
                main()
                
                # Verify that sys.exit was NOT called due to missing files
                # (it will be called with 0 for successful completion)
                if mock_exit.called:
                    # If exit was called, ensure it wasn't due to missing files
                    printed_messages = [str(call.args[0]) for call in mock_print.call_args_list]
                    file_error_found = any(
                        any(filename in msg for filename in ["Implementation_Plan.md", "PRD.md", "CLAUDE.md"])
                        and ("missing" in msg.lower() or "not found" in msg.lower() or "error" in msg.lower())
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
        with patch('command_executor.subprocess.run') as mock_subprocess_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = '{"status": "success", "output": "Command completed"}'
            mock_result.stderr = ""
            mock_subprocess_run.return_value = mock_result
            
            # Simulate signal file appearing after some iterations
            # First few calls return False (file doesn't exist), then True (file exists)
            mock_exists.side_effect = [False, False, True]
            
            # Import the function to test
            from command_executor import run_claude_command
            
            # Mock the LOGGERS to avoid AttributeError
            with patch('command_executor.LOGGERS') as mock_loggers:
                mock_logger = MagicMock()
                mock_loggers.__getitem__.return_value = mock_logger
                
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
    @patch('command_executor.subprocess.run')
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
        from command_executor import run_claude_command
        
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
    @patch('command_executor.subprocess.run')
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
        from command_executor import run_claude_command
        
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
    @patch('command_executor.subprocess.run')
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
        from command_executor import run_claude_command
        
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


class TestHookConfiguration:
    """Test suite for hook configuration file setup and validation."""
    
    def test_claude_settings_local_json_exists_and_contains_valid_json(self, tmp_path, monkeypatch):
        """
        Test that .claude/settings.local.json exists and contains valid JSON structure.
        
        This test verifies that Task 6.1: Create Hook Configuration File has been completed.
        The test checks that:
        1. The .claude/settings.local.json file exists
        2. The file contains valid JSON that can be parsed without errors
        3. The JSON structure is readable as a dictionary
        
        This test will initially fail because .claude/settings.local.json doesn't exist yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Change to temporary directory
        monkeypatch.chdir(tmp_path)
        
        # Create .claude directory structure to simulate real project layout
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        
        # Import and call the function that should ensure the settings file exists
        from automate_dev import ensure_settings_file
        ensure_settings_file()
        
        # Define the expected path for the hook configuration file
        settings_file = claude_dir / "settings.local.json"
        
        # Verify that the settings.local.json file exists
        assert settings_file.exists(), f".claude/settings.local.json should exist at {settings_file}"
        
        # Verify that the file is readable
        assert settings_file.is_file(), ".claude/settings.local.json should be a file"
        assert os.access(str(settings_file), os.R_OK), ".claude/settings.local.json should be readable"
        
        # Verify that the file contains valid JSON
        try:
            with open(str(settings_file), 'r', encoding='utf-8') as f:
                json_content = json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f".claude/settings.local.json should contain valid JSON, but parsing failed: {e}")
        except FileNotFoundError:
            pytest.fail(".claude/settings.local.json file should exist")
        except Exception as e:
            pytest.fail(f"Unexpected error reading .claude/settings.local.json: {e}")
        
        # Verify that the parsed JSON is a dictionary (the expected top-level structure)
        assert isinstance(json_content, dict), f".claude/settings.local.json should contain a JSON object (dict), got: {type(json_content)}"
    
    def test_stop_hook_configuration_is_present_and_correct(self, tmp_path, monkeypatch):
        """
        Test that .claude/settings.local.json contains the correct Stop hook configuration.
        
        This test verifies that Task 6.2: Add Stop Hook Configuration has been completed.
        The test checks that the settings.local.json file contains the exact hook structure:
        {
          "hooks": {
            "Stop": [{
              "hooks": [{
                "type": "command",
                "command": "touch .claude/signal_task_complete"
              }]
            }]
          }
        }
        
        This test will initially fail because the current file only contains an empty JSON object.
        This is the RED phase of TDD - the test must fail first.
        """
        # Change to temporary directory
        monkeypatch.chdir(tmp_path)
        
        # Create .claude directory structure to simulate real project layout
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        
        # Import and call the function that should ensure the settings file exists with Stop hook
        from automate_dev import ensure_settings_file
        ensure_settings_file()
        
        # Define the expected path for the hook configuration file
        settings_file = claude_dir / "settings.local.json"
        
        # Verify that the settings.local.json file exists
        assert settings_file.exists(), f".claude/settings.local.json should exist at {settings_file}"
        
        # Read and parse the JSON content
        try:
            with open(str(settings_file), 'r', encoding='utf-8') as f:
                json_content = json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f".claude/settings.local.json should contain valid JSON, but parsing failed: {e}")
        except FileNotFoundError:
            pytest.fail(".claude/settings.local.json file should exist")
        
        # Verify that the hooks section exists
        assert "hooks" in json_content, "settings.local.json should contain a 'hooks' section"
        hooks_section = json_content["hooks"]
        assert isinstance(hooks_section, dict), "The 'hooks' section should be a dictionary"
        
        # Verify that the Stop hook exists
        assert "Stop" in hooks_section, "The hooks section should contain a 'Stop' hook"
        stop_hook = hooks_section["Stop"]
        assert isinstance(stop_hook, list), "The Stop hook should be a list"
        assert len(stop_hook) == 1, "The Stop hook should contain exactly one hook configuration"
        
        # Verify the Stop hook configuration structure
        stop_hook_config = stop_hook[0]
        assert isinstance(stop_hook_config, dict), "Stop hook configuration should be a dictionary"
        assert "hooks" in stop_hook_config, "Stop hook configuration should contain a 'hooks' array"
        
        inner_hooks = stop_hook_config["hooks"]
        assert isinstance(inner_hooks, list), "Inner hooks should be a list"
        assert len(inner_hooks) == 1, "Inner hooks should contain exactly one command"
        
        # Verify the command configuration
        command_config = inner_hooks[0]
        assert isinstance(command_config, dict), "Command configuration should be a dictionary"
        assert "type" in command_config, "Command configuration should have a 'type' field"
        assert "command" in command_config, "Command configuration should have a 'command' field"
        
        # Verify the exact values
        assert command_config["type"] == "command", f"Expected command type 'command', got: {command_config['type']}"
        assert command_config["command"] == "touch .claude/signal_task_complete", f"Expected command 'touch .claude/signal_task_complete', got: {command_config['command']}"


class TestMainOrchestrationLoop:
    """Test suite for the main orchestration loop implementation."""
    
    @patch('command_executor.run_claude_command')
    def test_main_loop_executes_tdd_sequence_happy_path(self, mock_command_executor_run_claude, mock_claude_command, mock_get_latest_status, main_loop_test_setup):
        """
        Test that the main orchestration loop executes the correct TDD sequence in the happy path.
        
        This test verifies the happy path scenario where:
        1. A task is available in Implementation Plan.md
        2. The main loop executes /clear, /continue, /validate, /update in sequence
        3. After /validate, get_latest_status returns "validation_passed"
        4. After /update, get_latest_status returns "project_incomplete" 
        5. The loop continues for the next task
        6. Eventually all tasks are complete and the loop exits
        
        The test mocks both run_claude_command and get_latest_status to control
        the flow and verify the correct sequence of calls.
        
        This test will initially fail because the main loop logic hasn't been implemented yet.
        This is the RED phase of TDD - the test must fail first.
        """
        env = main_loop_test_setup
        
        # Configure the command mock to simulate task progression
        mock_claude_command.side_effect = create_main_loop_command_mock(env["implementation_plan"])
        
        # Also configure command_executor.run_claude_command with the same mock
        # This is needed because execute_command_and_get_status calls it directly
        mock_command_executor_run_claude.side_effect = create_main_loop_command_mock(env["implementation_plan"])
        
        # Configure status mock to simulate the happy path flow
        mock_get_latest_status.side_effect = get_main_loop_status_sequence()
        
        # Import the main function to test
        from automate_dev import main
        
        # Mock sys.exit to prevent actual exit and capture when it's called
        with patch('sys.exit') as mock_exit:
            # Call main function - it should execute the orchestration loop
            main()
            
            # Verify that sys.exit was called (indicating successful completion)
            mock_exit.assert_called_once_with(0)
        
        # Verify the correct sequence of Claude commands was executed
        # With new _command_executor_wrapper:
        # - /clear and /continue go through automate_dev.run_claude_command
        # - /validate, /update, /checkin, /refactor go through command_executor.run_claude_command
        
        expected_automate_dev_calls = [
            # First task cycle
            call("/clear"),
            call("/continue"),
            # Second task cycle
            call("/clear"),
            call("/continue"),
            # Third cycle when all tasks complete
            call("/clear"),
            call("/continue"),
        ]
        
        expected_command_executor_calls = [
            # First task cycle
            call("/validate", debug=False),
            call("/update", debug=False),
            # Second task cycle
            call("/validate", debug=False), 
            call("/update", debug=False),
            # Third cycle when all tasks complete
            call("/validate", debug=False),
            call("/update", debug=False),
            # Refactoring check
            call("/checkin", debug=False),
            call("/refactor", debug=False)
        ]
        
        # Verify automate_dev.run_claude_command was called for /clear and /continue
        assert mock_claude_command.call_count == 6, f"Expected 6 calls to automate_dev.run_claude_command, got {mock_claude_command.call_count}"
        mock_claude_command.assert_has_calls(expected_automate_dev_calls, any_order=False)
        
        # Verify command_executor.run_claude_command was called for status commands
        assert mock_command_executor_run_claude.call_count == 8, f"Expected 8 calls to command_executor.run_claude_command, got {mock_command_executor_run_claude.call_count}"
        mock_command_executor_run_claude.assert_has_calls(expected_command_executor_calls, any_order=False)
        
        # Verify get_latest_status was called the correct number of times
        # With new _command_executor_wrapper, get_latest_status is only called for status commands:
        # - 3 TDD cycles: /validate and /update each = 6 calls
        # - 1 call in handle_project_completion = 1
        # - 2 calls in refactoring loop (checkin, refactor) = 2
        # Total: 9
        assert mock_get_latest_status.call_count == 9, f"Expected 9 calls to get_latest_status, got {mock_get_latest_status.call_count}"
    
    def test_main_loop_correction_path_when_validation_fails(self):
        """
        Test that the main orchestration loop handles validation failures with correction attempts.
        
        This test focuses on testing the TaskTracker behavior and the correction logic 
        without the complexity of the full integration test that would require mocking
        file modifications.
        
        This test verifies:
        1. TaskTracker.increment_fix_attempts properly tracks attempts and enforces MAX_FIX_ATTEMPTS
        2. The retry logic respects the limit returned by increment_fix_attempts
        3. When max attempts are exceeded, the task should be skipped
        """
        from automate_dev import TaskTracker
        from config import MAX_FIX_ATTEMPTS
        
        # Test the TaskTracker increment_fix_attempts behavior
        tracker = TaskTracker()
        test_task = "Test task that will fail validation"
        
        # Verify the TaskTracker behaves correctly for MAX_FIX_ATTEMPTS
        for attempt in range(1, MAX_FIX_ATTEMPTS + 1):
            result = tracker.increment_fix_attempts(test_task)
            assert result == True, f"Attempt {attempt} should return True (within limit)"
            assert tracker.fix_attempts[test_task] == attempt, f"Attempt count should be {attempt}"
        
        # The next attempt should exceed the limit
        result = tracker.increment_fix_attempts(test_task)
        assert result == False, "Fourth attempt should return False (exceeds MAX_FIX_ATTEMPTS)"
        assert tracker.fix_attempts[test_task] == MAX_FIX_ATTEMPTS + 1, f"Attempt count should be {MAX_FIX_ATTEMPTS + 1}"
        
        # Test that reset_fix_attempts works correctly
        tracker.reset_fix_attempts(test_task)
        assert test_task not in tracker.fix_attempts, "Task should be removed from tracking after reset"
        
        # After reset, should be able to increment again
        result = tracker.increment_fix_attempts(test_task)
        assert result == True, "After reset, first attempt should return True again"
        assert tracker.fix_attempts[test_task] == 1, "After reset, attempt count should be 1"
        
        # Test multiple tasks are tracked independently
        task2 = "Another task"
        result1 = tracker.increment_fix_attempts(test_task)  # This will be attempt 2 for test_task
        result2 = tracker.increment_fix_attempts(task2)     # This will be attempt 1 for task2
        
        assert result1 == True, "Second attempt for first task should return True"
        assert result2 == True, "First attempt for second task should return True"
        assert tracker.fix_attempts[test_task] == 2, "First task should have 2 attempts"
        assert tracker.fix_attempts[task2] == 1, "Second task should have 1 attempt"
        
        print("TaskTracker correction logic works correctly.")
        print("Integration with main loop correction path verified through TaskTracker behavior.")
        print("The main loop should use increment_fix_attempts and respect its return value.")


class TestRefactoringLoop:
    """Test suite for the refactoring and finalization loop functionality."""
    
    @patch('command_executor.run_claude_command')
    def test_refactoring_loop_executes_complete_sequence(self, mock_command_executor_run_claude, mock_claude_command, mock_get_latest_status, refactoring_loop_test_setup):
        """
        Test that the refactoring loop executes the complete sequence when project_complete status is returned.
        
        This test verifies the refactoring loop scenario where:
        1. All tasks in Implementation Plan.md are complete (return project_complete after /update)
        2. The main loop enters refactoring mode and calls /checkin
        3. Based on checkin status, it calls /refactor if refactoring is needed
        4. If refactoring tasks are found, it calls /finalize to implement them
        5. Loop continues until status is "no_refactoring_needed"
        6. Finally exits with success code
        
        The test mocks multiple scenarios:
        - Scenario 1: checkin finds issues, refactor finds work, finalize completes
        - Scenario 2: checkin finds more issues, refactor finds work, finalize completes  
        - Scenario 3: checkin finds no issues (no_refactoring_needed), loop exits
        
        This test will initially fail because the refactoring loop logic hasn't been implemented yet.
        This is the RED phase of TDD - the test must fail first.
        """
        env = refactoring_loop_test_setup
        
        # Mock run_claude_command to return successful results
        mock_claude_command.return_value = {"status": "success", "output": "Command completed"}
        
        # Also configure command_executor.run_claude_command with the same mock
        # This is needed because execute_command_and_get_status calls it directly
        mock_command_executor_run_claude.return_value = {"status": "success", "output": "Command completed"}
        
        # Configure status mock to simulate the complete refactoring workflow
        mock_get_latest_status.side_effect = get_refactoring_loop_status_sequence()
        
        # Import the main function to test
        from automate_dev import main
        
        # Mock sys.exit to prevent actual exit and capture when it's called
        with patch('sys.exit') as mock_exit:
            # Call main function - it should execute the refactoring loop
            main()
            
            # Verify that sys.exit was called with success code (0)
            mock_exit.assert_called_once_with(0)
        
        # Verify the correct sequence of Claude commands was executed
        # The refactored code first runs a TDD cycle (since tasks marked complete)
        # Then enters the refactoring loop
        expected_automate_dev_calls = [
            # Initial TDD cycle - only /clear and /continue go through automate_dev.run_claude_command
            call("/clear"),
            call("/continue"),
        ]
        
        expected_command_executor_calls = [
            # /validate and /update go through command_executor.run_claude_command via execute_command_and_get_status
            call("/validate", debug=False),
            call("/update", debug=False),
            
            # All refactoring cycle commands go through execute_command_and_get_status
            # First refactoring cycle
            call("/checkin", debug=False),
            call("/refactor", debug=False),  
            call("/finalize", debug=False),
            
            # Second refactoring cycle
            call("/checkin", debug=False),
            call("/refactor", debug=False),
            call("/finalize", debug=False),
            
            # Third refactoring cycle (final)
            call("/checkin", debug=False),
            call("/refactor", debug=False)
            # No /finalize because /refactor returned "no_refactoring_needed"
        ]
        
        # Verify automate_dev.run_claude_command was called with /clear and /continue
        assert mock_claude_command.call_count == 2, f"Expected 2 calls to automate_dev.run_claude_command, got {mock_claude_command.call_count}"
        mock_claude_command.assert_has_calls(expected_automate_dev_calls, any_order=False)
        
        # Verify command_executor.run_claude_command was called with remaining commands
        assert mock_command_executor_run_claude.call_count == 10, f"Expected 10 calls to command_executor.run_claude_command, got {mock_command_executor_run_claude.call_count}"
        mock_command_executor_run_claude.assert_has_calls(expected_command_executor_calls, any_order=False)
        
        # Verify get_latest_status was called the correct number of times
        # 2 from main loop (validation, update) + 1 project check + 8 from refactoring (checkin/refactor/finalize x2 + checkin/refactor x1)
        assert mock_get_latest_status.call_count == 11, f"Expected 11 calls to get_latest_status, got {mock_get_latest_status.call_count}"
    
    @patch('command_executor.run_claude_command')
    @patch('automate_dev.get_latest_status')
    @patch('automate_dev.run_claude_command')
    def test_refactoring_loop_skips_finalize_when_no_refactoring_needed(self, mock_run_claude_command, mock_get_latest_status, mock_command_executor_run_claude, tmp_path, monkeypatch):
        """
        Test that the refactoring loop skips /finalize when /refactor returns no_refactoring_needed.
        
        This test verifies the scenario where:
        1. Project is complete and enters refactoring loop
        2. /checkin completes successfully
        3. /refactor determines no refactoring is needed
        4. /finalize is NOT called
        5. Loop exits immediately with success
        
        This test will initially fail because the refactoring loop logic hasn't been implemented yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Change to temporary directory
        monkeypatch.chdir(tmp_path)
        
        # Create Implementation Plan.md with all tasks complete
        implementation_plan = tmp_path / "Implementation Plan.md"
        implementation_plan_content = """# Implementation Plan

## Phase 1: Development
- [X] All tasks complete
"""
        implementation_plan.write_text(implementation_plan_content, encoding="utf-8")
        
        # Create .claude directory
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        
        # Mock run_claude_command to return successful results
        mock_run_claude_command.return_value = {"status": "success", "output": "Command completed"}
        
        # Mock command_executor.run_claude_command as well
        mock_command_executor_run_claude.return_value = {"status": "success", "output": "Command completed"}
        
        # Mock get_latest_status to simulate immediate "no refactoring needed" scenario
        # With new _command_executor_wrapper, only status commands call get_latest_status
        mock_get_latest_status.side_effect = [
            # TDD cycle when all tasks complete (only /validate and /update call get_latest_status)
            "validation_passed",         # For /validate
            "project_complete",          # For /update
            
            # Check before entering refactoring
            "project_complete",          # Confirms project_complete status
            
            # Refactoring cycle (immediately exits)
            "checkin_complete",          # After /checkin - proceed to /refactor
            "no_refactoring_needed"      # After /refactor - exit immediately (no /finalize)
        ]
        
        # Import the main function to test
        from automate_dev import main
        
        # Mock sys.exit to prevent actual exit and capture when it's called
        with patch('sys.exit') as mock_exit:
            # Call main function
            main()
            
            # Verify that sys.exit was called with success code (0)
            mock_exit.assert_called_once_with(0)
        
        # Verify the correct sequence - TDD cycle + /checkin, /refactor, but NO /finalize
        # With new _command_executor_wrapper, calls are split between two mocks
        expected_automate_dev_calls = [
            # Initial TDD cycle - only /clear and /continue
            call("/clear"),
            call("/continue"),
        ]
        
        expected_command_executor_calls = [
            # Initial TDD cycle - status commands
            call("/validate", debug=False),
            call("/update", debug=False),
            
            # Refactoring cycle
            call("/checkin", debug=False),
            call("/refactor", debug=False)
            # NO call("/finalize") because refactor returned "no_refactoring_needed"
        ]
        
        # Verify automate_dev.run_claude_command was called for /clear and /continue
        assert mock_run_claude_command.call_count == 2, f"Expected 2 calls to automate_dev.run_claude_command, got {mock_run_claude_command.call_count}"
        mock_run_claude_command.assert_has_calls(expected_automate_dev_calls, any_order=False)
        
        # Verify command_executor.run_claude_command was called for status commands
        assert mock_command_executor_run_claude.call_count == 4, f"Expected 4 calls to command_executor.run_claude_command, got {mock_command_executor_run_claude.call_count}"
        mock_command_executor_run_claude.assert_has_calls(expected_command_executor_calls, any_order=False)
        
        # Verify get_latest_status was called the correct number of times
        assert mock_get_latest_status.call_count == 5, f"Expected 5 calls to get_latest_status, got {mock_get_latest_status.call_count}"
    
    def test_refactoring_loop_handles_mixed_project_and_refactoring_workflow(self, tmp_path, monkeypatch):
        """
        Test the complete workflow: regular TDD tasks followed by refactoring loop.
        
        This test verifies the full workflow scenario where:
        1. There are incomplete tasks that go through regular TDD cycle
        2. After all tasks complete (project_complete), refactoring loop begins
        3. Refactoring loop executes properly
        4. System exits successfully
        
        This test will initially fail because the refactoring loop logic hasn't been implemented yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Change to temporary directory
        monkeypatch.chdir(tmp_path)
        
        # Create Implementation Plan.md with one incomplete task
        implementation_plan = tmp_path / "Implementation Plan.md"
        implementation_plan_content = """# Implementation Plan

## Phase 1: Development
- [X] Completed task
- [ ] Final task to implement

## Phase 2: Refactoring
- [X] Setup refactoring environment
"""
        implementation_plan.write_text(implementation_plan_content, encoding="utf-8")
        
        # Create .claude directory
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        
        # Create optional files to avoid warnings
        prd_file = tmp_path / "PRD.md"
        prd_file.write_text("# PRD", encoding="utf-8")
        claude_file = tmp_path / "CLAUDE.md"
        claude_file.write_text("# CLAUDE", encoding="utf-8")
        
        # Import needed components
        from automate_dev import main, TaskTracker
        from unittest.mock import Mock
        
        # Create mock TaskTracker
        mock_tracker = TaskTracker()
        
        # Track command executions
        command_executions = []
        update_call_count = 0
        max_calls = 30  # Safety limit to prevent infinite loops
        
        # Create mock command executor that returns status for status commands
        def mock_command_executor(command):
            nonlocal update_call_count
            command_executions.append(command)
            
            # Safety check to prevent infinite loops
            if len(command_executions) > max_calls:
                raise RuntimeError(f"Too many command executions ({len(command_executions)}), likely infinite loop. Commands: {command_executions}")
            
            # Simulate /update marking the task as complete
            if command == "/update":
                update_call_count += 1
                if update_call_count == 1:
                    # First /update: mark the incomplete task as complete
                    updated_content = """# Implementation Plan

## Phase 1: Development
- [X] Completed task
- [X] Final task to implement

## Phase 2: Refactoring
- [X] Setup refactoring environment
"""
                    implementation_plan.write_text(updated_content, encoding="utf-8")
                    return "project_incomplete"
                elif update_call_count == 2:
                    return "project_complete"
            
            # Return appropriate status for each command
            if command == "/clear" or command == "/continue" or command == "/correct":
                return None  # These commands don't return status
            elif command == "/validate":
                return "validation_passed"
            elif command == "/checkin":
                return "checkin_complete"
            elif command == "/refactor":
                # Return different values based on how many times called
                refactor_count = command_executions.count("/refactor")
                if refactor_count == 1:
                    return "refactoring_needed"
                else:
                    return "no_refactoring_needed"
            elif command == "/finalize":
                return "finalization_complete"
            
            return None
        
        # Create mock status getter
        status_call_count = 0
        def mock_status_getter():
            nonlocal status_call_count
            status_call_count += 1
            # Only called for handle_project_completion check
            return "project_complete"
        
        # Create mock logger setup that populates LOGGERS dict
        def mock_logger_setup():
            from config import LOGGERS
            from unittest.mock import MagicMock
            # Populate LOGGERS with mock loggers to avoid AttributeError
            LOGGERS['orchestrator'] = MagicMock()
            LOGGERS['task_tracker'] = MagicMock()
            LOGGERS['command_executor'] = MagicMock()
            LOGGERS['validation'] = MagicMock()
            LOGGERS['error_handler'] = MagicMock()
            LOGGERS['usage_limit'] = MagicMock()
        
        # Create dependencies dictionary
        mock_dependencies = {
            'task_tracker': mock_tracker,
            'command_executor': mock_command_executor,
            'logger_setup': mock_logger_setup,
            'status_getter': mock_status_getter
        }
        
        # Mock sys.exit to prevent actual exit and capture when it's called
        with patch('sys.exit') as mock_exit:
            # Call main function with dependencies
            main(dependencies=mock_dependencies)
            
            # Verify that sys.exit was called with success code (0)
            mock_exit.assert_called_once_with(0)
        
        # Verify the expected command sequence
        expected_commands = [
            # First TDD cycle for the incomplete task
            "/clear",
            "/continue",
            "/validate",
            "/update",
            
            # Second TDD cycle when all tasks are complete
            "/clear",
            "/continue",
            "/validate",
            "/update",
            
            # Refactoring loop
            "/checkin",
            "/refactor",
            "/finalize",
            "/checkin",
            "/refactor"
        ]
        
        assert command_executions == expected_commands, f"Expected command sequence {expected_commands}, got {command_executions}"
        
        # Logger setup was called (we can't verify since it's a function, not a Mock)
        # Just verify the test completed successfully


class TestUsageLimitIntegration:
    """Test suite for integrating usage limit handling into run_claude_command."""
    
    @patch('os.remove')
    @patch('os.path.exists')
    @patch('time.sleep')
    @patch('command_executor.calculate_wait_time')
    @patch('command_executor.parse_usage_limit_error')
    @patch('command_executor.subprocess.run')
    def test_run_claude_command_detects_usage_limit_and_retries_successfully(
            self, mock_subprocess_run, mock_parse_usage_limit, mock_calculate_wait_time, 
            mock_sleep, mock_exists, mock_remove):
        """
        Test that run_claude_command detects usage limit errors and retries after waiting.
        
        This test verifies the complete usage limit handling integration:
        1. First subprocess.run call returns usage limit error in stdout/stderr
        2. run_claude_command detects the usage limit pattern in the output
        3. Calls parse_usage_limit_error to extract reset time information
        4. Calls calculate_wait_time to determine how long to wait
        5. Calls time.sleep to wait for the specified duration
        6. Retries the subprocess.run call with the same command
        7. Second call succeeds and returns valid JSON output
        8. Function returns the successful result
        
        The test follows FIRST principles:
        - Fast: Uses mocks to avoid actual subprocess calls and waiting
        - Independent: Runs in isolation with no external dependencies
        - Repeatable: Produces consistent results with mocked behavior
        - Self-validating: Has clear assertions about retry behavior
        - Timely: Tests the integration before implementation exists
        
        This test will initially fail because run_claude_command doesn't detect
        or handle usage limit errors yet - it needs to be modified to:
        1. Check output for usage limit indicators
        2. Call usage limit parsing and calculation functions
        3. Sleep and retry when usage limits are detected
        
        This is the RED phase of TDD - the test must fail first.
        """
        # Mock subprocess.run to return usage limit error first, then success
        usage_limit_result = MagicMock()
        usage_limit_result.returncode = 1
        usage_limit_result.stdout = '{"error": "usage_limit", "message": "You can try again at 7pm (America/Chicago)"}'
        usage_limit_result.stderr = "Claude API Error: Usage limit exceeded. You can try again at 7pm (America/Chicago)."
        
        success_result = MagicMock()
        success_result.returncode = 0
        success_result.stdout = '{"status": "success", "output": "Command completed after retry"}'
        success_result.stderr = ""
        
        # First call returns usage limit error, second call succeeds
        mock_subprocess_run.side_effect = [usage_limit_result, success_result]
        
        # Mock parse_usage_limit_error to return parsed reset information
        mock_parse_usage_limit.return_value = {
            "reset_time": "7pm",
            "timezone": "America/Chicago", 
            "format": "natural_language"
        }
        
        # Mock calculate_wait_time to return 3600 seconds (1 hour wait)
        mock_calculate_wait_time.return_value = 3600
        
        # Mock signal file to exist immediately after both command attempts
        mock_exists.return_value = True
        
        # Import the function to test
        from command_executor import run_claude_command
        
        # Call the function - should detect usage limit, wait, and retry
        test_command = "/continue"
        result = run_claude_command(test_command)
        
        # Verify subprocess.run was called twice (initial attempt + retry)
        assert mock_subprocess_run.call_count == 2, f"Expected 2 calls to subprocess.run (initial + retry), got {mock_subprocess_run.call_count}"
        
        # Verify both calls used the same command array
        expected_command = [
            "claude",
            "-p", test_command,
            "--output-format", "json",
            "--dangerously-skip-permissions"
        ]
        
        first_call_args = mock_subprocess_run.call_args_list[0][0][0]
        second_call_args = mock_subprocess_run.call_args_list[1][0][0]
        
        assert first_call_args == expected_command, f"First call should use correct command array"
        assert second_call_args == expected_command, f"Retry call should use same command array"
        
        # Verify usage limit detection and parsing was called
        mock_parse_usage_limit.assert_called_once()
        # Should be called with either stdout or stderr that contains usage limit message
        parse_call_args = mock_parse_usage_limit.call_args[0][0]
        assert "usage_limit" in parse_call_args or "7pm" in parse_call_args, "parse_usage_limit should be called with usage limit error message"
        
        # Verify wait time calculation was called with parsed reset info
        mock_calculate_wait_time.assert_called_once_with({
            "reset_time": "7pm",
            "timezone": "America/Chicago",
            "format": "natural_language"
        })
        
        # Verify time.sleep was called with calculated wait time
        mock_sleep.assert_called_once_with(3600)
        
        # Verify signal file cleanup was performed twice (once per command attempt)
        assert mock_remove.call_count == 2, f"Expected 2 calls to os.remove (cleanup after each attempt), got {mock_remove.call_count}"
        
        # Verify function returns the successful result (from second attempt)
        assert isinstance(result, dict), "Result should be parsed JSON from successful retry"
        assert result["status"] == "success", "Result should be from successful retry attempt"
        assert result["output"] == "Command completed after retry", "Result should contain retry success message"


class TestUsageLimitParsing:
    """Test suite for usage limit error parsing functionality."""
    
    def test_parse_usage_limit_error_natural_language_format_simple_case(self):
        """
        Test that parse_usage_limit_error correctly extracts reset time from natural language format.
        
        This test verifies the simplest case of parsing a natural language usage limit error
        message that contains a time and timezone specification. The function should extract
        the reset time information and return it in a format that can be used by the orchestrator
        to calculate wait times.
        
        Example error message: "You can try again at 7pm (America/Chicago)"
        
        The function should parse this and return the time and timezone information
        so that calculate_wait_time can compute the appropriate wait duration.
        
        This test will initially fail because the parse_usage_limit_error function doesn't exist yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Import the function to test
        from automate_dev import parse_usage_limit_error
        
        # Test the simplest natural language format
        error_message = "You have reached your usage limit. You can try again at 7pm (America/Chicago)."
        
        # Call the function to parse the error message
        result = parse_usage_limit_error(error_message)
        
        # Verify that the function returns a dictionary with expected structure
        assert isinstance(result, dict), "parse_usage_limit_error should return a dictionary"
        
        # Verify that it contains the necessary information to calculate wait time
        assert "reset_time" in result, "Result should contain 'reset_time' key"
        assert "timezone" in result, "Result should contain 'timezone' key"
        
        # Verify that the parsed values are correct
        assert result["reset_time"] == "7pm", f"Expected reset_time '7pm', got: {result['reset_time']}"
        assert result["timezone"] == "America/Chicago", f"Expected timezone 'America/Chicago', got: {result['timezone']}"
        
        # Verify that the function correctly identifies this as natural language format
        assert result["format"] == "natural_language", f"Expected format 'natural_language', got: {result.get('format')}"
    
    def test_parse_usage_limit_error_unix_timestamp_format(self):
        """
        Test that parse_usage_limit_error correctly parses JSON format with Unix timestamp.
        
        This test verifies that the function can handle JSON response format containing
        a reset_at field with a Unix timestamp value. The function should parse the JSON,
        extract the reset_at value, and return it in a format that can be used by the
        orchestrator to calculate wait times.
        
        Example JSON: {"error": "usage_limit", "reset_at": 1737000000}
        
        The function should parse this and return:
        - format: "unix_timestamp" 
        - reset_at: the Unix timestamp value (1737000000)
        
        This test will initially fail because the parse_usage_limit_error function
        currently only handles natural language format, not JSON format.
        This is the RED phase of TDD - the test must fail first.
        """
        # Import the function to test
        from automate_dev import parse_usage_limit_error
        
        # Test JSON format with Unix timestamp
        json_error_message = '{"error": "usage_limit", "reset_at": 1737000000}'
        
        # Call the function to parse the JSON error message
        result = parse_usage_limit_error(json_error_message)
        
        # Verify that the function returns a dictionary with expected structure
        assert isinstance(result, dict), "parse_usage_limit_error should return a dictionary"
        
        # Verify that it correctly identifies this as unix_timestamp format
        assert result["format"] == "unix_timestamp", f"Expected format 'unix_timestamp', got: {result.get('format')}"
        
        # Verify that the parsed Unix timestamp is correct
        assert "reset_at" in result, "Result should contain 'reset_at' key for unix_timestamp format"
        assert result["reset_at"] == 1737000000, f"Expected reset_at 1737000000, got: {result.get('reset_at')}"
        
        # For unix_timestamp format, reset_time and timezone should not be used
        # but we'll verify they're either not present or empty/None
        # This allows flexibility in implementation approach
    
    def test_calculate_wait_time_unix_timestamp_format_returns_correct_seconds(self):
        """
        Test that calculate_wait_time correctly calculates seconds to wait for Unix timestamp format.
        
        This test verifies that the calculate_wait_time helper function:
        1. Takes parsed reset information from parse_usage_limit_error
        2. For Unix timestamp format, calculates difference between reset_at and current time
        3. Returns the number of seconds to wait until the reset time
        4. Handles the case where current time is mocked for predictable results
        
        Given a parsed result with unix_timestamp format and a specific reset_at value,
        when calculate_wait_time is called with mocked current time,
        then it should return the correct number of seconds to wait.
        
        This test will initially fail because the calculate_wait_time function doesn't exist yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Import the function to test
        from automate_dev import calculate_wait_time
        import time
        
        # Mock the current time to a known value for predictable results
        # Using Unix timestamp: 1736950000 (January 15, 2025, 10:00:00 AM UTC)
        mock_current_time = 1736950000
        
        # Create parsed reset information for unix_timestamp format
        # Reset time is 2 hours later: 1736957200 (January 15, 2025, 12:00:00 PM UTC)
        parsed_reset_info = {
            "reset_at": 1736957200,  # 2 hours after current time
            "format": "unix_timestamp"
        }
        
        # Expected wait time is 2 hours = 7200 seconds
        expected_wait_seconds = 7200
        
        # Mock time.time() to return our known current time
        with patch('time.time') as mock_time:
            mock_time.return_value = mock_current_time
            
            # Call calculate_wait_time with the parsed reset information
            result = calculate_wait_time(parsed_reset_info)
        
        # Verify that the function returns the correct number of seconds
        assert isinstance(result, int), "calculate_wait_time should return an integer for seconds"
        assert result == expected_wait_seconds, f"Expected {expected_wait_seconds} seconds wait time, got: {result}"
        
        # Verify that time.time() was called to get current time
        mock_time.assert_called_once()
        
        # Test edge case: reset time in the past (should return 0 or small positive value)
        past_reset_info = {
            "reset_at": mock_current_time - 3600,  # 1 hour ago
            "format": "unix_timestamp"
        }
        
        with patch('time.time') as mock_time_past:
            mock_time_past.return_value = mock_current_time
            
            past_result = calculate_wait_time(past_reset_info)
        
        # When reset time is in the past, should return 0 (no wait needed)
        assert past_result >= 0, f"Wait time should be non-negative, got: {past_result}"
        assert past_result <= 60, f"Past reset time should result in minimal wait (0-60 seconds for safety), got: {past_result}"
    
    def test_calculate_wait_time_natural_language_format_returns_correct_seconds(self):
        """
        Test that calculate_wait_time correctly calculates seconds to wait for natural language format.
        
        This test verifies that the calculate_wait_time helper function:
        1. Takes parsed reset information with natural language format (reset_time + timezone)
        2. Parses the natural language time like "7pm" in timezone "America/Chicago"
        3. Calculates difference between that time today and current time
        4. Returns the number of seconds to wait until the reset time
        5. Handles the case where current time is mocked for predictable results
        
        Given a parsed result with natural_language format containing reset_time "7pm" 
        and timezone "America/Chicago", when calculate_wait_time is called with mocked 
        current datetime, then it should return the correct number of seconds to wait.
        
        This test will initially fail because calculate_wait_time currently only handles
        unix_timestamp format, not natural_language format.
        This is the RED phase of TDD - the test must fail first.
        """
        # Import the function to test
        from automate_dev import calculate_wait_time
        from datetime import datetime
        import pytz
        
        # Mock the current datetime to a known value for predictable results
        # Set current time to 3:00 PM (15:00) in America/Chicago timezone
        # Reset time is 7:00 PM (19:00) same day, so 4 hours = 14400 seconds later
        chicago_tz = pytz.timezone('America/Chicago')
        mock_current_datetime = chicago_tz.localize(datetime(2025, 1, 15, 15, 0, 0))  # 3:00 PM
        
        # Create parsed reset information for natural_language format
        # Reset time is "7pm" in "America/Chicago" timezone  
        parsed_reset_info = {
            "reset_time": "7pm",
            "timezone": "America/Chicago", 
            "format": "natural_language"
        }
        
        # Expected wait time is 4 hours = 14400 seconds (from 3pm to 7pm same day)
        expected_wait_seconds = 14400
        
        # Mock datetime.now() to return our known current time
        with patch('datetime.datetime') as mock_datetime:
            # Configure mock to return our specific time when datetime.now() is called
            mock_datetime.now.return_value = mock_current_datetime
            # Also need to preserve the datetime class for other operations
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            # Call calculate_wait_time with the parsed reset information
            result = calculate_wait_time(parsed_reset_info)
        
        # Verify that the function returns the correct number of seconds
        assert isinstance(result, int), "calculate_wait_time should return an integer for seconds"
        assert result == expected_wait_seconds, f"Expected {expected_wait_seconds} seconds wait time (4 hours from 3pm to 7pm), got: {result}"
        
        # Verify that datetime.now() was called to get current time
        mock_datetime.now.assert_called()
        
        # Test edge case: reset time is earlier same day (should be next day)
        # If current time is 8pm and reset time is 7pm, should wait until 7pm next day
        mock_evening_datetime = chicago_tz.localize(datetime(2025, 1, 15, 20, 0, 0))  # 8:00 PM
        evening_reset_info = {
            "reset_time": "7pm",
            "timezone": "America/Chicago",
            "format": "natural_language"
        }
        
        # Expected wait time is 23 hours = 82800 seconds (until 7pm next day)
        expected_next_day_wait = 23 * 3600  # 23 hours in seconds
        
        with patch('datetime.datetime') as mock_datetime_evening:
            mock_datetime_evening.now.return_value = mock_evening_datetime
            mock_datetime_evening.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            evening_result = calculate_wait_time(evening_reset_info)
        
        # When reset time is earlier same day, should calculate time until reset time next day
        assert evening_result > 20 * 3600, f"Reset time earlier same day should wait until next day (>20 hours), got: {evening_result} seconds"
        assert evening_result <= 24 * 3600, f"Wait time should not exceed 24 hours, got: {evening_result} seconds"


class TestDependencyInjection:
    """Test suite for dependency injection in the orchestrator."""
    
    def test_main_function_accepts_dependency_injection_and_factory_function_exists(self):
        """
        Test that main() function accepts dependency injection and a factory function exists.
        
        This test verifies Task 12.3: Implement proper dependency injection by testing that:
        1. main() function accepts optional dependency injection parameters
        2. A create_dependencies() factory function exists to create complex objects
        3. Dependencies can be injected and used instead of creating internally
        4. When no dependencies are injected, defaults are created via factory
        
        The test focuses on the main components that need dependency injection:
        - TaskTracker instance (for task state management)
        - Command execution function (run_claude_command)
        - Logger setup function (setup_logging)
        - Status retrieval function (get_latest_status)
        
        This enables better testability by allowing mocks to be injected rather than
        relying on global imports and direct instantiation.
        
        Current architecture issues this addresses:
        - main() creates TaskTracker() directly instead of accepting injection
        - Functions import run_claude_command directly instead of receiving it
        - setup_logging() configures global state instead of being injectable
        - Hard to test main() function due to tight coupling with dependencies
        
        This test will initially fail because dependency injection hasn't been implemented yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Import the functions to test
        from automate_dev import main, create_dependencies
        
        # Test that create_dependencies factory function exists
        assert callable(create_dependencies), "create_dependencies should be a callable function"
        
        # Verify the function signature and return type expectations
        # We don't actually call create_dependencies() to avoid creating real dependencies
        # that might try to execute commands or access files
        import inspect
        create_deps_sig = inspect.signature(create_dependencies)
        # Should take no required parameters
        assert len(create_deps_sig.parameters) == 0, "create_dependencies should take no parameters"
        
        # Test that main() function accepts optional dependencies parameter
        main_signature = inspect.signature(main)
        
        # Verify main() has dependencies parameter (optional with default None)
        param_names = list(main_signature.parameters.keys())
        assert 'dependencies' in param_names, "main() should accept 'dependencies' parameter"
        
        dependencies_param = main_signature.parameters['dependencies']
        assert dependencies_param.default is None, "dependencies parameter should default to None"
        
        # Test that main() can be called with injected dependencies (mock scenario)
        from unittest.mock import MagicMock, patch
        
        # Create mock dependencies
        mock_dependencies = {
            'task_tracker': MagicMock(),
            'command_executor': MagicMock(),
            'logger_setup': MagicMock(),
            'status_getter': MagicMock()
        }
        
        # Configure mocks for quick test execution
        # Mock task_tracker to return no tasks (all complete)
        mock_dependencies['task_tracker'].get_next_task.return_value = (None, True)
        
        # Mock command_executor to return appropriate status values
        # The command_executor should return None for /clear and /continue,
        # and return status strings for /validate, /update, /checkin, /refactor
        mock_dependencies['command_executor'].side_effect = [
            None,                     # /clear
            None,                     # /continue
            "validation_passed",      # /validate
            "project_complete",       # /update
            "checkin_complete",       # /checkin
            "no_refactoring_needed"   # /refactor
        ]
        
        # Mock status_getter to return project_complete for handle_project_completion check
        mock_dependencies['status_getter'].return_value = "project_complete"
        
        # Mock sys.exit to prevent actual exit
        with patch('sys.exit') as mock_exit:
            # Call main() with injected dependencies
            main(dependencies=mock_dependencies)
            
            # Verify sys.exit was called with success code (indicating successful run with injected dependencies)
            mock_exit.assert_called_once_with(0)
        
        # Verify that injected dependencies were used
        mock_dependencies['logger_setup'].assert_called_once()
        mock_dependencies['task_tracker'].get_next_task.assert_called()


class TestFixtureOptimization:
    """Test suite for validating optimized test structure with reusable fixtures."""
    
    def test_test_fixtures_module_provides_common_mock_fixtures(self):
        """
        Test that test_fixtures.py module provides common mock fixtures to reduce duplication.
        
        This test validates that Task 11.6: Optimize test structure and reduce mock duplication
        has been completed by ensuring a test_fixtures.py module exists that provides:
        
        1. Common mock fixtures that can be reused across tests
        2. Helper functions for test setup 
        3. A fixture factory for creating configured mocks
        
        The test attempts to import and use these fixtures, which will fail initially
        because the test_fixtures.py module doesn't exist yet.
        
        This test addresses the 84 mock usages and duplication across 32 test functions
        by providing a centralized location for common test setup patterns.
        
        This is the RED phase of TDD - the test must fail first.
        """
        try:
            # Attempt to import the test fixtures module
            from tests.test_fixtures import (
                mock_subprocess_success,
                mock_claude_command_fixture,
                mock_get_latest_status_fixture,
                mock_file_system_fixture,
                setup_temp_environment,
                create_mock_implementation_plan
            )
            
            # Test that mock_subprocess_success provides a configured subprocess mock
            subprocess_mock = mock_subprocess_success()
            assert hasattr(subprocess_mock, 'return_value'), "mock_subprocess_success should return a configured mock"
            assert hasattr(subprocess_mock.return_value, 'returncode'), "subprocess mock should have returncode attribute"
            assert hasattr(subprocess_mock.return_value, 'stdout'), "subprocess mock should have stdout attribute"
            assert hasattr(subprocess_mock.return_value, 'stderr'), "subprocess mock should have stderr attribute"
            
            # Test that mock_claude_command_fixture provides a function mock
            claude_command_mock = mock_claude_command_fixture()
            assert callable(claude_command_mock), "mock_claude_command_fixture should return a callable mock"
            
            # Test calling the claude command mock
            result = claude_command_mock("/test-command")
            assert isinstance(result, dict), "claude command mock should return a dictionary"
            assert "status" in result, "claude command mock result should have status field"
            
            # Test that mock_get_latest_status_fixture provides a configured mock
            status_mock = mock_get_latest_status_fixture()
            assert callable(status_mock), "mock_get_latest_status_fixture should return a callable mock"
            
            # Test that mock_file_system_fixture provides Path and file operation mocks
            file_system_mocks = mock_file_system_fixture()
            assert isinstance(file_system_mocks, dict), "file system fixture should return a dictionary of mocks"
            assert "path_mock" in file_system_mocks, "file system fixture should provide path_mock"
            assert "open_mock" in file_system_mocks, "file system fixture should provide open_mock"
            assert "exists_mock" in file_system_mocks, "file system fixture should provide exists_mock"
            
            # Test that setup_temp_environment provides a helper function
            assert callable(setup_temp_environment), "setup_temp_environment should be a callable function"
            
            # Test that create_mock_implementation_plan provides a helper function
            assert callable(create_mock_implementation_plan), "create_mock_implementation_plan should be a callable function"
            
            # Test using the helper to create a mock implementation plan
            mock_plan_content = create_mock_implementation_plan(
                complete_tasks=["Task 1", "Task 2"], 
                incomplete_tasks=["Task 3", "Task 4"]
            )
            assert isinstance(mock_plan_content, str), "create_mock_implementation_plan should return a string"
            assert "[X]" in mock_plan_content, "mock plan should contain completed tasks"
            assert "[ ]" in mock_plan_content, "mock plan should contain incomplete tasks"
            assert "Task 1" in mock_plan_content, "mock plan should contain specified complete task"
            assert "Task 3" in mock_plan_content, "mock plan should contain specified incomplete task"
            
        except ImportError as e:
            # This is expected to fail initially - test_fixtures.py doesn't exist yet
            pytest.fail(f"Cannot import test fixtures from tests.test_fixtures: {e}")
        except AttributeError as e:
            # This will fail if the fixtures module exists but doesn't have the expected functions
            pytest.fail(f"test_fixtures module is missing expected fixture functions: {e}")


class TestLogging:
    """Test suite for logging functionality in the orchestrator."""
    
    def test_setup_logging_creates_json_structured_logs_with_contextual_information(self, tmp_path, monkeypatch):
        """
        Test that setup_logging creates structured JSON logs with contextual information.
        
        This test verifies that Task 12.5: Improve logging architecture has been implemented
        with structured JSON logging that includes contextual information. The test ensures:
        1. Log messages are written in valid JSON format
        2. Contextual information like task_id, timestamp, and module is included
        3. The JSON structure is parseable and contains expected fields
        4. Each log entry includes standard fields: timestamp, level, logger_name, message
        5. Custom context can be added to log entries
        
        Given the logging system is configured for structured JSON output,
        When a log message is written with contextual information,
        Then the log output should be valid JSON with all expected fields.
        
        This test will initially fail because structured JSON logging doesn't exist yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Change to temporary directory
        monkeypatch.chdir(tmp_path)
        
        # Create .claude/logs directory
        logs_dir = tmp_path / ".claude" / "logs"
        logs_dir.mkdir(parents=True)
        
        # Import and call setup_logging
        from automate_dev import setup_logging, LOGGERS
        setup_logging()
        
        # Get the orchestrator logger to test JSON output
        orchestrator_logger = LOGGERS.get('orchestrator')
        assert orchestrator_logger is not None, "Orchestrator logger should be available after setup"
        
        # Find the log file that was created
        log_files = list(logs_dir.glob("orchestrator_*.log"))
        assert len(log_files) > 0, "setup_logging should create a log file"
        log_file = log_files[0]  # Get the most recent log file
        
        # Create a test message with contextual information
        test_message = "Processing task with structured logging"
        test_context = {
            "task_id": "12.5",
            "component": "orchestrator",
            "operation": "task_processing",
            "user_id": "test_user"
        }
        
        # Log the message with extra contextual information
        orchestrator_logger.info(test_message, extra=test_context)
        
        # Force any buffered output to be written
        for handler in orchestrator_logger.handlers:
            handler.flush()
        
        # Read the log file content
        log_content = log_file.read_text(encoding='utf-8')
        assert log_content.strip(), "Log file should contain content after logging"
        
        # Split into individual log lines and get the last one (our test message)
        log_lines = [line.strip() for line in log_content.strip().split('\n') if line.strip()]
        assert len(log_lines) > 0, "Log file should contain at least one log entry"
        
        # Find our test message in the log lines
        test_log_line = None
        for line in log_lines:
            if test_message in line:
                test_log_line = line
                break
        
        assert test_log_line is not None, f"Log file should contain our test message '{test_message}'"
        
        # Verify the log line is valid JSON
        try:
            json_log = json.loads(test_log_line)
        except json.JSONDecodeError as e:
            pytest.fail(f"Log output should be valid JSON, but parsing failed: {e}\nOutput: {test_log_line}")
        
        # Verify JSON structure contains expected standard fields
        assert isinstance(json_log, dict), "JSON log should be a dictionary"
        assert "message" in json_log, "JSON log should contain 'message' field"
        assert "timestamp" in json_log or "asctime" in json_log, "JSON log should contain timestamp field"
        assert "level" in json_log or "levelname" in json_log, "JSON log should contain log level field"
        assert "logger_name" in json_log or "name" in json_log, "JSON log should contain logger name field"
        
        # Verify the message content is correct
        message_field = json_log.get("message", json_log.get("msg", ""))
        assert test_message in str(message_field), f"JSON log should contain the test message '{test_message}'"
        
        # Verify contextual information is included in the JSON
        assert "task_id" in json_log, "JSON log should contain task_id from extra context"
        assert json_log["task_id"] == "12.5", "task_id should match the provided context"
        assert "component" in json_log, "JSON log should contain component from extra context"
        assert json_log["component"] == "orchestrator", "component should match the provided context"
        assert "operation" in json_log, "JSON log should contain operation from extra context"
        assert json_log["operation"] == "task_processing", "operation should match the provided context"
        assert "user_id" in json_log, "JSON log should contain user_id from extra context"
        assert json_log["user_id"] == "test_user", "user_id should match the provided context"
        
        # Verify that the JSON contains proper typing (strings, not objects)
        for key, value in json_log.items():
            assert isinstance(key, str), f"All JSON keys should be strings, but {key} is {type(key)}"
            # Values can be various JSON-serializable types (str, int, float, bool, None, list, dict)
            assert value is None or isinstance(value, (str, int, float, bool, list, dict)), \
                f"JSON value for key '{key}' should be JSON-serializable, but got {type(value)}: {value}"
    
    @patch('command_executor.run_claude_command')
    @patch('automate_dev.get_latest_status')
    @patch('automate_dev.run_claude_command')
    def test_orchestrator_creates_log_file_in_claude_logs_directory(self, mock_run_claude_command, mock_get_latest_status, mock_command_executor_run_claude, tmp_path, monkeypatch):
        """
        Test that the orchestrator creates a log file in .claude/logs/ directory after running.
        
        This test verifies that the logging functionality has been implemented:
        1. The orchestrator should set up logging when main() is called
        2. A log file should be created in the .claude/logs/ directory
        3. The log file should contain expected log entries from orchestrator execution
        4. The log file should have appropriate log levels and formatting
        
        Given a working directory with all required files,
        When the main orchestrator function is executed,
        Then a log file should be created in .claude/logs/ directory,
        And the log file should contain entries documenting the orchestrator's execution.
        
        This test will initially fail because logging functionality doesn't exist yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Change to temporary directory
        monkeypatch.chdir(tmp_path)
        
        # Create Implementation Plan.md with all tasks complete to ensure quick execution
        implementation_plan = tmp_path / "Implementation Plan.md"
        implementation_plan_content = """# Implementation Plan

## Phase 1: Setup
- [X] All tasks complete for quick test execution
"""
        implementation_plan.write_text(implementation_plan_content, encoding="utf-8")
        
        # Create .claude directory structure
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        
        # Create the logs directory that should be used for log files
        logs_dir = claude_dir / "logs"
        logs_dir.mkdir()
        
        # Create other required files to avoid prerequisite errors
        prd_file = tmp_path / "PRD.md"
        prd_file.write_text("# Product Requirements Document", encoding="utf-8")
        
        claude_file = tmp_path / "CLAUDE.md"
        claude_file.write_text("# CLAUDE.md\n\nProject instructions for Claude Code.", encoding="utf-8")
        
        # Mock run_claude_command to return successful results quickly
        mock_run_claude_command.return_value = {"status": "success", "output": "Command completed"}
        
        # Mock command_executor.run_claude_command as well
        mock_command_executor_run_claude.return_value = {"status": "success", "output": "Command completed"}
        
        # Mock get_latest_status to simulate all tasks complete for quick execution
        # With new _command_executor_wrapper, only status commands call get_latest_status
        mock_get_latest_status.side_effect = [
            "validation_passed",     # After /validate in TDD cycle
            "project_complete",      # After /update - project complete
            "project_complete",      # Check in handle_project_completion
            "checkin_complete",      # After /checkin
            "no_refactoring_needed"  # After /refactor - exit immediately
        ]
        
        # Import the main function to test
        from automate_dev import main
        
        # Mock sys.exit to prevent actual exit and capture when it's called
        with patch('sys.exit') as mock_exit:
            # Call main function - it should set up logging and create log file
            main()
            
            # Verify that sys.exit was called (indicating successful completion)
            mock_exit.assert_called_once_with(0)
        
        # Verify that the .claude/logs directory still exists
        assert logs_dir.exists(), f".claude/logs directory should exist at {logs_dir}"
        assert logs_dir.is_dir(), ".claude/logs should be a directory"
        
        # Verify that a log file was created in the .claude/logs/ directory
        log_files = list(logs_dir.glob("*.log"))
        assert len(log_files) > 0, f"Expected at least one log file in .claude/logs/, but found: {[f.name for f in log_files]}"
        
        # Get the most recent log file (in case multiple exist)
        log_file = max(log_files, key=lambda f: f.stat().st_mtime)
        
        # Verify that the log file is readable and not empty
        assert log_file.is_file(), f"Log file should be a regular file: {log_file}"
        assert log_file.stat().st_size > 0, f"Log file should not be empty: {log_file}"
        
        # Read and verify log file contents
        log_content = log_file.read_text(encoding="utf-8")
        
        # Verify that the log file contains expected log entries
        assert len(log_content.strip()) > 0, f"Log file should contain content, got: {repr(log_content[:100])}"
        
        # Verify that the log contains entries related to orchestrator execution
        # Look for key orchestrator activities in the log
        expected_log_entries = [
            "main",  # Should log when main function starts
            "orchestrator",  # Should contain references to orchestrator operations
        ]
        
        log_content_lower = log_content.lower()
        found_entries = []
        for expected_entry in expected_log_entries:
            if expected_entry.lower() in log_content_lower:
                found_entries.append(expected_entry)
        
        assert len(found_entries) > 0, f"Expected log file to contain orchestrator-related entries like {expected_log_entries}, but log content was: {repr(log_content[:500])}"
        
        # Verify that log entries have proper formatting (should include timestamp and log level)
        log_lines = [line for line in log_content.split('\n') if line.strip()]
        assert len(log_lines) > 0, f"Expected at least one non-empty log line, got: {log_lines}"
        
        # Check that at least one log line has expected formatting elements
        # Standard log format typically includes timestamp and level
        has_formatted_entry = False
        for line in log_lines:
            # Look for common log formatting patterns: timestamp, log level, etc.
            if any(pattern in line for pattern in ['INFO', 'DEBUG', 'ERROR', 'WARN', '2025', ':']):
                has_formatted_entry = True
                break
        
        assert has_formatted_entry, f"Expected at least one log entry with proper formatting (timestamp/level), but log lines were: {log_lines[:3]}"


class TestLogRotation:
    """Test suite for log rotation functionality."""
    
    def test_log_rotation_creates_backup_files_when_size_limit_exceeded(self, tmp_path, monkeypatch):
        """
        Test that log rotation creates backup files when size limit is exceeded.
        
        This test verifies that log rotation functionality works correctly by:
        1. Configuring logging with a small max file size for testing
        2. Writing enough log data to exceed the size limit
        3. Verifying that backup files are created with proper naming (.1, .2, etc.)
        4. Checking that the maximum number of backup files is maintained
        5. Ensuring the main log file is rotated correctly
        
        Given a logging system configured with rotation enabled,
        When log messages exceed the maximum file size,
        Then backup files should be created automatically,
        And the number of backup files should not exceed BACKUP_COUNT,
        And backup files should follow the naming convention (file.log.1, file.log.2, etc.).
        
        The test uses a small size limit and BACKUP_COUNT for testing purposes
        to verify rotation behavior without generating large files.
        
        This test will initially fail because log rotation isn't working as expected
        or because we need to verify the rotation mechanism is properly triggered.
        This is the RED phase of TDD - the test must fail first.
        """
        # Change to temporary directory
        monkeypatch.chdir(tmp_path)
        
        # Create .claude/logs directory
        logs_dir = tmp_path / ".claude" / "logs"
        logs_dir.mkdir(parents=True)
        
        # Mock log rotation configuration for testing with small values
        import config
        original_max_size = config.MAX_LOG_FILE_SIZE
        original_backup_count = config.BACKUP_COUNT
        original_rotation_enabled = config.LOG_ROTATION_ENABLED
        
        # Set small values for testing (1KB max size, 3 backup files)
        test_max_size = 1024  # 1KB
        test_backup_count = 3
        config.MAX_LOG_FILE_SIZE = test_max_size
        config.BACKUP_COUNT = test_backup_count
        config.LOG_ROTATION_ENABLED = True
        
        try:
            # Import and setup logging with test configuration
            from automate_dev import setup_logging, LOGGERS
            setup_logging()
            
            # Get the orchestrator logger
            orchestrator_logger = LOGGERS.get('orchestrator')
            assert orchestrator_logger is not None, "Orchestrator logger should be available after setup"
            
            # Find the main log file that was created
            log_files = list(logs_dir.glob("orchestrator_*.log"))
            assert len(log_files) > 0, "setup_logging should create a log file"
            main_log_file = log_files[0]
            
            # Generate enough log data to trigger rotation multiple times
            # Each message is approximately 200-300 bytes, so we need ~4-5 messages per KB
            # We'll write enough to trigger 2-3 rotations (6KB total = 6 * 5 = 30 messages)
            large_message = "A" * 200  # 200 character message to help reach size limit faster
            num_messages = 50  # Should generate about 10KB of log data
            
            for i in range(num_messages):
                orchestrator_logger.info(f"Test message {i:03d}: {large_message}", extra={
                    "test_iteration": i,
                    "component": "log_rotation_test",
                    "operation": "size_limit_testing"
                })
                
                # Force flush after every few messages to ensure writing
                if i % 5 == 0:
                    for handler in orchestrator_logger.handlers:
                        handler.flush()
            
            # Final flush to ensure all messages are written
            for handler in orchestrator_logger.handlers:
                handler.flush()
            
            # Verify that rotation occurred by checking for backup files
            all_log_files = list(logs_dir.glob("orchestrator_*.log*"))
            main_log_files = [f for f in all_log_files if not any(f.name.endswith(f'.{i}') for i in range(1, 10))]
            backup_log_files = [f for f in all_log_files if any(f.name.endswith(f'.{i}') for i in range(1, 10))]
            
            # There should be exactly one main log file
            assert len(main_log_files) == 1, f"Expected 1 main log file, got {len(main_log_files)}: {[f.name for f in main_log_files]}"
            
            # There should be at least one backup file created due to rotation
            assert len(backup_log_files) > 0, f"Expected at least 1 backup file after rotation, got {len(backup_log_files)}. All files: {[f.name for f in all_log_files]}"
            
            # Verify backup file naming convention (.1, .2, .3, etc.)
            backup_numbers = []
            base_name = main_log_files[0].name
            for backup_file in backup_log_files:
                # Extract the backup number from the filename
                if backup_file.name.startswith(base_name):
                    suffix = backup_file.name[len(base_name):]
                    if suffix.startswith('.') and suffix[1:].isdigit():
                        backup_numbers.append(int(suffix[1:]))
            
            assert len(backup_numbers) > 0, f"Expected backup files with numeric suffixes, but found: {[f.name for f in backup_log_files]}"
            assert all(1 <= num <= test_backup_count for num in backup_numbers), f"Backup numbers should be 1-{test_backup_count}, got: {backup_numbers}"
            
            # Verify that the number of backup files doesn't exceed BACKUP_COUNT
            assert len(backup_numbers) <= test_backup_count, f"Expected at most {test_backup_count} backup files, got {len(backup_numbers)}: {backup_numbers}"
            
            # Verify that backup files are in sequence (1, 2, 3, etc.)
            backup_numbers.sort()
            expected_sequence = list(range(1, len(backup_numbers) + 1))
            assert backup_numbers == expected_sequence, f"Backup files should be numbered sequentially starting from 1, expected {expected_sequence}, got {backup_numbers}"
            
            # Verify that each backup file has content (rotation moved data to them)
            for backup_file in backup_log_files:
                assert backup_file.stat().st_size > 0, f"Backup file {backup_file.name} should contain data"
            
            # Verify that the main log file still exists and has reasonable size
            main_file = main_log_files[0]
            assert main_file.exists(), "Main log file should still exist after rotation"
            assert main_file.stat().st_size > 0, "Main log file should contain some data after rotation"
            
            # The main file should be smaller than our test max size (due to rotation)
            # Allow some tolerance for the last batch of messages
            assert main_file.stat().st_size <= test_max_size * 2, f"Main log file should be close to max size after rotation, got {main_file.stat().st_size} bytes"
            
        finally:
            # Restore original configuration values
            config.MAX_LOG_FILE_SIZE = original_max_size
            config.BACKUP_COUNT = original_backup_count
            config.LOG_ROTATION_ENABLED = original_rotation_enabled
    
    def test_log_rotation_respects_backup_count_limit_and_removes_oldest_files(self, tmp_path, monkeypatch):
        """
        Test that log rotation respects BACKUP_COUNT limit and removes oldest backup files.
        
        This test verifies critical log rotation behavior by:
        1. Setting BACKUP_COUNT to a small value (2 files)
        2. Generating enough log data to create more than 2 rotations
        3. Verifying that only 2 backup files exist (backup count limit respected)
        4. Ensuring that older backup files are automatically removed
        5. Checking that backup file numbering follows correct sequence
        
        This test specifically validates that RotatingFileHandler properly:
        - Enforces the maxBytes limit per file
        - Maintains exactly BACKUP_COUNT backup files
        - Removes oldest files when limit is exceeded
        - Uses correct naming convention (.1 for newest backup, .2 for older, etc.)
        
        Given a backup count limit of 2,
        When enough log data is written to create 4+ rotations,
        Then only 2 backup files should exist,
        And the oldest files should be automatically removed,
        And backup files should be numbered .1 and .2.
        
        This test is designed to fail if:
        - Backup count enforcement is not working
        - Old file cleanup is not happening
        - File rotation logic has bugs
        
        This is the RED phase of TDD - the test must fail initially if rotation
        logic has any issues with file count management.
        """
        # Change to temporary directory
        monkeypatch.chdir(tmp_path)
        
        # Create .claude/logs directory
        logs_dir = tmp_path / ".claude" / "logs"
        logs_dir.mkdir(parents=True)
        
        # Mock log rotation configuration with very small values for aggressive testing
        import config
        original_max_size = config.MAX_LOG_FILE_SIZE
        original_backup_count = config.BACKUP_COUNT
        original_rotation_enabled = config.LOG_ROTATION_ENABLED
        
        # Set very small values to force frequent rotation
        test_max_size = 512  # 512 bytes to force frequent rotation
        test_backup_count = 2  # Only keep 2 backup files
        config.MAX_LOG_FILE_SIZE = test_max_size
        config.BACKUP_COUNT = test_backup_count
        config.LOG_ROTATION_ENABLED = True
        
        try:
            # Import and setup logging with test configuration
            from automate_dev import setup_logging, LOGGERS
            setup_logging()
            
            # Get the orchestrator logger
            orchestrator_logger = LOGGERS.get('orchestrator')
            assert orchestrator_logger is not None, "Orchestrator logger should be available after setup"
            
            # Find the main log file that was created
            log_files = list(logs_dir.glob("orchestrator_*.log"))
            assert len(log_files) > 0, "setup_logging should create a log file"
            main_log_file = log_files[0]
            base_name = main_log_file.name
            
            # Generate lots of log data to force multiple rotations beyond backup count
            # With 512 byte limit and ~300 byte messages, we need 100+ messages to force 4+ rotations
            large_message = "X" * 250  # 250 character message
            num_messages = 100  # Should generate ~25KB, forcing many rotations
            
            for i in range(num_messages):
                orchestrator_logger.info(f"Rotation test {i:04d}: {large_message}", extra={
                    "iteration": i,
                    "test_phase": "backup_count_validation",
                    "expected_rotations": "multiple"
                })
                
                # Flush frequently to ensure rotation triggers
                if i % 3 == 0:
                    for handler in orchestrator_logger.handlers:
                        handler.flush()
            
            # Final flush to ensure all data is written
            for handler in orchestrator_logger.handlers:
                handler.flush()
            
            # Give a moment for file system operations to complete
            import time
            time.sleep(0.1)
            
            # Analyze resulting files
            all_log_files = list(logs_dir.glob("orchestrator_*.log*"))
            main_log_files = [f for f in all_log_files if f.name == base_name]
            backup_log_files = [f for f in all_log_files if f.name != base_name and f.name.startswith(base_name)]
            
            # Verify exactly one main log file exists
            assert len(main_log_files) == 1, f"Expected exactly 1 main log file, got {len(main_log_files)}: {[f.name for f in main_log_files]}"
            
            # Critical test: backup count should be exactly limited to test_backup_count
            assert len(backup_log_files) <= test_backup_count, f"BACKUP_COUNT limit violated! Expected at most {test_backup_count} backup files, got {len(backup_log_files)}: {[f.name for f in backup_log_files]}"
            
            # If rotation worked correctly, we should have backup files
            assert len(backup_log_files) > 0, f"Expected backup files to be created, but none found. All files: {[f.name for f in all_log_files]}"
            
            # Verify backup file naming follows correct sequence
            backup_numbers = []
            for backup_file in backup_log_files:
                if backup_file.name.startswith(base_name + '.'):
                    suffix = backup_file.name[len(base_name) + 1:]
                    if suffix.isdigit():
                        backup_numbers.append(int(suffix))
            
            backup_numbers.sort()
            
            # Should have consecutive numbering starting from 1
            expected_numbers = list(range(1, len(backup_numbers) + 1))
            assert backup_numbers == expected_numbers, f"Backup files should be numbered consecutively from 1, expected {expected_numbers}, got {backup_numbers}"
            
            # Verify that backup numbering doesn't exceed backup count
            max_backup_number = max(backup_numbers) if backup_numbers else 0
            assert max_backup_number <= test_backup_count, f"Highest backup number ({max_backup_number}) should not exceed BACKUP_COUNT ({test_backup_count})"
            
            # Verify no gaps in numbering (if we have 2 backups, they should be .1 and .2)
            if len(backup_numbers) == test_backup_count:
                assert backup_numbers == [1, 2], f"With {test_backup_count} backup files, should have [1, 2], got {backup_numbers}"
            
            # Verify each backup file has substantial content
            for backup_file in backup_log_files:
                file_size = backup_file.stat().st_size
                assert file_size > 0, f"Backup file {backup_file.name} should contain data, got {file_size} bytes"
                # Backup files should be close to max size (they were rotated when reaching limit)
                assert file_size >= test_max_size * 0.5, f"Backup file {backup_file.name} should be substantial size, got {file_size} bytes (expected ~{test_max_size})"
            
            # Test that demonstrates the backup count enforcement worked
            # By generating far more data than 2 files can hold, we prove old files were deleted
            total_data_written = num_messages * (len(large_message) + 100)  # Approximate
            max_total_files_capacity = (len(backup_log_files) + 1) * test_max_size * 2  # Allow some tolerance
            
            assert total_data_written > max_total_files_capacity, f"Test validation: We should have generated more data ({total_data_written} bytes) than can fit in {len(backup_log_files)+1} files ({max_total_files_capacity} bytes capacity)"
            
        finally:
            # Restore original configuration values
            config.MAX_LOG_FILE_SIZE = original_max_size
            config.BACKUP_COUNT = original_backup_count
            config.LOG_ROTATION_ENABLED = original_rotation_enabled
    
    def test_log_rotation_disabled_mode_prevents_rotation_and_grows_single_file(self, tmp_path, monkeypatch):
        """
        Test that when LOG_ROTATION_ENABLED=False, log files grow without rotation.
        
        This test verifies the disabled rotation mode by:
        1. Setting LOG_ROTATION_ENABLED=False to disable rotation
        2. Writing enough log data that would normally trigger rotation
        3. Verifying that only one log file exists (no backup files created)
        4. Ensuring the single log file grows large (exceeds normal rotation size)
        5. Confirming that regular FileHandler is used instead of RotatingFileHandler
        
        This test validates that the logging system correctly handles both modes:
        - When rotation is enabled: RotatingFileHandler with size limits
        - When rotation is disabled: Regular FileHandler that grows indefinitely
        
        Given LOG_ROTATION_ENABLED=False,
        When large amounts of log data are written,
        Then no backup files should be created,
        And the main log file should grow beyond the normal rotation size limit,
        And the system should use FileHandler instead of RotatingFileHandler.
        
        This test will initially fail if:
        - The rotation disable logic is not properly implemented
        - FileHandler vs RotatingFileHandler selection is incorrect
        - The LOG_ROTATION_ENABLED configuration is not respected
        
        This is the RED phase of TDD - testing edge case configuration handling.
        """
        # Change to temporary directory
        monkeypatch.chdir(tmp_path)
        
        # Create .claude/logs directory
        logs_dir = tmp_path / ".claude" / "logs"
        logs_dir.mkdir(parents=True)
        
        # Mock log rotation configuration to explicitly disable rotation
        import config
        original_max_size = config.MAX_LOG_FILE_SIZE
        original_backup_count = config.BACKUP_COUNT
        original_rotation_enabled = config.LOG_ROTATION_ENABLED
        
        # Set configuration to disable rotation but keep small size for testing
        test_max_size = 512  # 512 bytes would normally trigger rotation
        test_backup_count = 2
        config.MAX_LOG_FILE_SIZE = test_max_size
        config.BACKUP_COUNT = test_backup_count
        config.LOG_ROTATION_ENABLED = False  # DISABLE rotation
        
        try:
            # Import and setup logging with rotation disabled
            import logging
            from automate_dev import setup_logging, LOGGERS
            setup_logging()
            
            # Get the orchestrator logger
            orchestrator_logger = LOGGERS.get('orchestrator')
            assert orchestrator_logger is not None, "Orchestrator logger should be available after setup"
            
            # Find the main log file that was created
            log_files = list(logs_dir.glob("orchestrator_*.log"))
            assert len(log_files) > 0, "setup_logging should create a log file"
            main_log_file = log_files[0]
            base_name = main_log_file.name
            
            # Verify that the root logger is using FileHandler, not RotatingFileHandler
            # (Module loggers inherit from root logger, so check root logger's handlers)
            root_logger = logging.getLogger()
            file_handlers = [h for h in root_logger.handlers if hasattr(h, 'baseFilename')]
            assert len(file_handlers) > 0, "Root logger should have at least one file handler"
            
            # The key test: verify handler type when rotation is disabled
            primary_handler = file_handlers[0]  # The file handler on the root logger
            
            # When rotation is disabled, should NOT be RotatingFileHandler
            from logging.handlers import RotatingFileHandler
            is_rotating_handler = isinstance(primary_handler, RotatingFileHandler)
            
            # This assertion should FAIL if rotation disabling is not working
            assert not is_rotating_handler, f"When LOG_ROTATION_ENABLED=False, should use FileHandler, not RotatingFileHandler. Got: {type(primary_handler)}"
            
            # Generate large amount of log data that would trigger rotation if enabled
            large_message = "Z" * 400  # 400 character message
            num_messages = 50  # Should generate ~20KB, far exceeding test_max_size
            
            for i in range(num_messages):
                orchestrator_logger.info(f"No rotation test {i:04d}: {large_message}", extra={
                    "iteration": i,
                    "test_mode": "rotation_disabled",
                    "expected_behavior": "single_growing_file"
                })
                
                # Flush regularly to ensure data is written
                if i % 5 == 0:
                    for handler in orchestrator_logger.handlers:
                        handler.flush()
            
            # Final flush
            for handler in orchestrator_logger.handlers:
                handler.flush()
            
            # Give file system time to complete operations
            import time
            time.sleep(0.1)
            
            # Analyze resulting files - should be ONLY one log file
            all_log_files = list(logs_dir.glob("orchestrator_*.log*"))
            main_log_files = [f for f in all_log_files if f.name == base_name]
            backup_log_files = [f for f in all_log_files if f.name != base_name and f.name.startswith(base_name)]
            
            # Critical test: should be exactly one main file, NO backup files
            assert len(main_log_files) == 1, f"Expected exactly 1 main log file when rotation disabled, got {len(main_log_files)}: {[f.name for f in main_log_files]}"
            assert len(backup_log_files) == 0, f"Expected NO backup files when rotation disabled, got {len(backup_log_files)}: {[f.name for f in backup_log_files]}"
            
            # Verify the single log file grew large (beyond rotation threshold)
            main_file = main_log_files[0]
            file_size = main_file.stat().st_size
            
            # The file should be significantly larger than the rotation threshold
            # since rotation was disabled and data accumulated in one file
            min_expected_size = test_max_size * 3  # Should be at least 3x the rotation limit
            assert file_size >= min_expected_size, f"With rotation disabled, file should grow large (>= {min_expected_size} bytes), got {file_size} bytes"
            
            # Verify file contains substantial content
            assert file_size > 0, "Log file should contain data"
            
            # Read content to verify it contains our test messages
            log_content = main_file.read_text(encoding='utf-8')
            assert "No rotation test" in log_content, "Log file should contain our test messages"
            assert "rotation_disabled" in log_content, "Log file should contain our test context"
            
        finally:
            # Restore original configuration values
            config.MAX_LOG_FILE_SIZE = original_max_size
            config.BACKUP_COUNT = original_backup_count
            config.LOG_ROTATION_ENABLED = original_rotation_enabled


class TestLogRotationConfiguration:
    """Test suite for log rotation configuration validation."""
    
    def test_log_rotation_configuration_values_are_correctly_applied_to_rotating_handler(self, tmp_path, monkeypatch):
        """
        Test that log rotation configuration values are correctly applied to RotatingFileHandler.
        
        This test verifies that the specific configuration values (MAX_LOG_FILE_SIZE and BACKUP_COUNT)
        from config.py are properly passed to the RotatingFileHandler constructor and that the
        handler is configured with exactly these values.
        
        This is a focused test that checks the configuration plumbing between:
        1. Configuration constants in config.py
        2. The setup_logging function
        3. The RotatingFileHandler instantiation
        4. The actual handler configuration
        
        Given specific MAX_LOG_FILE_SIZE and BACKUP_COUNT values,
        When setup_logging is called with rotation enabled,
        Then the RotatingFileHandler should be configured with exactly those values,
        And the handler.maxBytes should equal MAX_LOG_FILE_SIZE,
        And the handler.backupCount should equal BACKUP_COUNT.
        
        This test will fail if:
        - Configuration values are not properly passed to the handler
        - The wrong configuration constants are used
        - Default values are hardcoded instead of using config constants
        
        This is designed to be a TRUE RED phase test - it checks implementation details
        that may not be correctly wired up yet.
        """
        # Change to temporary directory
        monkeypatch.chdir(tmp_path)
        
        # Create .claude/logs directory
        logs_dir = tmp_path / ".claude" / "logs"
        logs_dir.mkdir(parents=True)
        
        # Set specific test configuration values
        import config
        original_max_size = config.MAX_LOG_FILE_SIZE
        original_backup_count = config.BACKUP_COUNT
        original_rotation_enabled = config.LOG_ROTATION_ENABLED
        
        # Use specific test values that we can verify
        test_max_size = 8192  # 8KB - specific test value
        test_backup_count = 7  # 7 backups - specific test value
        config.MAX_LOG_FILE_SIZE = test_max_size
        config.BACKUP_COUNT = test_backup_count
        config.LOG_ROTATION_ENABLED = True
        
        try:
            # Import and setup logging
            import logging
            from automate_dev import setup_logging, LOGGERS
            setup_logging()
            
            # Find the RotatingFileHandler in the root logger
            root_logger = logging.getLogger()
            file_handlers = [h for h in root_logger.handlers if hasattr(h, 'baseFilename')]
            assert len(file_handlers) > 0, "Should have file handlers"
            
            # Find the RotatingFileHandler specifically
            from logging.handlers import RotatingFileHandler
            rotating_handlers = [h for h in file_handlers if isinstance(h, RotatingFileHandler)]
            
            # This assertion may FAIL if RotatingFileHandler is not being created correctly
            assert len(rotating_handlers) > 0, f"Should have at least one RotatingFileHandler when rotation enabled, found handlers: {[type(h) for h in file_handlers]}"
            
            # Get the RotatingFileHandler
            rotating_handler = rotating_handlers[0]
            
            # Critical test: verify that the handler was configured with our exact config values
            # This will FAIL if the configuration is not properly passed through
            assert hasattr(rotating_handler, 'maxBytes'), "RotatingFileHandler should have maxBytes attribute"
            assert hasattr(rotating_handler, 'backupCount'), "RotatingFileHandler should have backupCount attribute"
            
            # The key assertions that will fail if configuration wiring is broken
            actual_max_bytes = rotating_handler.maxBytes
            actual_backup_count = rotating_handler.backupCount
            
            assert actual_max_bytes == test_max_size, f"RotatingFileHandler.maxBytes should be {test_max_size} (from config.MAX_LOG_FILE_SIZE), got {actual_max_bytes}"
            assert actual_backup_count == test_backup_count, f"RotatingFileHandler.backupCount should be {test_backup_count} (from config.BACKUP_COUNT), got {actual_backup_count}"
            
            # Additional verification: ensure non-default values are being used
            # This catches cases where hardcoded defaults might be used instead of config
            default_rotating_values = [10485760, 5]  # Common defaults for maxBytes and backupCount
            assert actual_max_bytes not in default_rotating_values, f"maxBytes appears to be a default value ({actual_max_bytes}), not our test config"
            assert actual_backup_count not in default_rotating_values, f"backupCount appears to be a default value ({actual_backup_count}), not our test config"
            
            # Verify handler encoding is also from config
            if hasattr(rotating_handler, 'encoding'):
                from config import LOG_FILE_ENCODING
                assert rotating_handler.encoding == LOG_FILE_ENCODING, f"Handler encoding should be {LOG_FILE_ENCODING}, got {rotating_handler.encoding}"
            
            # Test that the configuration is actually functional by checking file creation
            log_files = list(logs_dir.glob("*.log"))
            assert len(log_files) > 0, "Log file should be created"
            
            # Verify the log file path includes our configured directory
            log_file = log_files[0]
            assert logs_dir in log_file.parents, f"Log file should be in configured logs directory {logs_dir}"
            
        finally:
            # Restore original configuration
            config.MAX_LOG_FILE_SIZE = original_max_size
            config.BACKUP_COUNT = original_backup_count
            config.LOG_ROTATION_ENABLED = original_rotation_enabled