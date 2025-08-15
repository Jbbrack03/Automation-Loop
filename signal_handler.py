"""Signal file handling module.

This module provides functions for waiting on signal files and cleaning them up.
Signal files are used to detect command completion in the automated workflow.
"""

import os
import time
from typing import Union

from config import SIGNAL_WAIT_TIMEOUT, SIGNAL_WAIT_SLEEP_INTERVAL, LOGGERS


def _get_logger():
    """Get the command executor logger for this module."""
    return LOGGERS.get('command_executor')


def wait_for_signal_file(signal_file_path: str, timeout: Union[int, float] = SIGNAL_WAIT_TIMEOUT, 
                        sleep_interval: Union[int, float] = SIGNAL_WAIT_SLEEP_INTERVAL,
                        debug: bool = False) -> None:
    """Wait for signal file to appear with timeout and error handling.
    
    This function implements robust signal file waiting with timeout protection
    and structured logging. It's used to wait for Claude CLI command completion signals.
    
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
    logger = _get_logger()
    
    if logger:
        logger.debug(f"Waiting for signal file: {signal_file_path} (timeout: {timeout}s)")
    
    start_time = time.time()
    elapsed_time = 0.0
    
    while elapsed_time < timeout:
        if os.path.exists(signal_file_path):
            if logger:
                logger.debug(f"Signal file appeared after {elapsed_time:.1f}s")
            
            try:
                os.remove(signal_file_path)
                if logger:
                    logger.debug("Signal file cleaned up successfully")
                return
            except OSError as e:
                # Log the error but don't fail - the command may have completed successfully
                if logger:
                    logger.warning(f"Failed to remove signal file: {e}")
                return
        
        time.sleep(sleep_interval)
        elapsed_time = time.time() - start_time
    
    # Timeout reached - this indicates a potential issue with Claude CLI execution
    error_msg = f"Signal file {signal_file_path} did not appear within {timeout}s timeout"
    if logger:
        logger.error(error_msg)
    raise TimeoutError(error_msg)


def cleanup_signal_file(signal_file_path: str) -> None:
    """Clean up a signal file by removing it from the filesystem.
    
    Attempts to delete the signal file. Handles file operation errors gracefully
    to ensure cleanup failures don't break the main workflow.
    
    Args:
        signal_file_path: Path to the signal file to delete
        
    Note:
        File deletion errors are handled gracefully and logged only.
        This prevents cleanup failures from breaking the main workflow.
    """
    logger = _get_logger()
    
    try:
        if os.path.exists(signal_file_path):
            os.remove(signal_file_path)
            if logger:
                logger.debug(f"Successfully cleaned up signal file: {signal_file_path}")
    except (OSError, FileNotFoundError, PermissionError) as e:
        # Continue if file deletion fails - don't break the workflow
        if logger:
            logger.warning(f"Failed to clean up signal file {signal_file_path}: {e}")