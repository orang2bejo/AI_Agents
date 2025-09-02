"""LLM Manager

Main interface for managing multiple LLM providers and routing requests.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Union, Iterator
from dataclasses import dataclass

from .base import LLMProvider, LLMMessage, LLMResponse, LLMConfig, ModelCapabilities
from .registry import ModelRegistry, ProviderConfig
from .router import LLMRouter, TaskType, RoutingPolicy, RoutingConfig
from .adapters import (
    OllamaProvider,
    GeminiProvider,
    AnthropicProvider,
    GroqProvider,
    DeepSeekProvider,
    QwenProvider
)

logger = logging.getLogger(__name__)


@dataclass
class LLMManagerConfig:
    """Configuration for LLM Manager"""
    default_provider: str = "ollama"
    default_model: str = "llama3.2:3b"
    routing_policy: RoutingPolicy = RoutingPolicy.OFFLINE_FIRST
    enable_fallback: bool = True
    max_retries: int = 3
    timeout_seconds: int = 30
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
    log_requests: bool = True
    log_responses: bool = False  # Set to False for privacy


class LLMManager:
    """Main LLM Manager for handling multiple providers"""
    
    def __init__(self, config: Optional[LLMManagerConfig] = None):
        self.config = config or LLMManagerConfig()
        self.registry = ModelRegistry()
        self.router = LLMRouter(self.registry)
        self.providers: Dict[str, LLMProvider] = {}
        self._request_cache: Dict[str, LLMResponse] = {}
        
        # Initialize providers
        self._initialize_providers()
        
        logger.info(f"LLM Manager initialized with {len(self.providers)} providers")
    
    def _initialize_providers(self):
        """Initialize available LLM providers"""
        # Ollama (local)
        try:
            ollama_provider = OllamaProvider()
            if ollama_provider.is_available():
                self.providers["ollama"] = ollama_provider
                self.registry.register_provider("ollama", ProviderConfig(
                    name="ollama",
                    api_key_env="OLLAMA_API_KEY",
                    base_url="http://localhost:11434",
                    enabled=True,
                    priority=1
                ))
                logger.info("Ollama provider initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Ollama provider: {e}")
        
        # Gemini
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            try:
                gemini_provider = GeminiProvider(api_key=gemini_key)
                self.providers["gemini"] = gemini_provider
                self.registry.register_provider("gemini", ProviderConfig(
                    name="gemini",
                    api_key_env="GEMINI_API_KEY",
                    enabled=True,
                    priority=2
                ))
                logger.info("Gemini provider initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini provider: {e}")
        
        # Anthropic Claude
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            try:
                anthropic_provider = AnthropicProvider(api_key=anthropic_key)
                self.providers["anthropic"] = anthropic_provider
                self.registry.register_provider("anthropic", ProviderConfig(
                    name="anthropic",
                    api_key_env="ANTHROPIC_API_KEY",
                    enabled=True,
                    priority=3
                ))
                logger.info("Anthropic provider initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Anthropic provider: {e}")
        
        # Groq
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            try:
                groq_provider = GroqProvider(api_key=groq_key)
                self.providers["groq"] = groq_provider
                self.registry.register_provider("groq", ProviderConfig(
                    name="groq",
                    api_key_env="GROQ_API_KEY",
                    enabled=True,
                    priority=4
                ))
                logger.info("Groq provider initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Groq provider: {e}")
        
        # DeepSeek
        deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        if deepseek_key:
            try:
                deepseek_provider = DeepSeekProvider(api_key=deepseek_key)
                self.providers["deepseek"] = deepseek_provider
                self.registry.register_provider("deepseek", ProviderConfig(
                    name="deepseek",
                    api_key_env="DEEPSEEK_API_KEY",
                    enabled=True,
                    priority=5
                ))
                logger.info("DeepSeek provider initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize DeepSeek provider: {e}")
        
        # Qwen
        qwen_key = os.getenv("QWEN_API_KEY")
        if qwen_key:
            try:
                qwen_provider = QwenProvider(api_key=qwen_key)
                self.providers["qwen"] = qwen_provider
                self.registry.register_provider("qwen", ProviderConfig(
                    name="qwen",
                    api_key_env="QWEN_API_KEY",
                    enabled=True,
                    priority=6
                ))
                logger.info("Qwen provider initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Qwen provider: {e}")
    
    def chat(
        self,
        messages: List[LLMMessage],
        tools: Optional[List[Dict[str, Any]]] = None,
        config: Optional[LLMConfig] = None,
        task_type: TaskType = TaskType.GENERAL,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> Union[LLMResponse, Iterator[LLMResponse]]:
        """Send chat completion request with intelligent routing"""
        if not config:
            config = LLMConfig()
        
        # Use specific provider if requested
        if provider and provider in self.providers:
            selected_provider = self.providers[provider]
            selected_model = model or self.config.default_model
        else:
            # Use router to select best provider and model
            routing_config = RoutingConfig(
                task_type=task_type,
                policy=self.config.routing_policy,
                max_cost=kwargs.get("max_cost"),
                max_latency_ms=kwargs.get("max_latency_ms"),
                require_tools=bool(tools),
                require_vision=kwargs.get("require_vision", False),
                require_json=config.response_format == "json"
            )
            
            selected_provider, selected_model = self.router.route_request(
                messages=messages,
                config=routing_config,
                available_providers=list(self.providers.keys())
            )
            
            if not selected_provider or selected_provider not in self.providers:
                raise RuntimeError("No suitable provider available")
            
            selected_provider = self.providers[selected_provider]
        
        # Log request if enabled
        if self.config.log_requests:
            logger.info(f"Sending request to {selected_provider.name} with model {selected_model}")
        
        # Check cache if enabled
        if self.config.enable_caching and not config.stream:
            cache_key = self._generate_cache_key(messages, tools, config, selected_model)
            if cache_key in self._request_cache:
                logger.debug("Returning cached response")
                return self._request_cache[cache_key]
        
        # Send request with retries
        last_exception = None
        for attempt in range(self.config.max_retries):
            try:
                response = selected_provider.chat(
                    messages=messages,
                    tools=tools,
                    config=config,
                    model=selected_model,
                    **kwargs
                )
                
                # Cache response if enabled and not streaming
                if self.config.enable_caching and not config.stream and isinstance(response, LLMResponse):
                    cache_key = self._generate_cache_key(messages, tools, config, selected_model)
                    self._request_cache[cache_key] = response
                
                # Log response if enabled
                if self.config.log_responses and isinstance(response, LLMResponse):
                    logger.info(f"Received response: {response.content[:100]}...")
                
                # Record success in router
                self.router.record_success(selected_provider.name, selected_model, response.latency_ms or 0)
                
                return response
            
            except Exception as e:
                last_exception = e
                logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                
                # Record failure in router
                self.router.record_failure(selected_provider.name, selected_model, str(e))
                
                # Try fallback if enabled and not last attempt
                if self.config.enable_fallback and attempt < self.config.max_retries - 1:
                    # Get next best provider
                    fallback_providers = [p for p in self.providers.keys() if p != selected_provider.name]
                    if fallback_providers:
                        routing_config = RoutingConfig(
                            task_type=task_type,
                            policy=RoutingPolicy.SPEED_OPTIMIZED,  # Prefer faster fallback
                            require_tools=bool(tools),
                            require_vision=kwargs.get("require_vision", False),
                            require_json=config.response_format == "json"
                        )
                        
                        fallback_provider, fallback_model = self.router.route_request(
                            messages=messages,
                            config=routing_config,
                            available_providers=fallback_providers
                        )
                        
                        if fallback_provider and fallback_provider in self.providers:
                            selected_provider = self.providers[fallback_provider]
                            selected_model = fallback_model
                            logger.info(f"Falling back to {fallback_provider} with model {fallback_model}")
        
        # All attempts failed
        raise RuntimeError(f"All {self.config.max_retries} attempts failed. Last error: {last_exception}")
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return list(self.providers.keys())
    
    def get_available_models(self, provider: Optional[str] = None) -> Dict[str, List[str]]:
        """Get available models for each provider"""
        if provider and provider in self.providers:
            return {provider: self.providers[provider].get_available_models()}
        
        models = {}
        for name, provider_instance in self.providers.items():
            try:
                models[name] = provider_instance.get_available_models()
            except Exception as e:
                logger.warning(f"Failed to get models for {name}: {e}")
                models[name] = []
        
        return models
    
    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all providers"""
        status = {}
        for name, provider in self.providers.items():
            try:
                is_available = provider.is_available()
                capabilities = provider.capabilities
                status[name] = {
                    "available": is_available,
                    "capabilities": {
                        "max_context": capabilities.max_context,
                        "supports_tools": capabilities.supports_tools,
                        "supports_vision": capabilities.supports_vision,
                        "supports_json_mode": capabilities.supports_json_mode,
                        "supports_streaming": capabilities.supports_streaming,
                        "cost_per_1k_input": capabilities.cost_per_1k_input,
                        "cost_per_1k_output": capabilities.cost_per_1k_output,
                        "typical_latency_ms": capabilities.typical_latency_ms
                    }
                }
            except Exception as e:
                status[name] = {
                    "available": False,
                    "error": str(e)
                }
        
        return status
    
    def estimate_cost(
        self,
        messages: List[LLMMessage],
        provider: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, float]:
        """Estimate cost for request across providers"""
        costs = {}
        
        if provider and provider in self.providers:
            providers_to_check = {provider: self.providers[provider]}
        else:
            providers_to_check = self.providers
        
        for name, provider_instance in providers_to_check.items():
            try:
                if hasattr(provider_instance, 'estimate_cost'):
                    cost = provider_instance.estimate_cost(messages, model)
                    costs[name] = cost
                else:
                    # Fallback estimation
                    capabilities = provider_instance.capabilities
                    input_tokens = provider_instance.count_tokens(messages)
                    output_tokens = min(1000, input_tokens // 4)
                    
                    input_cost = (input_tokens / 1000) * capabilities.cost_per_1k_input
                    output_cost = (output_tokens / 1000) * capabilities.cost_per_1k_output
                    costs[name] = input_cost + output_cost
            except Exception as e:
                logger.warning(f"Failed to estimate cost for {name}: {e}")
                costs[name] = 0.0
        
        return costs
    
    def clear_cache(self):
        """Clear the request cache"""
        self._request_cache.clear()
        logger.info("Request cache cleared")
    
    def _generate_cache_key(self, messages: List[LLMMessage], tools: Optional[List[Dict[str, Any]]], config: LLMConfig, model: str) -> str:
        """Generate cache key for request"""
        import hashlib
        import json
        
        # Create a deterministic representation
        cache_data = {
            "messages": [(msg.role.value, msg.content) for msg in messages],
            "tools": tools or [],
            "config": {
                "temperature": config.temperature,
                "top_p": config.top_p,
                "max_tokens": config.max_tokens,
                "response_format": config.response_format
            },
            "model": model
        }
        
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()