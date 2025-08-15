#!/usr/bin/env python3
"""Quick test to verify our refactoring is working correctly."""

import sys
import os

# Add the project directory to Python path
sys.path.insert(0, '/Users/jbbrack03/Claude_Development_Loop')

def test_imports():
    """Test that we can import all the functions we refactored."""
    try:
        from automate_dev import (
            parse_usage_limit_error,
            _parse_json_error_format,
            _parse_natural_language_format,
            _create_usage_limit_result
        )
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_function_behavior():
    """Test that refactored functions maintain expected behavior."""
    try:
        from automate_dev import parse_usage_limit_error
        
        # Test cases
        test_cases = [
            # Natural language format
            ("You can try again at 7pm (America/Chicago).", 
             {'reset_time': '7pm', 'timezone': 'America/Chicago', 'format': 'natural_language'}),
            
            # JSON format  
            ('{"reset_at": 1737000000}',
             {'reset_at': 1737000000, 'format': 'unix_timestamp'}),
            
            # No match
            ("Some other error",
             {'reset_time': '', 'timezone': '', 'format': 'natural_language'}),
             
            # Empty input
            ("",
             {'reset_time': '', 'timezone': '', 'format': 'natural_language'})
        ]
        
        for i, (input_msg, expected) in enumerate(test_cases, 1):
            result = parse_usage_limit_error(input_msg)
            if result != expected:
                print(f"❌ Test case {i} failed:")
                print(f"   Input: {repr(input_msg)}")
                print(f"   Expected: {expected}")
                print(f"   Got: {result}")
                return False
            else:
                print(f"✓ Test case {i} passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Function test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("Running refactoring validation tests...")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        return False
    
    # Test function behavior
    if not test_function_behavior():
        return False
    
    print("=" * 50)
    print("🎉 ALL REFACTORING TESTS PASSED!")
    print("Refactoring completed successfully while maintaining all functionality.")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)