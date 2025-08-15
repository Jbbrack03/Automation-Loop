"""Command execution module.

This module provides functions for executing Claude CLI commands and handling
their completion and error conditions.
"""

import json
import subprocess
import time
from typing import Dict, List, Optional

from config import SIGNAL_FILE, LOGGERS
from usage_limit import parse_usage_limit_error, calculate_wait_time
from signal_handler import wait_for_signal_file


# Exception hierarchy for command execution errors
def _format_error_message(error_type: str, message: str, command: str = "") -> str:
    """Format error message with consistent pattern across all exception types.
    
    Creates standardized error messages in the format:
    "[ERROR_TYPE]: {message} - Command: {command}" when command is provided
    "[ERROR_TYPE]: {message}" when no command is provided
    
    Args:
        error_type: The type of error (e.g., "COMMAND_EXECUTION", "JSON_PARSE")
        message: The detailed error message
        command: Optional command context for debugging
        
    Returns:
        Formatted error message string with consistent structure
        
    Example:
        >>> _format_error_message("COMMAND_EXECUTION", "Failed to run command", "/continue")
        "[COMMAND_EXECUTION]: Failed to run command - Command: /continue"
        >>> _format_error_message("JSON_PARSE", "Invalid JSON response")
        "[JSON_PARSE]: Invalid JSON response"
    """
    if command:
        return f"[{error_type}]: {message} - Command: {command}"
    else:
        return f"[{error_type}]: {message}"


class CommandExecutionError(Exception):
    """Exception raised when Claude CLI command execution fails."""
    def __init__(self, message: str, command: str = ""):
        super().__init__(_format_error_message("COMMAND_EXECUTION", message, command))


class JSONParseError(Exception):
    """Exception raised when JSON parsing fails."""
    def __init__(self, message: str, command: str = ""):
        super().__init__(_format_error_message("JSON_PARSE", message, command))


class CommandTimeoutError(Exception):
    """Exception raised when commands timeout waiting for completion signal."""
    def __init__(self, message: str, command: str = ""):
        super().__init__(_format_error_message("COMMAND_TIMEOUT", message, command))


def _handle_usage_limit_and_retry(command: str, command_array: List[str], 
                                 result: subprocess.CompletedProcess, debug: bool = False) -> subprocess.CompletedProcess:
    """Handle usage limit error by waiting and retrying the command.
    
    Args:
        command: The Claude command being executed (for logging/context)
        command_array: The complete command array to retry
        result: The initial subprocess result that contained the usage limit error
        debug: Whether to enable debug logging
        
    Returns:
        subprocess.CompletedProcess from the retry attempt
        
    Note:
        This function handles the complete usage limit workflow:
        1. Parse usage limit error from initial result
        2. Calculate wait time until reset
        3. Wait for the specified duration
        4. Wait for signal file from first attempt
        5. Retry the command execution
    """
    logger = LOGGERS.get('usage_limit')
    
    if logger:
        logger.warning(f"Usage limit detected for command '{command}', initiating retry workflow")
    
    # Parse usage limit error
    output_to_check = result.stdout + " " + result.stderr
    parsed_info = parse_usage_limit_error(output_to_check)
    if logger:
        logger.debug(f"Parsed usage limit info: {parsed_info}")
    
    # Calculate wait time
    wait_seconds = calculate_wait_time(parsed_info)
    if logger:
        logger.info(f"Calculated wait time: {wait_seconds} seconds")
    
    # Wait for reset time - also print for user visibility during long waits
    message = f"Usage limit reached. Waiting {wait_seconds} seconds for reset..."
    if logger:
        logger.info(message)
    print(message)  # Keep user-facing message for visibility
    time.sleep(wait_seconds)
    
    # Wait for signal file from first attempt
    if logger:
        logger.debug("Waiting for signal file from initial command attempt")
    _wait_for_completion_with_context(command, debug=debug)
    
    # Retry the command
    if logger:
        logger.info(f"Retrying command '{command}' after usage limit wait")
    return _execute_claude_subprocess(command_array, command, debug=debug)


def _wait_for_completion_with_context(command: str, debug: bool = False) -> None:
    """Wait for signal file and provide command-specific error context.
    
    Args:
        command: The Claude command being executed (for error context)
        debug: Whether to enable debug logging
        
    Raises:
        CommandTimeoutError: If signal file doesn't appear with command context
    """
    error_logger = LOGGERS.get('error_handler')
    
    try:
        wait_for_signal_file(SIGNAL_FILE, debug=debug)
    except TimeoutError as e:
        error_msg = f"Claude command timed out waiting for completion signal"
        if error_logger:
            error_logger.error(f"[COMMAND_TIMEOUT]: {error_msg} - Command: {command}")
        raise CommandTimeoutError(error_msg, command) from e


