#!/usr/bin/env python3
"""
LLM Provider Module for Windows Use Autonomous Agent

Integrated LLM provider system for managing various language models
and routing requests to appropriate providers.

Author: Jarvis AI Team
Date: 2024
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any, Union, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime
import aiohttp
import openai
from pathlib import Path

logger = logging.getLogger(__name__)

class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    GROQ = "groq"
    DEEPSEEK = "deepseek"
    QWEN = "qwen"
    OLLAMA = "ollama"
    AZURE_OPENAI = "azure_openai"
    COHERE = "cohere"
    HUGGINGFACE = "huggingface"
    OPENROUTER = "openrouter"

class MessageRole(Enum):
    """Message roles in conversation"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"
    TOOL = "tool"

class ResponseFormat(Enum):
    """Response format types"""
    TEXT = "text"
    JSON = "json"
    STRUCTURED = "structured"

@dataclass
class LLMMessage:
    """Message in LLM conversation"""
    role: MessageRole
    content: str
    name: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LLMResponse:
    """Response from LLM provider"""
    content: str
    provider: LLMProvider
    model: str
    usage: Dict[str, int]
    finish_reason: str
    response_time: float
    function_calls: Optional[List[Dict[str, Any]]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw_response: Optional[Dict[str, Any]] = None

@dataclass
class LLMConfig:
    """Configuration for LLM provider"""
    provider: LLMProvider
    model: str
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    api_version: Optional[str] = None
    organization: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout: int = 60
    max_retries: int = 3
    retry_delay: float = 1.0
    stream: bool = False
    response_format: ResponseFormat = ResponseFormat.TEXT
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None
    custom_headers: Dict[str, str] = field(default_factory=dict)
    extra_params: Dict[str, Any] = field(default_factory=dict)

class BaseLLMProvider(ABC):
    """Base class for all LLM providers"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{config.provider.value}")
        self.client = None
        self.session = None
        self._initialize_client()
    
    @abstractmethod
    def _initialize_client(self):
        """Initialize the provider client"""
        pass
    
    @abstractmethod
    async def generate_response(self, messages: List[LLMMessage], 
                              **kwargs) -> LLMResponse:
        """Generate response from messages"""
        pass
    
    @abstractmethod
    async def generate_stream(self, messages: List[LLMMessage], 
                            **kwargs) -> AsyncGenerator[str, None]:
        """Generate streaming response"""
        pass
    
    def _prepare_messages(self, messages: List[LLMMessage]) -> List[Dict[str, Any]]:
        """Convert LLMMessage objects to provider format"""
        formatted_messages = []
        for msg in messages:
            formatted_msg = {
                "role": msg.role.value,
                "content": msg.content
            }
            
            if msg.name:
                formatted_msg["name"] = msg.name
            if msg.function_call:
                formatted_msg["function_call"] = msg.function_call
            if msg.tool_calls:
                formatted_msg["tool_calls"] = msg.tool_calls
            
            formatted_messages.append(formatted_msg)
        
        return formatted_messages
    
    def _calculate_usage(self, response_data: Dict[str, Any]) -> Dict[str, int]:
        """Extract usage information from response"""
        usage = response_data.get("usage", {})
        return {
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0)
        }
    
    async def close(self):
        """Close provider connections"""
        if self.session:
            await self.session.close()

class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider"""
    
    def _initialize_client(self):
        """Initialize OpenAI client"""
        self.client = openai.AsyncOpenAI(
            api_key=self.config.api_key,
            base_url=self.config.api_base,
            organization=self.config.organization,
            timeout=self.config.timeout,
            max_retries=self.config.max_retries
        )
    
    async def generate_response(self, messages: List[LLMMessage], 
                              **kwargs) -> LLMResponse:
        """Generate response using OpenAI API"""
        start_time = time.time()
        
        try:
            # Prepare request parameters
            params = {
                "model": self.config.model,
                "messages": self._prepare_messages(messages),
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", self.config.temperature),
                "top_p": kwargs.get("top_p", self.config.top_p),
                "frequency_penalty": kwargs.get("frequency_penalty", self.config.frequency_penalty),
                "presence_penalty": kwargs.get("presence_penalty", self.config.presence_penalty),
                "stream": kwargs.get("stream", self.config.stream)
            }
            
            # Add tools if configured
            if self.config.tools:
                params["tools"] = self.config.tools
            if self.config.tool_choice:
                params["tool_choice"] = self.config.tool_choice
            
            # Add response format
            if self.config.response_format == ResponseFormat.JSON:
                params["response_format"] = {"type": "json_object"}
            
            # Add extra parameters
            params.update(self.config.extra_params)
            
            # Make API call
            response = await self.client.chat.completions.create(**params)
            
            # Extract response data
            choice = response.choices[0]
            content = choice.message.content or ""
            finish_reason = choice.finish_reason
            
            # Extract function/tool calls
            function_calls = None
            tool_calls = None
            
            if hasattr(choice.message, 'function_call') and choice.message.function_call:
                function_calls = [{
                    "name": choice.message.function_call.name,
                    "arguments": choice.message.function_call.arguments
                }]
            
            if hasattr(choice.message, 'tool_calls') and choice.message.tool_calls:
                tool_calls = [{
                    "id": tool_call.id,
                    "type": tool_call.type,
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments
                    }
                } for tool_call in choice.message.tool_calls]
            
            response_time = time.time() - start_time
            
            return LLMResponse(
                content=content,
                provider=self.config.provider,
                model=self.config.model,
                usage=self._calculate_usage(response.model_dump()),
                finish_reason=finish_reason,
                response_time=response_time,
                function_calls=function_calls,
                tool_calls=tool_calls,
                raw_response=response.model_dump()
            )
            
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            raise
    
    async def generate_stream(self, messages: List[LLMMessage], 
                            **kwargs) -> AsyncGenerator[str, None]:
        """Generate streaming response using OpenAI API"""
        try:
            # Prepare request parameters
            params = {
                "model": self.config.model,
                "messages": self._prepare_messages(messages),
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", self.config.temperature),
                "stream": True
            }
            
            # Add extra parameters
            params.update(self.config.extra_params)
            
            # Make streaming API call
            stream = await self.client.chat.completions.create(**params)
            
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            self.logger.error(f"OpenAI streaming error: {e}")
            raise

