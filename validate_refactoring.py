#!/usr/bin/env python3
"""Validate that the refactored parse_usage_limit_error function works correctly."""

import sys
import os

# Add current directory to path to import from automate_dev
sys.path.insert(0, '/Users/jbbrack03/Claude_Development_Loop')

def test_refactored_function():
    """Test the refactored parse_usage_limit_error function."""
    try:
        from automate_dev import parse_usage_limit_error
        
        print("Testing refactored parse_usage_limit_error function...")
        
        # Test 1: Natural language format
        natural_msg = "You can try again at 7pm (America/Chicago)."
        result1 = parse_usage_limit_error(natural_msg)
        expected1 = {'reset_time': '7pm', 'timezone': 'America/Chicago', 'format': 'natural_language'}
        assert result1 == expected1, f"Natural language test failed. Expected: {expected1}, Got: {result1}"
        print("✓ Natural language format test passed")
        
        # Test 2: JSON format
        json_msg = '{"reset_at": 1737000000}'
        result2 = parse_usage_limit_error(json_msg)
        expected2 = {'reset_at': 1737000000, 'format': 'unix_timestamp'}
        assert result2 == expected2, f"JSON format test failed. Expected: {expected2}, Got: {result2}"
        print("✓ JSON format test passed")
        
        # Test 3: No match case
        no_match_msg = "Some other error message"
        result3 = parse_usage_limit_error(no_match_msg)
        expected3 = {'reset_time': '', 'timezone': '', 'format': 'natural_language'}
        assert result3 == expected3, f"No match test failed. Expected: {expected3}, Got: {result3}"
        print("✓ No match case test passed")
        
        # Test 4: Empty/invalid input
        result4 = parse_usage_limit_error("")
        expected4 = {'reset_time': '', 'timezone': '', 'format': 'natural_language'}
        assert result4 == expected4, f"Empty input test failed. Expected: {expected4}, Got: {result4}"
        print("✓ Empty input test passed")
        
        print("\n🎉 ALL REFACTORING TESTS PASSED!")
        print("The refactored parse_usage_limit_error function maintains all expected behavior.")
        return True
        
    except Exception as e:
        print(f"❌ Refactoring validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_refactored_function()
    if not success:
        sys.exit(1)