def _execute_claude_subprocess(command_array: List[str], command: str, debug: bool = False) -> subprocess.CompletedProcess:
    """Execute Claude CLI subprocess and return the completed process.
    
    Args:
        command_array: The complete command array to execute
        command: The original Claude command for error context
        debug: Whether to enable debug logging
        
    Returns:
        subprocess.CompletedProcess object with stdout, stderr, and returncode
        
    Raises:
        CommandExecutionError: If subprocess execution fails
    """
    logger = LOGGERS.get('command_executor')
    error_logger = LOGGERS.get('error_handler')
    
    cmd_str = ' '.join(command_array)
    if logger:
        logger.debug(f"Executing subprocess: {cmd_str}")
    
    try:
        result = subprocess.run(
            command_array,
            capture_output=True,
            text=True,
            check=False  # Don't raise on non-zero exit codes
        )
        
        if logger:
            logger.debug(f"Subprocess completed with return code: {result.returncode}")
        if result.stderr:
            if logger:
                logger.debug(f"Subprocess stderr: {result.stderr}")
        if result.stdout:
            if logger:
                logger.debug(f"Subprocess stdout length: {len(result.stdout)} characters")
        
        return result
        
    except subprocess.SubprocessError as e:
        error_msg = f"Failed to execute Claude CLI command"
        if error_logger:
            error_logger.error(f"[COMMAND_EXECUTION]: {error_msg} - Command: {command}")
        raise CommandExecutionError(error_msg, command) from e


def run_claude_command(command: str, args: Optional[List[str]] = None, 
                      debug: bool = False) -> Dict:
    """Execute a Claude CLI command and return parsed JSON output.
    
    This function executes Claude CLI commands with robust signal file waiting and
    comprehensive error handling. It uses the Stop hook configuration in Claude CLI
    to detect command completion via signal file creation.
    
    Args:
        command: The Claude command to execute (e.g., "/continue", "/validate")
        args: Optional additional arguments to append to the command array
        debug: Whether to enable debug logging for troubleshooting
        
    Returns:
        Parsed JSON response from Claude CLI as a dictionary
        
    Raises:
        CommandExecutionError: If Claude CLI execution fails
        JSONParseError: If Claude CLI output is not valid JSON
        CommandTimeoutError: If signal file doesn't appear within timeout period
        
    Note:
        This function relies on the Stop hook configuration in .claude/settings.local.json
        which creates a signal file when Claude CLI commands complete. The signal file
        waiting mechanism provides reliable completion detection for automation workflows.
    """
    logger = LOGGERS.get('command_executor')
    
    if logger:
        logger.info(f"Executing Claude command: {command}")
    if args:
        if logger:
            logger.debug(f"Additional arguments: {args}")
    
    # Construct the base command array with required flags
    command_array = [
        "claude",
        "-p", command,
        "--output-format", "json",
        "--dangerously-skip-permissions"
    ]
    
    # Append additional args if provided
    if args:
        command_array.extend(args)
    
    if logger:
        logger.debug(f"Full command array: {command_array}")
    
    # Execute the Claude CLI command
    result = _execute_claude_subprocess(command_array, command, debug=debug)
    
    # Check for usage limit errors in stdout or stderr and handle retry if needed
    output_to_check = result.stdout + " " + result.stderr
    if "usage limit" in output_to_check.lower():
        if logger:
            logger.warning("Usage limit detected, initiating retry workflow")
        result = _handle_usage_limit_and_retry(command, command_array, result, debug=debug)
    
    # Wait for signal file to appear (indicates command completion)
    if logger:
        logger.debug("Waiting for command completion signal")
    _wait_for_completion_with_context(command, debug=debug)
    
    # Parse JSON output from stdout
    try:
        if logger:
            logger.debug(f"Parsing JSON output ({len(result.stdout)} characters)")
        
        parsed_result = json.loads(result.stdout)
        if logger:
            logger.info(f"Successfully executed Claude command '{command}'")
        return parsed_result
    except json.JSONDecodeError as e:
        error_logger = LOGGERS.get('error_handler')
        error_msg = f"Failed to parse Claude CLI JSON output"
        if error_logger:
            error_logger.error(f"[JSON_PARSE]: {error_msg} - Command: {command}")
        raise JSONParseError(error_msg, command) from e


def execute_command_and_get_status(command: str, debug: bool = False) -> Optional[str]:
    """Execute a Claude command and return the latest status.
    
    This helper function combines the common pattern of running a Claude command
    followed by checking the latest status from MCP server status files.
    
    Args:
        command: The Claude command to execute (e.g., "/validate", "/update")
        debug: Whether to enable debug logging for troubleshooting
        
    Returns:
        The status value from the newest status file, or None if no status available
        
    Note:
        This function encapsulates the run_claude_command + get_latest_status pattern
        that appears frequently in the main orchestration loop. Uses delayed import
        to avoid circular dependencies with automate_dev module.
    """
    logger = LOGGERS.get('error_handler')
    
    try:
        run_claude_command(command, debug=debug)
        # Import here to avoid circular imports - this is a minimal implementation
        # that keeps the function working while allowing module extraction
        import importlib
        automate_dev_module = importlib.import_module('automate_dev')
        status = automate_dev_module.get_latest_status(debug=debug)
        if logger:
            logger.debug(f"Command {command} executed successfully, status: {status}")
        return status
    except Exception as e:
        if logger:
            logger.error(f"Error executing command {command}: {e}")
        return None