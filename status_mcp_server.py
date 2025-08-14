"""
MCP Server for Reliable Status Reporting.

This module implements the StatusServer class with report_status tool
for creating timestamped JSON status files in the .claude/ directory.
"""

import json
import datetime
from pathlib import Path
from typing import Dict, Any, TypedDict
from mcp.server.fastmcp import FastMCP


# Configuration constants
SERVER_NAME = "status-server"
CLAUDE_DIR_NAME = ".claude"
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"
ISO_UTC_SUFFIX_FROM = "+00:00"
ISO_UTC_SUFFIX_TO = "Z"
FILE_PREFIX = "status_"
FILE_EXTENSION = ".json"


class StatusResponse(TypedDict):
    """Type definition for status report response."""
    success: bool
    file_created: str


class StatusServer:
    """
    MCP Server for reliable status reporting.
    
    Creates timestamped JSON files in .claude/ directory for status tracking.
    """
    
    def __init__(self) -> None:
        """Initialize StatusServer with FastMCP instance."""
        self._mcp = FastMCP(SERVER_NAME)
        
        # Register the report_status tool
        @self._mcp.tool()
        def report_status(status: str, details: Dict[str, Any], task_description: str) -> StatusResponse:
            """
            Report development status by creating timestamped JSON file.
            
            Args:
                status: Status type (e.g., "validation_passed", "validation_failed")
                details: Dictionary with status details
                task_description: Description of the current task
                
            Returns:
                Dictionary with success status and created file path
            """
            return self._create_status_file(status, details, task_description)
        
        # Bind the method to the instance for direct access
        self.report_status = report_status
    
    def _create_status_file(self, status: str, details: Dict[str, Any], task_description: str) -> StatusResponse:
        """
        Create timestamped JSON status file in .claude/ directory.
        
        Args:
            status: Status type
            details: Status details dictionary
            task_description: Task description
            
        Returns:
            Dictionary with success indicator and file path
        """
        # Generate single timestamp for consistency
        timestamp = datetime.datetime.now(datetime.timezone.utc)
        
        # Ensure .claude directory exists
        claude_dir = self._ensure_claude_directory()
        
        # Generate file path with timestamp
        file_path = self._generate_status_file_path(claude_dir, timestamp)
        
        # Create and write status data with same timestamp
        status_data = self._create_status_data(status, details, task_description, timestamp)
        self._write_json_file(file_path, status_data)
        
        return {
            "success": True,
            "file_created": str(file_path.resolve())
        }
    
    def _ensure_claude_directory(self) -> Path:
        """
        Ensure .claude directory exists and return Path object.
        
        Returns:
            Path object for .claude directory
        """
        claude_dir = Path(CLAUDE_DIR_NAME)
        claude_dir.mkdir(exist_ok=True)
        return claude_dir
    
    def _generate_status_file_path(self, claude_dir: Path, timestamp: datetime.datetime) -> Path:
        """
        Generate timestamped status file path.
        
        Args:
            claude_dir: Path to .claude directory
            timestamp: Timestamp to use for filename
            
        Returns:
            Path object for status file
        """
        timestamp_str = timestamp.strftime(TIMESTAMP_FORMAT)
        filename = f"{FILE_PREFIX}{timestamp_str}{FILE_EXTENSION}"
        return claude_dir / filename
    
    def _create_status_data(self, status: str, details: Dict[str, Any], task_description: str, timestamp: datetime.datetime) -> Dict[str, Any]:
        """
        Create status data dictionary for JSON serialization.
        
        Args:
            status: Status type
            details: Status details dictionary
            task_description: Task description
            timestamp: Timestamp to use for ISO format
            
        Returns:
            Status data dictionary
        """
        timestamp_iso = timestamp.isoformat().replace(ISO_UTC_SUFFIX_FROM, ISO_UTC_SUFFIX_TO)
        
        return {
            "timestamp": timestamp_iso,
            "status": status,
            "details": details,
            "task_description": task_description
        }
    
    def _write_json_file(self, file_path: Path, data: Dict[str, Any]) -> None:
        """
        Write data to JSON file with UTF-8 encoding.
        
        Args:
            file_path: Path where to write the file
            data: Data to serialize as JSON
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)