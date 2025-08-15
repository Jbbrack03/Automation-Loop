"""Automated development workflow orchestrator.

This module provides the main orchestrator function that manages prerequisite file
validation for the automated development workflow system.
"""

import json
import logging
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import datetime
import pytz

# File path constants
IMPLEMENTATION_PLAN_FILE = "Implementation Plan.md"
PRD_FILE = "PRD.md"
CLAUDE_FILE = "CLAUDE.md"
SIGNAL_FILE = ".claude/signal_task_complete"
SETTINGS_FILE = ".claude/settings.local.json"

# Default settings configuration structure
# This configuration sets up the Stop hook to create a signal file when Claude sessions end
# The hook enables reliable detection of task completion in automated workflows
DEFAULT_SETTINGS_CONFIG = {
    "hooks": {
        "Stop": [{
            "hooks": [{
                "type": "command",
                "command": f"touch {SIGNAL_FILE}"
            }]
        }]
    }
}

# Serialize the configuration to JSON string for file writing
DEFAULT_SETTINGS_JSON = json.dumps(DEFAULT_SETTINGS_CONFIG, indent=2)

# Exit codes
EXIT_SUCCESS = 0
EXIT_MISSING_CRITICAL_FILE = 1

# Workflow control constants
MAX_FIX_ATTEMPTS = 3
MIN_WAIT_TIME = 60  # minimum seconds to wait when usage limit reset time is in the past
SIGNAL_WAIT_SLEEP_INTERVAL = 0.1  # seconds between signal file checks
SIGNAL_WAIT_TIMEOUT = 30.0  # maximum seconds to wait for signal file

# Time parsing constants for calculate_wait_time
HOURS_12_CLOCK_CONVERSION = 12  # hours to add/subtract for 12-hour clock conversion
MIDNIGHT_HOUR_12_FORMAT = 12  # hour value that represents midnight in 12-hour format
NOON_HOUR_12_FORMAT = 12  # hour value that represents noon in 12-hour format

# Parsing constants
USAGE_LIMIT_TIME_PATTERN = r'try again at (\w+) \(([^)]+)\)'

# Status constants
VALIDATION_PASSED = "validation_passed"
VALIDATION_FAILED = "validation_failed"
PROJECT_COMPLETE = "project_complete"
PROJECT_INCOMPLETE = "project_incomplete"

# Refactoring status constants
CHECKIN_COMPLETE = "checkin_complete"
REFACTORING_NEEDED = "refactoring_needed"
NO_REFACTORING_NEEDED = "no_refactoring_needed"
FINALIZATION_COMPLETE = "finalization_complete"

# Command constants
CLEAR_CMD = "/clear"
CONTINUE_CMD = "/continue"
VALIDATE_CMD = "/validate"
UPDATE_CMD = "/update"
CORRECT_CMD = "/correct"
CHECKIN_CMD = "/checkin"
REFACTOR_CMD = "/refactor"
FINALIZE_CMD = "/finalize"


# Module-specific loggers for different components
LOGGERS = {
    'orchestrator': None,
    'task_tracker': None,
    'command_executor': None,
    'validation': None,
    'error_handler': None,
    'usage_limit': None
}


def setup_logging() -> None:
    """Set up comprehensive logging with module-specific loggers.
    
    Creates the .claude/logs/ directory if it doesn't exist and configures
    logging to write to a timestamped log file. Sets up module-specific loggers
    for different components of the orchestrator system.
    
    This provides comprehensive logging functionality throughout the orchestrator's
    execution with appropriate log levels and structured logging.
    """
    # Create .claude/logs directory if it doesn't exist
    log_dir = Path(".claude/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create timestamped log file name
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"orchestrator_{timestamp}.log"
    
    # Clear any existing handlers to avoid interference
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Configure logging with enhanced format for better debugging
    logging.basicConfig(
        level=logging.DEBUG,  # Enable all log levels
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8')
        ],
        force=True  # Force reconfiguration
    )
    
    # Initialize module-specific loggers
    LOGGERS['orchestrator'] = logging.getLogger('orchestrator')
    LOGGERS['task_tracker'] = logging.getLogger('task_tracker')
    LOGGERS['command_executor'] = logging.getLogger('command_executor')
    LOGGERS['validation'] = logging.getLogger('validation')
    LOGGERS['error_handler'] = logging.getLogger('error_handler')
    LOGGERS['usage_limit'] = logging.getLogger('usage_limit')
    
    # Set appropriate log levels for different modules
    LOGGERS['orchestrator'].setLevel(logging.INFO)
    LOGGERS['task_tracker'].setLevel(logging.INFO)
    LOGGERS['command_executor'].setLevel(logging.DEBUG)
    LOGGERS['validation'].setLevel(logging.INFO)
    LOGGERS['error_handler'].setLevel(logging.WARNING)
    LOGGERS['usage_limit'].setLevel(logging.INFO)
    
    # Log that setup is complete
    LOGGERS['orchestrator'].info("Orchestrator logging initialized with module-specific loggers")
    LOGGERS['orchestrator'].info(f"Log file created: {log_file}")



