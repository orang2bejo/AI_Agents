"""Natural Language Understanding (NLU) Package

Package ini menyediakan:
1. Grammar Parser untuk bahasa Indonesia
2. Intent Router untuk mengarahkan ke handler yang tepat
3. Context Manager untuk tracking state

Usage:
    from windows_use.nlu import GrammarParserID, IntentRouter, ContextManager
    from windows_use.nlu import IntentType, ParsedIntent, ExecutionResult
"""

from .grammar_id import (
    GrammarParserID,
    IntentType,
    ParsedIntent
)

from .router import (
    IntentRouter,
    ContextManager,
    RouterResult,
    ExecutionResult
)

__version__ = "1.0.0"
__author__ = "Windows Use Autonomous Agent"

__all__ = [
    # Grammar Parser
    "GrammarParserID",
    "IntentType",
    "ParsedIntent",
    
    # Router
    "IntentRouter",
    "ContextManager",
    "RouterResult",
    "ExecutionResult",
]

# Package level configuration
DEFAULT_CONFIDENCE_THRESHOLD = 0.7
SUPPORTED_LANGUAGE = "id"  # Indonesian

# Quick setup function
def create_default_router(confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD) -> IntentRouter:
    """Create router dengan konfigurasi default
    
    Args:
        confidence_threshold: Minimum confidence untuk fast path
        
    Returns:
        Configured IntentRouter instance
    """
    return IntentRouter(confidence_threshold=confidence_threshold)

def create_context_manager() -> ContextManager:
    """Create context manager baru
    
    Returns:
        New ContextManager instance
    """
    return ContextManager()