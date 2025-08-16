"""
Tests for the status_mcp_server.py MCP server implementation.

This file contains TDD tests for the MCP Server for Reliable Status Reporting.
Following the red-green-refactor cycle, these tests are written before implementation.

The MCP server should implement:
- StatusServer class
- report_status tool decorated with @Tool()
- Create timestamped JSON files in .claude/ directory
- Proper JSON structure with timestamp, status, and metadata
"""

import pytest
import os
import json
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone


class TestMCPStatusServerReportTool:
    """Test suite for the StatusServer MCP server report_status tool functionality."""
    
    def test_report_status_tool_creates_timestamped_json_file(self, tmp_path, monkeypatch):
        """
        Test that the StatusServer report_status tool creates a correctly formatted, timestamped JSON file.
        
        Given a StatusServer instance and valid status data,
        when the report_status tool is called,
        then it should create a timestamped JSON file in the .claude/ directory
        with the correct format, timestamp, and status information.
        
        This test will initially fail because the StatusServer class and report_status tool don't exist yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Change to temporary directory to isolate test
        monkeypatch.chdir(tmp_path)
        
        # Create .claude directory structure in temporary path
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        
        # Import StatusServer class to test
        try:
            from status_mcp_server import StatusServer
        except ImportError:
            pytest.fail("Cannot import StatusServer from status_mcp_server.py - file doesn't exist yet")
        
        # Create StatusServer instance
        server = StatusServer()
        
        # Verify that the server has the report_status tool
        assert hasattr(server, 'report_status'), "StatusServer should have report_status method"
        
        # Verify that report_status is decorated as a Tool (should have tool metadata)
        report_status_method = getattr(server, 'report_status')
        assert callable(report_status_method), "report_status should be callable"
        
        # Define test status data
        test_status = "validation_passed"
        test_details = {
            "tests_run": 15,
            "tests_passed": 15,
            "tests_failed": 0,
            "execution_time": "2.3s"
        }
        test_task_description = "Implement TaskTracker class with failure tracking"
        
        # Mock current time for consistent testing
        mock_timestamp = datetime(2024, 1, 15, 10, 30, 45, tzinfo=timezone.utc)
        with patch('status_mcp_server.datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_timestamp
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            # Call report_status tool
            result = server.report_status(
                status=test_status,
                details=test_details,
                task_description=test_task_description
            )
        
        # Verify that a status file was created in .claude directory
        claude_files = list(claude_dir.glob("status_*.json"))
        assert len(claude_files) == 1, f"Expected exactly 1 status file, found {len(claude_files)}"
        
        status_file = claude_files[0]
        
        # Verify filename format: status_[timestamp].json
        expected_timestamp_str = mock_timestamp.strftime("%Y%m%d_%H%M%S")
        expected_filename = f"status_{expected_timestamp_str}.json"
        assert status_file.name == expected_filename, f"Expected filename '{expected_filename}', got '{status_file.name}'"
        
        # Verify file contents
        with open(status_file, 'r', encoding='utf-8') as f:
            file_content = json.load(f)
        
        # Verify JSON structure and content
        assert isinstance(file_content, dict), "Status file should contain a JSON object"
        
        # Required fields
        assert "timestamp" in file_content, "Status file should contain 'timestamp' field"
        assert "status" in file_content, "Status file should contain 'status' field"
        assert "details" in file_content, "Status file should contain 'details' field"
        assert "task_description" in file_content, "Status file should contain 'task_description' field"
        
        # Verify field values
        assert file_content["status"] == test_status, f"Expected status '{test_status}', got '{file_content['status']}'"
        assert file_content["details"] == test_details, f"Expected details {test_details}, got {file_content['details']}"
        assert file_content["task_description"] == test_task_description, f"Expected task_description '{test_task_description}', got '{file_content['task_description']}'"
        
        # Verify timestamp format (ISO 8601)
        timestamp_str = file_content["timestamp"]
        try:
            parsed_timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            assert parsed_timestamp == mock_timestamp, f"Expected timestamp {mock_timestamp}, got {parsed_timestamp}"
        except ValueError:
            pytest.fail(f"Timestamp '{timestamp_str}' is not in valid ISO 8601 format")
        
        # Verify the tool returns success indication
        assert isinstance(result, dict), "report_status should return a dictionary"
        assert "success" in result, "Result should contain 'success' field"
        assert result["success"] is True, "Result should indicate success"
        assert "file_created" in result, "Result should contain 'file_created' field"
        assert result["file_created"] == str(status_file), "Result should contain the path of created file"
    
    def test_status_server_tool_handles_different_status_types(self, tmp_path, monkeypatch):
        """
        Test that the StatusServer report_status tool handles different status types correctly.
        
        Given a StatusServer instance,
        when the report_status tool is called with different status types,
        then it should create separate JSON files for each status with correct content.
        
        This test will initially fail because the StatusServer class doesn't exist yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Change to temporary directory to isolate test
        monkeypatch.chdir(tmp_path)
        
        # Create .claude directory structure in temporary path
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        
        # Import StatusServer class to test
        try:
            from status_mcp_server import StatusServer
        except ImportError:
            pytest.fail("Cannot import StatusServer from status_mcp_server.py - file doesn't exist yet")
        
        # Create StatusServer instance
        server = StatusServer()
        
        # Test data for different status types
        test_cases = [
            {
                "status": "validation_failed",
                "details": {"error": "Test failed", "line": 42},
                "task_description": "Fix failing unit test"
            },
            {
                "status": "project_complete",
                "details": {"total_tasks": 10, "completed_tasks": 10},
                "task_description": "All implementation tasks completed"
            },
            {
                "status": "refactoring_needed", 
                "details": {"issues": ["duplicate code", "long method"]},
                "task_description": "Code quality improvements needed"
            }
        ]
        
        # Process each test case
        created_files = []
        for i, test_case in enumerate(test_cases):
            # Mock different timestamps for each call
            mock_timestamp = datetime(2024, 1, 15, 10, 30, 45 + i, tzinfo=timezone.utc)
            with patch('status_mcp_server.datetime.datetime') as mock_datetime:
                mock_datetime.now.return_value = mock_timestamp
                mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
                
                # Call report_status tool
                result = server.report_status(
                    status=test_case["status"],
                    details=test_case["details"],
                    task_description=test_case["task_description"]
                )
                
                # Verify result indicates success
                assert result["success"] is True, f"Status report should succeed for status '{test_case['status']}'"
                created_files.append(result["file_created"])
        
        # Verify that multiple files were created
        claude_files = list(claude_dir.glob("status_*.json"))
        assert len(claude_files) == 3, f"Expected 3 status files, found {len(claude_files)}"
        
        # Verify each file contains correct status information
        for i, (test_case, file_path) in enumerate(zip(test_cases, created_files)):
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = json.load(f)
            
            assert file_content["status"] == test_case["status"], f"File {i} should contain correct status"
            assert file_content["details"] == test_case["details"], f"File {i} should contain correct details"
            assert file_content["task_description"] == test_case["task_description"], f"File {i} should contain correct task_description"
    
    def test_status_server_has_required_mcp_tool_decoration(self, tmp_path, monkeypatch):
        """
        Test that the StatusServer report_status method is properly decorated as an MCP tool.
        
        Given the StatusServer class,
        when examining the report_status method,
        then it should be decorated with @Tool() and have proper MCP tool metadata.
        
        This test will initially fail because the StatusServer class doesn't exist yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Change to temporary directory to isolate test
        monkeypatch.chdir(tmp_path)
        
        # Import StatusServer class to test
        try:
            from status_mcp_server import StatusServer
        except ImportError:
            pytest.fail("Cannot import StatusServer from status_mcp_server.py - file doesn't exist yet")
        
        # Import MCP Tool decorator to verify proper decoration
        try:
            from mcp.server.fastmcp import FastMCP
        except ImportError:
            pytest.skip("MCP Python SDK not available - skipping tool decoration test")
        
        # Create StatusServer instance
        server = StatusServer()
        
        # Verify that StatusServer inherits from or uses FastMCP
        # The server should either inherit from FastMCP or use FastMCP instance
        assert hasattr(server, 'report_status'), "StatusServer should have report_status method"
        
        # Verify the method is properly decorated as a tool
        report_status_method = getattr(server, 'report_status')
        assert callable(report_status_method), "report_status should be callable"
        
        # Check for MCP tool metadata (this varies by implementation approach)
        # The exact verification depends on how the tool is decorated
        # At minimum, it should be callable and properly registered
        
        # If using FastMCP, verify it's properly configured
        if hasattr(server, '_mcp'):
            # Server uses internal FastMCP instance
            mcp_instance = server._mcp
            assert isinstance(mcp_instance, FastMCP), "Server should use FastMCP instance"
        elif isinstance(server, FastMCP):
            # Server inherits from FastMCP directly
            pass
        else:
            pytest.fail("StatusServer should either use FastMCP instance or inherit from FastMCP")
        
        # Verify required parameters for report_status tool
        import inspect
        signature = inspect.signature(report_status_method)
        
        expected_params = {'status', 'details', 'task_description'}
        actual_params = set(signature.parameters.keys())
        
        # Remove 'self' if present (for instance methods)
        actual_params.discard('self')
        
        assert expected_params.issubset(actual_params), f"report_status should accept parameters {expected_params}, got {actual_params}"


class TestMCPStatusServerHealthCheck:
    """Test suite for the StatusServer MCP server health check functionality."""
    
    def test_health_check_tool_exists_and_returns_status(self, tmp_path, monkeypatch):
        """
        Test that the StatusServer has a health_check tool that returns server health information.
        
        Given a StatusServer instance,
        when the health_check tool is called,
        then it should return health status information including:
        - server status (healthy/unhealthy)
        - uptime information
        - last request time
        - memory usage
        
        This test will initially fail because the health_check tool doesn't exist yet.
        This is the RED phase of TDD - the test must fail first.
        """
        # Change to temporary directory to isolate test
        monkeypatch.chdir(tmp_path)
        
        # Import StatusServer class to test
        try:
            from status_mcp_server import StatusServer
        except ImportError:
            pytest.fail("Cannot import StatusServer from status_mcp_server.py - file doesn't exist yet")
        
        # Create StatusServer instance
        server = StatusServer()
        
        # Verify that the server has the health_check tool
        assert hasattr(server, 'health_check'), "StatusServer should have health_check method"
        
        # Verify that health_check is callable
        health_check_method = getattr(server, 'health_check')
        assert callable(health_check_method), "health_check should be callable"
        
        # Mock current time for consistent testing
        mock_start_time = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
        mock_current_time = datetime(2024, 1, 15, 10, 30, 45, tzinfo=timezone.utc)
        
        with patch('status_mcp_server.datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_current_time
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            # Call health_check tool
            result = server.health_check()
        
        # Verify that the tool returns a dictionary
        assert isinstance(result, dict), "health_check should return a dictionary"
        
        # Verify required fields in health check response
        required_fields = {"status", "uptime_seconds", "last_request_time", "memory_usage_mb"}
        actual_fields = set(result.keys())
        
        assert required_fields.issubset(actual_fields), f"health_check should return fields {required_fields}, got {actual_fields}"
        
        # Verify field types and values
        assert result["status"] in ["healthy", "unhealthy"], f"Status should be 'healthy' or 'unhealthy', got '{result['status']}'"
        assert isinstance(result["uptime_seconds"], (int, float)), "uptime_seconds should be a number"
        assert result["uptime_seconds"] >= 0, "uptime_seconds should be non-negative"
        
        # Verify timestamp format for last_request_time (should be ISO 8601)
        last_request_time = result["last_request_time"]
        if last_request_time is not None:
            try:
                # Should be parseable as ISO timestamp
                parsed_time = datetime.fromisoformat(last_request_time.replace('Z', '+00:00'))
                assert isinstance(parsed_time, datetime), "last_request_time should be valid ISO timestamp"
            except ValueError:
                pytest.fail(f"last_request_time '{last_request_time}' is not in valid ISO 8601 format")
        
        # Verify memory usage
        assert isinstance(result["memory_usage_mb"], (int, float)), "memory_usage_mb should be a number"
        assert result["memory_usage_mb"] > 0, "memory_usage_mb should be positive"
        
        # Verify server name is included if available
        if "server_name" in result:
            assert isinstance(result["server_name"], str), "server_name should be a string"
            assert len(result["server_name"]) > 0, "server_name should not be empty"