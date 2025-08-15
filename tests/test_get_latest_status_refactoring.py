"""
Test for refactoring get_latest_status function into smaller helper functions.

This test file contains TDD tests that verify the get_latest_status function is properly
refactored into smaller, focused helper functions following FIRST principles.
"""

import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestGetLatestStatusRefactoring:
    """Test suite for verifying get_latest_status function is properly broken down into helper functions."""
    
    def test_get_latest_status_uses_helper_functions_for_modular_design(self, tmp_path, monkeypatch):
        """
        Test that get_latest_status function uses helper functions for better modularity and maintainability.
        
        This test verifies that the long get_latest_status function has been refactored into
        smaller, focused helper functions following the Single Responsibility Principle:
        
        1. _find_status_files() - locates status_*.json files in .claude directory
        2. _get_newest_file() - determines which status file is newest based on timestamps
        3. _read_status_file() - reads and parses JSON from a specific status file
        4. _cleanup_status_files() - removes all status files after reading
        
        The test mocks these helper functions and verifies they are called in the correct order
        with appropriate parameters, ensuring the main function orchestrates the helpers properly.
        
        Given a directory with multiple status files,
        When get_latest_status is called,
        Then it should delegate to helper functions in the correct sequence:
        1. Call _find_status_files() to locate all status files
        2. Call _get_newest_file() with the found files to identify the newest
        3. Call _read_status_file() with the newest file to extract status
        4. Call _cleanup_status_files() with all files to clean up
        5. Return the extracted status value
        
        This test will initially fail because get_latest_status is currently implemented
        as one large function without these helper functions.
        This is the RED phase of TDD - the test must fail first.
        """
        # Change to temporary directory
        monkeypatch.chdir(tmp_path)
        
        # Create .claude directory with multiple status files for test context
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        
        # Create sample status files (these will be used by the mocked functions)
        status_files_data = [
            ("status_20240101_120000.json", {"status": "validation_failed"}),
            ("status_20240101_140000.json", {"status": "validation_passed"}),
            ("status_20240101_130000.json", {"status": "project_incomplete"})
        ]
        
        mock_status_files = []
        for filename, data in status_files_data:
            status_file = claude_dir / filename
            status_file.write_text(json.dumps(data), encoding="utf-8")
            mock_status_files.append(status_file)
        
        # Import the function to test
        from automate_dev import get_latest_status
        
        # Mock the helper functions that should be called by get_latest_status
        # Using create=True since these functions don't exist yet in the current implementation
        with patch('automate_dev._find_status_files', create=True) as mock_find_files:
            with patch('automate_dev._get_newest_file', create=True) as mock_get_newest:
                with patch('automate_dev._read_status_file', create=True) as mock_read_file:
                    with patch('automate_dev._cleanup_status_files') as mock_cleanup:
                        
                        # Configure mock return values to simulate the refactored workflow
                        mock_find_files.return_value = mock_status_files
                        mock_get_newest.return_value = mock_status_files[1]  # newest file
                        mock_read_file.return_value = "validation_passed"  # status from newest file
                        
                        # Call get_latest_status - should delegate to helper functions
                        result = get_latest_status()
                        
                        # Verify that _find_status_files was called to locate status files
                        mock_find_files.assert_called_once()
                        
                        # Verify that _get_newest_file was called with found files
                        mock_get_newest.assert_called_once_with(mock_status_files)
                        
                        # Verify that _read_status_file was called with the newest file
                        mock_read_file.assert_called_once_with(mock_status_files[1])
                        
                        # Verify that _cleanup_status_files was called with all files
                        mock_cleanup.assert_called_once_with(mock_status_files)
                        
                        # Verify that the result comes from the helper function chain
                        assert result == "validation_passed", f"Expected status from helper functions, got: {result}"
        
        # Verify that the main function acts as orchestrator, not doing direct file operations
        # This ensures separation of concerns - main function orchestrates, helpers do the work
        print("SUCCESS: get_latest_status properly delegates to helper functions")
        print("- _find_status_files() called to locate status files")  
        print("- _get_newest_file() called to identify newest file")
        print("- _read_status_file() called to extract status from newest file")
        print("- _cleanup_status_files() called to clean up all status files")
        print("- Main function orchestrates helper calls without direct file operations")