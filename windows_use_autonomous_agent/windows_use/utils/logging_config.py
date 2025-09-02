"""Comprehensive logging configuration for Jarvis AI.

This module provides a centralized logging system with:
- Multiple log levels and handlers
- File rotation and compression
- Structured logging with context
- Performance monitoring
- Error tracking and alerting
"""

import logging
import logging.handlers
import os
import sys
import json
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum

try:
    import colorama
    from colorama import Fore, Back, Style
    colorama.init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    # Fallback color constants
    class Fore:
        RED = ''
        GREEN = ''
        YELLOW = ''
        BLUE = ''
        MAGENTA = ''
        CYAN = ''
        WHITE = ''
        RESET = ''
    
    class Style:
        BRIGHT = ''
        RESET_ALL = ''


class LogLevel(Enum):
    """Enhanced log levels with descriptions."""
    CRITICAL = (50, "Critical system errors")
    ERROR = (40, "Error conditions")
    WARNING = (30, "Warning conditions")
    INFO = (20, "Informational messages")
    DEBUG = (10, "Debug-level messages")
    TRACE = (5, "Detailed trace information")
    
    def __init__(self, level: int, description: str):
        self.level = level
        self.description = description


@dataclass
class LogContext:
    """Context information for structured logging."""
    component: str
    operation: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    performance_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for console output."""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }
    
    def format(self, record):
        if COLORAMA_AVAILABLE:
            color = self.COLORS.get(record.levelname, '')
            record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
            record.name = f"{Fore.BLUE}{record.name}{Style.RESET_ALL}"
        
        return super().format(record)


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception information if present
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Add context information if present
        if hasattr(record, 'context'):
            log_entry['context'] = asdict(record.context)
        
        # Add custom fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'lineno', 'funcName', 'created',
                          'msecs', 'relativeCreated', 'thread', 'threadName',
                          'processName', 'process', 'getMessage', 'exc_info',
                          'exc_text', 'stack_info', 'context']:
                log_entry[key] = value
        
        return json.dumps(log_entry, ensure_ascii=False)


class PerformanceFilter(logging.Filter):
    """Filter to add performance metrics to log records."""
    
    def filter(self, record):
        # Add performance context if available
        if hasattr(record, 'context') and record.context.performance_data:
            record.performance = record.context.performance_data
        return True


class LoggingManager:
    """Centralized logging manager for Jarvis AI."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        self.loggers: Dict[str, logging.Logger] = {}
        self.log_dir = Path(self.config.get('log_directory', 'logs'))
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup root logger
        self._setup_root_logger()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default logging configuration."""
        return {
            'log_directory': 'logs',
            'log_level': 'INFO',
            'console_logging': True,
            'file_logging': True,
            'structured_logging': True,
            'max_file_size': 10 * 1024 * 1024,  # 10MB
            'backup_count': 5,
            'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'date_format': '%Y-%m-%d %H:%M:%S',
            'enable_colors': True,
            'performance_logging': True,
            'error_alerting': False,
        }
    
    def _setup_root_logger(self):
        """Setup the root logger with handlers."""
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.config['log_level'].upper()))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Console handler
        if self.config['console_logging']:
            console_handler = logging.StreamHandler(sys.stdout)
            if self.config['enable_colors'] and COLORAMA_AVAILABLE:
                console_formatter = ColoredFormatter(
                    self.config['log_format'],
                    datefmt=self.config['date_format']
                )
            else:
                console_formatter = logging.Formatter(
                    self.config['log_format'],
                    datefmt=self.config['date_format']
                )
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)
        
        # File handler with rotation
        if self.config['file_logging']:
            log_file = self.log_dir / 'jarvis.log'
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=self.config['max_file_size'],
                backupCount=self.config['backup_count'],
                encoding='utf-8'
            )
            file_formatter = logging.Formatter(
                self.config['log_format'],
                datefmt=self.config['date_format']
            )
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)
        
        # Structured logging handler
        if self.config['structured_logging']:
            structured_file = self.log_dir / 'jarvis_structured.log'
            structured_handler = logging.handlers.RotatingFileHandler(
                structured_file,
                maxBytes=self.config['max_file_size'],
                backupCount=self.config['backup_count'],
                encoding='utf-8'
            )
            structured_formatter = StructuredFormatter()
            structured_handler.setFormatter(structured_formatter)
            
            # Add performance filter
            if self.config['performance_logging']:
                structured_handler.addFilter(PerformanceFilter())
            
            root_logger.addHandler(structured_handler)
        
        # Error handler for critical errors
        error_file = self.log_dir / 'jarvis_errors.log'
        error_handler = logging.handlers.RotatingFileHandler(
            error_file,
            maxBytes=self.config['max_file_size'],
            backupCount=self.config['backup_count'],
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_formatter = StructuredFormatter()
        error_handler.setFormatter(error_formatter)
        root_logger.addHandler(error_handler)
    
    def get_logger(self, name: str, context: Optional[LogContext] = None) -> logging.Logger:
        """Get or create a logger with optional context."""
        if name not in self.loggers:
            logger = logging.getLogger(name)
            
            # Add context adapter if provided
            if context:
                logger = ContextAdapter(logger, context)
            
            self.loggers[name] = logger
        
        return self.loggers[name]
    
    def set_log_level(self, level: Union[str, int]):
        """Set the global log level."""
        if isinstance(level, str):
            level = getattr(logging, level.upper())
        
        logging.getLogger().setLevel(level)
        self.config['log_level'] = logging.getLevelName(level)
    
    def add_custom_handler(self, handler: logging.Handler, level: Optional[int] = None):
        """Add a custom handler to the root logger."""
        if level:
            handler.setLevel(level)
        logging.getLogger().addHandler(handler)
    
    def get_log_stats(self) -> Dict[str, Any]:
        """Get logging statistics."""
        stats = {
            'log_directory': str(self.log_dir),
            'active_loggers': len(self.loggers),
            'log_files': [],
            'total_log_size': 0
        }
        
        # Collect log file information
        for log_file in self.log_dir.glob('*.log*'):
            file_size = log_file.stat().st_size
            stats['log_files'].append({
                'name': log_file.name,
                'size': file_size,
                'modified': datetime.fromtimestamp(log_file.stat().st_mtime).isoformat()
            })
            stats['total_log_size'] += file_size
        
        return stats
    
    def cleanup_old_logs(self, days: int = 30):
        """Clean up log files older than specified days."""
        import time
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        
        cleaned_files = []
        for log_file in self.log_dir.glob('*.log*'):
            if log_file.stat().st_mtime < cutoff_time:
                try:
                    log_file.unlink()
                    cleaned_files.append(str(log_file))
                except OSError as e:
                    logging.error(f"Failed to delete old log file {log_file}: {e}")
        
        if cleaned_files:
            logging.info(f"Cleaned up {len(cleaned_files)} old log files")
        
        return cleaned_files


class ContextAdapter(logging.LoggerAdapter):
    """Logger adapter that adds context information to log records."""
    
    def __init__(self, logger: logging.Logger, context: LogContext):
        super().__init__(logger, {})
        self.context = context
    
    def process(self, msg, kwargs):
        # Add context to the log record
        kwargs['extra'] = kwargs.get('extra', {})
        kwargs['extra']['context'] = self.context
        return msg, kwargs
    
    def update_context(self, **kwargs):
        """Update the context with new values."""
        for key, value in kwargs.items():
            if hasattr(self.context, key):
                setattr(self.context, key, value)


# Global logging manager instance
_logging_manager: Optional[LoggingManager] = None


def setup_logging(config: Optional[Dict[str, Any]] = None) -> LoggingManager:
    """Setup global logging configuration."""
    global _logging_manager
    _logging_manager = LoggingManager(config)
    return _logging_manager


def get_logger(name: str, context: Optional[LogContext] = None) -> logging.Logger:
    """Get a logger instance."""
    global _logging_manager
    if _logging_manager is None:
        _logging_manager = setup_logging()
    return _logging_manager.get_logger(name, context)


def log_performance(func):
    """Decorator to log function performance."""
    import time
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(f"{func.__module__}.{func.__name__}")
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logger.info(
                f"Function {func.__name__} completed successfully",
                extra={
                    'execution_time': execution_time,
                    'function': func.__name__,
                    'module': func.__module__
                }
            )
            return result
        
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"Function {func.__name__} failed: {e}",
                extra={
                    'execution_time': execution_time,
                    'function': func.__name__,
                    'module': func.__module__,
                    'error': str(e)
                },
                exc_info=True
            )
            raise
    
    return wrapper


def log_api_call(func):
    """Decorator to log API calls with request/response details."""
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(f"api.{func.__name__}")
        
        # Log request
        logger.info(
            f"API call started: {func.__name__}",
            extra={
                'api_function': func.__name__,
                'args_count': len(args),
                'kwargs_keys': list(kwargs.keys())
            }
        )
        
        try:
            result = func(*args, **kwargs)
            
            # Log successful response
            logger.info(
                f"API call completed: {func.__name__}",
                extra={
                    'api_function': func.__name__,
                    'success': True,
                    'result_type': type(result).__name__
                }
            )
            return result
        
        except Exception as e:
            # Log error response
            logger.error(
                f"API call failed: {func.__name__}",
                extra={
                    'api_function': func.__name__,
                    'success': False,
                    'error': str(e),
                    'error_type': type(e).__name__
                },
                exc_info=True
            )
            raise
    
    return wrapper


# Export main components
__all__ = [
    'LogLevel',
    'LogContext',
    'LoggingManager',
    'ContextAdapter',
    'setup_logging',
    'get_logger',
    'log_performance',
    'log_api_call'
]