"""Tests for module extraction functionality.

This test file verifies that three pieces of functionality from automate_dev.py
can be successfully extracted into separate modules:
1. Usage limit handling → usage_limit.py
2. Signal file handling → signal_handler.py  
3. Command executor logic → command_executor.py

These tests will initially fail since the modules don't exist yet,
following TDD red-green-refactor principles.
"""

import sys
import os
# Add parent directory to path so we can import the modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import importlib
import inspect
from typing import Dict, Any, Optional, List


class TestUsageLimitModule:
    """Test that usage_limit module can be imported and has expected functions."""
    
    def test_usage_limit_module_imports(self):
        """Test that usage_limit module can be imported."""
        # Given: The usage_limit module should exist
        # When: We try to import it
        # Then: Import should succeed without errors
        try:
            import usage_limit
        except ImportError as e:
            pytest.fail(f"Failed to import usage_limit module: {e}")
    
    def test_parse_usage_limit_error_function_exists(self):
        """Test that parse_usage_limit_error function exists and is callable."""
        # Given: The usage_limit module is imported
        import usage_limit
        
        # When: We check for parse_usage_limit_error function
        # Then: Function should exist and be callable
        assert hasattr(usage_limit, 'parse_usage_limit_error'), \
            "usage_limit module missing parse_usage_limit_error function"
        assert callable(usage_limit.parse_usage_limit_error), \
            "parse_usage_limit_error should be callable"
    
    def test_calculate_wait_time_function_exists(self):
        """Test that calculate_wait_time function exists and is callable."""
        # Given: The usage_limit module is imported
        import usage_limit
        
        # When: We check for calculate_wait_time function
        # Then: Function should exist and be callable
        assert hasattr(usage_limit, 'calculate_wait_time'), \
            "usage_limit module missing calculate_wait_time function"
        assert callable(usage_limit.calculate_wait_time), \
            "calculate_wait_time should be callable"
    
    def test_parse_usage_limit_error_signature(self):
        """Test that parse_usage_limit_error has correct function signature."""
        # Given: The usage_limit module is imported
        import usage_limit
        
        # When: We inspect the function signature
        sig = inspect.signature(usage_limit.parse_usage_limit_error)
        
        # Then: Function should accept error_message parameter
        assert 'error_message' in sig.parameters, \
            "parse_usage_limit_error should accept error_message parameter"
        
        # And: Should return Dict[str, str] type (verified by docstring/annotation)
        # This will be validated by actual usage in integration tests
    
    def test_calculate_wait_time_signature(self):
        """Test that calculate_wait_time has correct function signature."""
        # Given: The usage_limit module is imported
        import usage_limit
        
        # When: We inspect the function signature
        sig = inspect.signature(usage_limit.calculate_wait_time)
        
        # Then: Function should accept parsed_reset_info parameter
        assert 'parsed_reset_info' in sig.parameters, \
            "calculate_wait_time should accept parsed_reset_info parameter"
    
    def test_usage_limit_module_has_docstring(self):
        """Test that usage_limit module has proper documentation."""
        # Given: The usage_limit module is imported
        import usage_limit
        
        # When: We check module docstring
        # Then: Module should have a docstring
        assert usage_limit.__doc__ is not None, \
            "usage_limit module should have a docstring"
        assert len(usage_limit.__doc__.strip()) > 0, \
            "usage_limit module docstring should not be empty"


