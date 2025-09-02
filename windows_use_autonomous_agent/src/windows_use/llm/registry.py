"""Model Registry and Catalog

Centralized registry for all supported LLM models and providers.
"""

from typing import Dict, List, Optional, Type
from dataclasses import dataclass
import os
import yaml
from pathlib import Path

from .base import LLMProvider, ModelCapabilities


# Model catalog with capabilities and metadata
MODEL_CATALOG = {
    # Google Gemini
    "gemini-1.5-flash": ModelCapabilities(
        max_context=1048576,  # 1M tokens
        supports_tools=True,
        supports_vision=True,
        supports_json_mode=True,
        supports_streaming=True,
        cost_per_1k_input=0.075,
        cost_per_1k_output=0.30,
        typical_latency_ms=800
    ),
    "gemini-1.5-pro": ModelCapabilities(
        max_context=2097152,  # 2M tokens
        supports_tools=True,
        supports_vision=True,
        supports_json_mode=True,
        supports_streaming=True,
        cost_per_1k_input=1.25,
        cost_per_1k_output=5.00,
        typical_latency_ms=1200
    ),
    
    # Anthropic Claude
    "claude-3.5-sonnet": ModelCapabilities(
        max_context=200000,
        supports_tools=True,
        supports_vision=True,
        supports_json_mode=False,
        supports_streaming=True,
        cost_per_1k_input=3.00,
        cost_per_1k_output=15.00,
        typical_latency_ms=1000
    ),
    "claude-3.5-haiku": ModelCapabilities(
        max_context=200000,
        supports_tools=True,
        supports_vision=True,
        supports_json_mode=False,
        supports_streaming=True,
        cost_per_1k_input=0.25,
        cost_per_1k_output=1.25,
        typical_latency_ms=600
    ),
    
    # Groq (Fast inference)
    "groq/llama-3.1-70b": ModelCapabilities(
        max_context=131072,
        supports_tools=True,
        supports_vision=False,
        supports_json_mode=True,
        supports_streaming=True,
        cost_per_1k_input=0.59,
        cost_per_1k_output=0.79,
        typical_latency_ms=300
    ),
    "groq/llama-3.1-8b": ModelCapabilities(
        max_context=131072,
        supports_tools=True,
        supports_vision=False,
        supports_json_mode=True,
        supports_streaming=True,
        cost_per_1k_input=0.05,
        cost_per_1k_output=0.08,
        typical_latency_ms=200
    ),
    
    # DeepSeek
    "deepseek-r1": ModelCapabilities(
        max_context=65536,
        supports_tools=True,
        supports_vision=False,
        supports_json_mode=True,
        supports_streaming=True,
        cost_per_1k_input=0.14,
        cost_per_1k_output=0.28,
        typical_latency_ms=1500
    ),
    "deepseek-chat": ModelCapabilities(
        max_context=32768,
        supports_tools=True,
        supports_vision=False,
        supports_json_mode=True,
        supports_streaming=True,
        cost_per_1k_input=0.14,
        cost_per_1k_output=0.28,
        typical_latency_ms=800
    ),
    
    # Qwen
    "qwen2.5-72b-instruct": ModelCapabilities(
        max_context=131072,
        supports_tools=True,
        supports_vision=False,
        supports_json_mode=True,
        supports_streaming=True,
        cost_per_1k_input=0.50,
        cost_per_1k_output=1.50,
        typical_latency_ms=1000
    ),
    "qwen2.5-7b-instruct": ModelCapabilities(
        max_context=131072,
        supports_tools=True,
        supports_vision=False,
        supports_json_mode=True,
        supports_streaming=True,
        cost_per_1k_input=0.07,
        cost_per_1k_output=0.07,
        typical_latency_ms=600
    ),
    
    # Ollama (Local)
    "ollama/llama3.2:3b": ModelCapabilities(
        max_context=131072,
        supports_tools=True,
        supports_vision=False,
        supports_json_mode=True,
        supports_streaming=True,
        cost_per_1k_input=0.0,  # Local = free
        cost_per_1k_output=0.0,
        typical_latency_ms=2000
    ),
    "ollama/qwen2.5:7b": ModelCapabilities(
        max_context=131072,
        supports_tools=True,
        supports_vision=False,
        supports_json_mode=True,
        supports_streaming=True,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        typical_latency_ms=3000
    ),
    "ollama/llama3.2-vision:11b": ModelCapabilities(
        max_context=131072,
        supports_tools=False,
        supports_vision=True,
        supports_json_mode=True,
        supports_streaming=True,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        typical_latency_ms=4000
    )
}


