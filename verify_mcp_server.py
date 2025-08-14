#!/usr/bin/env python3
"""Simple test to verify MCP server functionality before refactoring."""
import sys
import traceback
import tempfile
import json
from pathlib import Path

def test_mcp_server_basic():
    """Test basic MCP server functionality."""
    try:
        # Test import
        from status_mcp_server import StatusServer
        print("✅ StatusServer imported successfully")
        
        # Create instance
        server = StatusServer()
        print("✅ StatusServer instance created")
        
        # Check if report_status method exists
        if hasattr(server, 'report_status'):
            print("✅ report_status method exists")
        else:
            print("❌ report_status method missing")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        return False

def test_mcp_server_functionality():
    """Test actual functionality."""
    try:
        from status_mcp_server import StatusServer
        
        # Use temporary directory for test
        with tempfile.TemporaryDirectory() as tmp_dir:
            import os
            original_cwd = os.getcwd()
            os.chdir(tmp_dir)
            
            try:
                # Create server
                server = StatusServer()
                
                # Test report_status call
                result = server.report_status(
                    status="test_status",
                    details={"test": "value"},
                    task_description="Test task"
                )
                
                print("✅ report_status called successfully")
                
                # Check result structure
                if isinstance(result, dict) and result.get("success"):
                    print("✅ Result indicates success")
                else:
                    print(f"❌ Unexpected result: {result}")
                    return False
                    
                # Check if file was created
                claude_dir = Path(".claude")
                if claude_dir.exists():
                    status_files = list(claude_dir.glob("status_*.json"))
                    if status_files:
                        print(f"✅ Status file created: {status_files[0]}")
                    else:
                        print("❌ No status file created")
                        return False
                else:
                    print("❌ .claude directory not created")
                    return False
                    
                return True
                
            finally:
                os.chdir(original_cwd)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing MCP server before refactoring...")
    print("=" * 50)
    
    success = True
    
    print("\n1. Testing basic import and instantiation:")
    if not test_mcp_server_basic():
        success = False
    
    print("\n2. Testing functionality:")
    if not test_mcp_server_functionality():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All MCP server tests PASSED! Ready for refactoring.")
    else:
        print("❌ Some tests FAILED! Fix issues before refactoring.")
        sys.exit(1)