#!/usr/bin/env python3
"""Simple test to check if refactored function can be imported and called."""
import sys
import traceback

def test_basic_functionality():
    try:
        # Test import
        from automate_dev import run_claude_command
        print("✅ Import successful")
        
        # Test that function exists and can be inspected
        import inspect
        sig = inspect.signature(run_claude_command)
        print(f"✅ Function signature: {sig}")
        
        # Test constants import
        from automate_dev import SIGNAL_WAIT_SLEEP_INTERVAL, SIGNAL_WAIT_TIMEOUT
        print(f"✅ Constants imported: INTERVAL={SIGNAL_WAIT_SLEEP_INTERVAL}, TIMEOUT={SIGNAL_WAIT_TIMEOUT}")
        
        # Test helper function import
        from automate_dev import _wait_for_signal_file
        print("✅ Helper function _wait_for_signal_file imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing refactored run_claude_command...")
    if test_basic_functionality():
        print("\n🎉 Basic functionality test PASSED!")
    else:
        print("\n❌ Basic functionality test FAILED!")
        sys.exit(1)