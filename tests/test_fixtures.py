"""
Test fixtures module providing common mock fixtures to reduce duplication across tests.

This module addresses Task 11.6: Optimize test structure and reduce mock duplication
by providing centralized mock fixtures and helper functions that can be reused
across the 32 test functions that currently use 84 separate mock instances.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path


def mock_subprocess_success():
    """
    Returns a configured mock for successful subprocess operations.
    
    The mock provides return_value with returncode, stdout, and stderr attributes
    for simulating successful subprocess.run() calls.
    """
    mock = Mock()
    mock.return_value = Mock()
    mock.return_value.returncode = 0
    mock.return_value.stdout = "Command executed successfully"
    mock.return_value.stderr = ""
    return mock


def mock_claude_command_fixture():
    """
    Returns a callable mock for run_claude_command function.
    
    The mock returns a dictionary with status field to simulate successful
    Claude command execution.
    """
    mock = Mock()
    mock.return_value = {"status": "success", "output": "Command completed"}
    return mock


def mock_get_latest_status_fixture():
    """
    Returns a callable mock for get_latest_status function.
    
    The mock can be configured to return various status values for testing
    different workflow states.
    """
    mock = Mock()
    mock.return_value = "validation_passed"
    return mock


def mock_file_system_fixture():
    """
    Returns a dictionary of file system operation mocks.
    
    Provides mocks for Path operations, file opening, and existence checks
    commonly used in file system testing scenarios.
    """
    return {
        "path_mock": Mock(spec=Path),
        "open_mock": MagicMock(),
        "exists_mock": Mock(return_value=True)
    }


def setup_temp_environment(tmp_path):
    """
    Helper function to set up a temporary test environment structure.
    
    Creates the standard directory structure and files needed for testing
    the orchestrator functionality.
    
    Args:
        tmp_path: pytest tmp_path fixture providing temporary directory
        
    Returns:
        Dictionary with paths to created files and directories
    """
    # Create .claude directory structure
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    logs_dir = claude_dir / "logs"
    logs_dir.mkdir()
    
    # Create required files
    implementation_plan = tmp_path / "Implementation_Plan.md"
    prd_file = tmp_path / "PRD.md"
    claude_file = tmp_path / "CLAUDE.md"
    
    return {
        "tmp_path": tmp_path,
        "claude_dir": claude_dir,
        "logs_dir": logs_dir,
        "implementation_plan": implementation_plan,
        "prd_file": prd_file,
        "claude_file": claude_file
    }


def create_mock_implementation_plan(complete_tasks=None, incomplete_tasks=None):
    """
    Helper function to create mock Implementation Plan content for testing.
    
    Generates markdown content with specified completed and incomplete tasks
    using the standard checkbox format used by the orchestrator.
    
    Args:
        complete_tasks: List of completed task descriptions
        incomplete_tasks: List of incomplete task descriptions
        
    Returns:
        String containing formatted Implementation Plan markdown
    """
    if complete_tasks is None:
        complete_tasks = []
    if incomplete_tasks is None:
        incomplete_tasks = []
    
    content = "# Implementation Plan\n\n"
    
    # Add completed tasks
    for task in complete_tasks:
        content += f"- [X] {task}\n"
    
    # Add incomplete tasks  
    for task in incomplete_tasks:
        content += f"- [ ] {task}\n"
    
    return content


@pytest.fixture
def mock_claude_command():
    """
    Pytest fixture for mocking run_claude_command.
    
    Returns a MagicMock that can be used with patch decorators or context managers.
    Pre-configured to return successful command execution results.
    """
    with patch('automate_dev.run_claude_command') as mock:
        mock.return_value = {"status": "success", "output": "Command completed"}
        yield mock


@pytest.fixture
def mock_get_latest_status():
    """
    Pytest fixture for mocking get_latest_status.
    
    Returns a MagicMock that can be configured to return various status values.
    Default return value is "project_complete" for simple test cases.
    """
    with patch('automate_dev.get_latest_status') as mock:
        mock.return_value = "project_complete"
        yield mock


@pytest.fixture
def test_environment(tmp_path, monkeypatch):
    """
    Pytest fixture to set up a complete test environment.
    
    Creates a temporary directory with all standard files and directories
    needed for orchestrator testing, and changes to that directory.
    
    Returns:
        Dictionary with paths to all created files and directories
    """
    # Change to temporary directory
    monkeypatch.chdir(tmp_path)
    
    # Create .claude directory structure
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    logs_dir = claude_dir / "logs"
    logs_dir.mkdir()
    
    # Create Implementation_Plan.md with default content
    implementation_plan = tmp_path / "Implementation_Plan.md"
    default_plan_content = "# Implementation Plan\n\n- [X] Default completed task"
    implementation_plan.write_text(default_plan_content, encoding="utf-8")
    
    return {
        "tmp_path": tmp_path,
        "claude_dir": claude_dir,
        "logs_dir": logs_dir,
        "implementation_plan": implementation_plan,
        "prd_file": tmp_path / "PRD.md",
        "claude_file": tmp_path / "CLAUDE.md"
    }


@pytest.fixture
def prerequisite_files_setup(test_environment):
    """
    Pytest fixture that extends test_environment with all prerequisite files.
    
    Creates PRD.md and CLAUDE.md files in addition to the basic test environment.
    
    Returns:
        Dictionary with paths to all created files and directories
    """
    env = test_environment
    
    # Create PRD.md
    env["prd_file"].write_text("# Product Requirements Document", encoding="utf-8")
    
    # Create CLAUDE.md
    env["claude_file"].write_text("# CLAUDE.md\n\nProject instructions for Claude Code.", encoding="utf-8")
    
    return env


@pytest.fixture
def main_loop_test_setup(test_environment):
    """
    Pytest fixture for setting up the main orchestration loop happy path test.
    
    Creates a multi-task Implementation Plan and provides mocks for simulating
    the full TDD cycle progression.

    Returns:
        Dictionary with test environment and configured mocks
    """
    env = test_environment
    
    # Create Implementation_Plan.md with multiple tasks for testing progression
    implementation_plan_content = """# Implementation Plan

