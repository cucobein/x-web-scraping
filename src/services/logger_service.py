"""
Robust logging service with console and file output
"""
import os
import json
import traceback
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from pathlib import Path

from src.utils.env_helper import get_environment


class LogLevel(Enum):
    """Log levels for different types of messages"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LoggerService:
    """Robust logging service with console and file output"""
    
    def __init__(self, log_file_path: str = "logs/app.log", max_file_size_mb: int = 10, backup_count: int = 5):
        """
        Initialize logger service
        
        Args:
            log_file_path: Path to log file
            max_file_size_mb: Maximum log file size in MB before rotation
            backup_count: Number of backup files to keep
        """
        self.log_file_path = log_file_path
        self.max_file_size_mb = max_file_size_mb
        self.backup_count = backup_count
        
        # Ensure log directory exists
        self._ensure_log_directory()
        
        # Check if log file needs rotation
        self._check_rotation()
        
    def _ensure_log_directory(self):
        """Ensure log directory exists"""
        log_dir = Path(self.log_file_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
    def _check_rotation(self):
        """Check if log file needs rotation"""
        if not os.path.exists(self.log_file_path):
            return
            
        file_size_mb = os.path.getsize(self.log_file_path) / (1024 * 1024)
        if file_size_mb >= self.max_file_size_mb:
            self._rotate_log_file()
    
    def _rotate_log_file(self):
        """Rotate log file"""
        log_path = Path(self.log_file_path)
        
        # Remove oldest backup if it exists
        oldest_backup = log_path.with_suffix(f".{self.backup_count}.log")
        if oldest_backup.exists():
            oldest_backup.unlink()
        
        # Shift existing backups
        for i in range(self.backup_count - 1, 0, -1):
            old_backup = log_path.with_suffix(f".{i}.log")
            new_backup = log_path.with_suffix(f".{i + 1}.log")
            if old_backup.exists():
                old_backup.rename(new_backup)
        
        # Rename current log file to .1.log
        if log_path.exists():
            log_path.rename(log_path.with_suffix(".1.log"))
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for logging"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _format_message(self, level: LogLevel, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Format message for logging"""
        timestamp = self._get_timestamp()
        env = get_environment()
        
        # Base message
        formatted = f"[{timestamp}] [{level.value.upper()}] [{env.upper()}] {message}"
        
        # Add context if provided
        if context:
            # Format context as pretty JSON
            context_str = json.dumps(context, default=str, indent=2)
            formatted += f"\n  Context:\n{context_str}"
            
        return formatted
    
    def _log_to_console(self, level: LogLevel, message: str, context: Optional[Dict[str, Any]] = None):
        """Log message to console with appropriate formatting"""
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
    
    def _log_to_file(self, level: LogLevel, message: str, context: Optional[Dict[str, Any]] = None):
        """Log message to file"""
        try:
            formatted_message = self._format_message(level, message, context)
            
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(formatted_message + '\n')
                
        except Exception as e:
            # Don't let file logging failures break the app
            print(f"⚠️ Failed to write to log file: {e}")
    
    def log(self, level: LogLevel, message: str, context: Optional[Dict[str, Any]] = None):
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
    
    def log_exception(self, message: str, exception: Exception, context: Optional[Dict[str, Any]] = None):
        """Log exception with stack trace"""
        # Format the full error message with stack trace
        timestamp = self._get_timestamp()
        env = get_environment()
        
        # Base error message
        error_msg = f"[{timestamp}] [{LogLevel.ERROR.value.upper()}] [{env.upper()}] {message}"
        
        # Add exception details
        error_msg += f"\n  Exception: {type(exception).__name__}: {str(exception)}"
        
        # Add context if provided
        if context:
            context_str = json.dumps(context, default=str, indent=2)
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
        if context:
            context_str = json.dumps(context, default=str)
            file_msg += f" | Context: {context_str}"
        
        try:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(file_msg + '\n')
        except Exception as e:
            print(f"⚠️ Failed to write to log file: {e}") 