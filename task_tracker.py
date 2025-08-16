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
    """Tracks task completion status from Implementation_Plan.md file.
    
    This class manages task state by reading from Implementation_Plan.md and
    provides failure tracking functionality to limit retry attempts on failing tasks.
    
    Attributes:
        fix_attempts: Dictionary tracking failure count per task identifier
        _cached_content: Cached file content to minimize I/O operations
        _cached_mtime: Cached file modification time for cache invalidation
        _cache_hits: Number of cache hits for observability
        _cache_misses: Number of cache misses for observability
    """
    
    fix_attempts: Dict[str, int]
    _cached_content: Optional[str]
    _cached_mtime: Optional[float]
    _cache_hits: int
    _cache_misses: int
    
    def __init__(self) -> None:
        """Initialize TaskTracker with failure tracking.
        
        Sets up an empty dictionary to track fix attempts for tasks that fail
        during execution. Each task can have up to MAX_FIX_ATTEMPTS retries.
        """
        self.fix_attempts: Dict[str, int] = {}
        self._cached_content: Optional[str] = None
        self._cached_mtime: Optional[float] = None
        self._cache_hits: int = 0
        self._cache_misses: int = 0
    
    def _load_file_content(self) -> str:
        """Load Implementation_Plan file content with caching.
        
        This method handles file caching to minimize I/O operations. The cache
        is invalidated when the file modification time changes.
        
        Returns:
            The file content as a string
            
        Raises:
            FileNotFoundError: If the file does not exist
            PermissionError: If permission is denied
            UnicodeDecodeError: If file has encoding issues
            IOError, OSError: For other file-related errors
        """
        logger = LOGGERS['task_tracker']
        
        # Get current file modification time
        current_mtime = os.path.getmtime(IMPLEMENTATION_PLAN_FILE)
        
        # Check if we need to read the file (cache miss or invalidation)
        if self._cached_content is None or self._cached_mtime != current_mtime:
            # Cache miss or invalidation - read file content
            with open(IMPLEMENTATION_PLAN_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update cache
            self._cached_content = content
            self._cached_mtime = current_mtime
            self._cache_misses += 1
            
            logger.debug(f"Cache miss: File content loaded and cached with mtime {current_mtime} "
                        f"(total misses: {self._cache_misses})")
        else:
            # Cache hit - use cached content
            content = self._cached_content
            self._cache_hits += 1
            
            logger.debug(f"Cache hit: Using cached file content "
                        f"(total hits: {self._cache_hits})")
        
        return content
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics for monitoring and debugging.
        
        Returns:
            Dictionary containing cache hit and miss counts
        """
        return {
            'cache_hits': self._cache_hits,
            'cache_misses': self._cache_misses,
            'total_requests': self._cache_hits + self._cache_misses
        }
    
    def clear_cache(self) -> None:
        """Clear the file content cache.
        
        This method forces the next call to get_next_task() to reload
        the file from disk. Useful for testing or when you know the
        file has been modified externally.
        """
        logger = LOGGERS['task_tracker']
        logger.debug("Manually clearing file content cache")
        
        self._cached_content = None
        self._cached_mtime = None
    
    def get_next_task(self) -> Tuple[Optional[str], bool]:
        """Get the next incomplete task from Implementation_Plan.md.
        
        Reads the Implementation_Plan.md file and finds the first task marked
        as incomplete (with '- [ ]' marker). This implements sequential task
        processing where tasks must be completed in order.
        
        Uses file caching to minimize I/O operations. The cache is invalidated
        when the file modification time changes.
        
        Returns:
            Tuple of (task_line, all_complete) where:
            - task_line is the first incomplete task description or None if no incomplete tasks
            - all_complete is True if all tasks are complete or file is missing, False otherwise
            
        Raises:
            No exceptions are raised; file access errors are handled gracefully
            by returning (None, True) to indicate completion.
        """
        logger = LOGGERS['task_tracker']
        
        # Check if Implementation_Plan.md exists
        if not check_file_exists(IMPLEMENTATION_PLAN_FILE):
            logger.warning(f"Implementation Plan file not found: {IMPLEMENTATION_PLAN_FILE}")
            return (None, True)
        
        try:
            # Load file content using cached helper method
            content = self._load_file_content()
            
            # Parse file content
            lines = content.splitlines()
            logger.debug(f"Processing {len(lines)} lines from file content")
            
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
            logger.error(f"Implementation Plan file not found during read: {e}")
            return (None, True)
        except PermissionError as e:
            logger.error(f"Permission denied reading Implementation Plan file: {e}")
            return (None, True)
        except UnicodeDecodeError as e:
            logger.error(f"Encoding error reading Implementation Plan file: {e}")
            return (None, True)
        except (IOError, OSError) as e:
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