def check_file_exists(filepath: str) -> bool:
    """Check if a file exists.
    
    Args:
        filepath: Path to the file to check
        
    Returns:
        True if file exists, False otherwise
    """
    return os.path.exists(filepath)


def validate_critical_files(files: List[str]) -> Tuple[bool, List[str]]:
    """Validate that critical files exist.
    
    Args:
        files: List of file paths that are required
        
    Returns:
        Tuple of (all_exist, missing_files)
    """
    missing_files = [f for f in files if not check_file_exists(f)]
    return len(missing_files) == 0, missing_files


def validate_optional_files(files: List[str]) -> List[str]:
    """Validate optional files and return list of missing ones.
    
    Args:
        files: List of file paths that are optional
        
    Returns:
        List of missing file paths
    """
    return [f for f in files if not check_file_exists(f)]


def ensure_settings_file() -> None:
    """Ensure .claude/settings.local.json exists with valid JSON structure.
    
    Creates the .claude directory if it doesn't exist and initializes the
    settings file with an empty JSON object ({}) if the file is missing.
    
    The function handles file operation errors gracefully by following the
    codebase pattern of degrading gracefully rather than failing fast.
    
    Raises:
        No exceptions are raised; file operation errors are handled gracefully
        to ensure the workflow can continue even if settings creation fails.
    """
    settings_path = Path(SETTINGS_FILE)
    
    # Create .claude directory if it doesn't exist
    try:
        settings_path.parent.mkdir(parents=True, exist_ok=True)
    except (OSError, IOError) as e:
        # Graceful degradation - continue without failing the workflow
        # This follows the codebase pattern for file operation error handling
        return
    
    # Create settings file with minimal valid JSON if it doesn't exist
    if not settings_path.exists():
        try:
            settings_path.write_text(DEFAULT_SETTINGS_JSON, encoding="utf-8")
        except (OSError, IOError) as e:
            # Graceful degradation - continue without failing the workflow
            # File creation may fail due to permissions or disk space
            return


