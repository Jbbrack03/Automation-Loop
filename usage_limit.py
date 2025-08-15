"""Usage limit handling module.

This module provides functions for parsing usage limit error messages
and calculating wait times until usage can resume.
"""

import datetime
import json
import re
import time
from typing import Any, Dict, Optional, Union, TypedDict

import pytz

from config import (
    MIN_WAIT_TIME,
    USAGE_LIMIT_TIME_PATTERN,
    HOURS_12_CLOCK_CONVERSION,
    MIDNIGHT_HOUR_12_FORMAT,
    NOON_HOUR_12_FORMAT
)


class UsageLimitUnixResult(TypedDict):
    """Type definition for usage limit error result with Unix timestamp format."""
    reset_at: Union[int, float]
    format: str


class UsageLimitNaturalResult(TypedDict):
    """Type definition for usage limit error result with natural language format."""
    reset_time: str
    timezone: str
    format: str


# Union type for all possible usage limit result formats
UsageLimitResult = Union[UsageLimitUnixResult, UsageLimitNaturalResult]


def _parse_json_error_format(error_message: str) -> Optional[UsageLimitUnixResult]:
    """Parse JSON format usage limit error message.
    
    Args:
        error_message: The error message string that might be JSON
        
    Returns:
        Dictionary with unix_timestamp format result if valid JSON with reset_at,
        None if not valid JSON or doesn't contain reset_at field
    """
    try:
        json_data = json.loads(error_message)
        if isinstance(json_data, dict) and "reset_at" in json_data:
            return {
                "reset_at": json_data["reset_at"],
                "format": "unix_timestamp"
            }
    except (json.JSONDecodeError, ValueError):
        # Not JSON or parsing failed
        pass
    return None


def _parse_natural_language_format(error_message: str) -> Optional[UsageLimitNaturalResult]:
    """Parse natural language format usage limit error message.
    
    Args:
        error_message: The error message string to parse with regex
        
    Returns:
        Dictionary with natural_language format result if pattern matches,
        None if no match found
    """
    time_pattern_match = re.search(USAGE_LIMIT_TIME_PATTERN, error_message)
    
    if time_pattern_match:
        parsed_reset_time = time_pattern_match.group(1)
        parsed_timezone = time_pattern_match.group(2)
        return _create_usage_limit_result(parsed_reset_time, parsed_timezone)
    
    return None


def _create_usage_limit_result(reset_time: str = "", timezone: str = "", format_type: str = "natural_language") -> UsageLimitNaturalResult:
    """Create a standardized usage limit error result dictionary.
    
    This helper function ensures consistent structure across all parsing results,
    providing a single point of control for the result format.
    
    Args:
        reset_time: The time when usage can resume (e.g., "7pm"). Defaults to empty string.
        timezone: The timezone specification (e.g., "America/Chicago"). Defaults to empty string.
        format_type: The format type identifier ("natural_language" or "unix_timestamp").
                    Defaults to "natural_language".
        
    Returns:
        Dictionary with standardized keys and values for downstream processing.
        
    Example:
        >>> _create_usage_limit_result("7pm", "America/Chicago")
        {'reset_time': '7pm', 'timezone': 'America/Chicago', 'format': 'natural_language'}
    """
    return {
        "reset_time": reset_time,
        "timezone": timezone,
        "format": format_type
    }


