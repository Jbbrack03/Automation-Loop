#!/usr/bin/env python3
"""Test after Step 3: Extract usage limit handling."""
import subprocess
import sys
import os

def main():
    os.chdir("/Users/jbbrack03/Claude_Development_Loop")
    
    print("Testing after Step 3: Extract usage limit handling...")
    print("=" * 60)
    
    result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], 
                          text=True)
    
    if result.returncode == 0:
        print("\n✅ Step 3 SUCCESSFUL - Usage limit extraction working correctly!")
        return True
    else:
        print("\n❌ Step 3 FAILED - Need to fix usage limit extraction")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
