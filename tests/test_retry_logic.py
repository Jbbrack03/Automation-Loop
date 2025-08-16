"""
Tests for exponential backoff retry logic in command execution.

This test suite validates the implementation of retry logic with exponential backoff
for external command calls, specifically focusing on the run_claude_command function
in command_executor.py.

Following TDD principles, this test is written before the retry implementation exists
(RED phase) to define the expected behavior:

1. Retry on transient failures (network errors, timeouts)
2. Exponential backoff between retries (e.g., 1s, 2s, 4s, 8s)
3. Adding jitter to retry delays to prevent thundering herd
4. Respecting max_retries limit
5. Not retrying on permanent failures

The test will initially fail because:
- run_claude_command currently has no retry mechanism beyond usage limit handling
- No exponential backoff configuration exists
- No jitter is applied to retry delays
- No configurable retry parameters

This is the RED phase of TDD - the test must fail first.
"""

import json
import subprocess
import time
import pytest
from unittest.mock import Mock, MagicMock, patch, call
from command_executor import run_claude_command, CommandExecutionError, CommandTimeoutError


class TestExponentialBackoffRetryLogic:
    """Test suite for exponential backoff retry logic in command execution."""
    
    def test_run_claude_command_implements_exponential_backoff_retry_with_jitter_and_configurable_parameters(self):
        """
        Test that run_claude_command implements comprehensive exponential backoff retry logic.
        
        This test validates the complete retry mechanism with exponential backoff:
        1. Configurable max_retries parameter (default: 3)
        2. Exponential backoff timing: base_delay * (2 ^ attempt_number)
        3. Jitter applied to prevent thundering herd: delay +/- random(0, jitter_factor * delay)
        4. Retry only on transient failures (network errors, timeouts)
        5. No retry on permanent failures (HTTP 4xx errors, JSON decode errors)
        6. Respect max_retries limit
        
        Expected behavior:
        - First attempt: immediate execution
        - First retry: wait ~1s (base_delay=1s, with jitter)
        - Second retry: wait ~2s (1s * 2^1, with jitter)  
        - Third retry: wait ~4s (1s * 2^2, with jitter)
        - Fourth retry: wait ~8s (1s * 2^3, with jitter)
        - After max_retries (3), should raise the final exception
        
        Jitter calculation:
        - jitter_factor = 0.1 (10% of delay)
        - actual_delay = base_delay * (2^attempt) +/- random(0, jitter_factor * calculated_delay)
        
        The test will initially fail because:
        1. run_claude_command has no retry_config parameter
        2. No RetryConfig class exists for configuration
        3. No exponential backoff timing implementation
        4. No jitter calculation for delay randomization
        5. No retry attempt counter or logging
        6. No distinction between retryable and non-retryable errors
        
        This is the RED phase of TDD - the test must fail first.
        """
        # Test scenario: Simulate transient network failures followed by success
        
        # Configure retry behavior - this configuration should be possible
        retry_config = {
            'max_retries': 3,
            'base_delay': 1.0,  # 1 second base delay
            'jitter_factor': 0.1,  # 10% jitter
            'retryable_exceptions': (
                subprocess.SubprocessError,
                CommandTimeoutError,
                CommandExecutionError  # Only certain CommandExecutionErrors should be retryable
            )
        }
        
        # Mock time.sleep to capture retry delays and verify exponential backoff
        with patch('time.sleep') as mock_sleep, \
             patch('command_executor._execute_claude_subprocess') as mock_subprocess, \
             patch('command_executor._wait_for_completion_with_context') as mock_wait, \
             patch('random.uniform') as mock_random:
            
            # Configure random jitter to be predictable for testing
            mock_random.return_value = 0.05  # 5% jitter (within 10% factor)
            
            # Configure subprocess to fail 3 times, then succeed
            subprocess_error = subprocess.SubprocessError("Network connection failed")
            success_result = Mock()
            success_result.stdout = '{"status": "success", "output": "Command completed"}'
            success_result.stderr = ""
            success_result.returncode = 0
            
            mock_subprocess.side_effect = [
                subprocess_error,  # First attempt fails
                subprocess_error,  # Second attempt fails  
                subprocess_error,  # Third attempt fails
                success_result     # Fourth attempt succeeds
            ]
            
            # Execute the command with retry configuration
            # This should be the new signature after implementation:
            result = run_claude_command("/continue", retry_config=retry_config)
            
            # Verify the command eventually succeeded
            assert result == {"status": "success", "output": "Command completed"}
            
            # Verify all retry attempts were made (3 retries + 1 initial = 4 total calls)
            assert mock_subprocess.call_count == 4
            
            # Verify exponential backoff delays were applied with jitter
            expected_delays = [
                1.0 + 0.05,  # First retry: 1s base + 5% jitter (0.05s)
                2.0 + 0.10,  # Second retry: 2s (1s * 2^1) + 5% of 2s jitter (0.10s)
                4.0 + 0.20   # Third retry: 4s (1s * 2^2) + 5% of 4s jitter (0.20s)
            ]
            
            actual_sleep_calls = [call_args[0][0] for call_args in mock_sleep.call_args_list]
            assert len(actual_sleep_calls) == 3  # Three retry delays
            
            # Verify delays are approximately correct (within jitter bounds)
            for i, (expected, actual) in enumerate(zip(expected_delays, actual_sleep_calls)):
                base_delay = 1.0 * (2 ** i)
                jitter_range = 0.1 * base_delay
                min_delay = base_delay - jitter_range
                max_delay = base_delay + jitter_range
                
                assert min_delay <= actual <= max_delay, \
                    f"Retry {i+1}: delay {actual} not in expected range [{min_delay}, {max_delay}]"
            
            # Verify wait_for_completion was called for each attempt
            assert mock_wait.call_count == 4
            
            
    def test_run_claude_command_respects_max_retries_limit_and_raises_final_exception(self):
        """
        Test that retry logic respects max_retries limit and raises the final exception.
        
        This test validates:
        1. Retry attempts do not exceed max_retries
        2. The final exception from the last attempt is raised
        3. All retry delays are applied according to exponential backoff
        4. Proper error context is maintained throughout retries
        
        The test will initially fail because the retry mechanism doesn't exist.
        """
        retry_config = {
            'max_retries': 2,  # Only 2 retries allowed
            'base_delay': 0.5,
            'jitter_factor': 0.0  # No jitter for predictable testing
        }
        
        with patch('time.sleep') as mock_sleep, \
             patch('command_executor._execute_claude_subprocess') as mock_subprocess, \
             patch('command_executor._wait_for_completion_with_context') as mock_wait:
            
            # Configure all attempts to fail
            network_error = subprocess.SubprocessError("Persistent network failure")
            mock_subprocess.side_effect = network_error
            
            # Execute command and expect final exception
            with pytest.raises(CommandExecutionError) as exc_info:
                run_claude_command("/validate", retry_config=retry_config)
            
            # Verify the exception contains context about retries
            assert "after 2 retries" in str(exc_info.value) or "retry attempts exhausted" in str(exc_info.value)
            
            # Verify correct number of attempts (1 initial + 2 retries = 3 total)
            assert mock_subprocess.call_count == 3
            
            # Verify exponential backoff delays (0.5s, 1.0s)
            expected_delays = [0.5, 1.0]  # base_delay * 2^0, base_delay * 2^1
            actual_delays = [call_args[0][0] for call_args in mock_sleep.call_args_list]
            assert actual_delays == expected_delays


    def test_run_claude_command_does_not_retry_permanent_failures(self):
        """
        Test that permanent failures are not retried.
        
        This test validates:
        1. JSON decode errors are not retried (permanent failure)
        2. HTTP 4xx client errors are not retried (permanent failure)
        3. Invalid command errors are not retried (permanent failure)
        4. Only the initial attempt is made for permanent failures
        
        The test will initially fail because error classification doesn't exist.
        """
        retry_config = {
            'max_retries': 3,
            'base_delay': 1.0,
            'jitter_factor': 0.1
        }
        
        with patch('time.sleep') as mock_sleep, \
             patch('command_executor._execute_claude_subprocess') as mock_subprocess, \
             patch('command_executor._wait_for_completion_with_context') as mock_wait:
            
            # Configure subprocess to return invalid JSON (permanent failure)
            bad_result = Mock()
            bad_result.stdout = 'invalid json response'
            bad_result.stderr = ""
            bad_result.returncode = 0
            mock_subprocess.return_value = bad_result
            
            # Execute command and expect immediate failure without retries
            with pytest.raises(Exception):  # JSONParseError or similar
                run_claude_command("/continue", retry_config=retry_config)
            
            # Verify only one attempt was made (no retries for permanent failures)
            assert mock_subprocess.call_count == 1
            assert mock_sleep.call_count == 0  # No sleep calls for retries


    def test_run_claude_command_applies_jitter_to_prevent_thundering_herd(self):
        """
        Test that jitter is properly applied to retry delays.
        
        This test validates:
        1. Jitter adds randomness to delay calculations  
        2. Jitter stays within configured bounds (jitter_factor)
        3. Different random values produce different delays
        4. Base exponential backoff timing is preserved
        
        The test will initially fail because jitter implementation doesn't exist.
        """
        retry_config = {
            'max_retries': 2,
            'base_delay': 2.0,
            'jitter_factor': 0.2  # 20% jitter
        }
        
        with patch('time.sleep') as mock_sleep, \
             patch('command_executor._execute_claude_subprocess') as mock_subprocess, \
             patch('command_executor._wait_for_completion_with_context') as mock_wait, \
             patch('random.uniform') as mock_random:
            
            # Configure different jitter values for each retry
            mock_random.side_effect = [0.1, -0.15]  # +10%, -15% of delay
            
            # Configure subprocess to fail twice then succeed  
            subprocess_error = subprocess.SubprocessError("Network error")
            success_result = Mock()
            success_result.stdout = '{"status": "success"}'
            success_result.stderr = ""
            mock_subprocess.side_effect = [subprocess_error, subprocess_error, success_result]
            
            # Execute command
            result = run_claude_command("/update", retry_config=retry_config)
            
            # Verify jitter was applied correctly
            # First retry: base_delay=2.0, jitter=+0.1 (10% of 2.0) = 2.0 + 0.2 = 2.2
            # Second retry: base_delay=4.0, jitter=-0.15 (15% of 4.0) = 4.0 - 0.6 = 3.4
            expected_delays = [2.2, 3.4]
            actual_delays = [call_args[0][0] for call_args in mock_sleep.call_args_list]
            
            assert len(actual_delays) == 2
            assert actual_delays[0] == pytest.approx(2.2, rel=1e-3)
            assert actual_delays[1] == pytest.approx(3.4, rel=1e-3)
            
            # Verify random.uniform was called with correct jitter bounds
            expected_jitter_calls = [
                call(-0.4, 0.4),  # 20% of 2.0 = ±0.4
                call(-0.8, 0.8)   # 20% of 4.0 = ±0.8  
            ]
            mock_random.assert_has_calls(expected_jitter_calls)


    def test_run_claude_command_uses_default_retry_configuration_when_not_specified(self):
        """
        Test that sensible defaults are used when no retry configuration is provided.
        
        This test validates:
        1. Default retry behavior is enabled automatically
        2. Default parameters provide reasonable retry behavior
        3. Backward compatibility is maintained for existing calls
        
        Expected defaults:
        - max_retries: 3
        - base_delay: 1.0 seconds
        - jitter_factor: 0.1 (10%)
        - retryable_exceptions: network and timeout errors
        
        The test will initially fail because default retry configuration doesn't exist.
        """
        with patch('time.sleep') as mock_sleep, \
             patch('command_executor._execute_claude_subprocess') as mock_subprocess, \
             patch('command_executor._wait_for_completion_with_context') as mock_wait, \
             patch('random.uniform') as mock_random:
            
            # Configure predictable jitter for testing
            mock_random.return_value = 0.0  # No jitter for simpler verification
            
            # Configure two failures then success
            subprocess_error = subprocess.SubprocessError("Connection timeout")
            success_result = Mock()
            success_result.stdout = '{"status": "success"}'
            success_result.stderr = ""
            mock_subprocess.side_effect = [subprocess_error, subprocess_error, success_result]
            
            # Execute command without retry_config parameter (should use defaults)
            result = run_claude_command("/continue")
            
            # Verify default retry behavior was applied
            assert mock_subprocess.call_count == 3  # 1 initial + 2 retries (using default max_retries=3)
            assert mock_sleep.call_count == 2  # 2 retry delays
            
            # Verify default exponential backoff timing (base_delay=1.0)
            expected_delays = [1.0, 2.0]  # 1s, 2s (no jitter in this test)
            actual_delays = [call_args[0][0] for call_args in mock_sleep.call_args_list]
            assert actual_delays == expected_delays
            
            # Verify command succeeded  
            assert result == {"status": "success"}


    def test_run_claude_command_logs_retry_attempts_with_exponential_backoff_details(self):
        """
        Test that retry attempts are properly logged with timing and attempt details.
        
        This test validates:
        1. Each retry attempt is logged with attempt number
        2. Calculated delays (including jitter) are logged
        3. Exception details are logged for failed attempts
        4. Final success/failure is logged appropriately
        
        The test will initially fail because retry logging doesn't exist.
        """
        retry_config = {
            'max_retries': 2,
            'base_delay': 1.0,
            'jitter_factor': 0.1
        }
        
        with patch('time.sleep') as mock_sleep, \
             patch('command_executor._execute_claude_subprocess') as mock_subprocess, \
             patch('command_executor._wait_for_completion_with_context') as mock_wait, \
             patch('random.uniform') as mock_random, \
             patch('command_executor.LOGGERS') as mock_loggers:
            
            # Configure mock logger
            mock_logger = Mock()
            mock_loggers.get.return_value = mock_logger
            mock_random.return_value = 0.05  # 5% jitter
            
            # Configure one failure then success
            subprocess_error = subprocess.SubprocessError("Network timeout")
            success_result = Mock()
            success_result.stdout = '{"status": "success"}'
            success_result.stderr = ""
            mock_subprocess.side_effect = [subprocess_error, success_result]
            
            # Execute command
            result = run_claude_command("/validate", retry_config=retry_config)
            
            # Verify retry logging occurred
            log_calls = mock_logger.warning.call_args_list + mock_logger.info.call_args_list
            log_messages = [str(call) for call in log_calls]
            
            # Verify retry attempt was logged
            retry_logged = any("retry attempt 1" in msg.lower() or "retrying" in msg.lower() 
                             for msg in log_messages)
            assert retry_logged, f"Retry attempt not logged. Log calls: {log_messages}"
            
            # Verify delay calculation was logged
            delay_logged = any("delay" in msg.lower() and "1." in msg for msg in log_messages)
            assert delay_logged, f"Delay calculation not logged. Log calls: {log_messages}"
            
            # Verify final success was logged
            success_logged = any("success" in msg.lower() and "retry" in msg.lower() 
                                for msg in log_messages)
            assert success_logged, f"Final success not logged. Log calls: {log_messages}"