#!/usr/bin/env python3
"""Test backward compatibility of refactored get_latest_status function."""

import tempfile
import json
import os
import sys

def test_backward_compatibility():
    """Test that all existing calling patterns still work."""
    
    # Import the refactored function
    sys.path.insert(0, '/Users/jbbrack03/Claude_Development_Loop')
    from automate_dev import get_latest_status
    
    # Save current directory
    original_dir = os.getcwd()
    
    try:
        # Create temporary directory and change to it
        with tempfile.TemporaryDirectory() as tmp_dir:
            os.chdir(tmp_dir)
            
            # Create .claude directory
            claude_dir = os.path.join(tmp_dir, '.claude')
            os.makedirs(claude_dir)
            
            # Test: Existing calling pattern without parameters
            result = get_latest_status()  # This is how it's called in the actual code
            assert result is None, f"Expected None, got {result}"
            print("✓ Backward compatibility: get_latest_status() works without parameters")
            
            # Test: Create status files and verify functionality
            status_data = {'status': 'test_status', 'details': 'test details'}
            filepath = os.path.join(claude_dir, 'status_20240101_120000.json')
            with open(filepath, 'w') as f:
                json.dump(status_data, f)
            
            # Test existing calling pattern
            result = get_latest_status()
            assert result == 'test_status', f"Expected 'test_status', got {result}"
            print("✓ Backward compatibility: Returns correct status value")
            
            # Verify files are cleaned up
            remaining_files = [f for f in os.listdir(claude_dir) if f.startswith('status_')]
            assert len(remaining_files) == 0, f"Expected no files remaining, found {remaining_files}"
            print("✓ Backward compatibility: File cleanup still works")
            
            print("\n✅ All backward compatibility tests passed!")
            return True
            
    except Exception as e:
        print(f"❌ Backward compatibility test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        os.chdir(original_dir)

if __name__ == "__main__":
    success = test_backward_compatibility()
    if success:
        print("\n🎉 Refactoring successful - all existing code will continue working!")
    else:
        print("\n❌ Refactoring broke backward compatibility!")
    sys.exit(0 if success else 1)