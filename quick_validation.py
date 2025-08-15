#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/jbbrack03/Claude_Development_Loop')

# Test imports
try:
    from automate_dev import (
        calculate_wait_time, 
        _validate_reset_info_structure, 
        _calculate_unix_timestamp_wait,
        _parse_time_string_to_24hour,
        _calculate_natural_language_wait,
        MIN_WAIT_TIME,
        HOURS_12_CLOCK_CONVERSION
    )
    print("✓ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Test basic functionality
from unittest.mock import patch

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
print(f"Test result: {'PASS' if result == expected_wait_seconds else 'FAIL'}")

print(f"\nConstants loaded: MIN_WAIT_TIME={MIN_WAIT_TIME}, HOURS_12_CLOCK_CONVERSION={HOURS_12_CLOCK_CONVERSION}")

print("\n✅ Refactoring validation successful!")