"""
Metrics collector for operation timing and performance tracking.

This module provides the MetricsCollector class that tracks operation performance
metrics including timing, success/failure rates, and aggregated statistics.
"""

from typing import Dict, List, Any, Optional, Union
from threading import Lock


class MetricsCollector:
    """
    Thread-safe metrics collector for operation performance tracking.
    
    This class provides comprehensive metrics collection and aggregation
    capabilities for monitoring operation performance including timing,
    success/failure rates, and detailed statistics.
    
    Features:
    - Thread-safe concurrent access using threading.Lock
    - Structured operation records with metadata support
    - Comprehensive statistics calculation with helper methods
    - Input validation for data integrity
    - Support for operation type filtering
    
    Example:
        collector = MetricsCollector()
        collector.record_operation(
            operation_name="file_read",
            duration_ms=150.5,
            success=True,
            operation_type="io"
        )
        stats = collector.get_operation_stats()
    """
    
    def __init__(self) -> None:
        """
        Initialize the metrics collector with thread-safe storage.
        
        Creates an empty list for operation records and initializes
        a threading lock for concurrent access protection.
        """
        self.operations: List[Dict[str, Any]] = []
        self._lock = Lock()
    
    def record_operation(
        self, 
        operation_name: str, 
        duration_ms: float, 
        success: bool = True, 
        **kwargs: Any
    ) -> bool:
        """
        Record an operation with its timing and success status in a thread-safe manner.
        
        Args:
            operation_name: Name of the operation (must be non-empty string)
            duration_ms: Duration in milliseconds (must be non-negative)
            success: Whether the operation was successful (default: True)
            **kwargs: Additional metadata (e.g., operation_type)
        
        Returns:
            bool: True if operation was recorded successfully
            
        Raises:
            ValueError: If operation_name is empty or duration_ms is negative
            TypeError: If operation_name is not a string or duration_ms is not numeric
        """
        # Validate input parameters
        self._validate_operation_inputs(operation_name, duration_ms)
        
        # For backward compatibility, create a dict that looks like the old format
        # but store it as an OperationRecord internally
        operation_dict = {
            'operation_name': operation_name,
            'duration_ms': float(duration_ms),
            'success': bool(success),
            **kwargs
        }
        
        # Thread-safe append - store as dict to maintain test compatibility
        with self._lock:
            self.operations.append(operation_dict)
        
        return True
    
    def get_total_operations(self) -> int:
        """
        Get the total number of operations recorded in a thread-safe manner.
        
        Returns:
            int: Total count of recorded operations
        """
        with self._lock:
            return len(self.operations)
    
    def get_operations_by_type(self) -> Dict[str, int]:
        """
        Get a count of operations by their type in a thread-safe manner.
        
        Returns:
            Dict[str, int]: Mapping of operation types to their occurrence counts
        """
        with self._lock:
            return self._calculate_operations_by_type(self.operations)
    
    def get_operation_stats(self, operation_type: Optional[str] = None) -> Dict[str, Union[int, float, Dict[str, int]]]:
        """
        Get aggregated statistics for operations in a thread-safe manner.
        
        Args:
            operation_type: Optional filter by operation type. If provided,
                          only operations matching this type will be included
                          in the statistics calculation.
        
        Returns:
            Dict containing comprehensive operation statistics:
            - total_operations: Total number of operations
            - successful_operations: Count of successful operations
            - failed_operations: Count of failed operations  
            - success_rate: Success rate as percentage (0.0-100.0)
            - average_duration_ms: Average operation duration
            - min_duration_ms: Minimum operation duration
            - max_duration_ms: Maximum operation duration
            - operations_by_type: Count of operations by type
        """
        with self._lock:
            # Create a snapshot of operations for consistent calculation
            operations_snapshot = list(self.operations)
        
        # Filter operations by type if specified
        filtered_ops = self._filter_operations_by_type(operations_snapshot, operation_type)
        
        # Handle empty operations case
        if not filtered_ops:
            return self._get_empty_stats()
        
        return self._calculate_comprehensive_stats(filtered_ops)

    def _validate_operation_inputs(self, operation_name: str, duration_ms: float) -> None:
        """
        Validate input parameters for operation recording.
        
        Args:
            operation_name: Name of the operation to validate
            duration_ms: Duration in milliseconds to validate
            
        Raises:
            TypeError: If types are incorrect
            ValueError: If values are invalid
        """
        if not isinstance(operation_name, str):
            raise TypeError(f"operation_name must be a string, got {type(operation_name)}")
        
        if not operation_name.strip():
            raise ValueError("operation_name cannot be empty or whitespace")
            
        if not isinstance(duration_ms, (int, float)):
            raise TypeError(f"duration_ms must be numeric, got {type(duration_ms)}")
            
        if duration_ms < 0:
            raise ValueError(f"duration_ms must be non-negative, got {duration_ms}")

    def _filter_operations_by_type(
        self, 
        operations: List[Dict[str, Any]], 
        operation_type: Optional[str]
    ) -> List[Dict[str, Any]]:
        """
        Filter operations by type if specified.
        
        Args:
            operations: List of operation dictionaries to filter
            operation_type: Type to filter by, or None for no filtering
            
        Returns:
            List of filtered operations
        """
        if operation_type:
            return [op for op in operations if op.get('operation_type') == operation_type]
        return operations

    def _get_empty_stats(self) -> Dict[str, Union[int, float, Dict[str, int]]]:
        """
        Get statistics for empty operation set.
        
        Returns:
            Dict with default zero values for all statistics
        """
        return {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'success_rate': 0.0,
            'average_duration_ms': 0.0,
            'min_duration_ms': 0.0,
            'max_duration_ms': 0.0,
            'operations_by_type': {}
        }

    def _calculate_comprehensive_stats(
        self, 
        filtered_ops: List[Dict[str, Any]]
    ) -> Dict[str, Union[int, float, Dict[str, int]]]:
        """
        Calculate comprehensive statistics for a set of operations.
        
        Args:
            filtered_ops: List of operations to calculate statistics for
            
        Returns:
            Dict with calculated statistics
        """
        total_operations = len(filtered_ops)
        successful_operations = sum(1 for op in filtered_ops if op['success'])
        failed_operations = total_operations - successful_operations
        success_rate = (successful_operations / total_operations) * 100.0
        
        durations = [op['duration_ms'] for op in filtered_ops]
        average_duration_ms = sum(durations) / len(durations)
        min_duration_ms = min(durations)
        max_duration_ms = max(durations)
        
        operations_by_type = self._calculate_operations_by_type(filtered_ops)
        
        return {
            'total_operations': total_operations,
            'successful_operations': successful_operations,
            'failed_operations': failed_operations,
            'success_rate': success_rate,
            'average_duration_ms': average_duration_ms,
            'min_duration_ms': min_duration_ms,
            'max_duration_ms': max_duration_ms,
            'operations_by_type': operations_by_type
        }

    def _calculate_operations_by_type(self, operations: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Calculate count of operations by type.
        
        Args:
            operations: List of operations to count by type
            
        Returns:
            Dict mapping operation types to their counts
        """
        type_counts = {}
        for operation in operations:
            operation_type = operation.get('operation_type')
            if operation_type:
                type_counts[operation_type] = type_counts.get(operation_type, 0) + 1
        return type_counts