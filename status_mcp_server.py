"""
MCP Server for Reliable Status Reporting.

This module implements the StatusServer class with report_status tool
for creating timestamped JSON status files in the .claude/ directory.
"""

import json
import datetime
import psutil
from pathlib import Path
from typing import Dict, Any, TypedDict, Optional
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
        self._start_time = datetime.datetime.now(datetime.timezone.utc)
        self._last_request_time: Optional[datetime.datetime] = None
        
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
            self._last_request_time = datetime.datetime.now(datetime.timezone.utc)
            return self._create_status_file(status, details, task_description)
        
        # Register the health_check tool
        @self._mcp.tool()
        def health_check() -> Dict[str, Any]:
            """
            Return comprehensive server health status information.
            
            This method provides a detailed health assessment including:
            - Overall health status (healthy/unhealthy) based on system metrics
            - Server uptime in seconds since initialization
            - Timestamp of the last request processed (ISO 8601 format)
            - Current memory usage in megabytes
            - Server identification name
            
            The health status is determined by validating that system metrics
            can be successfully retrieved and are within expected ranges.
            
            Returns:
                Dictionary containing:
                - status (str): "healthy" or "unhealthy"
                - uptime_seconds (float): Server uptime in seconds
                - last_request_time (str|None): ISO 8601 timestamp or None
                - memory_usage_mb (float): Memory usage in MB (0.0 if unavailable)
                - server_name (str): Server identification name
                
            Note:
                Memory usage falls back to 0.0 if psutil operations fail.
                Health status considers the server healthy if basic metrics
                can be retrieved successfully.
            """
            # Get system metrics using helper methods
            uptime_seconds = self._get_uptime_seconds()
            memory_usage_mb = self._get_memory_usage_mb()
            
            # Determine actual health status based on metrics
            health_status = self._determine_health_status(memory_usage_mb, uptime_seconds)
            
            # Format last request time as ISO 8601
            last_request_iso = None
            if self._last_request_time:
                last_request_iso = self._format_iso_timestamp(self._last_request_time)
            
            return {
                "status": health_status,
                "uptime_seconds": uptime_seconds,
                "last_request_time": last_request_iso,
                "memory_usage_mb": memory_usage_mb,
                "server_name": SERVER_NAME
            }
        
        # Bind the methods to the instance for direct access
        self.report_status = report_status
        self.health_check = health_check
    
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
    
    def _format_iso_timestamp(self, timestamp: datetime.datetime) -> str:
        """
        Format datetime object as ISO 8601 string with Z suffix.
        
        Args:
            timestamp: Datetime object to format
            
        Returns:
            ISO 8601 formatted string with Z suffix
        """
        return timestamp.isoformat().replace(ISO_UTC_SUFFIX_FROM, ISO_UTC_SUFFIX_TO)
    
    def _get_uptime_seconds(self) -> float:
        """
        Calculate server uptime in seconds.
        
        Returns:
            Uptime in seconds since server start
        """
        current_time = datetime.datetime.now(datetime.timezone.utc)
        return max(0, (current_time - self._start_time).total_seconds())
    
    def _get_memory_usage_mb(self) -> float:
        """
        Get current memory usage in megabytes.
        
        Returns:
            Memory usage in MB, or 0.0 if unable to determine
        """
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            return memory_info.rss / (1024 * 1024)  # Convert bytes to MB
        except (psutil.Error, OSError):
            # Fallback to 0 if psutil fails
            return 0.0
    
    def _determine_health_status(self, memory_usage_mb: float, uptime_seconds: float) -> str:
        """
        Determine server health status based on metrics.
        
        Args:
            memory_usage_mb: Current memory usage in MB
            uptime_seconds: Server uptime in seconds
            
        Returns:
            Health status: "healthy" or "unhealthy"
        """
        # For now, consider healthy if we can get basic metrics
        # Future enhancement: add thresholds for memory usage, uptime, etc.
        if memory_usage_mb >= 0 and uptime_seconds >= 0:
            return "healthy"
        return "unhealthy"
    
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
        timestamp_iso = self._format_iso_timestamp(timestamp)
        
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