class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude LLM provider"""
    
    def _initialize_client(self):
        """Initialize Anthropic client"""
        try:
            import anthropic
            self.client = anthropic.AsyncAnthropic(
                api_key=self.config.api_key,
                base_url=self.config.api_base,
                timeout=self.config.timeout,
                max_retries=self.config.max_retries
            )
        except ImportError:
            raise ImportError("anthropic package not installed")
    
    async def generate_response(self, messages: List[LLMMessage], 
                              **kwargs) -> LLMResponse:
        """Generate response using Anthropic API"""
        start_time = time.time()
        
        try:
            # Convert messages to Anthropic format
            anthropic_messages = []
            system_message = None
            
            for msg in messages:
                if msg.role == MessageRole.SYSTEM:
                    system_message = msg.content
                else:
                    anthropic_messages.append({
                        "role": msg.role.value,
                        "content": msg.content
                    })
            
            # Prepare request parameters
            params = {
                "model": self.config.model,
                "messages": anthropic_messages,
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", self.config.temperature),
                "top_p": kwargs.get("top_p", self.config.top_p)
            }
            
            if system_message:
                params["system"] = system_message
            
            # Add extra parameters
            params.update(self.config.extra_params)
            
            # Make API call
            response = await self.client.messages.create(**params)
            
            content = response.content[0].text if response.content else ""
            response_time = time.time() - start_time
            
            return LLMResponse(
                content=content,
                provider=self.config.provider,
                model=self.config.model,
                usage={
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                },
                finish_reason=response.stop_reason,
                response_time=response_time,
                raw_response=response.model_dump()
            )
            
        except Exception as e:
            self.logger.error(f"Anthropic API error: {e}")
            raise
    
    async def generate_stream(self, messages: List[LLMMessage], 
                            **kwargs) -> AsyncGenerator[str, None]:
        """Generate streaming response using Anthropic API"""
        try:
            # Convert messages to Anthropic format
            anthropic_messages = []
            system_message = None
            
            for msg in messages:
                if msg.role == MessageRole.SYSTEM:
                    system_message = msg.content
                else:
                    anthropic_messages.append({
                        "role": msg.role.value,
                        "content": msg.content
                    })
            
            # Prepare request parameters
            params = {
                "model": self.config.model,
                "messages": anthropic_messages,
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", self.config.temperature),
                "stream": True
            }
            
            if system_message:
                params["system"] = system_message
            
            # Make streaming API call
            async with self.client.messages.stream(**params) as stream:
                async for text in stream.text_stream:
                    yield text
                    
        except Exception as e:
            self.logger.error(f"Anthropic streaming error: {e}")
            raise

class OpenRouterProvider(OpenAIProvider):
    """OpenRouter LLM provider - extends OpenAI provider with OpenRouter-specific configuration"""
    
    def _initialize_client(self):
        """Initialize OpenRouter client with custom base URL and headers"""
        self.client = openai.AsyncOpenAI(
            api_key=self.config.api_key,
            base_url="https://openrouter.ai/api/v1",
            organization=self.config.organization,
            timeout=self.config.timeout,
            max_retries=self.config.max_retries,
            default_headers={
                "HTTP-Referer": "https://jarvis-ai.local",
                "X-Title": "Jarvis AI Assistant",
                **self.config.custom_headers
            }
        )
    
    async def generate_response(self, messages: List[LLMMessage], 
                              **kwargs) -> LLMResponse:
        """Generate response using OpenRouter API"""
        response = await super().generate_response(messages, **kwargs)
        # Update provider info to reflect OpenRouter
        response.provider = LLMProvider.OPENROUTER
        return response
    
    async def generate_stream(self, messages: List[LLMMessage], 
                            **kwargs) -> AsyncGenerator[str, None]:
        """Generate streaming response using OpenRouter API"""
        async for chunk in super().generate_stream(messages, **kwargs):
            yield chunk

class OllamaProvider(BaseLLMProvider):
    """Ollama local LLM provider"""
    
    def _initialize_client(self):
        """Initialize Ollama client"""
        self.base_url = self.config.api_base or "http://localhost:11434"
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        )
    
    async def generate_response(self, messages: List[LLMMessage], 
                              **kwargs) -> LLMResponse:
        """Generate response using Ollama API"""
        start_time = time.time()
        
        try:
            # Prepare request data
            data = {
                "model": self.config.model,
                "messages": self._prepare_messages(messages),
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", self.config.temperature),
                    "top_p": kwargs.get("top_p", self.config.top_p),
                    "num_predict": kwargs.get("max_tokens", self.config.max_tokens)
                }
            }
            
            # Add extra parameters
            data.update(self.config.extra_params)
            
            # Make API call
            async with self.session.post(
                f"{self.base_url}/api/chat",
                json=data,
                headers=self.config.custom_headers
            ) as response:
                response.raise_for_status()
                result = await response.json()
            
            content = result.get("message", {}).get("content", "")
            response_time = time.time() - start_time
            
            return LLMResponse(
                content=content,
                provider=self.config.provider,
                model=self.config.model,
                usage={
                    "prompt_tokens": result.get("prompt_eval_count", 0),
                    "completion_tokens": result.get("eval_count", 0),
                    "total_tokens": result.get("prompt_eval_count", 0) + result.get("eval_count", 0)
                },
                finish_reason=result.get("done_reason", "stop"),
                response_time=response_time,
                raw_response=result
            )
            
        except Exception as e:
            self.logger.error(f"Ollama API error: {e}")
            raise
    
    async def generate_stream(self, messages: List[LLMMessage], 
                            **kwargs) -> AsyncGenerator[str, None]:
        """Generate streaming response using Ollama API"""
        try:
            # Prepare request data
            data = {
                "model": self.config.model,
                "messages": self._prepare_messages(messages),
                "stream": True,
                "options": {
                    "temperature": kwargs.get("temperature", self.config.temperature),
                    "top_p": kwargs.get("top_p", self.config.top_p),
                    "num_predict": kwargs.get("max_tokens", self.config.max_tokens)
                }
            }
            
            # Make streaming API call
            async with self.session.post(
                f"{self.base_url}/api/chat",
                json=data,
                headers=self.config.custom_headers
            ) as response:
                response.raise_for_status()
                
                async for line in response.content:
                    if line:
                        try:
                            chunk = json.loads(line.decode('utf-8'))
                            if "message" in chunk and "content" in chunk["message"]:
                                yield chunk["message"]["content"]
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            self.logger.error(f"Ollama streaming error: {e}")
            raise

class LLMRouter:
    """Router for managing multiple LLM providers"""
    
    def __init__(self):
        self.providers: Dict[str, BaseLLMProvider] = {}
        self.default_provider: Optional[str] = None
        self.logger = logging.getLogger(__name__)
        self.usage_stats: Dict[str, Dict[str, int]] = {}
        self.error_counts: Dict[str, int] = {}
    
    def add_provider(self, name: str, provider: BaseLLMProvider, 
                    is_default: bool = False):
        """Add a provider to the router"""
        self.providers[name] = provider
        self.usage_stats[name] = {
            "requests": 0,
            "tokens": 0,
            "errors": 0
        }
        self.error_counts[name] = 0
        
        if is_default or not self.default_provider:
            self.default_provider = name
        
        self.logger.info(f"Provider {name} added to router")
    
    def remove_provider(self, name: str):
        """Remove a provider from the router"""
        if name in self.providers:
            del self.providers[name]
            del self.usage_stats[name]
            del self.error_counts[name]
            
            if self.default_provider == name:
                self.default_provider = next(iter(self.providers.keys()), None)
            
            self.logger.info(f"Provider {name} removed from router")
    
    async def generate_response(self, messages: List[LLMMessage], 
                              provider_name: Optional[str] = None,
                              **kwargs) -> LLMResponse:
        """Generate response using specified or default provider"""
        provider_name = provider_name or self.default_provider
        
        if not provider_name or provider_name not in self.providers:
            raise ValueError(f"Provider {provider_name} not available")
        
        provider = self.providers[provider_name]
        
        try:
            # Update request count
            self.usage_stats[provider_name]["requests"] += 1
            
            # Generate response
            response = await provider.generate_response(messages, **kwargs)
            
            # Update usage stats
            self.usage_stats[provider_name]["tokens"] += response.usage.get("total_tokens", 0)
            
            return response
            
        except Exception as e:
            # Update error stats
            self.usage_stats[provider_name]["errors"] += 1
            self.error_counts[provider_name] += 1
            
            self.logger.error(f"Provider {provider_name} error: {e}")
            raise
    
    async def generate_stream(self, messages: List[LLMMessage], 
                            provider_name: Optional[str] = None,
                            **kwargs) -> AsyncGenerator[str, None]:
        """Generate streaming response using specified or default provider"""
        provider_name = provider_name or self.default_provider
        
        if not provider_name or provider_name not in self.providers:
            raise ValueError(f"Provider {provider_name} not available")
        
        provider = self.providers[provider_name]
        
        try:
            # Update request count
            self.usage_stats[provider_name]["requests"] += 1
            
            # Generate streaming response
            async for chunk in provider.generate_stream(messages, **kwargs):
                yield chunk
                
        except Exception as e:
            # Update error stats
            self.usage_stats[provider_name]["errors"] += 1
            self.error_counts[provider_name] += 1
            
            self.logger.error(f"Provider {provider_name} streaming error: {e}")
            raise
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return list(self.providers.keys())
    
    def get_provider_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get usage statistics for all providers"""
        stats = {}
        for name, provider in self.providers.items():
            stats[name] = {
                "provider_type": provider.config.provider.value,
                "model": provider.config.model,
                "usage": self.usage_stats[name],
                "error_count": self.error_counts[name],
                "is_default": name == self.default_provider
            }
        return stats
    
    async def close_all(self):
        """Close all provider connections"""
        for provider in self.providers.values():
            await provider.close()

