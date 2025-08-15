"""
Pytest configuration file for sharing fixtures across test modules.

This file is automatically discovered by pytest and makes fixtures
available to all tests in the tests/ directory.
"""

# Import all fixtures from test_fixtures to make them available globally
from tests.test_fixtures import (
    mock_claude_command,
    mock_get_latest_status,
    test_environment,
    prerequisite_files_setup,
    main_loop_test_setup,
    refactoring_loop_test_setup
)

# Re-export fixtures so they're available to all test modules
__all__ = [
    'mock_claude_command',
    'mock_get_latest_status', 
    'test_environment',
    'prerequisite_files_setup',
    'main_loop_test_setup',
    'refactoring_loop_test_setup'
]