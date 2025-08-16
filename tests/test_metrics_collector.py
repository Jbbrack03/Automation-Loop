"""
Tests for metrics collection for operation timing.

This file contains TDD tests for the metrics collection functionality that tracks
operation timing, success/failure rates, and provides aggregated statistics.
Following the red-green-refactor cycle, these tests are written before implementation.

The metrics collector should implement:
- MetricsCollector class to track operation performance metrics
- record_operation method to log operation duration and success/failure
- get_operation_stats method to retrieve aggregated metrics
- Integration with existing PerformanceTimer and logging infrastructure

Key Requirements for Task 13.4:
- Add metrics collection for operation timing
- Track success/failure rates
- Provide aggregated statistics (average duration, success rate, etc.)
- Support for different operation types
"""

import pytest
import time
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from pathlib import Path


class TestMetricsCollector:
    """Test suite for the metrics collection functionality."""
    
    def test_metrics_collector_operation_timing_and_aggregation(self, tmp_path, monkeypatch):
        """
        Test metrics collector can track operation timing and provide aggregated statistics.
        
        Given a MetricsCollector instance,
        when multiple operations are recorded with timing and success/failure status,
        then the collector should provide accurate aggregated metrics including:
        - Average operation duration
        - Success rate percentage
        - Total operation count
        - Operation counts by type
        - Min/max duration tracking
        
        This comprehensive test validates the core metrics collection functionality
        needed for monitoring operation performance in the automated development workflow.
        
        This test will initially fail because the MetricsCollector class doesn't exist yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Change to temporary directory to isolate test
        monkeypatch.chdir(tmp_path)
        
        # Import MetricsCollector class to test
        try:
            from metrics_collector import MetricsCollector
        except ImportError:
            pytest.fail("Cannot import MetricsCollector from metrics_collector.py - file doesn't exist yet")
        
        # Initialize metrics collector
        collector = MetricsCollector()
        
        # PHASE 1: Record multiple operations with varying durations and outcomes
        
        # Record successful operations
        result1 = collector.record_operation(
            operation_name="file_read",
            duration_ms=150.5,
            success=True,
            operation_type="io"
        )
        assert result1 is True, "record_operation should return True when recording successfully"
        
        result2 = collector.record_operation(
            operation_name="task_validation", 
            duration_ms=250.0,
            success=True,
            operation_type="validation"
        )
        assert result2 is True, "record_operation should return True for valid operation recording"
        
        # Record failed operation
        result3 = collector.record_operation(
            operation_name="command_execution",
            duration_ms=500.8,
            success=False,
            operation_type="command"
        )
        assert result3 is True, "record_operation should return True even for failed operations"
        
        # Record another successful operation of same type
        result4 = collector.record_operation(
            operation_name="file_write",
            duration_ms=75.2,
            success=True,
            operation_type="io"
        )
        assert result4 is True, "record_operation should handle multiple operations of same type"
        
        # PHASE 2: Verify individual operation tracking
        
        # Verify total operations count
        total_operations = collector.get_total_operations()
        assert total_operations == 4, f"Expected 4 total operations, got {total_operations}"
        
        # Verify operations by type
        operations_by_type = collector.get_operations_by_type()
        expected_type_counts = {"io": 2, "validation": 1, "command": 1}
        assert operations_by_type == expected_type_counts, f"Expected {expected_type_counts}, got {operations_by_type}"
        
        # PHASE 3: Test aggregated statistics
        
        # Get overall statistics
        overall_stats = collector.get_operation_stats()
        assert overall_stats is not None, "get_operation_stats should return statistics"
        
        # Verify required statistics fields
        required_fields = ['average_duration_ms', 'success_rate', 'total_operations', 
                          'successful_operations', 'failed_operations', 'min_duration_ms', 'max_duration_ms']
        for field in required_fields:
            assert field in overall_stats, f"Overall stats should include {field}"
        
        # Verify calculated statistics accuracy
        expected_avg_duration = (150.5 + 250.0 + 500.8 + 75.2) / 4  # 244.125
        assert abs(overall_stats['average_duration_ms'] - expected_avg_duration) < 0.1, \
            f"Expected average duration ~{expected_avg_duration:.1f}ms, got {overall_stats['average_duration_ms']}"
        
        expected_success_rate = 75.0  # 3 successes out of 4 operations = 75%
        assert overall_stats['success_rate'] == expected_success_rate, \
            f"Expected success rate {expected_success_rate}%, got {overall_stats['success_rate']}"
        
        assert overall_stats['total_operations'] == 4, "Total operations should be 4"
        assert overall_stats['successful_operations'] == 3, "Successful operations should be 3"
        assert overall_stats['failed_operations'] == 1, "Failed operations should be 1"
        assert overall_stats['min_duration_ms'] == 75.2, "Min duration should be 75.2ms"
        assert overall_stats['max_duration_ms'] == 500.8, "Max duration should be 500.8ms"
        
        # PHASE 4: Test statistics by operation type
        
        # Get statistics filtered by operation type
        io_stats = collector.get_operation_stats(operation_type="io")
        assert io_stats is not None, "Should be able to get stats for specific operation type"
        
        # Verify IO operations statistics (150.5ms success + 75.2ms success = 2 operations)
        expected_io_avg = (150.5 + 75.2) / 2  # 112.85
        assert abs(io_stats['average_duration_ms'] - expected_io_avg) < 0.1, \
            f"Expected IO average duration ~{expected_io_avg:.1f}ms, got {io_stats['average_duration_ms']}"
        
        assert io_stats['success_rate'] == 100.0, "IO operations should have 100% success rate"
        assert io_stats['total_operations'] == 2, "Should have 2 IO operations"
        
        # Test statistics for operation type with failure
        command_stats = collector.get_operation_stats(operation_type="command")
        assert command_stats['success_rate'] == 0.0, "Command operations should have 0% success rate"
        assert command_stats['total_operations'] == 1, "Should have 1 command operation"
        
        # PHASE 5: Test edge cases and validation
        
        # Test getting stats for non-existent operation type
        nonexistent_stats = collector.get_operation_stats(operation_type="nonexistent")
        assert nonexistent_stats['total_operations'] == 0, "Non-existent type should have 0 operations"
        assert nonexistent_stats['success_rate'] == 0.0, "Non-existent type should have 0% success rate"
        
        # Test that metrics persist across multiple queries
        overall_stats_2 = collector.get_operation_stats()
        assert overall_stats_2 == overall_stats, "Statistics should be consistent across multiple queries"