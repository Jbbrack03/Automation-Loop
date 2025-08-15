#!/usr/bin/env python3
"""Validate that refactored calculate_wait_time maintains expected behavior."""

import sys
import os
import time
from unittest.mock import patch

# Add project directory to path
sys.path.insert(0, '/Users/jbbrack03/Claude_Development_Loop')

try:
    from automate_dev import calculate_wait_time, MIN_WAIT_TIME
    print(f"Successfully imported calculate_wait_time and MIN_WAIT_TIME = {MIN_WAIT_TIME}")
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

def test_basic_functionality():
    """Test that the basic functionality still works as expected."""
    print("\n=== Testing Basic Functionality ===")
    
    # Mock time values from the original test
    mock_current_time = 1736950000
    parsed_reset_info = {
        "reset_at": 1736957200,  # 2 hours after current time
        "format": "unix_timestamp"
    }
    expected_wait_seconds = 7200
    
    with patch('time.time') as mock_time:
        mock_time.return_value = mock_current_time
        result = calculate_wait_time(parsed_reset_info)
    
    print(f"Expected: {expected_wait_seconds}, Got: {result}")
    assert result == expected_wait_seconds, f"Expected {expected_wait_seconds}, got {result}"
    print("✓ Basic functionality test passed")

def test_past_reset_time():
    """Test that past reset times return MIN_WAIT_TIME."""
    print("\n=== Testing Past Reset Time ===")
    
    mock_current_time = 1736950000
    past_reset_info = {
        "reset_at": mock_current_time - 3600,  # 1 hour ago
        "format": "unix_timestamp"
    }
    
    with patch('time.time') as mock_time:
        mock_time.return_value = mock_current_time
        result = calculate_wait_time(past_reset_info)
    
    print(f"Expected: {MIN_WAIT_TIME}, Got: {result}")
    assert result == MIN_WAIT_TIME, f"Expected {MIN_WAIT_TIME}, got {result}"
    assert result >= 0, f"Result should be non-negative, got {result}"
    print("✓ Past reset time test passed")

def test_validation():
    """Test new validation functionality."""
    print("\n=== Testing Validation ===")
    
    # Test invalid input type
    try:
        calculate_wait_time("not a dict")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"✓ Correctly caught invalid input type: {e}")
    
    # Test missing reset_at key
    try:
        calculate_wait_time({"format": "unix_timestamp"})
        assert False, "Should have raised KeyError"
    except KeyError as e:
        print(f"✓ Correctly caught missing reset_at key: {e}")
    
    # Test invalid reset_at type
    try:
        calculate_wait_time({"reset_at": "not a number", "format": "unix_timestamp"})
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"✓ Correctly caught invalid reset_at type: {e}")

if __name__ == "__main__":
    try:
        test_basic_functionality()
        test_past_reset_time()
        test_validation()
        print("\n🎉 All refactoring validation tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)