"""Automated development workflow orchestrator.

This module provides the main orchestrator function that manages prerequisite file
validation for the automated development workflow system.
"""

import glob
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

# Exit codes
EXIT_SUCCESS = 0
EXIT_MISSING_CRITICAL_FILE = 1

# Failure tracking constants
MAX_FIX_ATTEMPTS = 3

# Signal file waiting constants
SIGNAL_WAIT_SLEEP_INTERVAL = 0.1  # seconds between signal file checks
SIGNAL_WAIT_TIMEOUT = 30.0  # maximum seconds to wait for signal file


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


def main():
    """Main orchestrator function with prerequisite file checks."""
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


if __name__ == "__main__":
    main()