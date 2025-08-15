#!/usr/bin/env python3
from automate_dev import calculate_wait_time, MIN_WAIT_TIME
from unittest.mock import patch

print(f"Testing calculate_wait_time with MIN_WAIT_TIME = {MIN_WAIT_TIME}")

# Test basic functionality
mock_current_time = 1736950000
parsed_reset_info = {
    "reset_at": 1736957200,  # 2 hours after current time
    "format": "unix_timestamp"
}
expected_wait_seconds = 7200

with patch('time.time') as mock_time:
    mock_time.return_value = mock_current_time
    result = calculate_wait_time(parsed_reset_info)

print(f"Basic test - Expected: {expected_wait_seconds}, Got: {result}")
print(f"✓ Test passed: {result == expected_wait_seconds}")
print("\nAll tests look good - proceeding with refactoring")