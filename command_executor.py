"""Command execution module.

This module provides functions for executing Claude CLI commands and handling
their completion and error conditions.
"""

import json
import random
import subprocess
import time
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypedDict

from config import SIGNAL_FILE, LOGGERS
from usage_limit import parse_usage_limit_error, calculate_wait_time
from signal_handler import wait_for_signal_file


class RetryConfig(TypedDict, total=False):
    """Configuration for exponential backoff retry logic.
    
    Attributes:
        max_retries: Maximum number of retry attempts (default: 3)
        base_delay: Base delay in seconds for exponential backoff (default: 1.0)
        max_delay: Maximum delay in seconds to cap exponential growth (default: 60.0)
        jitter_factor: Jitter factor for randomizing delays (default: 0.1)
        retryable_exceptions: Tuple of exception types that should trigger retries
    """
    max_retries: int
    base_delay: float
    max_delay: float
    jitter_factor: float
    retryable_exceptions: tuple


class CircuitBreakerConfig(TypedDict, total=False):
    """Configuration for circuit breaker pattern.
    
    Attributes:
        failure_threshold: Number of consecutive failures before opening circuit (default: 5)
        recovery_timeout: Time in seconds before attempting to close circuit (default: 60.0)
        half_open_max_calls: Maximum calls in half-open state before fully closing (default: 3)
    """
    failure_threshold: int
    recovery_timeout: float
    half_open_max_calls: int


