"""Task tracking module for automated development workflow.

This module provides the TaskTracker class for managing task completion status
from Implementation_Plan.md file with failure tracking functionality to limit
retry attempts on failing tasks.

Classes:
    TaskTracker: Main class for tracking task completion and failure attempts

Functions:
    check_file_exists: Utility function to check if a file exists

The module implements a circuit breaker pattern through failure tracking to
prevent infinite retry loops on persistently failing tasks.
"""

import os
from typing import Dict, Optional, Tuple

from config import (
    IMPLEMENTATION_PLAN_FILE,
    MAX_FIX_ATTEMPTS,
    LOGGERS
)

# Constants for task parsing
INCOMPLETE_TASK_MARKER = "- [ ]"
COMPLETED_TASK_MARKER = "- [X]"


def check_file_exists(filepath: str) -> bool:
    """Check if a file exists.
    
    Args:
        filepath: Path to the file to check
        
    Returns:
        True if file exists, False otherwise
    """
    return os.path.exists(filepath)


class TaskTracker:
    """Tracks task completion status from Implementation Plan.md file.
    
    This class manages task state by reading from Implementation Plan.md and
    provides failure tracking functionality to limit retry attempts on failing tasks.
    
    Attributes:
        fix_attempts: Dictionary tracking failure count per task identifier
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
            
            # Look for first incomplete task using marker constant
            for i, line in enumerate(lines):
                line = line.strip()
                if INCOMPLETE_TASK_MARKER in line:
                    # Extract the task description after the marker
                    task = line.split(INCOMPLETE_TASK_MARKER, 1)[1].strip()
                    logger.info(f"Found next incomplete task on line {i+1}: {task}")
                    return (task, False)
            
            # No incomplete tasks found - all are complete
            logger.info("All tasks in Implementation Plan are complete")
            return (None, True)
            
        except FileNotFoundError as e:
            # Should not happen since we check file existence above, but handle gracefully
            logger.error(f"Implementation Plan file not found during read: {e}")
            return (None, True)
        except PermissionError as e:
            # File exists but permission denied
            logger.error(f"Permission denied reading Implementation Plan file: {e}")
            return (None, True)
        except UnicodeDecodeError as e:
            # File has encoding issues
            logger.error(f"Encoding error reading Implementation Plan file: {e}")
            return (None, True)
        except (IOError, OSError) as e:
            # Other file-related errors
            logger.error(f"I/O error reading Implementation Plan file: {e}")
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
            
        Raises:
            ValueError: If task is None or empty string
        """
        if not task or not isinstance(task, str):
            raise ValueError("Task identifier must be a non-empty string")
        
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
            
        Raises:
            ValueError: If task is None or empty string
            
        Note:
            This method is safe to call even if the task is not currently being tracked.
        """
        if not task or not isinstance(task, str):
            raise ValueError("Task identifier must be a non-empty string")
        
        logger = LOGGERS['task_tracker']
        
        # Remove the task from the dictionary if it exists
        if task in self.fix_attempts:
            attempts = self.fix_attempts[task]
            del self.fix_attempts[task]
            logger.info(f"Reset fix attempts for task '{task}' (had {attempts} attempts)")
        else:
            logger.debug(f"No fix attempts to reset for task '{task}'")