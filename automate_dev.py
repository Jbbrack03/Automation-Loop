"""Automated development workflow orchestrator.

This module provides the main orchestrator function that manages prerequisite file
validation for the automated development workflow system.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Constants for prerequisite files
IMPLEMENTATION_PLAN_FILE = "Implementation Plan.md"
PRD_FILE = "PRD.md"
CLAUDE_FILE = "CLAUDE.md"

# Signal file constant
SIGNAL_FILE = ".claude/signal_task_complete"

# Settings file constant  
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

# Failure tracking constants
MAX_FIX_ATTEMPTS = 3

# Signal file waiting constants
SIGNAL_WAIT_SLEEP_INTERVAL = 0.1  # seconds between signal file checks
SIGNAL_WAIT_TIMEOUT = 30.0  # maximum seconds to wait for signal file

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
        # Check if Implementation Plan.md exists
        if not check_file_exists(IMPLEMENTATION_PLAN_FILE):
            return (None, True)
        
        try:
            with open(IMPLEMENTATION_PLAN_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Look for first incomplete task ([ ] pattern)
            for line in lines:
                line = line.strip()
                if '- [ ]' in line:
                    # Extract the task description after "- [ ] "
                    task = line.split('- [ ]', 1)[1].strip()
                    return (task, False)
            
            # No incomplete tasks found - all are complete
            return (None, True)
            
        except (IOError, OSError):
            # File exists but can't be read - treat as all complete
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
        # Initialize or increment the count for this task
        if task not in self.fix_attempts:
            self.fix_attempts[task] = 0
        
        self.fix_attempts[task] += 1
        
        # Return True if still within limit, False if at or over limit
        return self.fix_attempts[task] <= MAX_FIX_ATTEMPTS
    
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
        # Remove the task from the dictionary if it exists
        if task in self.fix_attempts:
            del self.fix_attempts[task]


def _wait_for_signal_file(signal_file_path: str, timeout: float = SIGNAL_WAIT_TIMEOUT, 
                         sleep_interval: float = SIGNAL_WAIT_SLEEP_INTERVAL,
                         debug: bool = False) -> None:
    """Wait for signal file to appear with timeout and error handling.
    
    This helper function implements robust signal file waiting with timeout protection
    and optional debug logging. It's used by run_claude_command to wait for Claude CLI
    command completion signals.
    
    Args:
        signal_file_path: Path to the signal file to wait for
        timeout: Maximum seconds to wait before raising TimeoutError
        sleep_interval: Seconds to sleep between file existence checks
        debug: Whether to print debug information during waiting
        
    Raises:
        TimeoutError: If signal file doesn't appear within timeout period
        OSError: If there are file system access errors during cleanup
        
    Note:
        This function will remove the signal file after it appears to clean up
        the file system state for subsequent command executions.
    """
    if debug:
        print(f"Waiting for signal file: {signal_file_path}")
    
    start_time = time.time()
    elapsed_time = 0.0
    
    while elapsed_time < timeout:
        if os.path.exists(signal_file_path):
            if debug:
                print(f"Signal file appeared after {elapsed_time:.1f}s")
            
            try:
                os.remove(signal_file_path)
                if debug:
                    print("Signal file cleaned up successfully")
                return
            except OSError as e:
                # Log the error but don't fail - the command may have completed successfully
                if debug:
                    print(f"Warning: Failed to remove signal file: {e}")
                return
        
        time.sleep(sleep_interval)
        elapsed_time = time.time() - start_time
    
    # Timeout reached - this indicates a potential issue with Claude CLI execution
    raise TimeoutError(f"Signal file {signal_file_path} did not appear within {timeout}s timeout")


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
    if debug:
        print(f"Executing Claude command: {command}")
        if args:
            print(f"Additional arguments: {args}")
    
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
    
    try:
        # Execute the Claude CLI command
        if debug:
            print(f"Running subprocess: {' '.join(command_array)}")
        
        result = subprocess.run(
            command_array,
            capture_output=True,
            text=True,
            check=False  # Don't raise on non-zero exit codes
        )
        
        if debug:
            print(f"Subprocess completed with return code: {result.returncode}")
            if result.stderr:
                print(f"Subprocess stderr: {result.stderr}")
        
    except subprocess.SubprocessError as e:
        raise subprocess.SubprocessError(f"Failed to execute Claude CLI command '{command}': {e}") from e
    
    # Wait for signal file to appear (indicates command completion)
    try:
        _wait_for_signal_file(SIGNAL_FILE, debug=debug)
    except TimeoutError as e:
        # Re-raise with additional context about the command that timed out
        raise TimeoutError(f"Claude command '{command}' timed out: {e}") from e
    
    # Parse JSON output from stdout
    try:
        if debug:
            print(f"Parsing JSON output: {result.stdout[:200]}{'...' if len(result.stdout) > 200 else ''}")
        
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Failed to parse Claude CLI JSON output for command '{command}': {e.msg}",
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
        if debug:
            print(f"Error executing command {command}: {e}")
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
    run_claude_command(CLEAR_CMD)
    run_claude_command(CONTINUE_CMD)
    run_claude_command(VALIDATE_CMD)
    
    return get_latest_status()


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
            print(f"Max fix attempts ({MAX_FIX_ATTEMPTS}) exceeded for task '{task}', skipping")
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
        for missing_file in missing_critical:
            print(f"Error: {missing_file} is missing")
        sys.exit(EXIT_MISSING_CRITICAL_FILE)
    
    # Check optional files - warn if missing
    missing_optional = validate_optional_files(optional_files)
    for missing_file in missing_optional:
        print(f"Warning: {missing_file} is missing")


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
    tracker = TaskTracker()
    
    while True:
        # Get next task
        task, all_complete = tracker.get_next_task()
        
        # Always execute TDD cycle - even when all tasks are complete,
        # we need to validate the final state before transitioning to refactoring
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
                print(f"ERROR: Final validation failed with status: {validation_status}")
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
    # Validate prerequisites and initialize workflow
    validate_prerequisites()
    
    # Start main orchestration loop
    execute_main_orchestration_loop()


if __name__ == "__main__":
    main()