"""
Tests for signal file handling efficiency improvements.

This test file verifies that signal_handler implements exponential backoff
for wait_for_signal_file to reduce CPU usage during long waits.

Phase 13, Task 13.2: Improve signal file handling efficiency with exponential backoff.
"""

import sys
import os
import time
import logging
from unittest.mock import patch, Mock, call
from pathlib import Path

# Add parent directory to path so we can import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from signal_handler import wait_for_signal_file
from config import LOGGERS


class TestSignalHandlingEfficiency:
    """Test suite for signal file handling efficiency improvements."""
    
    def setup_method(self):
        """Set up mock logger for each test method."""
        # Store original logger state for cleanup
        self.original_logger = LOGGERS.get('command_executor')
        # Mock the logger to avoid AttributeError on None
        mock_logger = Mock()
        LOGGERS['command_executor'] = mock_logger
    
    def teardown_method(self):
        """Clean up after each test method."""
        # Restore original logger state
        LOGGERS['command_executor'] = self.original_logger
    
    def test_wait_for_signal_file_uses_exponential_backoff(self, tmp_path, monkeypatch):
        """
        Test that wait_for_signal_file implements exponential backoff for efficient polling.
        
        This test verifies the efficiency optimization for Task 13.2:
        1. Initial polling starts with a minimum interval (e.g., 0.1 seconds)
        2. Wait interval increases exponentially up to a maximum (e.g., 2.0 seconds)
        3. Total number of file system checks is reduced compared to fixed-interval polling
        4. The function accepts min_interval and max_interval parameters for backoff configuration
        
        This test follows the FIRST principles:
        - Fast: Uses mocking to avoid actual file system delays
        - Independent: Creates isolated test environment with controlled timing
        - Repeatable: Deterministic timing control through mocked time.sleep
        - Self-validating: Clear assertions on sleep intervals and call patterns
        - Timely: Written before exponential backoff implementation exists (red phase of TDD)
        
        The test will fail initially because wait_for_signal_file currently uses
        a fixed sleep interval without any exponential backoff mechanism.
        """
        # Change to temporary directory
        monkeypatch.chdir(tmp_path)
        
        # Create test signal file path (file does not exist initially)
        signal_file_path = tmp_path / "test_signal_file"
        
        # Track sleep calls to verify exponential backoff pattern
        sleep_calls = []
        file_exists_calls = []
        
        def mock_sleep(duration):
            """Mock sleep function that records the sleep duration."""
            sleep_calls.append(duration)
        
        def mock_exists(path):
            """Mock os.path.exists that records calls and returns False to simulate waiting."""
            file_exists_calls.append(str(path))
            # Return False for the first few calls, then True to end the wait
            # This simulates a signal file that appears after several polling attempts
            return len(file_exists_calls) > 5
        
        def mock_remove(path):
            """Mock os.remove that does nothing but prevents errors."""
            pass
        
        # Mock time.time to provide controlled elapsed time calculation
        start_time = 1000.0
        time_calls = [start_time]  # First call returns start time
        
        def mock_time():
            """Mock time.time that simulates passage of time based on sleep calls."""
            if len(time_calls) == 1:
                return start_time
            else:
                # Calculate elapsed time based on accumulated sleep durations
                elapsed = sum(sleep_calls)
                return start_time + elapsed
        
        with patch('time.sleep', side_effect=mock_sleep), \
             patch('os.path.exists', side_effect=mock_exists), \
             patch('os.remove', side_effect=mock_remove), \
             patch('time.time', side_effect=mock_time):
            
            # Call wait_for_signal_file with exponential backoff parameters
            # This should use new parameters: min_interval=0.1, max_interval=2.0
            wait_for_signal_file(
                signal_file_path,
                timeout=30.0,
                min_interval=0.1,  # Start with 0.1 second intervals
                max_interval=2.0,  # Cap at 2.0 second intervals
                debug=True
            )
        
        # Verify that sleep was called multiple times (polling occurred)
        assert len(sleep_calls) > 0, "wait_for_signal_file should have polled multiple times"
        assert len(sleep_calls) >= 3, f"Expected at least 3 polling attempts for exponential backoff, got {len(sleep_calls)}"
        
        # Verify exponential backoff pattern
        # First interval should be the minimum (0.1 seconds)
        assert sleep_calls[0] == 0.1, f"First sleep interval should be min_interval (0.1), but was {sleep_calls[0]}"
        
        # Second interval should be larger (exponential increase)
        if len(sleep_calls) > 1:
            assert sleep_calls[1] > sleep_calls[0], f"Second interval ({sleep_calls[1]}) should be larger than first ({sleep_calls[0]})"
            assert sleep_calls[1] <= 2.0, f"Second interval ({sleep_calls[1]}) should not exceed max_interval (2.0)"
        
        # Third interval should be larger still, but capped at max_interval
        if len(sleep_calls) > 2:
            assert sleep_calls[2] >= sleep_calls[1], f"Third interval ({sleep_calls[2]}) should be >= second ({sleep_calls[1]})"
            assert sleep_calls[2] <= 2.0, f"Third interval ({sleep_calls[2]}) should not exceed max_interval (2.0)"
        
        # Verify that intervals eventually reach the maximum and stay there
        max_intervals_reached = [interval for interval in sleep_calls if interval == 2.0]
        assert len(max_intervals_reached) > 0, f"Expected some intervals to reach max_interval (2.0), but got intervals: {sleep_calls}"
        
        # Verify exponential progression before hitting the cap
        exponential_intervals = []
        for i, interval in enumerate(sleep_calls):
            if interval < 2.0:  # Before hitting the cap
                exponential_intervals.append(interval)
        
        # Check that early intervals follow exponential pattern (each roughly double the previous)
        if len(exponential_intervals) >= 2:
            for i in range(1, len(exponential_intervals)):
                ratio = exponential_intervals[i] / exponential_intervals[i-1]
                assert 1.8 <= ratio <= 2.2, f"Exponential backoff ratio should be ~2.0, but interval {i} ratio was {ratio:.2f} (intervals: {exponential_intervals})"
        
        # Verify efficiency: with exponential backoff, we should have fewer total file checks
        # compared to fixed interval polling for the same time period
        total_sleep_time = sum(sleep_calls)
        expected_fixed_interval_checks = int(total_sleep_time / 0.1) + 1  # +1 for initial check
        actual_checks = len(file_exists_calls)
        
        # Exponential backoff should result in fewer file system checks
        efficiency_improvement = (expected_fixed_interval_checks - actual_checks) / expected_fixed_interval_checks
        assert efficiency_improvement > 0.2, (
            f"Exponential backoff should reduce file system checks by at least 20%. "
            f"Expected ~{expected_fixed_interval_checks} checks with fixed interval (0.1s), "
            f"but got {actual_checks} checks with exponential backoff. "
            f"Efficiency improvement: {efficiency_improvement:.1%}. "
            f"Sleep intervals used: {sleep_calls}"
        )
        
        # Summary assertion for the complete exponential backoff behavior
        # This test will fail initially because current wait_for_signal_file implementation
        # uses a fixed sleep interval without exponential backoff parameters
        assert hasattr(wait_for_signal_file, '__code__'), "wait_for_signal_file should be a function"
        
        # Check if the function signature includes the new parameters
        function_params = wait_for_signal_file.__code__.co_varnames
        missing_params = []
        for required_param in ['min_interval', 'max_interval']:
            if required_param not in function_params:
                missing_params.append(required_param)
        
        assert len(missing_params) == 0, (
            f"wait_for_signal_file function signature should include exponential backoff parameters: {missing_params}. "
            f"Current parameters: {list(function_params)}. "
            f"Expected parameters: signal_file_path, timeout, min_interval, max_interval, debug. "
            f"This indicates that exponential backoff has not been implemented yet."
        )