"""Groq Provider Adapter

Adapter for Groq API (fast inference for open source models).
"""

import json
import time
from typing import List, Dict, Any, Optional, Iterator, Union

try:
    import groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    groq = None

from ..base import LLMProvider, LLMMessage, LLMResponse, LLMConfig, ModelCapabilities, MessageRole
from ..registry import MODEL_CATALOG


class GroqProvider(LLMProvider):
    """Groq provider for fast inference"""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        if not GROQ_AVAILABLE:
            raise ImportError("groq package not installed. Install with: pip install groq")
        
        super().__init__(api_key=api_key, **kwargs)
        
        if not api_key:
            raise ValueError("Groq API key is required")
        
        self.client = groq.Groq(api_key=api_key)
    
    @property
    def name(self) -> str:
        return "groq"
    
    @property
    def capabilities(self) -> ModelCapabilities:
        # Return default capabilities for Llama 3.1 70B
        return MODEL_CATALOG.get("llama-3.1-70b-versatile", ModelCapabilities(
            max_context=131072,
            supports_tools=True,
            supports_vision=False,
            supports_json_mode=True,
            supports_streaming=True,
            cost_per_1k_input=0.59,
            cost_per_1k_output=0.79,
            typical_latency_ms=300
        ))
    
    def chat(
        self,
        messages: List[LLMMessage],
        tools: Optional[List[Dict[str, Any]]] = None,
        config: Optional[LLMConfig] = None,
        model: str = "llama-3.1-70b-versatile",
        **kwargs
    ) -> Union[LLMResponse, Iterator[LLMResponse]]:
        """Send chat completion request to Groq"""
        if not config:
            config = LLMConfig()
        
        # Convert messages to OpenAI format (Groq uses OpenAI-compatible API)
        openai_messages = self._convert_messages(messages)
        
        # Build request parameters
        request_params = {
            "model": model,
            "messages": openai_messages,
            "max_tokens": config.max_tokens or 4096,
            "temperature": config.temperature,
            "top_p": config.top_p,
            "stream": config.stream
        }
        
        # Add tools if provided
        if tools:
            request_params["tools"] = tools
            request_params["tool_choice"] = "auto"
        
        # Add JSON mode if requested
        if config.response_format == "json":
            request_params["response_format"] = {"type": "json_object"}
        
        start_time = time.time()
        
        try:
            if config.stream:
                return self._stream_chat(request_params, start_time, model)
            else:
                return self._sync_chat(request_params, start_time, model)
        
        except Exception as e:
            raise RuntimeError(f"Groq request failed: {e}")
    
    def _sync_chat(self, request_params: Dict[str, Any], start_time: float, model_name: str) -> LLMResponse:
        """Synchronous chat completion"""
        response = self.client.chat.completions.create(**request_params)
        
        latency_ms = (time.time() - start_time) * 1000
        
        choice = response.choices[0]
        message = choice.message
        
        # Extract tool calls
        tool_calls = None
        if hasattr(message, 'tool_calls') and message.tool_calls:
            tool_calls = []
            for tc in message.tool_calls:
                tool_calls.append({
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                })
        
        # Extract usage information
        usage = None
        if hasattr(response, 'usage') and response.usage:
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        
        return LLMResponse(
            content=message.content or "",
            tool_calls=tool_calls,
            finish_reason=choice.finish_reason,
            usage=usage,
            model=model_name,
            provider=self.name,
            latency_ms=latency_ms
        )
    
    def _stream_chat(self, request_params: Dict[str, Any], start_time: float, model_name: str) -> Iterator[LLMResponse]:
        """Streaming chat completion"""
        stream = self.client.chat.completions.create(**request_params)
        
        accumulated_content = ""
        accumulated_tool_calls = None
        
        for chunk in stream:
            if not chunk.choices:
                continue
            
            choice = chunk.choices[0]
            delta = choice.delta
            
            # Handle content delta
            if hasattr(delta, 'content') and delta.content:
                content_delta = delta.content
                accumulated_content += content_delta
                
                yield LLMResponse(
                    content=content_delta,
                    tool_calls=None,
                    finish_reason=None,
                    usage=None,
                    model=model_name,
                    provider=self.name,
                    latency_ms=None
                )
            
            # Handle tool calls delta
            if hasattr(delta, 'tool_calls') and delta.tool_calls:
                if not accumulated_tool_calls:
                    accumulated_tool_calls = []
                
                for tc_delta in delta.tool_calls:
                    # Extend tool calls list if needed
                    while len(accumulated_tool_calls) <= tc_delta.index:
                        accumulated_tool_calls.append({
                            "id": "",
                            "type": "function",
                            "function": {"name": "", "arguments": ""}
                        })
                    
                    # Update tool call
                    if tc_delta.id:
                        accumulated_tool_calls[tc_delta.index]["id"] = tc_delta.id
                    
                    if tc_delta.function:
                        if tc_delta.function.name:
                            accumulated_tool_calls[tc_delta.index]["function"]["name"] = tc_delta.function.name
                        if tc_delta.function.arguments:
                            accumulated_tool_calls[tc_delta.index]["function"]["arguments"] += tc_delta.function.arguments
            
            # Handle finish
            if choice.finish_reason:
                latency_ms = (time.time() - start_time) * 1000
                
                # Extract usage from final chunk if available
                usage = None
                if hasattr(chunk, 'usage') and chunk.usage:
                    usage = {
                        "prompt_tokens": chunk.usage.prompt_tokens,
                        "completion_tokens": chunk.usage.completion_tokens,
                        "total_tokens": chunk.usage.total_tokens
                    }
                
                yield LLMResponse(
                    content="",
                    tool_calls=accumulated_tool_calls,
                    finish_reason=choice.finish_reason,
                    usage=usage,
                    model=model_name,
                    provider=self.name,
                    latency_ms=latency_ms
                )
                break
    
    def count_tokens(self, messages: List[LLMMessage]) -> int:
        """Estimate token count (rough approximation)"""
        # Groq uses similar tokenization to OpenAI models
        # Rough estimate: 4 characters per token
        total_chars = sum(len(msg.content) for msg in messages)
        return int(total_chars / 4)
    
    def is_available(self) -> bool:
        """Check if Groq API is available"""
        try:
            # Simple test request
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return True
        except Exception:
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        try:
            models = self.client.models.list()
            return [model.id for model in models.data]
        except Exception:
            # Return known Groq models as fallback
            return [
                "llama-3.1-405b-reasoning",
                "llama-3.1-70b-versatile",
                "llama-3.1-8b-instant",
                "llama3-groq-70b-8192-tool-use-preview",
                "llama3-groq-8b-8192-tool-use-preview",
                "mixtral-8x7b-32768",
                "gemma2-9b-it",
                "gemma-7b-it"
            ]
    
    def _convert_messages(self, messages: List[LLMMessage]) -> List[Dict[str, Any]]:
        """Convert messages to OpenAI format"""
        openai_messages = []
        
        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                openai_messages.append({
                    "role": "system",
                    "content": msg.content
                })
            
            elif msg.role == MessageRole.USER:
                openai_messages.append({
                    "role": "user",
                    "content": msg.content
                })
            
            elif msg.role == MessageRole.ASSISTANT:
                message = {
                    "role": "assistant",
                    "content": msg.content
                }
                
                # Add tool calls if present
                if msg.tool_calls:
                    message["tool_calls"] = msg.tool_calls
                
                openai_messages.append(message)
            
            elif msg.role == MessageRole.TOOL:
                openai_messages.append({
                    "role": "tool",
                    "content": msg.content,
                    "tool_call_id": msg.tool_call_id
                })
        
        return openai_messages