## Phase 1: Development
- [ ] Implement user authentication
- [ ] Create database schema
- [X] Already completed task

## Phase 2: Testing  
- [ ] Write integration tests
"""
    env["implementation_plan"].write_text(implementation_plan_content, encoding="utf-8")
    
    return env


def create_main_loop_command_mock(implementation_plan_path):
    """
    Helper function to create a mock command handler for main loop tests.
    
    This mock simulates the /update command progressively marking tasks complete
    by rewriting the Implementation_Plan.md file.
    
    Args:
        implementation_plan_path: Path to the Implementation_Plan.md file to modify
        
    Returns:
        Mock function that can be used as side_effect for run_claude_command
    """
    update_call_count = 0
    
    def mock_run_command_happy_path(command, *args, **kwargs):
        nonlocal update_call_count
        # Simulate /update marking tasks as complete progressively
        if command == "/update":
            update_call_count += 1
            if update_call_count == 1:
                # First /update: mark first task as complete
                updated_content = """# Implementation Plan

## Phase 1: Setup
- [X] Create project structure

## Phase 2: Testing  
- [ ] Write integration tests
"""
                implementation_plan_path.write_text(updated_content, encoding="utf-8")
            elif update_call_count == 2:
                # Second /update: mark second task as complete
                updated_content = """# Implementation Plan

## Phase 1: Setup
- [X] Create project structure

## Phase 2: Testing  
- [X] Write integration tests
"""
                implementation_plan_path.write_text(updated_content, encoding="utf-8")
            elif update_call_count == 3:
                # Third /update: all tasks already complete, no change needed
                pass
        
        return {"status": "success", "output": "Command completed"}
    
    return mock_run_command_happy_path


def get_main_loop_status_sequence():
    """
    Helper function that returns the status sequence for main loop happy path testing.
    
    Returns:
        List of status values to be used with mock_get_latest_status.side_effect
    """
    # With the new _command_executor_wrapper, get_latest_status is only called for
    # commands that need status (/validate, /update, /checkin, /refactor)
    # /clear and /continue don't call get_latest_status anymore
    return [
        # First task TDD cycle (2 status calls: validate, update)
        "validation_passed",     # /validate via execute_command_and_get_status
        "project_incomplete",    # /update via execute_command_and_get_status
        
        # Second task TDD cycle  
        "validation_passed",     # /validate
        "project_incomplete",    # /update
        
        # Third task TDD cycle
        "validation_passed",     # /validate
        "project_complete",      # /update - all tasks complete
        
        # Extra values for handle_project_completion and refactoring loop
        "project_complete",      # Check in handle_project_completion
        "checkin_complete",      # /checkin in refactoring loop
        "no_refactoring_needed", # /refactor - causes exit
    ]


@pytest.fixture
def refactoring_loop_test_setup(test_environment):
    """
    Pytest fixture for setting up refactoring loop tests.
    
    Creates an Implementation Plan with all tasks complete to trigger
    the refactoring loop workflow.

    Returns:
        Dictionary with test environment configured for refactoring tests
    """
    env = test_environment
    
    # Create Implementation_Plan.md with all tasks complete
    implementation_plan_content = """# Implementation Plan

## Phase 1: Development
- [X] Implement user authentication
- [X] Create database schema
- [X] Write integration tests

## Phase 2: Testing  
- [X] All tests implemented
"""
    env["implementation_plan"].write_text(implementation_plan_content, encoding="utf-8")
    
    return env


def get_refactoring_loop_status_sequence():
    """
    Helper function that returns the status sequence for refactoring loop testing.
    
    Returns:
        List of status values for the complete refactoring workflow
    """
    return [
        # First complete TDD cycle
        "validation_passed",        # After /validate when all tasks complete
        "project_complete",         # After /update - triggers refactoring mode
        "project_complete",         # Check in handle_project_completion
        
        # First refactoring cycle
        "checkin_complete",         # After /checkin - issues found
        "refactoring_needed",       # After /refactor - work needed (matches REFACTORING_NEEDED constant)
        "refactoring_complete",     # After /finalize - work done
        
        # Second refactoring cycle
        "checkin_complete",         # After /checkin - more issues found
        "refactoring_needed",       # After /refactor - more work needed (matches REFACTORING_NEEDED constant)
        "refactoring_complete",     # After /finalize - work done
        
        # Final refactoring cycle
        "checkin_complete",         # After /checkin - no issues
        "no_refactoring_needed"     # After /refactor - exits loop
    ]