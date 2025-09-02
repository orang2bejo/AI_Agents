"""Windows Use - AI Agent for Windows Desktop Automation.

This package provides an AI agent that can interact with Windows OS at the GUI level,
offering comprehensive desktop automation, voice control, and intelligent task execution.
"""

import sys
import logging
from typing import Optional

# Package metadata
__version__ = "0.1.31"
__author__ = "Jeomon George"
__email__ = "jeogeoalukka@gmail.com"
__description__ = "An AI Agent that interacts with Windows OS at GUI level."

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Import core modules with error handling
try:
    from .agent import WindowsAgent
    from .desktop import DesktopAutomation
    from .tools import ToolManager
    from .llm import LLMProvider
    
    # Optional imports with graceful degradation
    _voice_available = False
    try:
        from .jarvis_ai import VoiceInput, TextToSpeech
        _voice_available = True
    except ImportError as e:
        logger.warning(f"Voice features not available: {e}")
        VoiceInput = None
        TextToSpeech = None
    
    _office_available = False
    try:
        from .office import OfficeAutomation
        _office_available = True
    except ImportError as e:
        logger.warning(f"Office automation not available: {e}")
        OfficeAutomation = None
    
    _web_available = False
    try:
        from .web import WebAutomation
        _web_available = True
    except ImportError as e:
        logger.warning(f"Web automation not available: {e}")
        WebAutomation = None
    
    _security_available = False
    try:
        from .security import SecurityManager
        _security_available = True
    except ImportError as e:
        logger.warning(f"Security features not available: {e}")
        SecurityManager = None
    
    _observability_available = False
    try:
        from .observability import ObservabilityManager
        _observability_available = True
    except ImportError as e:
        logger.warning(f"Observability features not available: {e}")
        ObservabilityManager = None
    
    _evolution_available = False
    try:
        from .evolution import EvolutionEngine
        _evolution_available = True
    except ImportError as e:
        logger.warning(f"Evolution features not available: {e}")
        EvolutionEngine = None
    
    # Import utilities
    _utils_available = False
    try:
        from .utils import (
            DependencyManager,
            dependency_manager,
            require_dependency,
            safe_import,
            handle_errors,
            log_errors,
            ErrorContext,
            check_system_requirements,
            setup_fallback_handlers,
            LoggingManager,
            setup_logging,
            get_logger,
            log_performance,
            log_api_call,
            logging_manager,
        )
        _utils_available = True
    except ImportError as e:
        logger.warning(f"Utilities not available: {e}")
        DependencyManager = None
        dependency_manager = None
        require_dependency = None
        safe_import = None
        handle_errors = None
        log_errors = None
        ErrorContext = None
        check_system_requirements = None
        setup_fallback_handlers = None
        LoggingManager = None
        setup_logging = None
        get_logger = None
        log_performance = None
        log_api_call = None
        logging_manager = None

except ImportError as e:
    logger.error(f"Failed to import core modules: {e}")
    # Provide minimal fallback
    WindowsAgent = None
    DesktopAutomation = None
    ToolManager = None
    LLMProvider = None
    VoiceInput = None
    TextToSpeech = None
    OfficeAutomation = None
    WebAutomation = None
    SecurityManager = None
    ObservabilityManager = None
    EvolutionEngine = None
    DependencyManager = None
    dependency_manager = None
    require_dependency = None
    safe_import = None
    handle_errors = None
    log_errors = None
    ErrorContext = None
    check_system_requirements = None
    setup_fallback_handlers = None
    LoggingManager = None
    setup_logging = None
    get_logger = None
    log_performance = None
    log_api_call = None
    logging_manager = None
    _voice_available = False
    _office_available = False
    _web_available = False
    _security_available = False
    _observability_available = False
    _evolution_available = False
    _utils_available = False

# Feature availability flags
FEATURES = {
    'voice': _voice_available,
    'office': _office_available,
    'web': _web_available,
    'security': _security_available,
    'observability': _observability_available,
    'evolution': _evolution_available,
    'utils': _utils_available,
}

# Public API
__all__ = [
    # Core classes
    'WindowsAgent',
    'DesktopAutomation',
    'ToolManager',
    'LLMProvider',
    
    # Optional features
    'VoiceInput',
    'TextToSpeech',
    'OfficeAutomation',
    'WebAutomation',
    'SecurityManager',
    'ObservabilityManager',
    'EvolutionEngine',
    
    # Utilities
    'DependencyManager',
    'dependency_manager',
    'require_dependency',
    'safe_import',
    'handle_errors',
    'log_errors',
    'ErrorContext',
    'check_system_requirements',
    'setup_fallback_handlers',
    'LoggingManager',
    'setup_logging',
    'get_logger',
    'log_performance',
    'log_api_call',
    'logging_manager',
    'FEATURES',
    'get_version',
    'check_requirements',
    'create_agent',
]

def get_version() -> str:
    """Get the package version."""
    return __version__

def check_requirements() -> dict:
    """Check which optional requirements are available."""
    return FEATURES.copy()

def create_agent(config: Optional[dict] = None) -> Optional['WindowsAgent']:
    """Create a Windows agent instance with optional configuration.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        WindowsAgent instance or None if core modules not available
    """
    if WindowsAgent is None:
        logger.error("Cannot create agent: core modules not available")
        return None
    
    try:
        return WindowsAgent(config=config)
    except Exception as e:
        logger.error(f"Failed to create agent: {e}")
        return None

# Version check
if sys.version_info < (3, 12):
    logger.warning(
        f"Python {sys.version_info.major}.{sys.version_info.minor} detected. "
        "Python 3.12+ is recommended for optimal performance."
    )

logger.info(f"Windows Use v{__version__} initialized")
logger.info(f"Available features: {[k for k, v in FEATURES.items() if v]}")