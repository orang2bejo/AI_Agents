"""Multi-Provider LLM Module

This module provides a unified interface for working with multiple LLM providers
including Gemini, Claude, Groq, DeepSeek, Qwen, and Ollama.

Key Components:
- Base provider interface and abstractions
- Provider-specific adapters
- Model registry and configuration
- Intelligent routing and failover
- Token counting and management
- Tool calling normalization
"""

import logging

logger = logging.getLogger(__name__)

from .base import LLMProvider, LLMResponse, LLMMessage
from .registry import ModelRegistry, MODEL_CATALOG
from .router import LLMRouter

# Import new LLM provider components
try:
    from .llm_provider import (
        LLMRouter as NewLLMRouter,
        BaseLLMProvider,
        OpenAIProvider,
        AnthropicProvider,
        OllamaProvider,
        LLMProvider as NewLLMProvider,
        LLMMessage as NewLLMMessage,
        LLMResponse as NewLLMResponse,
        LLMConfig,
        MessageRole,
        ResponseFormat,
        create_openai_provider,
        create_anthropic_provider,
        create_ollama_provider
    )
except ImportError as e:
    logger.warning(f"Failed to import new LLM provider components: {e}")

# Import model registry components
try:
    from .model_registry import (
        ModelRegistry as NewModelRegistry,
        ModelInfo,
        ModelCapability,
        ModelTier,
        ModelStatus,
        ModelPricing,
        ModelLimits,
        MODEL_CATALOG as NEW_MODEL_CATALOG
    )
except ImportError as e:
    logger.warning(f"Failed to import model registry components: {e}")

__all__ = [
    'LLMProvider',
    'LLMResponse',
    'LLMMessage',
    'ModelRegistry',
    'MODEL_CATALOG',
    'LLMRouter',
    'NewLLMRouter',
    'BaseLLMProvider',
    'OpenAIProvider',
    'AnthropicProvider',
    'OllamaProvider',
    'NewLLMProvider',
    'NewLLMMessage',
    'NewLLMResponse',
    'LLMConfig',
    'MessageRole',
    'ResponseFormat',
    'create_openai_provider',
    'create_anthropic_provider',
    'create_ollama_provider',
    'NewModelRegistry',
    'ModelInfo',
    'ModelCapability',
    'ModelTier',
    'ModelStatus',
    'ModelPricing',
    'ModelLimits',
    'NEW_MODEL_CATALOG'
]