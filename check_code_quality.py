#!/usr/bin/env python3
"""Check code quality after refactoring."""
import ast
import sys
sys.path.insert(0, '/Users/jbbrack03/Claude_Development_Loop')

def check_syntax():
    """Check that the refactored code has valid Python syntax."""
    try:
        with open('/Users/jbbrack03/Claude_Development_Loop/automate_dev.py', 'r') as f:
            code = f.read()
        
        # Parse the AST to check syntax
        ast.parse(code)
        print("✓ Syntax check passed")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error checking syntax: {e}")
        return False

def check_imports():
    """Check that all imports work correctly."""
    try:
        from automate_dev import (
            calculate_wait_time,
            _validate_reset_info_structure,
            _calculate_unix_timestamp_wait,
            _parse_time_string_to_24hour,
            _calculate_natural_language_wait,
            MIN_WAIT_TIME,
            HOURS_12_CLOCK_CONVERSION,
            MIDNIGHT_HOUR_12_FORMAT,
            NOON_HOUR_12_FORMAT
        )
        print("✓ All refactored imports work correctly")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def check_function_signatures():
    """Check that function signatures are correct."""
    try:
        from automate_dev import (
            calculate_wait_time,
            _validate_reset_info_structure,
            _calculate_unix_timestamp_wait,
            _parse_time_string_to_24hour,
            _calculate_natural_language_wait
        )
        import inspect
        
        # Check main function signature
        sig = inspect.signature(calculate_wait_time)
        params = list(sig.parameters.keys())
        expected_params = ['parsed_reset_info']
        assert params == expected_params, f"Expected {expected_params}, got {params}"
        
        # Check return type annotation
        return_annotation = sig.return_annotation
        assert return_annotation == int, f"Expected int return type, got {return_annotation}"
        
        print("✓ Function signatures are correct")
        return True
    except Exception as e:
        print(f"❌ Function signature error: {e}")
        return False

if __name__ == "__main__":
    print("Checking code quality after refactoring...")
    print("="*50)
    
    checks = [
        ("Syntax", check_syntax),
        ("Imports", check_imports),
        ("Function Signatures", check_function_signatures)
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"\nChecking {name}:")
        if not check_func():
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("✅ All code quality checks passed!")
    else:
        print("❌ Some code quality checks failed!")
        sys.exit(1)