class TaskTracker:
    """Tracks task completion status from Implementation Plan.md file.
    
    This class manages task state by reading from Implementation Plan.md and
    provides failure tracking functionality to limit retry attempts on failing tasks.
    """
    
    def __init__(self) -> None:
        """Initialize TaskTracker with failure tracking.
        
        Sets up an empty dictionary to track fix attempts for tasks that fail
        during execution. Each task can have up to MAX_FIX_ATTEMPTS retries.
        """
        self.fix_attempts: Dict[str, int] = {}
    
    def get_next_task(self) -> Tuple[Optional[str], bool]:
        """Get the next incomplete task from Implementation Plan.md.
        
        Reads the Implementation Plan.md file and finds the first task marked
        as incomplete (with '- [ ]' marker). This implements sequential task
        processing where tasks must be completed in order.
        
        Returns:
            Tuple of (task_line, all_complete) where:
            - task_line is the first incomplete task description or None if no incomplete tasks
            - all_complete is True if all tasks are complete or file is missing, False otherwise
            
        Raises:
            No exceptions are raised; file access errors are handled gracefully
            by returning (None, True) to indicate completion.
        """
        logger = LOGGERS['task_tracker']
        
        # Check if Implementation Plan.md exists
        if not check_file_exists(IMPLEMENTATION_PLAN_FILE):
            logger.warning(f"Implementation Plan file not found: {IMPLEMENTATION_PLAN_FILE}")
            return (None, True)
        
        try:
            with open(IMPLEMENTATION_PLAN_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            logger.debug(f"Reading {len(lines)} lines from {IMPLEMENTATION_PLAN_FILE}")
            
            # Look for first incomplete task ([ ] pattern)
            for i, line in enumerate(lines):
                line = line.strip()
                if '- [ ]' in line:
                    # Extract the task description after "- [ ] "
                    task = line.split('- [ ]', 1)[1].strip()
                    logger.info(f"Found next incomplete task on line {i+1}: {task}")
                    return (task, False)
            
            # No incomplete tasks found - all are complete
            logger.info("All tasks in Implementation Plan are complete")
            return (None, True)
            
        except (IOError, OSError) as e:
            # File exists but can't be read - treat as all complete
            logger.error(f"Failed to read Implementation Plan file: {e}")
            return (None, True)
    
    def increment_fix_attempts(self, task: str) -> bool:
        """Increment fix attempts count for a task.
        
        Tracks how many times a task has failed and been retried. This implements
        a circuit breaker pattern to prevent infinite retry loops on persistently
        failing tasks.
        
        Args:
            task: The task identifier (description) to increment attempts for
            
        Returns:
            True if still within MAX_FIX_ATTEMPTS limit and retries should continue,
            False if the limit has been exceeded and no more retries should be attempted
        """
        logger = LOGGERS['task_tracker']
        
        # Initialize or increment the count for this task
        if task not in self.fix_attempts:
            self.fix_attempts[task] = 0
        
        self.fix_attempts[task] += 1
        current_attempts = self.fix_attempts[task]
        
        logger.info(f"Incremented fix attempts for task '{task}': {current_attempts}/{MAX_FIX_ATTEMPTS}")
        
        # Return True if still within limit, False if at or over limit
        within_limit = current_attempts <= MAX_FIX_ATTEMPTS
        if not within_limit:
            logger.warning(f"Task '{task}' has exceeded max fix attempts ({MAX_FIX_ATTEMPTS})")
        
        return within_limit
    
    def reset_fix_attempts(self, task: str) -> None:
        """Reset fix attempts for a task by removing it from tracking.
        
        Called when a task completes successfully to clean up the failure tracking
        state. This ensures that if the same task needs to be executed again in the
        future (e.g., in a different workflow run), it starts with a clean slate.
        
        Args:
            task: The task identifier (description) to reset attempts for
            
        Note:
            This method is safe to call even if the task is not currently being tracked.
        """
        logger = LOGGERS['task_tracker']
        
        # Remove the task from the dictionary if it exists
        if task in self.fix_attempts:
            attempts = self.fix_attempts[task]
            del self.fix_attempts[task]
            logger.info(f"Reset fix attempts for task '{task}' (had {attempts} attempts)")
        else:
            logger.debug(f"No fix attempts to reset for task '{task}'")


def _wait_for_signal_file(signal_file_path: str, timeout: float = SIGNAL_WAIT_TIMEOUT, 
                         sleep_interval: float = SIGNAL_WAIT_SLEEP_INTERVAL,
                         debug: bool = False) -> None:
    """Wait for signal file to appear with timeout and error handling.
    
    This helper function implements robust signal file waiting with timeout protection
    and structured logging. It's used by run_claude_command to wait for Claude CLI
    command completion signals.
    
    Args:
        signal_file_path: Path to the signal file to wait for
        timeout: Maximum seconds to wait before raising TimeoutError
        sleep_interval: Seconds to sleep between file existence checks
        debug: Whether to enable debug-level logging
        
    Raises:
        TimeoutError: If signal file doesn't appear within timeout period
        OSError: If there are file system access errors during cleanup
        
    Note:
        This function will remove the signal file after it appears to clean up
        the file system state for subsequent command executions.
    """
    logger = LOGGERS['command_executor']
    
    logger.debug(f"Waiting for signal file: {signal_file_path} (timeout: {timeout}s)")
    
    start_time = time.time()
    elapsed_time = 0.0
    
    while elapsed_time < timeout:
        if os.path.exists(signal_file_path):
            logger.debug(f"Signal file appeared after {elapsed_time:.1f}s")
            
            try:
                os.remove(signal_file_path)
                logger.debug("Signal file cleaned up successfully")
                return
            except OSError as e:
                # Log the error but don't fail - the command may have completed successfully
                logger.warning(f"Failed to remove signal file: {e}")
                return
        
        time.sleep(sleep_interval)
        elapsed_time = time.time() - start_time
    
    # Timeout reached - this indicates a potential issue with Claude CLI execution
    error_msg = f"Signal file {signal_file_path} did not appear within {timeout}s timeout"
    logger.error(error_msg)
    raise TimeoutError(error_msg)


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
    logger = LOGGERS['usage_limit']
    
    logger.warning(f"Usage limit detected for command '{command}', initiating retry workflow")
    
    # Parse usage limit error
    output_to_check = result.stdout + " " + result.stderr
    parsed_info = parse_usage_limit_error(output_to_check)
    logger.debug(f"Parsed usage limit info: {parsed_info}")
    
    # Calculate wait time
    wait_seconds = calculate_wait_time(parsed_info)
    logger.info(f"Calculated wait time: {wait_seconds} seconds")
    
    # Wait for reset time - also print for user visibility during long waits
    message = f"Usage limit reached. Waiting {wait_seconds} seconds for reset..."
    logger.info(message)
    print(message)  # Keep user-facing message for visibility
    time.sleep(wait_seconds)
    
    # Wait for signal file from first attempt
    logger.debug("Waiting for signal file from initial command attempt")
    _wait_for_completion_with_context(command, debug=debug)
    
    # Retry the command
    logger.info(f"Retrying command '{command}' after usage limit wait")
    return _execute_claude_subprocess(command_array, debug=debug)


def _wait_for_completion_with_context(command: str, debug: bool = False) -> None:
    """Wait for signal file and provide command-specific error context.
    
    Args:
        command: The Claude command being executed (for error context)
        debug: Whether to enable debug logging
        
    Raises:
        TimeoutError: If signal file doesn't appear with command context
    """
    try:
        _wait_for_signal_file(SIGNAL_FILE, debug=debug)
    except TimeoutError as e:
        # Re-raise with additional context about the command that timed out
        raise TimeoutError(f"Claude command '{command}' timed out: {e}") from e


def _execute_claude_subprocess(command_array: List[str], debug: bool = False) -> subprocess.CompletedProcess:
    """Execute Claude CLI subprocess and return the completed process.
    
    Args:
        command_array: The complete command array to execute
        debug: Whether to enable debug logging
        
    Returns:
        subprocess.CompletedProcess object with stdout, stderr, and returncode
        
    Raises:
        subprocess.SubprocessError: If subprocess execution fails
    """
    logger = LOGGERS['command_executor']
    
    cmd_str = ' '.join(command_array)
    logger.debug(f"Executing subprocess: {cmd_str}")
    
    try:
        result = subprocess.run(
            command_array,
            capture_output=True,
            text=True,
            check=False  # Don't raise on non-zero exit codes
        )
        
        logger.debug(f"Subprocess completed with return code: {result.returncode}")
        if result.stderr:
            logger.debug(f"Subprocess stderr: {result.stderr}")
        if result.stdout:
            logger.debug(f"Subprocess stdout length: {len(result.stdout)} characters")
        
        return result
        
    except subprocess.SubprocessError as e:
        error_msg = f"Failed to execute Claude CLI command: {e}"
        logger.error(error_msg)
        raise subprocess.SubprocessError(error_msg) from e


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
        subprocess.SubprocessError: If Claude CLI execution fails
        json.JSONDecodeError: If Claude CLI output is not valid JSON
        TimeoutError: If signal file doesn't appear within timeout period
        
    Note:
        This function relies on the Stop hook configuration in .claude/settings.local.json
        which creates a signal file when Claude CLI commands complete. The signal file
        waiting mechanism provides reliable completion detection for automation workflows.
    """
    logger = LOGGERS['command_executor']
    
    logger.info(f"Executing Claude command: {command}")
    if args:
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
    
    logger.debug(f"Full command array: {command_array}")
    
    # Execute the Claude CLI command
    result = _execute_claude_subprocess(command_array, debug=debug)
    
    # Check for usage limit errors in stdout or stderr and handle retry if needed
    output_to_check = result.stdout + " " + result.stderr
    if "usage limit" in output_to_check.lower():
        logger.warning("Usage limit detected, initiating retry workflow")
        result = _handle_usage_limit_and_retry(command, command_array, result, debug=debug)
    
    # Wait for signal file to appear (indicates command completion)
    logger.debug("Waiting for command completion signal")
    _wait_for_completion_with_context(command, debug=debug)
    
    # Parse JSON output from stdout
    try:
        logger.debug(f"Parsing JSON output ({len(result.stdout)} characters)")
        
        parsed_result = json.loads(result.stdout)
        logger.info(f"Successfully executed Claude command '{command}'")
        return parsed_result
    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse Claude CLI JSON output for command '{command}': {e.msg}"
        logger.error(f"{error_msg}. Raw output: {result.stdout[:500]}...")
        raise json.JSONDecodeError(
            error_msg,
            result.stdout,
            e.pos
        ) from e


def _cleanup_status_files(status_files: List[Path], debug: bool = False) -> None:
    """Clean up all status files after reading.
    
    Args:
        status_files: List of status file paths to delete
        debug: Whether to enable debug logging for troubleshooting
    """
    for status_file in status_files:
        try:
            status_file.unlink()
            if debug:
                print(f"Debug: Cleaned up status file: {status_file}")
        except OSError as e:
            # Continue if file deletion fails, but log if debug enabled
            if debug:
                print(f"Warning: Failed to delete status file {status_file}: {e}")


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
        that appears frequently in the main orchestration loop.
    """
    try:
        run_claude_command(command, debug=debug)
        return get_latest_status(debug=debug)
    except Exception as e:
        logger = LOGGERS['error_handler']
        logger.error(f"Error executing command {command}: {e}")
        return None




def execute_tdd_cycle() -> str:
    """Execute the TDD cycle: clear, continue, validate.
    
    Runs the core Test-Driven Development sequence of commands:
    1. Clear the session state
    2. Continue with implementation
    3. Validate the current state
    
    Returns:
        The validation status from the latest status check
    """
    logger = LOGGERS['orchestrator']
    
    logger.info("Starting TDD cycle: clear -> continue -> validate")
    
    logger.debug("Executing /clear command")
    run_claude_command(CLEAR_CMD)
    
    logger.debug("Executing /continue command")
    run_claude_command(CONTINUE_CMD)
    
    logger.debug("Executing /validate command")
    run_claude_command(VALIDATE_CMD)
    
    logger.debug("Getting latest validation status")
    status = get_latest_status()
    logger.info(f"TDD cycle completed with status: {status}")
    
    return status


def handle_validation_result(validation_status: str, task: str, tracker: TaskTracker) -> bool:
    """Handle the result of validation and determine next action.
    
    Processes validation results and executes appropriate follow-up actions:
    - For VALIDATION_PASSED: Updates task and checks project completion
    - For VALIDATION_FAILED: Attempts correction within retry limits
    
    Args:
        validation_status: The status returned from validation
        task: The current task being processed
        tracker: TaskTracker instance for managing failure counts
        
    Returns:
        True if the main loop should continue, False if it should exit
        
    Raises:
        SystemExit: When project is complete (EXIT_SUCCESS)
    """
    if validation_status == VALIDATION_PASSED:
        # Validation passed - update the task as complete
        run_claude_command(UPDATE_CMD)
        
        # Check if project is complete
        project_status = get_latest_status()
        if project_status == PROJECT_COMPLETE:
            handle_project_completion()
        # Continue to next task if project is incomplete
        return True
            
    elif validation_status == VALIDATION_FAILED:
        # Validation failed - attempt correction if under retry limit
        if tracker.increment_fix_attempts(task):
            # Still under retry limit - attempt correction
            run_claude_command(CORRECT_CMD)
            # After correction, loop will re-run validation on next iteration
            return True
        else:
            # Max attempts exceeded - skip to next task
            logger = LOGGERS['error_handler']
            warning_msg = f"Max fix attempts ({MAX_FIX_ATTEMPTS}) exceeded for task '{task}', skipping"
            logger.warning(warning_msg)
            print(warning_msg)  # Keep user-facing warning
            return True
    
    # Unknown validation status - continue with next iteration
    return True


def validate_prerequisites() -> None:
    """Validate prerequisite files and settings for the workflow.
    
    Checks for critical and optional files, ensures settings file exists,
    and reports any missing files. Critical files are required for the
    workflow to proceed, while optional files generate warnings.
    
    Raises:
        SystemExit: If any critical files are missing (EXIT_MISSING_CRITICAL_FILE)
    """
    # Ensure settings file exists
    ensure_settings_file()
    
    # Define critical and optional files
    critical_files = [IMPLEMENTATION_PLAN_FILE]
    optional_files = [PRD_FILE, CLAUDE_FILE]
    
    # Check critical files - exit if any are missing
    all_critical_exist, missing_critical = validate_critical_files(critical_files)
    if not all_critical_exist:
        logger = LOGGERS['validation']
        for missing_file in missing_critical:
            error_msg = f"Critical file is missing: {missing_file}"
            logger.error(error_msg)
            print(f"Error: {missing_file} is missing")  # Keep user-facing error
        logger.critical("Exiting due to missing critical files")
        sys.exit(EXIT_MISSING_CRITICAL_FILE)
    
    # Check optional files - warn if missing
    missing_optional = validate_optional_files(optional_files)
    if missing_optional:
        logger = LOGGERS['validation']
        for missing_file in missing_optional:
            logger.warning(f"Optional file is missing: {missing_file}")
            print(f"Warning: {missing_file} is missing")  # Keep user-facing warning


def handle_project_completion() -> None:
    """Handle project completion by checking status and entering appropriate workflow.
    
    Checks the current project status and either:
    - Enters the refactoring loop if project is complete
    - Exits successfully if project is not complete
    
    This function centralizes the project completion logic to reduce duplication
    across the orchestration workflow.
    
    Raises:
        SystemExit: Always exits with EXIT_SUCCESS
    """
    project_status = get_latest_status()
    if project_status == PROJECT_COMPLETE:
        # Enter refactoring loop
        execute_refactoring_loop()
    else:
        # Project not complete for some reason, exit
        sys.exit(EXIT_SUCCESS)
        return  # For testing - handle mocked sys.exit


def execute_refactoring_loop() -> None:
    """Execute the refactoring loop until no more refactoring is needed.
    
    This function implements the continuous refactoring workflow:
    1. Perform checkin to assess current state
    2. Run refactor analysis to identify improvement opportunities
    3. If refactoring is needed, execute finalization and repeat
    4. If no refactoring is needed, exit the workflow successfully
    
    The loop continues until the refactor command indicates that no further
    improvements are necessary, at which point the workflow terminates.
    
    Raises:
        SystemExit: When the refactoring workflow is complete (EXIT_SUCCESS)
    """
    while True:
        # Start with checkin to assess current state
        checkin_status = execute_command_and_get_status(CHECKIN_CMD)
        
        # Run refactor analysis to identify improvement opportunities
        refactor_status = execute_command_and_get_status(REFACTOR_CMD)
        
        # If no refactoring needed, workflow is complete
        if refactor_status == NO_REFACTORING_NEEDED:
            sys.exit(EXIT_SUCCESS)
            return  # For testing - handle mocked sys.exit
        
        # If refactoring needed, execute finalization
        if refactor_status == REFACTORING_NEEDED:
            finalize_status = execute_command_and_get_status(FINALIZE_CMD)
            # Continue loop for next refactoring cycle
            continue


def _parse_json_error_format(error_message: str) -> Optional[Dict[str, str]]:
    """Parse JSON format usage limit error message.
    
    Args:
        error_message: The error message string that might be JSON
        
    Returns:
        Dictionary with unix_timestamp format result if valid JSON with reset_at,
        None if not valid JSON or doesn't contain reset_at field
    """
    try:
        json_data = json.loads(error_message)
        if isinstance(json_data, dict) and "reset_at" in json_data:
            return {
                "reset_at": json_data["reset_at"],
                "format": "unix_timestamp"
            }
    except (json.JSONDecodeError, ValueError):
        # Not JSON or parsing failed
        pass
    return None


def _parse_natural_language_format(error_message: str) -> Optional[Dict[str, str]]:
    """Parse natural language format usage limit error message.
    
    Args:
        error_message: The error message string to parse with regex
        
    Returns:
        Dictionary with natural_language format result if pattern matches,
        None if no match found
    """
    time_pattern_match = re.search(USAGE_LIMIT_TIME_PATTERN, error_message)
    
    if time_pattern_match:
        parsed_reset_time = time_pattern_match.group(1)
        parsed_timezone = time_pattern_match.group(2)
        return _create_usage_limit_result(parsed_reset_time, parsed_timezone)
    
    return None


def _create_usage_limit_result(reset_time: str = "", timezone: str = "", format_type: str = "natural_language") -> Dict[str, str]:
    """Create a standardized usage limit error result dictionary.
    
    Args:
        reset_time: The time when usage can resume (e.g., "7pm")
        timezone: The timezone specification (e.g., "America/Chicago")
        format_type: The format type identifier
        
    Returns:
        Dictionary with standardized keys and values
    """
    return {
        "reset_time": reset_time,
        "timezone": timezone,
        "format": format_type
    }


def parse_usage_limit_error(error_message: str) -> Dict[str, str]:
    """Parse usage limit error message to extract reset time information.
    
    This function parses usage limit error messages from Claude API in two formats:
    1. JSON format with unix timestamp (e.g., {"reset_at": 1737000000})
    2. Natural language format (e.g., "try again at 7pm (America/Chicago)")
    
    Args:
        error_message: The error message string from Claude API. Must be a non-empty string.
        
    Returns:
        Dictionary containing parsed reset time information:
        - For JSON format: {"reset_at": timestamp, "format": "unix_timestamp"}
        - For natural language: {"reset_time": "7pm", "timezone": "America/Chicago", "format": "natural_language"}
        - For no match: {"reset_time": "", "timezone": "", "format": "natural_language"}
        
    Example:
        >>> parse_usage_limit_error('{"reset_at": 1737000000}')
        {'reset_at': 1737000000, 'format': 'unix_timestamp'}
        
        >>> parse_usage_limit_error("You can try again at 7pm (America/Chicago).")
        {'reset_time': '7pm', 'timezone': 'America/Chicago', 'format': 'natural_language'}
        
        >>> parse_usage_limit_error("Some other error message")
        {'reset_time': '', 'timezone': '', 'format': 'natural_language'}
    
    Note:
        Returns empty values for reset_time and timezone if no match is found,
        while maintaining consistent structure for downstream processing.
    """
    # Input validation
    if not error_message or not isinstance(error_message, str):
        return _create_usage_limit_result()
    
    # Try to parse as JSON first
    json_result = _parse_json_error_format(error_message)
    if json_result is not None:
        return json_result
    
    # Fall back to natural language parsing
    natural_language_result = _parse_natural_language_format(error_message)
    if natural_language_result is not None:
        return natural_language_result
    
    # If no match found, return empty values (minimal implementation)
    return _create_usage_limit_result()


def _validate_reset_info_structure(parsed_reset_info: Any) -> None:
    """Validate that parsed_reset_info is a dictionary with proper structure.
    
    Args:
        parsed_reset_info: The input to validate
        
    Raises:
        ValueError: If parsed_reset_info is not a dictionary
    """
    if not isinstance(parsed_reset_info, dict):
        raise ValueError("parsed_reset_info must be a dictionary")


def _calculate_unix_timestamp_wait(parsed_reset_info: Dict[str, Any]) -> int:
    """Calculate wait time for Unix timestamp format.
    
    Args:
        parsed_reset_info: Dictionary containing 'reset_at' key with Unix timestamp
        
    Returns:
        Number of seconds to wait until reset time
        
    Raises:
        KeyError: If 'reset_at' key is missing
        ValueError: If reset_at is not a numeric value
    """
    if "reset_at" not in parsed_reset_info:
        raise KeyError("parsed_reset_info must contain 'reset_at' key for unix_timestamp format")
    
    # Extract and validate reset timestamp
    reset_at = parsed_reset_info["reset_at"]
    if not isinstance(reset_at, (int, float)):
        raise ValueError("reset_at must be a numeric timestamp")
    
    # Get current time and calculate difference
    current_time = time.time()
    wait_seconds = int(reset_at - current_time)
    
    # Return at least MIN_WAIT_TIME seconds if reset time is in the past
    # This provides a safety buffer for potential clock skew or timing issues
    if wait_seconds < 0:
        return MIN_WAIT_TIME
    
    return wait_seconds


def _parse_time_string_to_24hour(reset_time_str: str) -> int:
    """Parse time string and convert to 24-hour format.
    
    Handles formats like "7pm", "7am", "19", "7:30pm" etc.
    
    Args:
        reset_time_str: Time string to parse
        
    Returns:
        Hour in 24-hour format (0-23)
        
    Raises:
        ValueError: If time string format is invalid
    """
    reset_time_str = reset_time_str.lower().strip()
    
    try:
        if reset_time_str.endswith("pm"):
            hour = int(reset_time_str[:-2])
            if hour != NOON_HOUR_12_FORMAT:
                hour += HOURS_12_CLOCK_CONVERSION
        elif reset_time_str.endswith("am"):
            hour = int(reset_time_str[:-2])
            if hour == MIDNIGHT_HOUR_12_FORMAT:
                hour = 0
        else:
            # Assume 24-hour format
            hour = int(reset_time_str)
        
        # Validate hour range
        if not 0 <= hour <= 23:
            raise ValueError(f"Hour must be between 0 and 23, got {hour}")
            
        return hour
    except (ValueError, IndexError) as e:
        raise ValueError(f"Invalid time format '{reset_time_str}': {e}")


def _calculate_natural_language_wait(parsed_reset_info: Dict[str, Any]) -> int:
    """Calculate wait time for natural language format.
    
    Args:
        parsed_reset_info: Dictionary containing 'reset_time' and 'timezone' keys
        
    Returns:
        Number of seconds to wait until reset time
        
    Raises:
        KeyError: If required keys are missing
        ValueError: If timezone is invalid or time format is incorrect
    """
    # Validate required keys
    if "reset_time" not in parsed_reset_info or "timezone" not in parsed_reset_info:
        raise KeyError("parsed_reset_info must contain 'reset_time' and 'timezone' keys for natural_language format")
    
    reset_time_str = parsed_reset_info["reset_time"]
    timezone_str = parsed_reset_info["timezone"]
    
    # Parse timezone
    try:
        tz = pytz.timezone(timezone_str)
    except pytz.exceptions.UnknownTimeZoneError:
        raise ValueError(f"Invalid timezone: {timezone_str}")
    
    # Get current time in the specified timezone
    current_dt = datetime.datetime.now(tz)
    
    # Parse reset time to 24-hour format
    hour = _parse_time_string_to_24hour(reset_time_str)
    
    # Create reset datetime for today
    reset_dt = current_dt.replace(hour=hour, minute=0, second=0, microsecond=0)
    
    # If reset time is earlier than current time, use next day
    if reset_dt <= current_dt:
        reset_dt += datetime.timedelta(days=1)
    
    # Calculate seconds difference
    wait_seconds = int((reset_dt - current_dt).total_seconds())
    
    return max(wait_seconds, MIN_WAIT_TIME)


def calculate_wait_time(parsed_reset_info: Dict[str, Any]) -> int:
    """Calculate seconds to wait until reset time for Unix timestamp or natural language format.
    
    This function handles the timing calculation for Claude usage limit resets,
    ensuring safe retry behavior even when reset times are in the past.
    
    Args:
        parsed_reset_info: Dictionary from parse_usage_limit_error containing:
            For unix_timestamp format:
                - reset_at: Unix timestamp (int or float) when usage can resume
                - format: "unix_timestamp"
            For natural_language format:
                - reset_time: Time string like "7pm"
                - timezone: Timezone string like "America/Chicago"
                - format: "natural_language"
    
    Returns:
        Number of seconds to wait until reset time. Returns at least MIN_WAIT_TIME
        seconds if the reset time is in the past for safety. Always returns a
        non-negative integer.
        
    Raises:
        KeyError: If parsed_reset_info missing required keys for the format
        ValueError: If values are not valid for the format
    """
    # Validate input structure first
    _validate_reset_info_structure(parsed_reset_info)
    
    # Determine format type and delegate to appropriate handler
    format_type = parsed_reset_info.get("format", "unix_timestamp")
    
    if format_type == "unix_timestamp":
        return _calculate_unix_timestamp_wait(parsed_reset_info)
    elif format_type == "natural_language":
        return _calculate_natural_language_wait(parsed_reset_info)
    else:
        raise ValueError(f"Unsupported format type: {format_type}. Supported formats: 'unix_timestamp', 'natural_language'")


def get_latest_status(debug: bool = False) -> Optional[str]:
    """Get the latest status from MCP server status files.
    
    Finds all status_*.json files in .claude/ directory, reads the newest file
    based on lexicographic sort (timestamp-based), deletes all status files 
    after reading, and returns the status value.
    
    The function uses lexicographic sorting to identify the newest file because
    status files use timestamp format YYYYMMDD_HHMMSS which sorts correctly
    alphabetically.
    
    Args:
        debug: Whether to enable debug logging for troubleshooting
    
    Returns:
        The status value from the newest status file, or None if no files exist
        or if any error occurs during file operations
        
    Note:
        This function deletes ALL status files after reading to prevent stale
        status confusion. This is critical for the workflow state management.
    """
    # Find all status files using pathlib for better cross-platform compatibility
    claude_dir = Path('.claude')
    
    # Handle missing .claude directory gracefully
    if not claude_dir.exists():
        if debug:
            print("Debug: .claude directory does not exist")
        return None
    
    # Find all status files
    status_files = list(claude_dir.glob('status_*.json'))
    
    # Return None if no status files exist
    if not status_files:
        if debug:
            print("Debug: No status files found in .claude directory")
        return None
    
    # Sort files lexicographically (newest timestamp will be last)
    status_files.sort(key=lambda p: p.name)
    newest_file = status_files[-1]
    
    if debug:
        print(f"Debug: Found {len(status_files)} status files, reading newest: {newest_file}")
    
    # Read and parse the newest file
    try:
        with open(newest_file, 'r', encoding='utf-8') as f:
            status_data = json.load(f)
        
        if debug:
            print(f"Debug: Successfully read JSON from {newest_file}")
            
    except json.JSONDecodeError as e:
        # JSON parsing error - return None for graceful degradation
        if debug:
            print(f"Debug: JSON parsing error in {newest_file}: {e}")
        return None
    except (IOError, OSError) as e:
        # File I/O error - return None for graceful degradation
        if debug:
            print(f"Debug: File I/O error reading {newest_file}: {e}")
        return None
    
    # Extract status value
    status = status_data.get('status')
    
    if debug:
        print(f"Debug: Extracted status: {status}")
    
    # Clean up all status files after successful reading
    _cleanup_status_files(status_files, debug=debug)
    
    return status



def execute_main_orchestration_loop() -> None:
    """Execute the main task orchestration loop.
    
    Continuously processes tasks from Implementation_Plan.md using the TDD workflow:
    1. Get next incomplete task
    2. Execute TDD cycle (clear, continue, validate)
    3. Handle validation results and retry logic
    4. Continue until all tasks are complete
    
    When all tasks are complete, delegates to project completion handler
    which manages the transition to the refactoring workflow.
    """
    logger = LOGGERS['orchestrator']
    tracker = TaskTracker()
    
    logger.info("Starting main orchestration loop")
    
    while True:
        # Get next task
        task, all_complete = tracker.get_next_task()
        
        if task:
            logger.info(f"Processing task: {task}")
        else:
            logger.info("No more tasks to process - checking final validation")
        
        # Always execute TDD cycle - even when all tasks are complete,
        # we need to validate the final state before transitioning to refactoring
        logger.debug("Executing TDD cycle")
        validation_status = execute_tdd_cycle()
        
        if all_complete:
            # All tasks complete - handle final validation and potential refactoring
            if validation_status == VALIDATION_PASSED:
                # Update to mark project complete
                run_claude_command(UPDATE_CMD)
                update_status = get_latest_status()
                if update_status == PROJECT_COMPLETE:
                    # Enter refactoring workflow
                    handle_project_completion()
                    return  # For testing - refactoring loop will exit
                else:
                    # Exit if not marked as complete
                    sys.exit(EXIT_SUCCESS)
                    return  # For testing
            else:
                # Final validation failed
                logger = LOGGERS['error_handler']
                error_msg = f"Final validation failed with status: {validation_status}"
                logger.error(error_msg)
                print(f"ERROR: {error_msg}")  # Keep user-facing error
                sys.exit(1)
                return  # For testing
        else:
            # Normal task processing
            should_continue = handle_validation_result(validation_status, task, tracker)
            if should_continue:
                continue


def main():
    """Main orchestrator function for the automated development workflow.
    
    Entry point for the automated development system. Validates prerequisites
    and launches the main orchestration loop for task processing and workflow
    management.
    
    The workflow progresses through two main phases:
    1. Task execution phase: Process Implementation_Plan.md tasks using TDD
    2. Refactoring phase: Continuous code quality improvements
    """
    # Set up logging first
    setup_logging()
    
    logger = LOGGERS['orchestrator']
    logger.info("=== Starting automated development orchestrator ===")
    
    # Validate prerequisites and initialize workflow
    logger.info("Validating prerequisites...")
    validate_prerequisites()
    logger.info("Prerequisites validated successfully")
    
    # Start main orchestration loop
    logger.info("Starting main orchestration loop")
    execute_main_orchestration_loop()
    
    logger.info("=== Automated development orchestrator completed ===")


if __name__ == "__main__":
    main()