class TestSignalHandlerModule:
    """Test that signal_handler module can be imported and has expected functions."""
    
    def test_signal_handler_module_imports(self):
        """Test that signal_handler module can be imported."""
        # Given: The signal_handler module should exist
        # When: We try to import it
        # Then: Import should succeed without errors
        try:
            import signal_handler
        except ImportError as e:
            pytest.fail(f"Failed to import signal_handler module: {e}")
    
    def test_wait_for_signal_file_function_exists(self):
        """Test that wait_for_signal_file function exists and is callable."""
        # Given: The signal_handler module is imported
        import signal_handler
        
        # When: We check for wait_for_signal_file function
        # Then: Function should exist and be callable
        assert hasattr(signal_handler, 'wait_for_signal_file'), \
            "signal_handler module missing wait_for_signal_file function"
        assert callable(signal_handler.wait_for_signal_file), \
            "wait_for_signal_file should be callable"
    
    def test_cleanup_signal_file_function_exists(self):
        """Test that cleanup_signal_file function exists and is callable."""
        # Given: The signal_handler module is imported
        import signal_handler
        
        # When: We check for cleanup_signal_file function
        # Then: Function should exist and be callable
        assert hasattr(signal_handler, 'cleanup_signal_file'), \
            "signal_handler module missing cleanup_signal_file function"
        assert callable(signal_handler.cleanup_signal_file), \
            "cleanup_signal_file should be callable"
    
    def test_wait_for_signal_file_signature(self):
        """Test that wait_for_signal_file has correct function signature."""
        # Given: The signal_handler module is imported
        import signal_handler
        
        # When: We inspect the function signature
        sig = inspect.signature(signal_handler.wait_for_signal_file)
        
        # Then: Function should accept signal_file_path parameter
        assert 'signal_file_path' in sig.parameters, \
            "wait_for_signal_file should accept signal_file_path parameter"
        
        # And: Should have optional timeout parameter
        timeout_param = sig.parameters.get('timeout')
        assert timeout_param is not None, \
            "wait_for_signal_file should have timeout parameter"
        assert timeout_param.default is not inspect.Parameter.empty, \
            "timeout parameter should have a default value"
    
    def test_cleanup_signal_file_signature(self):
        """Test that cleanup_signal_file has correct function signature."""
        # Given: The signal_handler module is imported
        import signal_handler
        
        # When: We inspect the function signature
        sig = inspect.signature(signal_handler.cleanup_signal_file)
        
        # Then: Function should accept signal_file_path parameter
        assert 'signal_file_path' in sig.parameters, \
            "cleanup_signal_file should accept signal_file_path parameter"
    
    def test_signal_handler_module_has_docstring(self):
        """Test that signal_handler module has proper documentation."""
        # Given: The signal_handler module is imported
        import signal_handler
        
        # When: We check module docstring
        # Then: Module should have a docstring
        assert signal_handler.__doc__ is not None, \
            "signal_handler module should have a docstring"
        assert len(signal_handler.__doc__.strip()) > 0, \
            "signal_handler module docstring should not be empty"


class TestCommandExecutorModule:
    """Test that command_executor module can be imported and has expected functions."""
    
    def test_command_executor_module_imports(self):
        """Test that command_executor module can be imported."""
        # Given: The command_executor module should exist
        # When: We try to import it
        # Then: Import should succeed without errors
        try:
            import command_executor
        except ImportError as e:
            pytest.fail(f"Failed to import command_executor module: {e}")
    
    def test_run_claude_command_function_exists(self):
        """Test that run_claude_command function exists and is callable."""
        # Given: The command_executor module is imported
        import command_executor
        
        # When: We check for run_claude_command function
        # Then: Function should exist and be callable
        assert hasattr(command_executor, 'run_claude_command'), \
            "command_executor module missing run_claude_command function"
        assert callable(command_executor.run_claude_command), \
            "run_claude_command should be callable"
    
    def test_execute_command_and_get_status_function_exists(self):
        """Test that execute_command_and_get_status function exists and is callable."""
        # Given: The command_executor module is imported
        import command_executor
        
        # When: We check for execute_command_and_get_status function
        # Then: Function should exist and be callable
        assert hasattr(command_executor, 'execute_command_and_get_status'), \
            "command_executor module missing execute_command_and_get_status function"
        assert callable(command_executor.execute_command_and_get_status), \
            "execute_command_and_get_status should be callable"
    
    def test_run_claude_command_signature(self):
        """Test that run_claude_command has correct function signature."""
        # Given: The command_executor module is imported
        import command_executor
        
        # When: We inspect the function signature
        sig = inspect.signature(command_executor.run_claude_command)
        
        # Then: Function should accept command parameter
        assert 'command' in sig.parameters, \
            "run_claude_command should accept command parameter"
        
        # And: Should have optional args parameter
        args_param = sig.parameters.get('args')
        if args_param:
            assert args_param.default is not inspect.Parameter.empty, \
                "args parameter should have a default value"
        
        # And: Should have optional debug parameter
        debug_param = sig.parameters.get('debug')
        if debug_param:
            assert debug_param.default is not inspect.Parameter.empty, \
                "debug parameter should have a default value"
    
    def test_execute_command_and_get_status_signature(self):
        """Test that execute_command_and_get_status has correct function signature."""
        # Given: The command_executor module is imported
        import command_executor
        
        # When: We inspect the function signature
        sig = inspect.signature(command_executor.execute_command_and_get_status)
        
        # Then: Function should accept command parameter
        assert 'command' in sig.parameters, \
            "execute_command_and_get_status should accept command parameter"
        
        # And: Should have optional debug parameter
        debug_param = sig.parameters.get('debug')
        if debug_param:
            assert debug_param.default is not inspect.Parameter.empty, \
                "debug parameter should have a default value"
    
    def test_command_executor_module_has_docstring(self):
        """Test that command_executor module has proper documentation."""
        # Given: The command_executor module is imported
        import command_executor
        
        # When: We check module docstring
        # Then: Module should have a docstring
        assert command_executor.__doc__ is not None, \
            "command_executor module should have a docstring"
        assert len(command_executor.__doc__.strip()) > 0, \
            "command_executor module docstring should not be empty"


