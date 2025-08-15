#!/usr/bin/env python3
"""Test the refactored calculate_wait_time function to ensure it still works."""
import sys
sys.path.insert(0, '/Users/jbbrack03/Claude_Development_Loop')

from unittest.mock import patch
from automate_dev import calculate_wait_time, MIN_WAIT_TIME

def test_refactored_function():
    """Test that refactored function maintains same behavior."""
    print(f"Testing refactored calculate_wait_time with MIN_WAIT_TIME = {MIN_WAIT_TIME}")
    
    # Test 1: Basic Unix timestamp functionality
    mock_current_time = 1736950000
    parsed_reset_info = {
        "reset_at": 1736957200,  # 2 hours after current time
        "format": "unix_timestamp"
    }
    expected_wait_seconds = 7200
    
    with patch('time.time') as mock_time:
        mock_time.return_value = mock_current_time
        result = calculate_wait_time(parsed_reset_info)
    
    print(f"Test 1 - Expected: {expected_wait_seconds}, Got: {result}")
    assert result == expected_wait_seconds, f"Expected {expected_wait_seconds}, got {result}"
    print("✓ Test 1 passed: Basic Unix timestamp functionality")
    
    # Test 2: Past reset time should return MIN_WAIT_TIME
    past_reset_info = {
        "reset_at": mock_current_time - 3600,  # 1 hour ago
        "format": "unix_timestamp"
    }
    
    with patch('time.time') as mock_time:
        mock_time.return_value = mock_current_time
        result = calculate_wait_time(past_reset_info)
    
    print(f"Test 2 - Expected: {MIN_WAIT_TIME}, Got: {result}")
    assert result == MIN_WAIT_TIME, f"Expected {MIN_WAIT_TIME}, got {result}"
    print("✓ Test 2 passed: Past reset time returns MIN_WAIT_TIME")
    
    # Test 3: Validation - invalid input type
    try:
        calculate_wait_time("not a dict")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"✓ Test 3 passed: Correctly caught invalid input type: {e}")
    
    # Test 4: Validation - missing reset_at key
    try:
        calculate_wait_time({"format": "unix_timestamp"})
        assert False, "Should have raised KeyError"
    except KeyError as e:
        print(f"✓ Test 4 passed: Correctly caught missing reset_at key: {e}")
    
    # Test 5: Validation - invalid reset_at type
    try:
        calculate_wait_time({"reset_at": "not a number", "format": "unix_timestamp"})
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"✓ Test 5 passed: Correctly caught invalid reset_at type: {e}")
    
    # Test 6: Unsupported format type
    try:
        calculate_wait_time({"format": "unsupported_format"})
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"✓ Test 6 passed: Correctly caught unsupported format: {e}")
    
    # Test 7: Test helper function _parse_time_string_to_24hour
    from automate_dev import _parse_time_string_to_24hour
    
    test_cases = [
        ("7pm", 19),
        ("7am", 7),
        ("12pm", 12),  # noon
        ("12am", 0),   # midnight
        ("19", 19),    # 24-hour format
    ]
    
    for time_str, expected_hour in test_cases:
        result_hour = _parse_time_string_to_24hour(time_str)
        print(f"✓ Time parsing: '{time_str}' -> {result_hour} (expected {expected_hour})") 
        assert result_hour == expected_hour, f"Expected {expected_hour}, got {result_hour}"
    
    print("\n🎉 All refactoring tests passed! Function behavior is preserved.")

if __name__ == "__main__":
    try:
        test_refactored_function()
        print("\n✅ Refactoring successful - all tests green!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)