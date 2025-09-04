"""Utilities Package

Provides utility functions and classes for the Windows Use package.
"""

from .error_handling import (
    DependencyError,
    GracefulDegradationError,
    DependencyManager,
    dependency_manager,
    require_dependency,
    safe_import,
    handle_errors,
    log_errors,
    ErrorContext,
    check_system_requirements,
    setup_fallback_handlers,
)

from .logging_config import (
    LogLevel,
    LogContext,
    ColoredFormatter,
    StructuredFormatter,
    PerformanceFilter,
    LoggingManager,
    ContextAdapter,
    setup_logging,
    get_logger,
    log_performance,
    log_api_call,
)

__all__ = [
    'DependencyError',
    'GracefulDegradationError',
    'DependencyManager',
    'dependency_manager',
    'require_dependency',
    'safe_import',
    'handle_errors',
    'log_errors',
    'ErrorContext',
    'check_system_requirements',
    'setup_fallback_handlers',
    'LogLevel',
    'LogContext',
    'ColoredFormatter',
    'StructuredFormatter',
    'PerformanceFilter',
    'LoggingManager',
    'ContextAdapter',
    'setup_logging',
    'get_logger',
    'log_performance',
    'log_api_call',
]