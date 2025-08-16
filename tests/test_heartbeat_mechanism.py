"""
Tests for heartbeat mechanism implementation.

This file contains TDD tests for the heartbeat mechanism that tracks long-running operations.
Following the red-green-refactor cycle, these tests are written before implementation.

The heartbeat mechanism should implement:
- HeartbeatTracker class to manage operation heartbeats
- start_heartbeat method to begin tracking an operation
- update_heartbeat method to signal operation is still alive
- is_operation_alive method to check if operation is still running
- get_stale_operations method to find operations that haven't sent heartbeat recently
- Integration with the existing automate_dev.py orchestrator
"""

import pytest
import time
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock
from pathlib import Path


class TestHeartbeatMechanism:
    """Test suite for the heartbeat mechanism functionality."""
    
    def test_heartbeat_tracker_lifecycle_with_stale_detection(self, tmp_path, monkeypatch):
        """
        Test complete heartbeat tracker lifecycle: start tracking, update heartbeat, and detect stale operations.
        
        Given a HeartbeatTracker instance,
        when an operation starts heartbeat tracking with a timeout,
        then the operation should be trackable as alive,
        and when the timeout expires without updates, it should be detected as stale,
        but when heartbeat is updated before timeout, it should remain alive.
        
        This comprehensive test validates the core heartbeat mechanism functionality
        needed for monitoring long-running operations in the automated development workflow.
        
        This test will initially fail because the HeartbeatTracker class doesn't exist yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Change to temporary directory to isolate test
        monkeypatch.chdir(tmp_path)
        
        # Import HeartbeatTracker class to test
        try:
            from heartbeat_tracker import HeartbeatTracker
        except ImportError:
            pytest.fail("Cannot import HeartbeatTracker from heartbeat_tracker.py - file doesn't exist yet")
        
        # Initialize heartbeat tracker
        tracker = HeartbeatTracker()
        
        # Define operation parameters
        operation_id = "test_operation_001"
        timeout_seconds = 0.2  # 200ms timeout for fast test execution
        
        # PHASE 1: Start heartbeat tracking
        result = tracker.start_heartbeat(operation_id, timeout_seconds)
        
        # Verify heartbeat tracking was started successfully
        assert result is True, "start_heartbeat should return True when successfully starting tracking"
        
        # Verify operation is considered alive immediately after starting
        is_alive = tracker.is_operation_alive(operation_id)
        assert is_alive is True, f"Operation {operation_id} should be alive immediately after starting heartbeat"
        
        # Verify operation appears in active operations list
        active_operations = tracker.get_active_operations()
        assert operation_id in active_operations, f"Operation {operation_id} should appear in active operations list"
        
        # Verify operation has correct configuration and recent timestamp
        operation_info = tracker.get_operation_info(operation_id)
        assert operation_info is not None, f"Operation {operation_id} should have operation info available"
        assert operation_info['timeout_seconds'] == timeout_seconds, "Operation should have correct timeout configured"
        assert 'last_heartbeat' in operation_info, "Operation info should include last_heartbeat timestamp"
        assert 'started_at' in operation_info, "Operation info should include started_at timestamp"
        
        # PHASE 2: Update heartbeat to keep operation alive
        time.sleep(timeout_seconds / 2)  # Wait partway through timeout period
        
        update_result = tracker.update_heartbeat(operation_id)
        assert update_result is True, "update_heartbeat should return True for active operation"
        
        # Verify operation is still alive after heartbeat update
        is_alive = tracker.is_operation_alive(operation_id)
        assert is_alive is True, f"Operation {operation_id} should still be alive after heartbeat update"
        
        # PHASE 3: Let operation become stale by not updating heartbeat
        time.sleep(timeout_seconds + 0.05)  # Wait past timeout without updating
        
        # Verify operation is now considered stale/dead
        is_alive = tracker.is_operation_alive(operation_id)
        assert is_alive is False, f"Operation {operation_id} should be dead after timeout expires"
        
        # Verify operation appears in stale operations list with timing details
        stale_operations = tracker.get_stale_operations()
        assert operation_id in stale_operations, f"Operation {operation_id} should appear in stale operations list"
        
        stale_info = stale_operations[operation_id]
        assert 'last_heartbeat' in stale_info, "Stale operation info should include last_heartbeat"
        assert 'timeout_seconds' in stale_info, "Stale operation info should include timeout_seconds"
        assert 'time_since_heartbeat' in stale_info, "Stale operation info should include time_since_heartbeat"
        assert stale_info['time_since_heartbeat'] > timeout_seconds, "time_since_heartbeat should exceed timeout"