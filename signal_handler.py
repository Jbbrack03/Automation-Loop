"""Signal file handling module.

This module provides functions for waiting on signal files and cleaning them up.
Signal files are used to detect command completion in the automated workflow.
"""

import logging
import os
import random
import time
from pathlib import Path
from typing import Union, Optional

from config import SIGNAL_WAIT_TIMEOUT, SIGNAL_WAIT_SLEEP_INTERVAL, LOGGERS


def _get_logger() -> Optional[logging.Logger]:
    """Get the command executor logger for this module."""
    return LOGGERS.get('command_executor')


def _calculate_next_interval(iteration: int, min_interval: float, max_interval: float, 
                           jitter: bool = False) -> float:
    """Calculate the next polling interval using exponential backoff.
    
    Implements exponential backoff with optional jitter to reduce CPU usage
    and prevent thundering herd issues when multiple processes are waiting.
    
    Args:
        iteration: Current iteration number (0-based)
        min_interval: Initial interval in seconds
        max_interval: Maximum interval cap in seconds
        jitter: Whether to add random jitter (±10%) to prevent thundering herd
        
    Returns:
        Next interval duration in seconds
        
    Algorithm:
        - First 4 iterations: min_interval * (2 ^ iteration)
        - 5th iteration and beyond: max_interval
        - Optional jitter adds ±10% randomization
        
    Example:
        With min_interval=0.1, max_interval=2.0:
        - Iteration 0: 0.1s
        - Iteration 1: 0.2s  
        - Iteration 2: 0.4s
        - Iteration 3: 0.8s
        - Iteration 4+: 2.0s
    """
    if iteration < 4:
        # Exponential backoff: double the interval each iteration
        interval = min_interval * (2 ** iteration)
    else:
        # Cap at maximum interval after 4 iterations
        interval = max_interval
    
    # Ensure we don't exceed the maximum interval during exponential phase
    interval = min(interval, max_interval)
    
    # Add jitter if requested (±10% randomization)
    if jitter:
        jitter_factor = 1.0 + random.uniform(-0.1, 0.1)
        interval = interval * jitter_factor
        # Re-apply max_interval cap after jitter
        interval = min(interval, max_interval)
    
    return interval


def wait_for_signal_file(signal_file_path: Union[str, Path], timeout: float = SIGNAL_WAIT_TIMEOUT, 
                        sleep_interval: float = None,
                        min_interval: float = 0.1,
                        max_interval: float = 2.0,
                        jitter: bool = False,
                        debug: bool = False) -> None:
    """Wait for signal file to appear with timeout and error handling.
    
    This function implements robust signal file waiting with timeout protection
    and structured logging. It uses exponential backoff to reduce CPU usage
    and optional jitter to prevent thundering herd issues.
    
    Args:
        signal_file_path: Path to the signal file to wait for (str or Path object)
        timeout: Maximum seconds to wait before raising TimeoutError
        sleep_interval: Deprecated. Use min_interval and max_interval instead
        min_interval: Initial seconds to sleep between file existence checks
        max_interval: Maximum seconds to sleep between file existence checks
        jitter: Whether to add random jitter (±10%) to backoff intervals
        debug: Whether to enable debug-level logging
        
    Raises:
        TimeoutError: If signal file doesn't appear within timeout period
        OSError: If there are file system access errors during cleanup
        
    Note:
        This function will remove the signal file after it appears to clean up
        the file system state for subsequent command executions.
        
    Backoff Algorithm:
        Uses exponential backoff starting from min_interval, doubling each iteration
        until max_interval is reached. Optional jitter prevents thundering herd.
    """
    logger = _get_logger()
    
    # Handle backward compatibility
    if sleep_interval is not None:
        current_interval = sleep_interval
        use_exponential_backoff = False
    else:
        current_interval = min_interval
        use_exponential_backoff = True
    
    if logger:
        logger.debug(f"Waiting for signal file: {signal_file_path} (timeout: {timeout}s)")
    
    start_time = time.time()
    elapsed_time = 0.0
    iterations = 0
    
    while elapsed_time < timeout:
        if os.path.exists(str(signal_file_path)):
            if logger:
                logger.debug(f"Signal file appeared after {elapsed_time:.1f}s")
            
            try:
                os.remove(str(signal_file_path))
                if logger:
                    logger.debug("Signal file cleaned up successfully")
                return
            except OSError as e:
                # Log the error but don't fail - the command may have completed successfully
                if logger:
                    logger.warning(f"Failed to remove signal file: {e}")
                return
        
        # Calculate interval using exponential backoff
        if use_exponential_backoff:
            current_interval = _calculate_next_interval(
                iterations, min_interval, max_interval, jitter
            )
            
            # Log backoff progression for observability
            if logger and debug:
                if iterations == 0:
                    logger.debug(f"Starting exponential backoff: min={min_interval}s, max={max_interval}s, jitter={jitter}")
                
                if current_interval == max_interval and iterations >= 4:
                    logger.debug(f"Backoff reached maximum interval: {current_interval}s (iteration {iterations})")
                else:
                    logger.debug(f"Backoff interval: {current_interval:.3f}s (iteration {iterations})")
        
        time.sleep(current_interval)
        elapsed_time = time.time() - start_time
        iterations += 1
    
    # Timeout reached - this indicates a potential issue with Claude CLI execution
    error_msg = f"Signal file {signal_file_path} did not appear within {timeout}s timeout"
    if logger:
        logger.error(error_msg)
    raise TimeoutError(error_msg)


def cleanup_signal_file(signal_file_path: Union[str, Path]) -> None:
    """Clean up a signal file by removing it from the filesystem.
    
    Attempts to delete the signal file. Handles file operation errors gracefully
    to ensure cleanup failures don't break the main workflow.
    
    Args:
        signal_file_path: Path to the signal file to delete (str or Path object)
        
    Note:
        File deletion errors are handled gracefully and logged only.
        This prevents cleanup failures from breaking the main workflow.
    """
    logger = _get_logger()
    
    try:
        if os.path.exists(str(signal_file_path)):
            os.remove(str(signal_file_path))
            if logger:
                logger.debug(f"Successfully cleaned up signal file: {signal_file_path}")
    except (OSError, FileNotFoundError, PermissionError) as e:
        # Continue if file deletion fails - don't break the workflow
        if logger:
            logger.warning(f"Failed to clean up signal file {signal_file_path}: {e}")