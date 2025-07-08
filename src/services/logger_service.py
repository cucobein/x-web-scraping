"""
Robust logging service with console and file output
"""

import asyncio
import functools
import glob
import json
import os
import time
import traceback
from contextlib import AbstractContextManager, contextmanager
from datetime import datetime
from enum import Enum
from queue import Queue
from threading import Lock
from typing import Any, Dict, Optional

from src.services.environment_service import EnvironmentService


class LogLevel(Enum):
    """Log levels for different types of messages"""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LoggerService:
    """Logger service for application-wide logging"""

    def __init__(
        self,
        log_file_path: str = "logs/app.log",
        max_file_size_mb: int = 10,
        backup_count: int = 5,
        json_output: bool = False,
        environment_service: Optional[EnvironmentService] = None,
    ):
        """
        Initialize logger service

        Args:
            log_file_path: Path to log file
            max_file_size_mb: Maximum log file size in MB before rotation
            backup_count: Number of backup files to keep
            json_output: Whether to output logs in JSON format for machine parsing
            environment_service: Optional environment service
        """
        self.log_file_path = log_file_path
        self.max_file_size_mb = max_file_size_mb
        self.backup_count = backup_count
        self.json_output = json_output
        self.env_service = environment_service

        # Async logging setup
        self._async_queue = Queue()
        self._queue_lock = Lock()
        self._async_worker_running = False

        # Ensure log directory exists
        self._ensure_log_directory()

    def _get_environment(self) -> str:
        if self.env_service:
            return self.env_service.get_environment()
        return EnvironmentService.get_default_environment()

    def _ensure_log_directory(self):
        """Ensure log directory exists"""
        log_dir = os.path.dirname(self.log_file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

    def _get_backup_filename(self) -> str:
        """Generate a timestamped backup filename for the log file."""
        base, ext = os.path.splitext(self.log_file_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{base}.{timestamp}{ext}"

    def _rotate_log_file(self):
        """Rotate the log file with a timestamped backup, keep only backup_count backups."""
        with self._queue_lock:
            if os.path.exists(self.log_file_path):
                backup_file = self._get_backup_filename()
                os.rename(self.log_file_path, backup_file)
                # Remove old backups if exceeding backup_count
                base, ext = os.path.splitext(self.log_file_path)
                pattern = f"{base}.*{ext}"
                backups = sorted(glob.glob(pattern), reverse=True)
                if len(backups) > self.backup_count:
                    for old_backup in backups[self.backup_count :]:
                        try:
                            os.remove(old_backup)
                        except Exception as e:
                            print(f"⚠️ Failed to remove old log backup: {e}")

    def _check_rotation(self):
        """Check if log file needs rotation (runtime, before every write)."""
        if os.path.exists(self.log_file_path):
            size_mb = os.path.getsize(self.log_file_path) / (1024 * 1024)
            if size_mb >= self.max_file_size_mb:
                self._rotate_log_file()

    def _get_timestamp(self) -> str:
        """Get current timestamp for logging"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _format_json_log(
        self, level: LogLevel, message: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Format log entry as JSON for machine parsing"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level.value.upper(),
            "environment": self._get_environment().upper(),
            "message": message,
        }

        if context is not None:
            if not isinstance(context, dict):
                context = {"context": str(context)}
            log_entry["context"] = context

        try:
            return json.dumps(log_entry, default=str)
        except Exception as e:
            # Fallback to string representation if JSON serialization fails
            print(f"⚠️ LoggerService: Failed to serialize JSON log: {e}")
            return json.dumps(
                {
                    "timestamp": datetime.now().isoformat(),
                    "level": level.value.upper(),
                    "environment": self._get_environment().upper(),
                    "message": message,
                    "context": {
                        "error": "JSON serialization failed",
                        "original_context": str(context),
                    },
                },
                default=str,
            )

    def _start_async_worker(self):
        """Start the async worker if not already running"""
        with self._queue_lock:
            if not self._async_worker_running:
                self._async_worker_running = True
                # Start worker in a separate thread to avoid blocking
                import threading

                worker_thread = threading.Thread(
                    target=self._async_worker_loop, daemon=True
                )
                worker_thread.start()

    def _async_worker_loop(self):
        """Background worker loop to process async log messages"""
        while self._async_worker_running:
            try:
                # Get log entry from queue with timeout
                log_entry = self._async_queue.get(timeout=1.0)
                if log_entry is None:  # Shutdown signal
                    break

                # Process the log entry
                level, message, context = log_entry
                self._log_to_console(level, message, context)
                self._log_to_file(level, message, context)

                self._async_queue.task_done()
            except Exception as e:
                # Don't let worker failures break the app
                print(f"⚠️ Async logger worker error: {e}")
                continue

    def _queue_log_entry(
        self, level: LogLevel, message: str, context: Optional[Dict[str, Any]] = None
    ):
        """Queue a log entry for async processing"""
        try:
            self._start_async_worker()
            self._async_queue.put((level, message, context))
        except Exception as e:
            # Fallback to sync logging if queue fails
            print(f"⚠️ Failed to queue log entry, falling back to sync: {e}")
            self._log_to_console(level, message, context)
            self._log_to_file(level, message, context)

    def _format_message(
        self, level: LogLevel, message: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Format message for logging"""
        timestamp = self._get_timestamp()
        env = self._get_environment()

        # Base message
        formatted = f"[{timestamp}] [{level.value.upper()}] [{env.upper()}] {message}"

        # Add context if provided
        if context is not None:
            if not isinstance(context, dict):
                # Log a warning about improper context usage
                warning_msg = f"LoggerService: context should be a dict, got {type(context).__name__}. Converting to string."
                print(f"⚠️ {warning_msg}")
                context = {"context": str(context)}
            try:
                context_str = json.dumps(context, default=str, indent=2)
            except Exception as e:
                context_str = str(context)
                print(f"⚠️ LoggerService: Failed to serialize context: {e}")
            formatted += f"\n  Context:\n{context_str}"

        return formatted

    def _log_to_console(
        self, level: LogLevel, message: str, context: Optional[Dict[str, Any]] = None
    ):
        """Log message to console with appropriate formatting"""
        if self.json_output:
            # JSON format for machine parsing
            json_log = self._format_json_log(level, message, context)
            print(json_log)
        else:
            # Human-readable format
            formatted_message = self._format_message(level, message, context)

            # Use different colors/prefixes for different levels
            if level == LogLevel.ERROR or level == LogLevel.CRITICAL:
                print(f"❌ {formatted_message}")
            elif level == LogLevel.WARNING:
                print(f"⚠️ {formatted_message}")
            elif level == LogLevel.INFO:
                print(f"ℹ️ {formatted_message}")
            elif level == LogLevel.DEBUG:
                print(f"🔍 {formatted_message}")

            # Add extra spacing for errors and critical messages
            if level in [LogLevel.ERROR, LogLevel.CRITICAL]:
                print()

    def _log_to_file(
        self, level: LogLevel, message: str, context: Optional[Dict[str, Any]] = None
    ):
        """Log message to file, with runtime rotation."""
        try:
            self._check_rotation()
            if self.json_output:
                # JSON format for machine parsing
                json_log = self._format_json_log(level, message, context)
                with open(self.log_file_path, "a", encoding="utf-8") as f:
                    f.write(json_log + "\n")
            else:
                # Human-readable format
                formatted_message = self._format_message(level, message, context)
                with open(self.log_file_path, "a", encoding="utf-8") as f:
                    f.write(formatted_message + "\n")

        except Exception as e:
            # Don't let file logging failures break the app
            print(f"⚠️ Failed to write to log file: {e}")

    def log(
        self, level: LogLevel, message: str, context: Optional[Dict[str, Any]] = None
    ):
        """
        Log message with specified level

        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Log message
            context: Additional context data
        """
        # Log to console
        self._log_to_console(level, message, context)

        # Log to file
        self._log_to_file(level, message, context)

    def debug(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log debug message"""
        self.log(LogLevel.DEBUG, message, context)

    def info(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log info message"""
        self.log(LogLevel.INFO, message, context)

    def warning(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log warning message"""
        self.log(LogLevel.WARNING, message, context)

    def error(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log error message"""
        self.log(LogLevel.ERROR, message, context)

    def critical(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log critical message"""
        self.log(LogLevel.CRITICAL, message, context)

    # Async logging methods
    def log_async(
        self, level: LogLevel, message: str, context: Optional[Dict[str, Any]] = None
    ):
        """
        Log message asynchronously with specified level

        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Log message
            context: Additional context data
        """
        self._queue_log_entry(level, message, context)

    def debug_async(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log debug message asynchronously"""
        self.log_async(LogLevel.DEBUG, message, context)

    def info_async(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log info message asynchronously"""
        self.log_async(LogLevel.INFO, message, context)

    def warning_async(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log warning message asynchronously"""
        self.log_async(LogLevel.WARNING, message, context)

    def error_async(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log error message asynchronously"""
        self.log_async(LogLevel.ERROR, message, context)

    def critical_async(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log critical message asynchronously"""
        self.log_async(LogLevel.CRITICAL, message, context)

    def log_exception(
        self,
        message: str,
        exception: Exception,
        context: Optional[Dict[str, Any]] = None,
    ):
        """Log exception with stack trace"""
        # Format the full error message with stack trace
        timestamp = self._get_timestamp()
        env = self._get_environment()

        # Base error message
        error_msg = (
            f"[{timestamp}] [{LogLevel.ERROR.value.upper()}] [{env.upper()}] {message}"
        )

        # Add exception details
        error_msg += f"\n  Exception: {type(exception).__name__}: {str(exception)}"

        # Add context if provided
        if context is not None:
            if not isinstance(context, dict):
                warning_msg = f"LoggerService: context should be a dict, got {type(context).__name__}. Converting to string."
                print(f"⚠️ {warning_msg}")
                context = {"context": str(context)}
            try:
                context_str = json.dumps(context, default=str, indent=2)
            except Exception as e:
                context_str = str(context)
                print(f"⚠️ LoggerService: Failed to serialize context: {e}")
            error_msg += f"\n  Context:\n{context_str}"

        # Add stack trace
        stack_trace = traceback.format_exc()
        if stack_trace and stack_trace != "NoneType: None\n":
            error_msg += f"\n  Traceback:\n{stack_trace}"

        # Log to console with proper formatting
        print(f"❌ {error_msg}")
        print()

        # Log to file (single line for file)
        file_msg = f"[{timestamp}] [{LogLevel.ERROR.value.upper()}] [{env.upper()}] {message} | Exception: {type(exception).__name__}: {str(exception)}"
        if context is not None:
            if not isinstance(context, dict):
                context = {"context": str(context)}
            try:
                context_str = json.dumps(context, default=str)
            except Exception:
                context_str = str(context)
            file_msg += f" | Context: {context_str}"

        try:
            with open(self.log_file_path, "a", encoding="utf-8") as f:
                f.write(file_msg + "\n")
        except Exception as e:
            print(f"⚠️ Failed to write to log file: {e}")

    def log_exception_async(
        self,
        message: str,
        exception: Exception,
        context: Optional[Dict[str, Any]] = None,
    ):
        """Log exception asynchronously with stack trace"""
        # Ensure context is a dict
        if context is not None and not isinstance(context, dict):
            warning_msg = f"LoggerService: context should be a dict, got {type(context).__name__}. Converting to string."
            print(f"⚠️ {warning_msg}")
            context = {"context": str(context)}
        self._queue_log_entry(LogLevel.ERROR, message, context)
        # Also queue the exception details
        exception_msg = f"Exception: {type(exception).__name__}: {str(exception)}"
        self._queue_log_entry(LogLevel.ERROR, exception_msg, context)

    @contextmanager
    def timing(
        self, operation_name: str, context: Optional[Dict[str, Any]] = None
    ) -> AbstractContextManager:
        """
        Context manager for timing a code block.
        Usage:
            with logger.timing('my_operation'):
                ...
        """
        start = time.perf_counter()
        self.info(f"[Timing] Started: {operation_name}", context)
        try:
            yield
        finally:
            end = time.perf_counter()
            duration = end - start
            timing_context = dict(context) if context else {}
            timing_context.update(
                {"operation": operation_name, "duration_seconds": duration}
            )
            self.info(
                f"[Timing] Finished: {operation_name} (duration: {duration:.4f}s)",
                timing_context,
            )

    def timeit(self, operation_name: str, context: Optional[Dict[str, Any]] = None):
        """
        Decorator for timing a function (sync or async).
        Usage:
            @logger.timeit('my_func')
            def my_func(...): ...
        """

        def decorator(func):
            if asyncio.iscoroutinefunction(func):

                @functools.wraps(func)
                async def async_wrapper(*args, **kwargs):
                    start = time.perf_counter()
                    self.info(f"[Timing] Started: {operation_name}", context)
                    try:
                        result = await func(*args, **kwargs)
                        return result
                    finally:
                        end = time.perf_counter()
                        duration = end - start
                        timing_context = dict(context) if context else {}
                        timing_context.update(
                            {"operation": operation_name, "duration_seconds": duration}
                        )
                        self.info(
                            f"[Timing] Finished: {operation_name} (duration: {duration:.4f}s)",
                            timing_context,
                        )

                return async_wrapper
            else:

                @functools.wraps(func)
                def sync_wrapper(*args, **kwargs):
                    start = time.perf_counter()
                    self.info(f"[Timing] Started: {operation_name}", context)
                    try:
                        result = func(*args, **kwargs)
                        return result
                    finally:
                        end = time.perf_counter()
                        duration = end - start
                        timing_context = dict(context) if context else {}
                        timing_context.update(
                            {"operation": operation_name, "duration_seconds": duration}
                        )
                        self.info(
                            f"[Timing] Finished: {operation_name} (duration: {duration:.4f}s)",
                            timing_context,
                        )

                return sync_wrapper

        return decorator