@dataclass
class ProviderConfig:
    """Configuration for a provider"""
    provider_class: Type[LLMProvider]
    api_key_env: Optional[str] = None
    base_url: Optional[str] = None
    enabled: bool = True
    models: List[str] = None


class ModelRegistry:
    """Registry for managing LLM providers and models"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.providers: Dict[str, ProviderConfig] = {}
        self.instances: Dict[str, LLMProvider] = {}
        self.config_path = config_path
        
        # Load configuration if provided
        if config_path and os.path.exists(config_path):
            self.load_config(config_path)
    
    def register_provider(
        self, 
        name: str, 
        provider_class: Type[LLMProvider],
        api_key_env: Optional[str] = None,
        base_url: Optional[str] = None,
        models: Optional[List[str]] = None
    ):
        """Register a new provider"""
        self.providers[name] = ProviderConfig(
            provider_class=provider_class,
            api_key_env=api_key_env,
            base_url=base_url,
            models=models or []
        )
    
    def get_provider(self, name: str) -> Optional[LLMProvider]:
        """Get provider instance"""
        if name in self.instances:
            return self.instances[name]
        
        if name not in self.providers:
            return None
        
        config = self.providers[name]
        if not config.enabled:
            return None
        
        # Get API key from environment
        api_key = None
        if config.api_key_env:
            api_key = os.getenv(config.api_key_env)
        
        # Create instance
        kwargs = {}
        if api_key:
            kwargs['api_key'] = api_key
        if config.base_url:
            kwargs['base_url'] = config.base_url
        
        try:
            instance = config.provider_class(**kwargs)
            self.instances[name] = instance
            return instance
        except Exception as e:
            print(f"Failed to create provider {name}: {e}")
            return None
    
    def get_model_info(self, model_name: str) -> Optional[ModelCapabilities]:
        """Get model capabilities"""
        return MODEL_CATALOG.get(model_name)
    
    def list_available_models(self) -> List[str]:
        """List all available models"""
        available = []
        for model_name in MODEL_CATALOG.keys():
            provider_name = self._get_provider_name(model_name)
            provider = self.get_provider(provider_name)
            if provider and provider.is_available():
                available.append(model_name)
        return available
    
    def list_models_by_capability(
        self, 
        supports_tools: Optional[bool] = None,
        supports_vision: Optional[bool] = None,
        max_cost_per_1k: Optional[float] = None,
        max_latency_ms: Optional[int] = None
    ) -> List[str]:
        """Filter models by capabilities"""
        filtered = []
        
        for model_name, caps in MODEL_CATALOG.items():
            # Check capability filters
            if supports_tools is not None and caps.supports_tools != supports_tools:
                continue
            if supports_vision is not None and caps.supports_vision != supports_vision:
                continue
            if max_cost_per_1k is not None:
                if caps.cost_per_1k_output and caps.cost_per_1k_output > max_cost_per_1k:
                    continue
            if max_latency_ms is not None:
                if caps.typical_latency_ms and caps.typical_latency_ms > max_latency_ms:
                    continue
            
            # Check if provider is available
            provider_name = self._get_provider_name(model_name)
            provider = self.get_provider(provider_name)
            if provider and provider.is_available():
                filtered.append(model_name)
        
        return filtered
    
    def _get_provider_name(self, model_name: str) -> str:
        """Extract provider name from model name"""
        if "/" in model_name:
            return model_name.split("/")[0]
        elif model_name.startswith("gemini"):
            return "gemini"
        elif model_name.startswith("claude"):
            return "anthropic"
        elif model_name.startswith("deepseek"):
            return "deepseek"
        elif model_name.startswith("qwen"):
            return "qwen"
        else:
            return "unknown"
    
    def load_config(self, config_path: str):
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Update provider configurations
            for provider_name, provider_config in config.get('providers', {}).items():
                if provider_name in self.providers:
                    self.providers[provider_name].enabled = provider_config.get('enabled', True)
                    if 'base_url' in provider_config:
                        self.providers[provider_name].base_url = provider_config['base_url']
        
        except Exception as e:
            print(f"Failed to load config from {config_path}: {e}")
    
    def save_config(self, config_path: str):
        """Save current configuration to YAML file"""
        config = {
            'providers': {}
        }
        
        for name, provider_config in self.providers.items():
            config['providers'][name] = {
                'enabled': provider_config.enabled,
                'api_key_env': provider_config.api_key_env,
                'base_url': provider_config.base_url,
                'models': provider_config.models
            }
        
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
        except Exception as e:
            print(f"Failed to save config to {config_path}: {e}")


# Global registry instance
registry = ModelRegistry()