class CircuitState:
    """Simple circuit breaker state management.
    
    This is a basic implementation that tracks failures and manages circuit state
    for preventing cascading failures in retry scenarios.
    """
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half-open
        self.half_open_calls = 0
    
    def can_execute(self) -> bool:
        """Check if execution is allowed based on circuit state."""
        if self.state == 'closed':
            return True
        elif self.state == 'open':
            # Check if recovery timeout has passed
            if (time.time() - self.last_failure_time) > self.config.get('recovery_timeout', 60.0):
                self.state = 'half-open'
                self.half_open_calls = 0
                return True
            return False
        elif self.state == 'half-open':
            return self.half_open_calls < self.config.get('half_open_max_calls', 3)
        return False
    
    def record_success(self):
        """Record successful execution."""
        if self.state == 'half-open':
            self.half_open_calls += 1
            if self.half_open_calls >= self.config.get('half_open_max_calls', 3):
                self.state = 'closed'
                self.failure_count = 0
        elif self.state == 'closed':
            self.failure_count = 0
    
    def record_failure(self):
        """Record failed execution."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == 'closed' and self.failure_count >= self.config.get('failure_threshold', 5):
            self.state = 'open'
        elif self.state == 'half-open':
            self.state = 'open'


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


def _get_default_retry_config() -> RetryConfig:
    """Get default retry configuration.
    
    Returns:
        Default retry configuration with sensible values for most use cases
    """
    return {
        'max_retries': 3,
        'base_delay': 1.0,
        'max_delay': 60.0,
        'jitter_factor': 0.1,
        'retryable_exceptions': (
            subprocess.SubprocessError,
            CommandTimeoutError,
            CommandExecutionError
        )
    }


def _get_default_circuit_breaker_config() -> CircuitBreakerConfig:
    """Get default circuit breaker configuration.
    
    Returns:
        Default circuit breaker configuration with sensible values
    """
    return {
        'failure_threshold': 5,
        'recovery_timeout': 60.0,
        'half_open_max_calls': 3
    }


def _is_retryable_error(exception: Exception, retryable_exceptions: tuple) -> bool:
    """Check if an exception is retryable based on configuration.
    
    Args:
        exception: The exception to check
        retryable_exceptions: Tuple of exception types that should trigger retries
        
    Returns:
        True if the exception should trigger a retry, False otherwise
    """
    # JSON decode errors are never retryable (permanent failure)
    if isinstance(exception, json.JSONDecodeError) or isinstance(exception, JSONParseError):
        return False
    
    # Check if exception type is in retryable list
    return isinstance(exception, retryable_exceptions)


def _calculate_retry_delay(attempt: int, base_delay: float, max_delay: float, jitter_factor: float) -> float:
    """Calculate retry delay with exponential backoff and jitter.
    
    Args:
        attempt: The retry attempt number (0-based)
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        jitter_factor: Factor for adding randomness (0.0 to 1.0)
        
    Returns:
        Calculated delay in seconds with jitter applied
    """
    # Calculate exponential backoff: base_delay * (2 ^ attempt)
    exponential_delay = base_delay * (2 ** attempt)
    
    # Cap at max_delay
    capped_delay = min(exponential_delay, max_delay)
    
    # Add jitter: delay +/- (jitter_factor * delay)
    # Call random.uniform with jitter_factor range, then multiply by delay
    jitter_range = jitter_factor * capped_delay
    jitter_percentage = random.uniform(-jitter_range, jitter_range)
    # Scale the percentage by the delay to get final jitter
    jitter = jitter_percentage * capped_delay
    
    return capped_delay + jitter


def with_retry_and_circuit_breaker(
    retry_config: Optional[RetryConfig] = None,
    circuit_config: Optional[CircuitBreakerConfig] = None,
    logger_name: str = 'command_executor'
) -> Callable:
    """Decorator that adds retry logic with exponential backoff and circuit breaker pattern.
    
    This decorator provides reusable retry functionality that can be applied to any function.
    It implements exponential backoff with jitter and includes a circuit breaker pattern
    to prevent cascading failures.
    
    Args:
        retry_config: Optional retry configuration. Uses defaults if not provided.
        circuit_config: Optional circuit breaker configuration. Uses defaults if not provided.
        logger_name: Name of logger to use for retry/circuit breaker logging.
        
    Returns:
        Decorator function that wraps the target function with retry logic.
        
    Example:
        @with_retry_and_circuit_breaker(
            retry_config={'max_retries': 5, 'base_delay': 2.0},
            circuit_config={'failure_threshold': 3}
        )
        def my_function():
            # Function that may fail and should be retried
            pass
    """
    # Merge configs with defaults
    default_retry = _get_default_retry_config()
    if retry_config:
        merged_retry = default_retry.copy()
        merged_retry.update(retry_config)
        retry_config = merged_retry
    else:
        retry_config = default_retry
    
    default_circuit = _get_default_circuit_breaker_config()
    if circuit_config:
        merged_circuit = default_circuit.copy()
        merged_circuit.update(circuit_config)
        circuit_config = merged_circuit
    else:
        circuit_config = default_circuit
    
    # Create circuit breaker instance
    circuit = CircuitState(circuit_config)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = LOGGERS.get(logger_name)
            
            # Check circuit breaker state
            if not circuit.can_execute():
                error_msg = f"Circuit breaker is open, rejecting call to {func.__name__}"
                if logger:
                    logger.error(error_msg)
                raise CommandExecutionError(error_msg)
            
            last_exception = None
            for attempt in range(retry_config['max_retries'] + 1):  # +1 for initial attempt
                try:
                    result = func(*args, **kwargs)
                    circuit.record_success()
                    
                    if logger and attempt > 0:
                        logger.info(f"Successfully executed {func.__name__} after {attempt} retry attempts")
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    circuit.record_failure()
                    
                    # Check if this is a retryable error
                    if not _is_retryable_error(e, retry_config['retryable_exceptions']):
                        # Permanent failure - don't retry
                        if logger:
                            logger.error(f"Permanent failure in {func.__name__}: {e}")
                        raise e
                    
                    # Check if we've exhausted retries
                    if attempt >= retry_config['max_retries']:
                        # Out of retries - raise the final exception
                        error_msg = f"{func.__name__} failed after {retry_config['max_retries']} retries"
                        if logger:
                            logger.error(error_msg)
                        raise CommandExecutionError(error_msg) from last_exception
                    
                    # Calculate delay for next retry
                    delay = _calculate_retry_delay(
                        attempt,
                        retry_config['base_delay'],
                        retry_config['max_delay'],
                        retry_config['jitter_factor']
                    )
                    
                    # Log retry attempt
                    if logger:
                        logger.warning(f"{func.__name__} failed on attempt {attempt + 1}, retrying with delay {delay:.2f}s: {e}")
                    
                    # Wait before retrying
                    time.sleep(delay)
                    continue
            
            # This should never be reached, but just in case
            raise CommandExecutionError(f"{func.__name__} failed after all retry attempts") from last_exception
        
        return wrapper
    return decorator


def _execute_command_with_signal_wait(command_array: List[str], command: str, debug: bool = False) -> subprocess.CompletedProcess:
    """Execute command and wait for signal completion. 
    
    This function encapsulates the core command execution logic that was
    previously embedded in the retry loop. It handles:
    1. Subprocess execution
    2. Signal file waiting
    3. Combining any errors from both operations
    
    Args:
        command_array: The complete command array to execute
        command: The original Claude command for error context
        debug: Whether to enable debug logging
        
    Returns:
        subprocess.CompletedProcess object with stdout, stderr, and returncode
        
    Raises:
        Exception: Any exception from subprocess execution or signal waiting
    """
    logger = LOGGERS.get('command_executor')
    
    # Execute the Claude CLI command and wait for completion
    subprocess_exception = None
    result = None
    
    try:
        # Execute the Claude CLI command
        result = _execute_claude_subprocess(command_array, command, debug=debug)
    except Exception as e:
        subprocess_exception = e
    
    # Always wait for signal file completion, regardless of subprocess success/failure
    # Claude CLI with Stop hook creates signal files even for failed commands
    try:
        if logger:
            logger.debug("Waiting for command completion signal")
        _wait_for_completion_with_context(command, debug=debug)
    except Exception as wait_error:
        if logger:
            logger.debug(f"Signal file wait failed: {wait_error}")
        # If subprocess succeeded but wait failed, that's still an error
        if subprocess_exception is None:
            subprocess_exception = wait_error
    
    # If any subprocess execution failed, raise the error
    if subprocess_exception is not None:
        raise subprocess_exception
    
    return result


def _execute_claude_command_core(command: str, args: Optional[List[str]] = None, debug: bool = False) -> subprocess.CompletedProcess:
    """Core Claude command execution logic without retry wrapper.
    
    This function contains the essential command execution logic that was
    previously embedded in run_claude_command. It handles:
    1. Command array construction
    2. Command execution with signal waiting
    3. Usage limit detection and handling
    
    Args:
        command: The Claude command to execute (e.g., "/continue", "/validate")
        args: Optional additional arguments to append to the command array
        debug: Whether to enable debug logging for troubleshooting
        
    Returns:
        subprocess.CompletedProcess object with stdout, stderr, and returncode
        
    Raises:
        Exception: Any exception from command execution or signal handling
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
    
    # Execute command with signal waiting
    result = _execute_command_with_signal_wait(command_array, command, debug=debug)
    
    # Check for usage limit errors in stdout or stderr and handle retry if needed
    output_to_check = result.stdout + " " + result.stderr
    if "usage limit" in output_to_check.lower():
        if logger:
            logger.warning("Usage limit detected, initiating retry workflow")
        result = _handle_usage_limit_and_retry(command, command_array, result, debug=debug)
    
    return result


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
                      debug: bool = False, retry_config: Optional[RetryConfig] = None) -> Dict[str, Any]:
    """Execute a Claude CLI command and return parsed JSON output.
    
    This function executes Claude CLI commands with robust signal file waiting,
    exponential backoff retry logic, and comprehensive error handling. It uses the 
    Stop hook configuration in Claude CLI to detect command completion via signal file creation.
    
    Args:
        command: The Claude command to execute (e.g., "/continue", "/validate")
        args: Optional additional arguments to append to the command array
        debug: Whether to enable debug logging for troubleshooting
        retry_config: Optional retry configuration for exponential backoff retry logic
        
    Returns:
        Parsed JSON response from Claude CLI as a dictionary
        
    Raises:
        CommandExecutionError: If Claude CLI execution fails after all retries
        JSONParseError: If Claude CLI output is not valid JSON (not retried)
        CommandTimeoutError: If signal file doesn't appear within timeout period
        
    Note:
        This function relies on the Stop hook configuration in .claude/settings.local.json
        which creates a signal file when Claude CLI commands complete. The signal file
        waiting mechanism provides reliable completion detection for automation workflows.
        
        Retry logic is now handled by the @with_retry_and_circuit_breaker decorator,
        making the core logic cleaner and more focused.
    """
    logger = LOGGERS.get('command_executor')
    
    # Apply retry decorator dynamically with provided config
    @with_retry_and_circuit_breaker(retry_config=retry_config)
    def _wrapped_execute():
        """Execute the core command logic with retry wrapper."""
        return _execute_claude_command_core(command, args, debug)
    
    # Execute the core command logic with retry wrapper
    result = _wrapped_execute()
    
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