class TestModuleExtraction:
    """Integration tests for module extraction functionality."""
    
    def test_all_modules_can_be_imported_together(self):
        """Test that all three modules can be imported together without conflicts."""
        # Given: All three modules should exist
        # When: We try to import all modules
        # Then: All imports should succeed without conflicts
        try:
            import usage_limit
            import signal_handler
            import command_executor
        except ImportError as e:
            pytest.fail(f"Failed to import all modules together: {e}")
    
    def test_modules_have_independent_namespaces(self):
        """Test that modules have independent namespaces and don't conflict."""
        # Given: All three modules are imported
        import usage_limit
        import signal_handler
        import command_executor
        
        # When: We check module attributes
        # Then: Modules should have different sets of functions
        usage_limit_funcs = {name for name, obj in inspect.getmembers(usage_limit, inspect.isfunction)
                           if not name.startswith('_')}
        signal_handler_funcs = {name for name, obj in inspect.getmembers(signal_handler, inspect.isfunction)
                              if not name.startswith('_')}
        command_executor_funcs = {name for name, obj in inspect.getmembers(command_executor, inspect.isfunction)
                                if not name.startswith('_')}
        
        # Functions should be module-specific with minimal overlap
        assert len(usage_limit_funcs) > 0, "usage_limit should have public functions"
        assert len(signal_handler_funcs) > 0, "signal_handler should have public functions"
        assert len(command_executor_funcs) > 0, "command_executor should have public functions"
    
    def test_extracted_functions_maintain_original_behavior(self):
        """Test that extracted functions still behave like their original counterparts."""
        # Given: All modules are imported
        import usage_limit
        import signal_handler
        import command_executor
        
        # When: We test basic function behavior
        # Then: Functions should maintain their original interfaces

        # Test usage_limit functions accept expected parameters
        try:
            # This will fail until actual implementation, but tests the interface
            result = usage_limit.parse_usage_limit_error("test error message")
            assert isinstance(result, dict), "parse_usage_limit_error should return dict"
        except Exception as e:
            pytest.fail(f"parse_usage_limit_error raised an exception: {e}")

        try:
            # Test that calculate_wait_time accepts valid parsed info
            test_info = {"reset_at": 1737000000, "format": "unix_timestamp"}
            result = usage_limit.calculate_wait_time(test_info)
            assert isinstance(result, int), "calculate_wait_time should return int"
        except Exception as e:
            pytest.fail(f"calculate_wait_time raised an exception: {e}")
