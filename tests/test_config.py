"""
Tests for the config.py module containing organized constants.

This file contains TDD tests for the configuration module that centralizes
all constants extracted from automate_dev.py. Following the red-green-refactor 
cycle, this test is written before the config.py module exists.
"""

import pytest
import sys
import os
from pathlib import Path


class TestConfigModule:
    """Test suite for config.py module structure and constant organization."""
    
    def test_config_module_exists_and_contains_organized_constants(self):
        """
        Test that config.py module exists and contains all essential constants
        organized by category.
        
        This test verifies:
        1. The config.py module can be imported
        2. It contains essential constants organized into logical categories:
           - File path constants
           - Exit code constants  
           - Workflow control constants
           - Status constants
           - Command constants
        3. The constants can be imported and used
        4. The constants have expected values matching automate_dev.py
        
        This test will initially fail because config.py doesn't exist yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Test that config module can be imported
        try:
            import config
        except ImportError as e:
            pytest.fail(f"Cannot import config module: {e}")
        
        # Test file path constants exist and have correct values
        expected_file_paths = {
            'IMPLEMENTATION_PLAN_FILE': "Implementation Plan.md",
            'PRD_FILE': "PRD.md", 
            'CLAUDE_FILE': "CLAUDE.md",
            'SIGNAL_FILE': ".claude/signal_task_complete",
            'SETTINGS_FILE': ".claude/settings.local.json"
        }
        
        for constant_name, expected_value in expected_file_paths.items():
            assert hasattr(config, constant_name), f"config should have {constant_name} constant"
            actual_value = getattr(config, constant_name)
            assert actual_value == expected_value, f"{constant_name} should be '{expected_value}', got '{actual_value}'"
        
        # Test exit code constants exist and have correct values
        expected_exit_codes = {
            'EXIT_SUCCESS': 0,
            'EXIT_MISSING_CRITICAL_FILE': 1
        }
        
        for constant_name, expected_value in expected_exit_codes.items():
            assert hasattr(config, constant_name), f"config should have {constant_name} constant"
            actual_value = getattr(config, constant_name)
            assert actual_value == expected_value, f"{constant_name} should be {expected_value}, got {actual_value}"
        
        # Test workflow control constants exist and have correct values
        expected_workflow_constants = {
            'MAX_FIX_ATTEMPTS': 3,
            'MIN_WAIT_TIME': 60,
            'SIGNAL_WAIT_SLEEP_INTERVAL': 0.1,
            'SIGNAL_WAIT_TIMEOUT': 30.0
        }
        
        for constant_name, expected_value in expected_workflow_constants.items():
            assert hasattr(config, constant_name), f"config should have {constant_name} constant"
            actual_value = getattr(config, constant_name)
            assert actual_value == expected_value, f"{constant_name} should be {expected_value}, got {actual_value}"
        
        # Test status constants exist and have correct values
        expected_status_constants = {
            'VALIDATION_PASSED': "validation_passed",
            'VALIDATION_FAILED': "validation_failed", 
            'PROJECT_COMPLETE': "project_complete",
            'PROJECT_INCOMPLETE': "project_incomplete"
        }
        
        for constant_name, expected_value in expected_status_constants.items():
            assert hasattr(config, constant_name), f"config should have {constant_name} constant"
            actual_value = getattr(config, constant_name)
            assert actual_value == expected_value, f"{constant_name} should be '{expected_value}', got '{actual_value}'"
        
        # Test command constants exist and have correct values
        expected_command_constants = {
            'CLEAR_CMD': "/clear",
            'CONTINUE_CMD': "/continue",
            'VALIDATE_CMD': "/validate", 
            'UPDATE_CMD': "/update",
            'CORRECT_CMD': "/correct"
        }
        
        for constant_name, expected_value in expected_command_constants.items():
            assert hasattr(config, constant_name), f"config should have {constant_name} constant"
            actual_value = getattr(config, constant_name)
            assert actual_value == expected_value, f"{constant_name} should be '{expected_value}', got '{actual_value}'"