"""Error Handling Utilities

Provides comprehensive error handling and graceful degradation
for missing dependencies and runtime errors.
"""

import logging
import sys
import traceback
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type, Union

logger = logging.getLogger(__name__)

class DependencyError(Exception):
    """Raised when a required dependency is missing."""
    pass

class GracefulDegradationError(Exception):
    """Raised when a feature cannot be used due to missing dependencies."""
    pass

class DependencyManager:
    """Manages optional dependencies and provides graceful degradation."""
    
    def __init__(self):
        self._available_modules = {}
        self._missing_modules = set()
        self._fallback_handlers = {}
        
    def check_dependency(self, module_name: str, package_name: str = None) -> bool:
        """Check if a dependency is available.
        
        Args:
            module_name: Name of the module to import
            package_name: Name of the package (for error messages)
            
        Returns:
            True if dependency is available, False otherwise
        """
        if module_name in self._available_modules:
            return self._available_modules[module_name] is not None
            
        try:
            module = __import__(module_name)
            self._available_modules[module_name] = module
            logger.debug(f"Dependency '{module_name}' is available")
            return True
        except ImportError as e:
            self._available_modules[module_name] = None
            self._missing_modules.add(module_name)
            package_display = package_name or module_name
            logger.warning(
                f"Optional dependency '{package_display}' not available: {e}. "
                f"Install with: pip install {package_display}"
            )
            return False
    
    def get_module(self, module_name: str) -> Any:
        """Get a module if available.
        
        Args:
            module_name: Name of the module
            
        Returns:
            The imported module or None if not available
        """
        return self._available_modules.get(module_name)
    
    def register_fallback(self, module_name: str, fallback_handler: Callable):
        """Register a fallback handler for a missing dependency.
        
        Args:
            module_name: Name of the module
            fallback_handler: Function to call when module is not available
        """
        self._fallback_handlers[module_name] = fallback_handler
    
    def get_fallback(self, module_name: str) -> Optional[Callable]:
        """Get fallback handler for a module.
        
        Args:
            module_name: Name of the module
            
        Returns:
            Fallback handler or None
        """
        return self._fallback_handlers.get(module_name)
    
    def get_missing_dependencies(self) -> List[str]:
        """Get list of missing dependencies."""
        return list(self._missing_modules)
    
    def get_available_dependencies(self) -> List[str]:
        """Get list of available dependencies."""
        return [name for name, module in self._available_modules.items() if module is not None]

# Global dependency manager instance
dependency_manager = DependencyManager()

def require_dependency(module_name: str, package_name: str = None, fallback: Any = None):
    """Decorator to require a dependency for a function.
    
    Args:
        module_name: Name of the module to check
        package_name: Name of the package for error messages
        fallback: Fallback value to return if dependency is missing
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not dependency_manager.check_dependency(module_name, package_name):
                if fallback is not None:
                    logger.warning(
                        f"Function '{func.__name__}' requires '{package_name or module_name}'. "
                        f"Using fallback: {fallback}"
                    )
                    return fallback
                
                fallback_handler = dependency_manager.get_fallback(module_name)
                if fallback_handler:
                    logger.warning(
                        f"Function '{func.__name__}' requires '{package_name or module_name}'. "
                        "Using fallback handler."
                    )
                    return fallback_handler(*args, **kwargs)
                
                raise DependencyError(
                    f"Function '{func.__name__}' requires '{package_name or module_name}'. "
                    f"Install with: pip install {package_name or module_name}"
                )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def safe_import(module_name: str, package_name: str = None, fallback: Any = None) -> Any:
    """Safely import a module with optional fallback.
    
    Args:
        module_name: Name of the module to import
        package_name: Name of the package for error messages
        fallback: Fallback value if import fails
        
    Returns:
        Imported module or fallback value
    """
    if dependency_manager.check_dependency(module_name, package_name):
        return dependency_manager.get_module(module_name)
    
    if fallback is not None:
        return fallback
    
    raise DependencyError(
        f"Required module '{package_name or module_name}' not available. "
        f"Install with: pip install {package_name or module_name}"
    )

def handle_errors(exceptions: Union[Type[Exception], tuple] = Exception, 
                 fallback: Any = None,
                 log_level: int = logging.ERROR):
    """Decorator to handle errors gracefully.
    
    Args:
        exceptions: Exception types to catch
        fallback: Fallback value to return on error
        log_level: Logging level for errors
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                logger.log(
                    log_level,
                    f"Error in '{func.__name__}': {e}\n{traceback.format_exc()}"
                )
                if fallback is not None:
                    return fallback
                raise
        return wrapper
    return decorator

def log_errors(func: Callable) -> Callable:
    """Decorator to log errors without suppressing them."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(
                f"Error in '{func.__name__}': {e}\n{traceback.format_exc()}"
            )
            raise
    return wrapper

class ErrorContext:
    """Context manager for error handling."""
    
    def __init__(self, 
                 operation: str,
                 exceptions: Union[Type[Exception], tuple] = Exception,
                 fallback: Any = None,
                 log_level: int = logging.ERROR):
        self.operation = operation
        self.exceptions = exceptions
        self.fallback = fallback
        self.log_level = log_level
        self.error = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type and issubclass(exc_type, self.exceptions):
            self.error = exc_val
            logger.log(
                self.log_level,
                f"Error in {self.operation}: {exc_val}\n{traceback.format_exc()}"
            )
            if self.fallback is not None:
                return True  # Suppress exception
        return False
    
    def get_result(self, default: Any = None) -> Any:
        """Get fallback result if error occurred."""
        if self.error:
            return self.fallback if self.fallback is not None else default
        return default

def check_system_requirements() -> Dict[str, bool]:
    """Check system requirements and dependencies.
    
    Returns:
        Dictionary of requirement names and their availability
    """
    requirements = {
        'python_version': sys.version_info >= (3, 12),
        'audio_backend': False,
        'voice_processing': False,
        'office_automation': False,
        'web_automation': False,
        'image_processing': False,
    }
    
    # Check audio backends
    if (dependency_manager.check_dependency('pyaudio') or 
        dependency_manager.check_dependency('sounddevice')):
        requirements['audio_backend'] = True
    
    # Check voice processing
    if (dependency_manager.check_dependency('whisper', 'openai-whisper') or
        dependency_manager.check_dependency('vosk')):
        requirements['voice_processing'] = True
    
    # Check office automation
    if dependency_manager.check_dependency('win32com.client', 'pywin32'):
        requirements['office_automation'] = True
    
    # Check web automation
    if dependency_manager.check_dependency('selenium'):
        requirements['web_automation'] = True
    
    # Check image processing
    if dependency_manager.check_dependency('PIL', 'Pillow'):
        requirements['image_processing'] = True
    
    return requirements

def setup_fallback_handlers():
    """Setup fallback handlers for common missing dependencies."""
    
    def audio_fallback(*args, **kwargs):
        logger.warning("Audio functionality not available - no audio backend found")
        return None
    
    def voice_fallback(*args, **kwargs):
        logger.warning("Voice processing not available - install whisper or vosk")
        return None
    
    def office_fallback(*args, **kwargs):
        logger.warning("Office automation not available - install pywin32")
        return None
    
    dependency_manager.register_fallback('pyaudio', audio_fallback)
    dependency_manager.register_fallback('sounddevice', audio_fallback)
    dependency_manager.register_fallback('whisper', voice_fallback)
    dependency_manager.register_fallback('vosk', voice_fallback)
    dependency_manager.register_fallback('win32com.client', office_fallback)

# Initialize fallback handlers
setup_fallback_handlers()

# Export main utilities
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
]