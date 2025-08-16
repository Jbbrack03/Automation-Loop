"""
Heartbeat mechanism for tracking long-running operations.

This module implements a thread-safe heartbeat tracking system to monitor
the health and activity of long-running operations in the automated
development workflow.

Key Features:
    - Thread-safe operation tracking with lock protection
    - Structured data types for operation information
    - Comprehensive error handling and validation
    - Real-time heartbeat monitoring with configurable timeouts
    - Operation lifecycle management and stale detection

Example Usage:
    >>> tracker = HeartbeatTracker()
    >>> tracker.start_heartbeat("my_operation", 30.0)  # 30 second timeout
    >>> tracker.update_heartbeat("my_operation")
    >>> tracker.is_operation_alive("my_operation")
    True
    >>> tracker.get_active_operations()
    ['my_operation']
"""

import time
import threading
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Dict, List, Optional, Union


class HeartbeatError(Exception):
    """Base exception class for heartbeat-related errors."""
    pass


class OperationNotFoundError(HeartbeatError):
    """Raised when attempting to access a non-existent operation."""
    pass


class InvalidTimeoutError(HeartbeatError):
    """Raised when an invalid timeout value is provided."""
    pass


@dataclass
class OperationInfo:
    """
    Structured information about a tracked operation.
    
    Attributes:
        started_at: Unix timestamp when operation tracking began
        last_heartbeat: Unix timestamp of most recent heartbeat
        timeout_seconds: Maximum time allowed between heartbeats
    """
    started_at: float
    last_heartbeat: float
    timeout_seconds: float
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary format for backward compatibility."""
        return {
            'started_at': self.started_at,
            'last_heartbeat': self.last_heartbeat,
            'timeout_seconds': self.timeout_seconds
        }


class HeartbeatTracker:
    """
    Thread-safe tracker for heartbeats of long-running operations.
    
    This class provides a robust mechanism for monitoring the health of
    long-running operations by tracking heartbeat signals and detecting
    stale processes that haven't sent heartbeats within their timeout period.
    
    Thread Safety:
        All operations are protected by an internal threading lock to ensure
        safe concurrent access from multiple threads.
    
    Error Handling:
        Methods validate inputs and raise domain-specific exceptions for
        invalid operations or missing operations.
        
    Example:
        >>> tracker = HeartbeatTracker()
        >>> tracker.start_heartbeat("task_123", timeout_seconds=60.0)
        >>> time.sleep(30)
        >>> tracker.update_heartbeat("task_123")
        >>> alive = tracker.is_operation_alive("task_123")  # Returns True
    """
    
    def __init__(self) -> None:
        """
        Initialize the heartbeat tracker with empty operation storage.
        
        Creates a thread-safe tracker with an internal lock for concurrent access protection.
        """
        self._operations: Dict[str, OperationInfo] = {}
        self._lock = threading.Lock()
    
    def _validate_operation_id(self, operation_id: str) -> None:
        """
        Validate operation ID parameter.
        
        Args:
            operation_id: The operation identifier to validate
            
        Raises:
            TypeError: If operation_id is not a string
            ValueError: If operation_id is empty or None
        """
        if not isinstance(operation_id, str):
            raise TypeError(f"operation_id must be a string, got {type(operation_id).__name__}")
        if not operation_id or not operation_id.strip():
            raise ValueError("operation_id cannot be empty or whitespace")

    def _validate_timeout(self, timeout_seconds: Union[int, float]) -> None:
        """
        Validate timeout parameter.
        
        Args:
            timeout_seconds: The timeout value to validate
            
        Raises:
            TypeError: If timeout_seconds is not a number
            InvalidTimeoutError: If timeout_seconds is not positive
        """
        if not isinstance(timeout_seconds, (int, float)):
            raise TypeError(f"timeout_seconds must be a number, got {type(timeout_seconds).__name__}")
        if timeout_seconds <= 0:
            raise InvalidTimeoutError(f"timeout_seconds must be positive, got {timeout_seconds}")

    def start_heartbeat(self, operation_id: str, timeout_seconds: Union[int, float]) -> bool:
        """
        Start tracking heartbeat for an operation.
        
        This method begins monitoring a new operation with the specified timeout.
        If an operation with the same ID already exists, it will be replaced.
        
        Args:
            operation_id: Unique identifier for the operation (must be non-empty string)
            timeout_seconds: Maximum time allowed between heartbeats (must be positive)
            
        Returns:
            True if tracking started successfully
            
        Raises:
            TypeError: If parameters have incorrect types
            ValueError: If operation_id is empty
            InvalidTimeoutError: If timeout_seconds is not positive
            
        Example:
            >>> tracker.start_heartbeat("data_processing", 120.0)
            True
        """
        self._validate_operation_id(operation_id)
        self._validate_timeout(timeout_seconds)
        
        current_time = time.time()
        operation_info = OperationInfo(
            started_at=current_time,
            last_heartbeat=current_time,
            timeout_seconds=float(timeout_seconds)
        )
        
        with self._lock:
            self._operations[operation_id] = operation_info
        
        return True
    
    def is_operation_alive(self, operation_id: str) -> bool:
        """
        Check if an operation is still alive based on heartbeat timeout.
        
        This method determines if an operation is still considered active by
        comparing the time since its last heartbeat to its configured timeout.
        
        Args:
            operation_id: Operation identifier to check
            
        Returns:
            True if operation exists and is within timeout, False otherwise
            
        Raises:
            TypeError: If operation_id is not a string
            ValueError: If operation_id is empty
            
        Example:
            >>> tracker.is_operation_alive("active_task")
            True
            >>> tracker.is_operation_alive("missing_task")
            False
        """
        self._validate_operation_id(operation_id)
        
        with self._lock:
            if operation_id not in self._operations:
                return False
            
            operation = self._operations[operation_id]
            current_time = time.time()
            time_since_heartbeat = current_time - operation.last_heartbeat
            
            return time_since_heartbeat <= operation.timeout_seconds
    
    def update_heartbeat(self, operation_id: str) -> bool:
        """
        Update the heartbeat timestamp for an operation.
        
        This method records a new heartbeat for the specified operation,
        resetting its timeout countdown. The operation must exist to be updated.
        
        Args:
            operation_id: Operation identifier to update
            
        Returns:
            True if update successful, False if operation not found
            
        Raises:
            TypeError: If operation_id is not a string
            ValueError: If operation_id is empty
            
        Example:
            >>> tracker.update_heartbeat("my_task")
            True
            >>> tracker.update_heartbeat("nonexistent_task")
            False
        """
        self._validate_operation_id(operation_id)
        
        with self._lock:
            if operation_id not in self._operations:
                return False
            
            self._operations[operation_id].last_heartbeat = time.time()
            return True
    
    def get_active_operations(self) -> List[str]:
        """
        Get list of all tracked operation IDs that are still alive.
        
        This method efficiently retrieves all operations that are currently
        within their timeout period. The check is performed atomically.
        
        Returns:
            List of operation IDs that are still alive (empty list if none)
            
        Example:
            >>> tracker.get_active_operations()
            ['task_1', 'task_2', 'background_job']
        """
        active_ops = []
        current_time = time.time()
        
        with self._lock:
            for op_id, operation in self._operations.items():
                time_since_heartbeat = current_time - operation.last_heartbeat
                if time_since_heartbeat <= operation.timeout_seconds:
                    active_ops.append(op_id)
        
        return active_ops
    
    def get_operation_info(self, operation_id: str) -> Optional[Dict[str, float]]:
        """
        Get detailed information about a tracked operation.
        
        This method returns a copy of the operation's metadata including
        start time, last heartbeat, and timeout configuration.
        
        Args:
            operation_id: Operation identifier to query
            
        Returns:
            Dictionary with operation details if found, None otherwise.
            Contains: 'started_at', 'last_heartbeat', 'timeout_seconds'
            
        Raises:
            TypeError: If operation_id is not a string
            ValueError: If operation_id is empty
            
        Example:
            >>> info = tracker.get_operation_info("my_task")
            >>> print(f"Started: {info['started_at']}")
        """
        self._validate_operation_id(operation_id)
        
        with self._lock:
            if operation_id not in self._operations:
                return None
            
            return self._operations[operation_id].to_dict()
    
    def get_stale_operations(self) -> Dict[str, Dict[str, float]]:
        """
        Get information about operations that have exceeded their timeout.
        
        This method identifies operations that haven't sent heartbeats within
        their configured timeout period and returns detailed timing information.
        
        Returns:
            Dictionary mapping operation_id to stale info. Each stale info contains:
            - 'last_heartbeat': Timestamp of last heartbeat
            - 'timeout_seconds': Configured timeout duration  
            - 'time_since_heartbeat': Actual time elapsed since last heartbeat
            
        Example:
            >>> stale = tracker.get_stale_operations()
            >>> for op_id, info in stale.items():
            ...     print(f"{op_id} stale for {info['time_since_heartbeat']:.1f}s")
        """
        stale_ops = {}
        current_time = time.time()
        
        with self._lock:
            for op_id, operation in self._operations.items():
                time_since_heartbeat = current_time - operation.last_heartbeat
                
                if time_since_heartbeat > operation.timeout_seconds:
                    stale_ops[op_id] = {
                        'last_heartbeat': operation.last_heartbeat,
                        'timeout_seconds': operation.timeout_seconds,
                        'time_since_heartbeat': time_since_heartbeat
                    }
        
        return stale_ops