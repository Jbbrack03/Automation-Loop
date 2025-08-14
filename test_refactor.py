#!/usr/bin/env python3
"""Test script to verify run_claude_command refactoring."""
import sys
import os

# Add current directory to path
sys.path.insert(0, '.')

def test_imports():
    """Test that all imports work correctly."""
    try:
        from automate_dev import run_claude_command, _wait_for_signal_file
        from automate_dev import SIGNAL_WAIT_SLEEP_INTERVAL, SIGNAL_WAIT_TIMEOUT
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_function_signatures():
    """Test that function signatures are correct."""
    try:
        from automate_dev import run_claude_command, _wait_for_signal_file
        import inspect
        
        # Test run_claude_command signature
        sig = inspect.signature(run_claude_command)
        params = list(sig.parameters.keys())
        expected_params = ['command', 'args', 'debug']
        
        if params == expected_params:
            print("✅ run_claude_command signature correct")
        else:
            print(f"❌ run_claude_command signature incorrect: got {params}, expected {expected_params}")
            return False
            
        # Test _wait_for_signal_file signature
        sig = inspect.signature(_wait_for_signal_file)
        params = list(sig.parameters.keys())
        expected_params = ['signal_file_path', 'timeout', 'sleep_interval', 'debug']
        
        if params == expected_params:
            print("✅ _wait_for_signal_file signature correct")
        else:
            print(f"❌ _wait_for_signal_file signature incorrect: got {params}, expected {expected_params}")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Signature test failed: {e}")
        return False

def test_constants():
    """Test that constants are defined."""
    try:
        from automate_dev import SIGNAL_WAIT_SLEEP_INTERVAL, SIGNAL_WAIT_TIMEOUT
        
        if isinstance(SIGNAL_WAIT_SLEEP_INTERVAL, (int, float)) and SIGNAL_WAIT_SLEEP_INTERVAL > 0:
            print(f"✅ SIGNAL_WAIT_SLEEP_INTERVAL = {SIGNAL_WAIT_SLEEP_INTERVAL}")
        else:
            print(f"❌ SIGNAL_WAIT_SLEEP_INTERVAL invalid: {SIGNAL_WAIT_SLEEP_INTERVAL}")
            return False
            
        if isinstance(SIGNAL_WAIT_TIMEOUT, (int, float)) and SIGNAL_WAIT_TIMEOUT > 0:
            print(f"✅ SIGNAL_WAIT_TIMEOUT = {SIGNAL_WAIT_TIMEOUT}")
        else:
            print(f"❌ SIGNAL_WAIT_TIMEOUT invalid: {SIGNAL_WAIT_TIMEOUT}")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Constants test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing run_claude_command refactoring...")
    print("=" * 50)
    
    all_passed = True
    all_passed &= test_imports()
    all_passed &= test_function_signatures()
    all_passed &= test_constants()
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All refactoring tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)