def parse_usage_limit_error(error_message: str) -> UsageLimitResult:
    """Parse usage limit error message to extract reset time information.
    
    This function parses usage limit error messages from Claude API in two formats:
    1. JSON format with unix timestamp (e.g., {"reset_at": 1737000000})
    2. Natural language format (e.g., "try again at 7pm (America/Chicago)")
    
    Args:
        error_message: The error message string from Claude API. Must be a non-empty string.
        
    Returns:
        Dictionary containing parsed reset time information:
        - For JSON format: {"reset_at": timestamp, "format": "unix_timestamp"}
        - For natural language: {"reset_time": "7pm", "timezone": "America/Chicago", "format": "natural_language"}
        - For no match: {"reset_time": "", "timezone": "", "format": "natural_language"}
        
    Example:
        >>> parse_usage_limit_error('{"reset_at": 1737000000}')
        {'reset_at': 1737000000, 'format': 'unix_timestamp'}
        
        >>> parse_usage_limit_error("You can try again at 7pm (America/Chicago).")
        {'reset_time': '7pm', 'timezone': 'America/Chicago', 'format': 'natural_language'}
        
        >>> parse_usage_limit_error("Some other error message")
        {'reset_time': '', 'timezone': '', 'format': 'natural_language'}
    
    Note:
        Returns empty values for reset_time and timezone if no match is found,
        while maintaining consistent structure for downstream processing.
    """
    # Input validation
    if not error_message or not isinstance(error_message, str):
        return _create_usage_limit_result()
    
    # Try to parse as JSON first
    json_result = _parse_json_error_format(error_message)
    if json_result is not None:
        return json_result
    
    # Fall back to natural language parsing
    natural_language_result = _parse_natural_language_format(error_message)
    if natural_language_result is not None:
        return natural_language_result
    
    # If no match found, return empty values (minimal implementation)
    return _create_usage_limit_result()


def _validate_reset_info_structure(parsed_reset_info: Any) -> None:
    """Validate that parsed_reset_info is a dictionary with proper structure.
    
    Args:
        parsed_reset_info: The input to validate
        
    Raises:
        ValueError: If parsed_reset_info is not a dictionary with required format
    """
    if not isinstance(parsed_reset_info, dict):
        raise ValueError("parsed_reset_info must be a dictionary")
    
    if "format" not in parsed_reset_info:
        raise ValueError("parsed_reset_info must contain 'format' key")


def _calculate_unix_timestamp_wait(parsed_reset_info: UsageLimitUnixResult) -> int:
    """Calculate wait time for Unix timestamp format.
    
    Args:
        parsed_reset_info: Dictionary containing 'reset_at' key with Unix timestamp
        
    Returns:
        Number of seconds to wait until reset time
        
    Raises:
        KeyError: If 'reset_at' key is missing
        ValueError: If reset_at is not a numeric value
    """
    if "reset_at" not in parsed_reset_info:
        raise KeyError("parsed_reset_info must contain 'reset_at' key for unix_timestamp format")
    
    # Extract and validate reset timestamp
    reset_at = parsed_reset_info["reset_at"]
    if not isinstance(reset_at, (int, float)):
        raise ValueError("reset_at must be a numeric timestamp")
    
    # Get current time and calculate difference
    current_time = time.time()
    wait_seconds = int(reset_at - current_time)
    
    # Return at least MIN_WAIT_TIME seconds if reset time is in the past
    # This provides a safety buffer for potential clock skew or timing issues
    if wait_seconds < 0:
        return MIN_WAIT_TIME
    
    return wait_seconds


def _parse_time_string_to_24hour(reset_time_str: str) -> int:
    """Parse time string and convert to 24-hour format.
    
    Handles formats like "7pm", "7am", "19", "7:30pm" etc.
    
    Args:
        reset_time_str: Time string to parse
        
    Returns:
        Hour in 24-hour format (0-23)
        
    Raises:
        ValueError: If time string format is invalid
    """
    reset_time_str = reset_time_str.lower().strip()
    
    try:
        if reset_time_str.endswith("pm"):
            hour = int(reset_time_str[:-2])
            if hour != NOON_HOUR_12_FORMAT:
                hour += HOURS_12_CLOCK_CONVERSION
        elif reset_time_str.endswith("am"):
            hour = int(reset_time_str[:-2])
            if hour == MIDNIGHT_HOUR_12_FORMAT:
                hour = 0
        else:
            # Assume 24-hour format
            hour = int(reset_time_str)
        
        # Validate hour range
        if not 0 <= hour <= 23:
            raise ValueError(f"Hour must be between 0 and 23, got {hour}")
            
        return hour
    except (ValueError, IndexError) as e:
        raise ValueError(f"Invalid time format '{reset_time_str}': {e}")


