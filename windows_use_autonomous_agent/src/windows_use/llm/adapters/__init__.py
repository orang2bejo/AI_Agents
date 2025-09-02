"""LLM Provider Adapters

Adapters for different LLM providers to normalize their APIs
into a common interface.
"""

from .ollama import OllamaProvider

# Import other adapters as they are implemented
try:
    from .gemini import GeminiProvider
except ImportError:
    GeminiProvider = None

try:
    from .anthropic_claude import AnthropicProvider
except ImportError:
    AnthropicProvider = None

try:
    from .groq import GroqProvider
except ImportError:
    GroqProvider = None

try:
    from .deepseek import DeepSeekProvider
except ImportError:
    DeepSeekProvider = None

try:
    from .qwen import QwenProvider
except ImportError:
    QwenProvider = None

__all__ = [
    'OllamaProvider',
    'GeminiProvider',
    'AnthropicProvider', 
    'GroqProvider',
    'DeepSeekProvider',
    'QwenProvider'
]