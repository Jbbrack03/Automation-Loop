"""
Tests for consistent error handling in the automate_dev.py orchestrator.

This test suite validates that error handling follows consistent patterns across
the orchestrator functions, focusing on the run_claude_command function as a
critical component. Tests check for:

1. Specific exception types are used instead of generic Exception
2. Error messages follow a consistent format
3. All error paths have appropriate logging

Following TDD principles, these tests are written before the error handling
improvements are implemented (RED phase).
"""

import json
import subprocess
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path


class TestErrorHandlingConsistency:
    """Test suite for consistent error handling patterns in the orchestrator."""
    
    def test_run_claude_command_raises_specific_exception_types_with_consistent_formatting(self):
        """
        Test that run_claude_command raises specific exception types with consistent error message formatting.
        
        This test validates that the run_claude_command function implements consistent error handling:
        1. Uses specific exception types (CommandExecutionError, JSONParseError) instead of generic Exception
        2. Error messages follow a consistent format: "[ERROR_TYPE]: {detailed_message} - Command: {command}"
        3. All error paths have appropriate logging with the error_handler logger
        
        This test focuses on three main error scenarios:
        - Subprocess execution failure: Should raise CommandExecutionError
        - JSON parsing failure: Should raise JSONParseError  
        - Signal file timeout: Should raise CommandTimeoutError
        
        The test will initially fail because:
        1. run_claude_command currently uses generic exceptions (subprocess.SubprocessError, json.JSONDecodeError)
        2. Error message formatting is inconsistent across error types
        3. Not all error paths use the error_handler logger
        
        This is the RED phase of TDD - the test must fail first.
        """
        # Import the function to test
        from command_executor import run_claude_command
        
        # Test Scenario 1: Subprocess execution failure should raise CommandExecutionError
        with patch('command_executor.subprocess.run') as mock_subprocess_run:
            # Configure subprocess to raise an exception
            mock_subprocess_run.side_effect = subprocess.SubprocessError("Command execution failed")
            
            # Mock the logger to capture error logs
            with patch('command_executor.LOGGERS') as mock_loggers:
                mock_error_logger = MagicMock()
                mock_loggers.__getitem__.return_value = mock_error_logger
                
                test_command = "/continue"
                
                # Expect CommandExecutionError (specific type, not generic Exception)
                with pytest.raises(Exception) as exc_info:
                    run_claude_command(test_command)
                
                # Verify specific exception type (will fail - currently raises subprocess.SubprocessError)
                assert exc_info.type.__name__ == "CommandExecutionError", (
                    f"Expected CommandExecutionError, got {exc_info.type.__name__}. "
                    "run_claude_command should raise specific exception types, not generic ones."
                )
                
                # Verify consistent error message format
                expected_format = f"[COMMAND_EXECUTION]: Failed to execute Claude CLI command - Command: {test_command}"
                assert expected_format in str(exc_info.value), (
                    f"Error message format is inconsistent. Expected format like '{expected_format}', "
                    f"got: {str(exc_info.value)}"
                )
                
                # Verify error was logged with error_handler logger (will fail - not currently implemented)
                mock_error_logger.error.assert_called_once()
                logged_message = mock_error_logger.error.call_args[0][0]
                assert "[COMMAND_EXECUTION]" in logged_message, (
                    f"Error should be logged with consistent format using error_handler logger. "
                    f"Got log message: {logged_message}"
                )
        
        # Test Scenario 2: JSON parsing failure should raise JSONParseError
        with patch('command_executor.subprocess.run') as mock_subprocess_run:
            with patch('os.path.exists', return_value=True):
                with patch('os.remove'):
                    # Configure subprocess to return invalid JSON
                    mock_result = MagicMock()
                    mock_result.returncode = 0
                    mock_result.stdout = "invalid json content {"
                    mock_result.stderr = ""
                    mock_subprocess_run.return_value = mock_result
                    
                    # Mock the logger to capture error logs  
                    with patch('command_executor.LOGGERS') as mock_loggers:
                        mock_error_logger = MagicMock()
                        mock_loggers.__getitem__.return_value = mock_error_logger
                        
                        test_command = "/validate"
                        
                        # Expect JSONParseError (specific type, not json.JSONDecodeError)
                        with pytest.raises(Exception) as exc_info:
                            run_claude_command(test_command)
                        
                        # Verify specific exception type (will fail - currently raises json.JSONDecodeError)
                        assert exc_info.type.__name__ == "JSONParseError", (
                            f"Expected JSONParseError, got {exc_info.type.__name__}. "
                            "run_claude_command should raise specific exception types for JSON parsing failures."
                        )
                        
                        # Verify consistent error message format
                        expected_format = f"[JSON_PARSE]: Failed to parse Claude CLI JSON output - Command: {test_command}"
                        assert expected_format in str(exc_info.value), (
                            f"JSON parse error message format is inconsistent. Expected format like '{expected_format}', "
                            f"got: {str(exc_info.value)}"
                        )
                        
                        # Verify error was logged with error_handler logger
                        mock_error_logger.error.assert_called()
                        logged_messages = [call[0][0] for call in mock_error_logger.error.call_args_list]
                        json_error_logged = any("[JSON_PARSE]" in msg for msg in logged_messages)
                        assert json_error_logged, (
                            f"JSON parse error should be logged with consistent format using error_handler logger. "
                            f"Got log messages: {logged_messages}"
                        )
        
        # Test Scenario 3: Signal file timeout should raise CommandTimeoutError
        with patch('command_executor.subprocess.run') as mock_subprocess_run:
            with patch('os.path.exists', return_value=False):  # Signal file never appears
                with patch('time.time', side_effect=[0, 1000, 2000, 3000]):  # Simulate time progression past timeout
                    # Configure subprocess to return valid result but signal file times out
                    mock_result = MagicMock()
                    mock_result.returncode = 0
                    mock_result.stdout = '{"status": "success"}'
                    mock_result.stderr = ""
                    mock_subprocess_run.return_value = mock_result
                    
                    # Mock the logger to capture error logs
                    with patch('command_executor.LOGGERS') as mock_loggers:
                        mock_error_logger = MagicMock()
                        mock_loggers.__getitem__.return_value = mock_error_logger
                        
                        test_command = "/update"
                        
                        # Expect CommandTimeoutError (specific type, not TimeoutError)  
                        with pytest.raises(Exception) as exc_info:
                            run_claude_command(test_command)
                        
                        # Verify specific exception type (will fail - currently raises TimeoutError)
                        assert exc_info.type.__name__ == "CommandTimeoutError", (
                            f"Expected CommandTimeoutError, got {exc_info.type.__name__}. "
                            "run_claude_command should raise specific exception types for timeout failures."
                        )
                        
                        # Verify consistent error message format  
                        expected_format = f"[COMMAND_TIMEOUT]: Claude command timed out waiting for completion signal - Command: {test_command}"
                        assert expected_format in str(exc_info.value), (
                            f"Timeout error message format is inconsistent. Expected format like '{expected_format}', "
                            f"got: {str(exc_info.value)}"
                        )
                        
                        # Verify error was logged with error_handler logger
                        mock_error_logger.error.assert_called()
                        logged_messages = [call[0][0] for call in mock_error_logger.error.call_args_list]
                        timeout_error_logged = any("[COMMAND_TIMEOUT]" in msg for msg in logged_messages)
                        assert timeout_error_logged, (
                            f"Timeout error should be logged with consistent format using error_handler logger. "
                            f"Got log messages: {logged_messages}"
                        )
    
    def test_error_handling_uses_specific_exception_hierarchy(self):
        """
        Test that the orchestrator defines a proper exception hierarchy for different error types.
        
        This test validates that the codebase defines specific exception classes that inherit
        from appropriate base classes, rather than using generic Exception types throughout.
        The exception hierarchy should be:
        
        OrchestratorError (base)
        ├── CommandExecutionError (subprocess failures)
        ├── JSONParseError (JSON parsing failures) 
        ├── CommandTimeoutError (signal file timeouts)
        └── ValidationError (validation failures)
        
        This test will initially fail because these specific exception classes don't exist yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Import the module to check for exception classes
        import automate_dev
        
        # Verify base orchestrator exception exists
        assert hasattr(automate_dev, 'OrchestratorError'), (
            "OrchestratorError base exception class should be defined for consistent error handling"
        )
        
        # Verify specific exception types exist
        expected_exceptions = [
            'CommandExecutionError',
            'JSONParseError', 
            'CommandTimeoutError',
            'ValidationError'
        ]
        
        for exc_name in expected_exceptions:
            assert hasattr(automate_dev, exc_name), (
                f"{exc_name} exception class should be defined for consistent error handling"
            )
        
        # Verify inheritance hierarchy
        OrchestratorError = getattr(automate_dev, 'OrchestratorError', None)
        if OrchestratorError:
            for exc_name in expected_exceptions:
                exc_class = getattr(automate_dev, exc_name, None)
                if exc_class:
                    assert issubclass(exc_class, OrchestratorError), (
                        f"{exc_name} should inherit from OrchestratorError for consistent error handling"
                    )
                    assert issubclass(exc_class, Exception), (
                        f"{exc_name} should inherit from Exception"
                    )
        
        # Verify exception classes have consistent error message formatting
        if hasattr(automate_dev, 'CommandExecutionError'):
            # Test that exceptions can be instantiated with consistent format
            try:
                exc = automate_dev.CommandExecutionError("test message", command="/test")
                assert "[COMMAND_EXECUTION]" in str(exc), (
                    "CommandExecutionError should include consistent error type prefix in message"
                )
            except TypeError:
                pytest.fail("CommandExecutionError should accept 'command' parameter for consistent formatting")
    
    def test_error_handler_logger_is_used_consistently(self):
        """
        Test that all error handling in run_claude_command uses the error_handler logger consistently.
        
        This test validates that:
        1. Error logging uses the LOGGERS['error_handler'] logger, not other loggers
        2. Error log messages follow a consistent format: "[ERROR_TYPE]: {message} - Command: {command}"
        3. Error logging happens before exceptions are raised
        4. Log level is appropriate (ERROR for failures, WARNING for recoverable issues)
        
        This test will initially fail because current error handling doesn't consistently
        use the error_handler logger or follow consistent message formatting.
        This is the RED phase of TDD - the test must fail first.
        """
        from command_executor import run_claude_command
        
        # Test that subprocess errors use error_handler logger
        with patch('command_executor.subprocess.run') as mock_subprocess_run:
            mock_subprocess_run.side_effect = subprocess.SubprocessError("Mock subprocess failure")
            
            with patch('command_executor.LOGGERS') as mock_loggers:
                # Set up mock loggers
                mock_error_logger = MagicMock()
                mock_command_logger = MagicMock()
                mock_loggers.__getitem__.side_effect = lambda key: {
                    'error_handler': mock_error_logger,
                    'command_executor': mock_command_logger
                }.get(key, MagicMock())
                
                test_command = "/test"
                
                try:
                    run_claude_command(test_command)
                except Exception:
                    pass  # We expect an exception
                
                # Verify error_handler logger was used for error logging (will fail initially)
                mock_error_logger.error.assert_called_once(), (
                    "Subprocess errors should be logged using LOGGERS['error_handler'], not other loggers"
                )
                
                # Verify consistent error message format
                logged_message = mock_error_logger.error.call_args[0][0]
                assert "[COMMAND_EXECUTION]:" in logged_message, (
                    f"Error log message should include consistent error type prefix. Got: {logged_message}"
                )
                assert f"Command: {test_command}" in logged_message, (
                    f"Error log message should include command context. Got: {logged_message}"
                )
                
                # Verify command_executor logger was not used for error logging
                # (it should only be used for normal operation logging)
                mock_command_logger.error.assert_not_called(), (
                    "Error logging should use error_handler logger, not command_executor logger"
                )
        
        # Test that JSON parsing errors use error_handler logger
        with patch('command_executor.subprocess.run') as mock_subprocess_run:
            with patch('os.path.exists', return_value=True):
                with patch('os.remove'):
                    # Mock subprocess to return invalid JSON
                    mock_result = MagicMock()
                    mock_result.returncode = 0
                    mock_result.stdout = "invalid json"
                    mock_result.stderr = ""
                    mock_subprocess_run.return_value = mock_result
                    
                    with patch('command_executor.LOGGERS') as mock_loggers:
                        mock_error_logger = MagicMock()
                        mock_loggers.__getitem__.return_value = mock_error_logger
                        
                        test_command = "/validate"
                        
                        try:
                            run_claude_command(test_command)
                        except Exception:
                            pass  # We expect an exception
                        
                        # Verify error_handler logger was used for JSON parse errors
                        mock_error_logger.error.assert_called()
                        
                        # Check that at least one log message has the correct format
                        logged_messages = [call[0][0] for call in mock_error_logger.error.call_args_list]
                        json_error_found = False
                        for msg in logged_messages:
                            if "[JSON_PARSE]:" in msg and f"Command: {test_command}" in msg:
                                json_error_found = True
                                break
                        
                        assert json_error_found, (
                            f"JSON parse error should be logged with consistent format. "
                            f"Expected '[JSON_PARSE]: ... Command: {test_command}' in messages: {logged_messages}"
                        )
        
        print("Error handler logger consistency test completed.")
        print("This test validates that all error paths use the error_handler logger with consistent formatting.")
        print("When implemented, error messages should follow: '[ERROR_TYPE]: {message} - Command: {command}'")