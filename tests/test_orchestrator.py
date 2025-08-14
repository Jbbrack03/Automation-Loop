"""
Tests for the automate_dev.py orchestrator script.

This file contains TDD tests for the automated development workflow orchestrator.
Following the red-green-refactor cycle, these tests are written before implementation.
"""

import pytest
import sys
import os
from unittest.mock import patch

class TestOrchestratorScriptExecution:
    """Test suite for basic orchestrator script functionality."""
    
    def test_main_function_import_and_executable(self):
        """
        Test that the main function can be imported from automate_dev.py
        and that the script is executable.
        
        This test will initially fail because automate_dev.py doesn't exist yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Attempt to import the main function from automate_dev.py
        try:
            from automate_dev import main
            
            # Verify that main is callable (a function)
            assert callable(main), "main should be a callable function"
            
            # Verify that the main function can be called without error
            # (for now, we just check it exists and is callable)
            assert hasattr(main, '__call__'), "main should have __call__ attribute"
            
        except ImportError as e:
            # This is expected to fail initially - automate_dev.py doesn't exist yet
            pytest.fail(f"Cannot import main function from automate_dev.py: {e}")
        
    def test_automate_dev_script_exists(self):
        """
        Test that the automate_dev.py script file exists in the root directory.
        
        This test ensures the orchestrator script is present and readable.
        """
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "automate_dev.py")
        
        assert os.path.exists(script_path), f"automate_dev.py should exist at {script_path}"
        assert os.path.isfile(script_path), "automate_dev.py should be a file"
        assert os.access(script_path, os.R_OK), "automate_dev.py should be readable"


class TestOrchestratorPrerequisiteFileChecks:
    """Test suite for prerequisite file validation in the orchestrator."""
    
    def test_orchestrator_exits_gracefully_when_implementation_plan_missing(self, tmp_path, monkeypatch):
        """
        Test that the orchestrator exits gracefully with an error if Implementation Plan.md is missing.
        
        This test creates a temporary directory without the Implementation Plan.md file,
        changes to that directory, and verifies that the orchestrator exits with the
        appropriate error code and message.
        
        This test will initially fail because main() doesn't implement these checks yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Change to temporary directory where Implementation Plan.md doesn't exist
        monkeypatch.chdir(tmp_path)
        
        # Import main function to test
        from automate_dev import main
        
        # Mock sys.exit to capture exit calls and prevent actual exit
        with patch('sys.exit') as mock_exit:
            # Mock print to capture error messages
            with patch('builtins.print') as mock_print:
                # Call main function - it should detect missing Implementation Plan.md
                main()
                
                # Verify that sys.exit was called with error code (non-zero)
                mock_exit.assert_called_once()
                exit_code = mock_exit.call_args[0][0] if mock_exit.call_args[0] else 1
                assert exit_code != 0, "Expected non-zero exit code when Implementation Plan.md is missing"
                
                # Verify that an appropriate error message was printed
                mock_print.assert_called()
                printed_messages = [str(call.args[0]) for call in mock_print.call_args_list]
                error_message_found = any(
                    "Implementation Plan.md" in msg or "implementation plan" in msg.lower()
                    for msg in printed_messages
                )
                assert error_message_found, f"Expected error message about missing Implementation Plan.md, got: {printed_messages}"
    
    def test_orchestrator_prints_warning_when_prd_md_missing(self, tmp_path, monkeypatch):
        """
        Test that the orchestrator prints a warning if PRD.md is missing.
        
        This test creates a temporary directory with Implementation Plan.md present
        but PRD.md missing, and verifies that a warning is printed.
        
        This test will initially fail because main() doesn't implement these checks yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Change to temporary directory
        monkeypatch.chdir(tmp_path)
        
        # Create Implementation Plan.md to avoid the exit condition
        implementation_plan = tmp_path / "Implementation Plan.md"
        implementation_plan.write_text("# Implementation Plan\n\n- [ ] Task 1", encoding="utf-8")
        
        # Ensure PRD.md does NOT exist
        prd_file = tmp_path / "PRD.md"
        if prd_file.exists():
            prd_file.unlink()
        
        # Import main function to test
        from automate_dev import main
        
        # Mock sys.exit to prevent actual exit
        with patch('sys.exit') as mock_exit:
            # Mock print to capture warning messages
            with patch('builtins.print') as mock_print:
                # Call main function - it should detect missing PRD.md and print warning
                main()
                
                # Verify that an appropriate warning message was printed
                mock_print.assert_called()
                printed_messages = [str(call.args[0]) for call in mock_print.call_args_list]
                warning_message_found = any(
                    ("PRD.md" in msg and ("missing" in msg.lower() or "warning" in msg.lower()))
                    for msg in printed_messages
                )
                assert warning_message_found, f"Expected warning message about missing PRD.md, got: {printed_messages}"
    
    def test_orchestrator_prints_warning_when_claude_md_missing(self, tmp_path, monkeypatch):
        """
        Test that the orchestrator prints a warning if CLAUDE.md is missing.
        
        This test creates a temporary directory with Implementation Plan.md present
        but CLAUDE.md missing, and verifies that a warning is printed.
        
        This test will initially fail because main() doesn't implement these checks yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Change to temporary directory
        monkeypatch.chdir(tmp_path)
        
        # Create Implementation Plan.md to avoid the exit condition
        implementation_plan = tmp_path / "Implementation Plan.md"
        implementation_plan.write_text("# Implementation Plan\n\n- [ ] Task 1", encoding="utf-8")
        
        # Ensure CLAUDE.md does NOT exist
        claude_file = tmp_path / "CLAUDE.md"
        if claude_file.exists():
            claude_file.unlink()
        
        # Import main function to test
        from automate_dev import main
        
        # Mock sys.exit to prevent actual exit
        with patch('sys.exit') as mock_exit:
            # Mock print to capture warning messages
            with patch('builtins.print') as mock_print:
                # Call main function - it should detect missing CLAUDE.md and print warning
                main()
                
                # Verify that an appropriate warning message was printed
                mock_print.assert_called()
                printed_messages = [str(call.args[0]) for call in mock_print.call_args_list]
                warning_message_found = any(
                    ("CLAUDE.md" in msg and ("missing" in msg.lower() or "warning" in msg.lower()))
                    for msg in printed_messages
                )
                assert warning_message_found, f"Expected warning message about missing CLAUDE.md, got: {printed_messages}"
    
    def test_orchestrator_continues_when_all_prerequisite_files_present(self, tmp_path, monkeypatch):
        """
        Test that the orchestrator continues normally when all prerequisite files are present.
        
        This test creates a temporary directory with all required files present
        and verifies that no error or warning messages are printed.
        
        This test will initially fail because main() doesn't implement these checks yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Change to temporary directory
        monkeypatch.chdir(tmp_path)
        
        # Create all prerequisite files
        implementation_plan = tmp_path / "Implementation Plan.md"
        implementation_plan.write_text("# Implementation Plan\n\n- [ ] Task 1", encoding="utf-8")
        
        prd_file = tmp_path / "PRD.md"
        prd_file.write_text("# Product Requirements Document", encoding="utf-8")
        
        claude_file = tmp_path / "CLAUDE.md"
        claude_file.write_text("# CLAUDE.md\n\nProject instructions for Claude Code.", encoding="utf-8")
        
        # Import main function to test
        from automate_dev import main
        
        # Mock sys.exit to prevent actual exit and capture exit calls
        with patch('sys.exit') as mock_exit:
            # Mock print to capture any messages
            with patch('builtins.print') as mock_print:
                # Call main function - it should not exit or print warnings
                main()
                
                # Verify that sys.exit was NOT called due to missing files
                # (it might be called for other reasons once more functionality is implemented)
                if mock_exit.called:
                    # If exit was called, ensure it wasn't due to missing files
                    printed_messages = [str(call.args[0]) for call in mock_print.call_args_list]
                    file_error_found = any(
                        any(filename in msg for filename in ["Implementation Plan.md", "PRD.md", "CLAUDE.md"])
                        and ("missing" in msg.lower() or "not found" in msg.lower())
                        for msg in printed_messages
                    )
                    assert not file_error_found, f"No file-related errors should be printed when all files are present, got: {printed_messages}"