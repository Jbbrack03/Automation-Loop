"""Automated development workflow orchestrator.

This module provides the main orchestrator function that manages prerequisite file
validation for the automated development workflow system.
"""

import os
import sys
from typing import List, Tuple

# Constants for prerequisite files
IMPLEMENTATION_PLAN_FILE = "Implementation Plan.md"
PRD_FILE = "PRD.md"
CLAUDE_FILE = "CLAUDE.md"

# Exit codes
EXIT_SUCCESS = 0
EXIT_MISSING_CRITICAL_FILE = 1


def check_file_exists(filepath: str) -> bool:
    """Check if a file exists.
    
    Args:
        filepath: Path to the file to check
        
    Returns:
        True if file exists, False otherwise
    """
    return os.path.exists(filepath)


def validate_critical_files(files: List[str]) -> Tuple[bool, List[str]]:
    """Validate that critical files exist.
    
    Args:
        files: List of file paths that are required
        
    Returns:
        Tuple of (all_exist, missing_files)
    """
    missing_files = [f for f in files if not check_file_exists(f)]
    return len(missing_files) == 0, missing_files


def validate_optional_files(files: List[str]) -> List[str]:
    """Validate optional files and return list of missing ones.
    
    Args:
        files: List of file paths that are optional
        
    Returns:
        List of missing file paths
    """
    return [f for f in files if not check_file_exists(f)]


def main():
    """Main orchestrator function with prerequisite file checks."""
    # Define critical and optional files
    critical_files = [IMPLEMENTATION_PLAN_FILE]
    optional_files = [PRD_FILE, CLAUDE_FILE]
    
    # Check critical files - exit if any are missing
    all_critical_exist, missing_critical = validate_critical_files(critical_files)
    if not all_critical_exist:
        for missing_file in missing_critical:
            print(f"Error: {missing_file} is missing")
        sys.exit(EXIT_MISSING_CRITICAL_FILE)
    
    # Check optional files - warn if missing
    missing_optional = validate_optional_files(optional_files)
    for missing_file in missing_optional:
        print(f"Warning: {missing_file} is missing")


if __name__ == "__main__":
    main()