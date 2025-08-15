"""Configuration constants for the automated development workflow.

This module centralizes all configuration constants used throughout the automated
development workflow system. Constants are organized into logical categories
with clear section headers for better maintainability and understanding.

Categories:
- File Paths: All file and directory paths used by the system
- Exit Codes: Standard exit codes for the orchestrator
- Workflow Control: Timing and control parameters for the TDD loop
- Status Values: String constants for various workflow states
- Command Names: Slash command identifiers
- Settings Configuration: Default settings and parsing patterns
- Time Conversion: Constants for time calculation and parsing
- Refactoring States: Status constants for refactoring workflow
- Logging: Module-specific logger configuration
"""

import json


# =============================================================================
# FILE PATHS
# =============================================================================
# Core project files and directories
IMPLEMENTATION_PLAN_FILE = "Implementation Plan.md"
PRD_FILE = "PRD.md"
CLAUDE_FILE = "CLAUDE.md"
SIGNAL_FILE = ".claude/signal_task_complete"
SETTINGS_FILE = ".claude/settings.local.json"


# =============================================================================
# EXIT CODES
# =============================================================================
# Standard exit codes for the orchestrator process
EXIT_SUCCESS = 0
EXIT_MISSING_CRITICAL_FILE = 1


# =============================================================================
# WORKFLOW CONTROL
# =============================================================================
# Parameters controlling the TDD loop behavior
MAX_FIX_ATTEMPTS = 3                # Maximum correction attempts per task
MIN_WAIT_TIME = 60                  # Minimum wait time in seconds
SIGNAL_WAIT_SLEEP_INTERVAL = 0.1    # Sleep interval when waiting for signals
SIGNAL_WAIT_TIMEOUT = 30.0          # Timeout for signal waiting


# =============================================================================
# STATUS VALUES
# =============================================================================
# String constants for workflow states
VALIDATION_PASSED = "validation_passed"
VALIDATION_FAILED = "validation_failed"
PROJECT_COMPLETE = "project_complete"
PROJECT_INCOMPLETE = "project_incomplete"

# Refactoring workflow states
CHECKIN_COMPLETE = "checkin_complete"
REFACTORING_NEEDED = "refactoring_needed"
NO_REFACTORING_NEEDED = "no_refactoring_needed"
FINALIZATION_COMPLETE = "finalization_complete"


# =============================================================================
# COMMAND NAMES
# =============================================================================
# Primary TDD workflow commands
CLEAR_CMD = "/clear"
CONTINUE_CMD = "/continue"
VALIDATE_CMD = "/validate"
UPDATE_CMD = "/update"
CORRECT_CMD = "/correct"

# Refactoring workflow commands
CHECKIN_CMD = "/checkin"
REFACTOR_CMD = "/refactor"
FINALIZE_CMD = "/finalize"


# =============================================================================
# SETTINGS CONFIGURATION
# =============================================================================
# Default settings configuration structure
# This configuration sets up the Stop hook to create a signal file when Claude sessions end
# The hook enables reliable detection of task completion in automated workflows
DEFAULT_SETTINGS_CONFIG = {
    "hooks": {
        "Stop": [{
            "hooks": [{
                "type": "command",
                "command": f"touch {SIGNAL_FILE}"
            }]
        }]
    }
}

# Serialize the configuration to JSON string for file writing
DEFAULT_SETTINGS_JSON = json.dumps(DEFAULT_SETTINGS_CONFIG, indent=2)

# Regular expression pattern for parsing usage limit messages
USAGE_LIMIT_TIME_PATTERN = r'try again at (\w+) \(([^)]+)\)'


# =============================================================================
# TIME CONVERSION
# =============================================================================
# Constants for 12-hour to 24-hour time conversion
HOURS_12_CLOCK_CONVERSION = 12      # Hours to add/subtract for 12-hour clock conversion
MIDNIGHT_HOUR_12_FORMAT = 12        # Hour value representing midnight in 12-hour format
NOON_HOUR_12_FORMAT = 12            # Hour value representing noon in 12-hour format


# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================
# Module-specific loggers for different components
LOGGERS = {
    'orchestrator': None,
    'task_tracker': None,
    'command_executor': None,
    'validation': None,
    'error_handler': None,
    'usage_limit': None
}