def _calculate_natural_language_wait(parsed_reset_info: UsageLimitNaturalResult) -> int:
    """Calculate wait time for natural language format.
    
    Args:
        parsed_reset_info: Dictionary containing 'reset_time' and 'timezone' keys
        
    Returns:
        Number of seconds to wait until reset time
        
    Raises:
        KeyError: If required keys are missing
        ValueError: If timezone is invalid or time format is incorrect
    """
    # Validate required keys
    if "reset_time" not in parsed_reset_info or "timezone" not in parsed_reset_info:
        raise KeyError("parsed_reset_info must contain 'reset_time' and 'timezone' keys for natural_language format")
    
    reset_time_str = parsed_reset_info["reset_time"]
    timezone_str = parsed_reset_info["timezone"]
    
    # Parse timezone
    try:
        tz = pytz.timezone(timezone_str)
    except pytz.exceptions.UnknownTimeZoneError:
        raise ValueError(f"Invalid timezone: {timezone_str}")
    
    # Get current time in the specified timezone
    current_dt = datetime.datetime.now(tz)
    
    # Parse reset time to 24-hour format
    hour = _parse_time_string_to_24hour(reset_time_str)
    
    # Create reset datetime for today
    reset_dt = current_dt.replace(hour=hour, minute=0, second=0, microsecond=0)
    
    # If reset time is earlier than current time, use next day
    if reset_dt <= current_dt:
        reset_dt += datetime.timedelta(days=1)
    
    # Calculate seconds difference
    wait_seconds = int((reset_dt - current_dt).total_seconds())
    
    return max(wait_seconds, MIN_WAIT_TIME)


def calculate_wait_time(parsed_reset_info: UsageLimitResult) -> int:
    """Calculate seconds to wait until reset time for Unix timestamp or natural language format.
    
    This function handles the timing calculation for Claude usage limit resets,
    ensuring safe retry behavior even when reset times are in the past.
    
    Args:
        parsed_reset_info: Dictionary from parse_usage_limit_error containing:
            For unix_timestamp format:
                - reset_at: Unix timestamp (int or float) when usage can resume
                - format: "unix_timestamp"
            For natural_language format:
                - reset_time: Time string like "7pm"
                - timezone: Timezone string like "America/Chicago"
                - format: "natural_language"
    
    Returns:
        Number of seconds to wait until reset time. Returns at least MIN_WAIT_TIME
        seconds if the reset time is in the past for safety. Always returns a
        non-negative integer.
        
    Raises:
        KeyError: If parsed_reset_info missing required keys for the format
        ValueError: If values are not valid for the format
    """
    # Validate input structure first
    _validate_reset_info_structure(parsed_reset_info)
    
    # Determine format type and delegate to appropriate handler
    format_type = parsed_reset_info.get("format", "unix_timestamp")
    
    if format_type == "unix_timestamp":
        return _calculate_unix_timestamp_wait(parsed_reset_info)
    elif format_type == "natural_language":
        return _calculate_natural_language_wait(parsed_reset_info)
    else:
        raise ValueError(f"Unsupported format type: {format_type}. Supported formats: 'unix_timestamp', 'natural_language'")


def parse_timestamp_to_datetime(timestamp: Union[int, float], 
                               timezone: Optional[str] = None) -> Optional[datetime.datetime]:
    """Parse a Unix timestamp to a datetime object with optional timezone.
    
    Args:
        timestamp: Unix timestamp as int or float
        timezone: Optional timezone string (e.g., "America/Chicago")
        
    Returns:
        datetime object or None if conversion fails
    """
    try:
        # Convert timestamp to datetime in UTC
        dt = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
        
        # Convert to specified timezone if provided
        if timezone:
            try:
                tz = pytz.timezone(timezone)
                dt = dt.astimezone(tz)
            except pytz.exceptions.UnknownTimeZoneError:
                return None
                
        return dt
    except (ValueError, OSError, OverflowError):
        return None