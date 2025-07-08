"""
Unit tests for LoggerService
"""

import pytest
import time
from unittest.mock import patch, MagicMock
from src.services.logger_service import LoggerService, LogLevel
import asyncio


class TestLoggerService:
    """Test cases for LoggerService"""

    def setup_method(self):
        """Reset logger instance before each test"""
        # Reset singleton instance
        LoggerService._instance = None
        LoggerService._initialized = False

    def test_singleton_pattern(self):
        """Test that LoggerService follows singleton pattern"""
        logger1 = LoggerService()
        logger2 = LoggerService()
        assert logger1 is logger2

    def test_get_instance_method(self):
        """Test get_instance class method"""
        logger1 = LoggerService.get_instance()
        logger2 = LoggerService.get_instance()
        assert logger1 is logger2

    def test_sync_logging_methods(self):
        """Test all sync logging methods"""
        logger = LoggerService()
        
        # Test all log levels
        with patch('builtins.print') as mock_print:
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")
            logger.critical("Critical message")
            
            # Verify all methods were called (at least 5 calls for our test messages)
            assert mock_print.call_count >= 5
            
            # Verify our specific messages were logged
            all_calls = str(mock_print.call_args_list)
            assert "Debug message" in all_calls
            assert "Info message" in all_calls
            assert "Warning message" in all_calls
            assert "Error message" in all_calls
            assert "Critical message" in all_calls

    def test_sync_logging_with_context(self):
        """Test sync logging with context data"""
        logger = LoggerService()
        
        with patch('builtins.print') as mock_print:
            context = {"user_id": 123, "action": "test"}
            logger.info("Test message", context)
            
            # Verify the call was made
            assert mock_print.call_count == 1
            call_args = mock_print.call_args[0][0]
            assert "Test message" in call_args
            assert "user_id" in call_args
            assert "123" in call_args

    def test_async_logging_methods(self):
        """Test all async logging methods"""
        logger = LoggerService()
        
        # Test all async log levels
        with patch.object(logger, '_queue_log_entry') as mock_queue:
            logger.debug_async("Debug message")
            logger.info_async("Info message")
            logger.warning_async("Warning message")
            logger.error_async("Error message")
            logger.critical_async("Critical message")
            
            # Verify all async methods queued entries
            assert mock_queue.call_count == 5

    def test_async_logging_with_context(self):
        """Test async logging with context data"""
        logger = LoggerService()
        
        with patch.object(logger, '_queue_log_entry') as mock_queue:
            context = {"user_id": 456, "action": "async_test"}
            logger.info_async("Async test message", context)
            
            # Verify the call was made with correct parameters
            assert mock_queue.call_count == 1
            call_args = mock_queue.call_args[0]
            assert call_args[0] == LogLevel.INFO
            assert call_args[1] == "Async test message"
            assert call_args[2] == context

    def test_log_exception_sync(self):
        """Test sync exception logging"""
        logger = LoggerService()
        
        with patch('builtins.print') as mock_print:
            try:
                raise ValueError("Test exception")
            except ValueError as e:
                logger.log_exception("Exception occurred", e)
            
            # Verify exception was logged
            assert mock_print.call_count >= 1

    def test_log_exception_async(self):
        """Test async exception logging"""
        logger = LoggerService()
        
        with patch.object(logger, '_queue_log_entry') as mock_queue:
            try:
                raise ValueError("Test async exception")
            except ValueError as e:
                logger.log_exception_async("Async exception occurred", e)
            
            # Verify exception was queued (should be 2 calls: message + exception details)
            assert mock_queue.call_count == 2

    def test_async_worker_startup(self):
        """Test that async worker starts when needed"""
        logger = LoggerService()
        
        with patch('threading.Thread') as mock_thread:
            logger._start_async_worker()
            
            # Verify worker thread was started
            mock_thread.assert_called_once()
            assert mock_thread.return_value.start.called

    def test_async_worker_not_started_twice(self):
        """Test that async worker doesn't start multiple times"""
        logger = LoggerService()
        
        with patch('threading.Thread') as mock_thread:
            logger._start_async_worker()
            logger._start_async_worker()  # Second call
            
            # Verify worker thread was started only once
            assert mock_thread.call_count == 1

    def test_queue_log_entry_fallback(self):
        """Test that queue failures fall back to sync logging"""
        logger = LoggerService()
        
        with patch.object(logger, '_async_queue') as mock_queue:
            # Make queue.put raise an exception
            mock_queue.put.side_effect = Exception("Queue error")
            
            with patch.object(logger, '_log_to_console') as mock_console:
                with patch.object(logger, '_log_to_file') as mock_file:
                    logger._queue_log_entry(LogLevel.INFO, "Test message")
                    
                    # Verify fallback to sync logging
                    mock_console.assert_called_once()
                    mock_file.assert_called_once()

    def test_log_level_enum(self):
        """Test LogLevel enum values"""
        assert LogLevel.DEBUG.value == "debug"
        assert LogLevel.INFO.value == "info"
        assert LogLevel.WARNING.value == "warning"
        assert LogLevel.ERROR.value == "error"
        assert LogLevel.CRITICAL.value == "critical"

    def test_json_output_format(self):
        """Test JSON output format"""
        logger = LoggerService(json_output=True)
        
        with patch('builtins.print') as mock_print:
            logger.info("Test JSON message", {"key": "value"})
            
            # Verify JSON output
            assert mock_print.call_count == 1
            json_output = mock_print.call_args[0][0]
            
            # Parse JSON and verify structure
            import json
            log_entry = json.loads(json_output)
            assert log_entry["level"] == "INFO"
            assert log_entry["message"] == "Test JSON message"
            assert log_entry["context"]["key"] == "value"
            assert "timestamp" in log_entry
            assert "environment" in log_entry

    def test_json_output_without_context(self):
        """Test JSON output format without context"""
        logger = LoggerService(json_output=True)
        
        with patch('builtins.print') as mock_print:
            logger.info("Test JSON message")
            
            # Verify JSON output
            assert mock_print.call_count == 1
            json_output = mock_print.call_args[0][0]
            
            # Parse JSON and verify structure
            import json
            log_entry = json.loads(json_output)
            assert log_entry["level"] == "INFO"
            assert log_entry["message"] == "Test JSON message"
            assert "context" not in log_entry

    def test_set_json_output_runtime(self):
        """Test changing JSON output setting at runtime"""
        logger = LoggerService(json_output=False)
        
        # Test human-readable format
        with patch('builtins.print') as mock_print:
            logger.info("Test message")
            assert mock_print.call_count == 1
            output = mock_print.call_args[0][0]
            assert "ℹ️" in output  # Human-readable format
            
        # Switch to JSON format
        logger.set_json_output(True)
        
        with patch('builtins.print') as mock_print:
            logger.info("Test JSON message")
            assert mock_print.call_count == 1
            json_output = mock_print.call_args[0][0]
            
            # Verify it's valid JSON
            import json
            log_entry = json.loads(json_output)
            assert log_entry["level"] == "INFO" 

    def test_non_dict_context(self):
        """Test logging with non-dict context (should convert to string and warn)"""
        logger = LoggerService()
        with patch('builtins.print') as mock_print:
            logger.info("Test message", [1, 2, 3])
            # Should print a warning about context type
            assert any("context should be a dict" in str(call) for call in mock_print.call_args_list)
            # Should print the log message
            assert any("Test message" in str(call) for call in mock_print.call_args_list)

    def test_unserializable_context(self):
        """Test logging with unserializable object in context (should fallback to str)"""
        logger = LoggerService()
        class Unserializable:
            pass
        unserializable_obj = Unserializable()
        context = {"bad": unserializable_obj}
        with patch('builtins.print') as mock_print:
            logger.info("Test unserializable context", context)
            # Should print the log message
            assert any("Test unserializable context" in str(call) for call in mock_print.call_args_list)
            # Should not raise

    def test_nested_dict_context(self):
        """Test logging with nested dict context (should pretty print)"""
        logger = LoggerService()
        context = {"outer": {"inner": {"value": 42}}}
        with patch('builtins.print') as mock_print:
            logger.info("Test nested context", context)
            # Should print the log message
            assert any("Test nested context" in str(call) for call in mock_print.call_args_list)
            # Should pretty print nested dict
            assert any("inner" in str(call) for call in mock_print.call_args_list) 

    def test_timing_context_manager(self):
        """Test timing context manager logs start and end with duration"""
        logger = LoggerService()
        with patch.object(logger, 'info') as mock_info:
            with logger.timing('test_operation'):
                time.sleep(0.01)
            # Should log start and finish
            calls = [c[0][0] for c in mock_info.call_args_list]
            assert any('[Timing] Started: test_operation' in call for call in calls)
            assert any('[Timing] Finished: test_operation' in call for call in calls)
            # Check duration in context
            finish_call = mock_info.call_args_list[-1][0][1]
            assert 'operation' in finish_call and finish_call['operation'] == 'test_operation'
            assert 'duration_seconds' in finish_call and finish_call['duration_seconds'] > 0

    def test_timeit_decorator_sync(self):
        """Test timeit decorator for sync function"""
        logger = LoggerService()
        with patch.object(logger, 'info') as mock_info:
            @logger.timeit('decorated_sync')
            def foo():
                time.sleep(0.01)
                return 42
            result = foo()
            assert result == 42
            calls = [c[0][0] for c in mock_info.call_args_list]
            assert any('[Timing] Started: decorated_sync' in call for call in calls)
            assert any('[Timing] Finished: decorated_sync' in call for call in calls)
            finish_call = mock_info.call_args_list[-1][0][1]
            assert 'operation' in finish_call and finish_call['operation'] == 'decorated_sync'
            assert 'duration_seconds' in finish_call and finish_call['duration_seconds'] > 0

    @pytest.mark.asyncio
    async def test_timeit_decorator_async(self):
        """Test timeit decorator for async function"""
        logger = LoggerService()
        with patch.object(logger, 'info') as mock_info:
            @logger.timeit('decorated_async')
            async def bar():
                await asyncio.sleep(0.01)
                return 99
            result = await bar()
            assert result == 99
            calls = [c[0][0] for c in mock_info.call_args_list]
            assert any('[Timing] Started: decorated_async' in call for call in calls)
            assert any('[Timing] Finished: decorated_async' in call for call in calls)
            finish_call = mock_info.call_args_list[-1][0][1]
            assert 'operation' in finish_call and finish_call['operation'] == 'decorated_async'
            assert 'duration_seconds' in finish_call and finish_call['duration_seconds'] > 0 