# Factory functions
def create_openai_provider(api_key: str, model: str = "gpt-3.5-turbo", 
                          **kwargs) -> OpenAIProvider:
    """Create OpenAI provider"""
    config = LLMConfig(
        provider=LLMProvider.OPENAI,
        model=model,
        api_key=api_key,
        **kwargs
    )
    return OpenAIProvider(config)

def create_anthropic_provider(api_key: str, model: str = "claude-3-sonnet-20240229", 
                             **kwargs) -> AnthropicProvider:
    """Create Anthropic provider"""
    config = LLMConfig(
        provider=LLMProvider.ANTHROPIC,
        model=model,
        api_key=api_key,
        **kwargs
    )
    return AnthropicProvider(config)

def create_ollama_provider(model: str, base_url: str = "http://localhost:11434", 
                          **kwargs) -> OllamaProvider:
    """Create Ollama provider"""
    config = LLMConfig(
        provider=LLMProvider.OLLAMA,
        model=model,
        api_base=base_url,
        **kwargs
    )
    return OllamaProvider(config)

def create_openrouter_provider(api_key: str, model: str = "openai/gpt-3.5-turbo", 
                              **kwargs) -> OpenRouterProvider:
    """Create OpenRouter provider"""
    config = LLMConfig(
        provider=LLMProvider.OPENROUTER,
        model=model,
        api_key=api_key,
        **kwargs
    )
    return OpenRouterProvider(config)

# Export main classes
__all__ = [
    'LLMRouter',
    'BaseLLMProvider',
    'OpenAIProvider',
    'AnthropicProvider',
    'OpenRouterProvider',
    'OllamaProvider',
    'LLMProvider',
    'LLMMessage',
    'LLMResponse',
    'LLMConfig',
    'MessageRole',
    'ResponseFormat',
    'create_openai_provider',
    'create_anthropic_provider',
    'create_openrouter_provider',
    'create_ollama_provider'
]