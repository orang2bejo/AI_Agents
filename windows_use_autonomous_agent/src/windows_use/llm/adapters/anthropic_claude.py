"""Anthropic Claude Provider Adapter

Adapter for Anthropic Claude API.
"""

import json
import time
from typing import List, Dict, Any, Optional, Iterator, Union

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    anthropic = None

from ..base import LLMProvider, LLMMessage, LLMResponse, LLMConfig, ModelCapabilities, MessageRole
from ..registry import MODEL_CATALOG


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider"""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic package not installed. Install with: pip install anthropic")
        
        super().__init__(api_key=api_key, **kwargs)
        
        if not api_key:
            raise ValueError("Anthropic API key is required")
        
        self.client = anthropic.Anthropic(api_key=api_key)
    
    @property
    def name(self) -> str:
        return "anthropic"
    
    @property
    def capabilities(self) -> ModelCapabilities:
        # Return default capabilities for Claude 3.5 Sonnet
        return MODEL_CATALOG.get("claude-3.5-sonnet", ModelCapabilities(
            max_context=200000,
            supports_tools=True,
            supports_vision=True,
            supports_json_mode=False,
            supports_streaming=True,
            cost_per_1k_input=3.00,
            cost_per_1k_output=15.00,
            typical_latency_ms=1000
        ))
    
    def chat(
        self,
        messages: List[LLMMessage],
        tools: Optional[List[Dict[str, Any]]] = None,
        config: Optional[LLMConfig] = None,
        model: str = "claude-3-5-sonnet-20241022",
        **kwargs
    ) -> Union[LLMResponse, Iterator[LLMResponse]]:
        """Send chat completion request to Claude"""
        if not config:
            config = LLMConfig()
        
        # Convert messages to Claude format
        claude_messages, system_message = self._convert_messages(messages)
        
        # Build request parameters
        request_params = {
            "model": model,
            "messages": claude_messages,
            "max_tokens": config.max_tokens or 4096,
            "temperature": config.temperature,
            "top_p": config.top_p,
            "stream": config.stream
        }
        
        # Add system message if present
        if system_message:
            request_params["system"] = system_message
        
        # Add tools if provided
        if tools:
            request_params["tools"] = self._convert_tools(tools)
        
        start_time = time.time()
        
        try:
            if config.stream:
                return self._stream_chat(request_params, start_time, model)
            else:
                return self._sync_chat(request_params, start_time, model)
        
        except Exception as e:
            raise RuntimeError(f"Claude request failed: {e}")
    
    def _sync_chat(self, request_params: Dict[str, Any], start_time: float, model_name: str) -> LLMResponse:
        """Synchronous chat completion"""
        response = self.client.messages.create(**request_params)
        
        latency_ms = (time.time() - start_time) * 1000
        
        # Extract content and tool calls
        content = ""
        tool_calls = None
        
        for content_block in response.content:
            if content_block.type == "text":
                content += content_block.text
            elif content_block.type == "tool_use":
                if not tool_calls:
                    tool_calls = []
                
                tool_call = {
                    "id": content_block.id,
                    "type": "function",
                    "function": {
                        "name": content_block.name,
                        "arguments": json.dumps(content_block.input)
                    }
                }
                tool_calls.append(tool_call)
        
        # Extract usage information
        usage = None
        if hasattr(response, 'usage') and response.usage:
            usage = {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            }
        
        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            finish_reason=response.stop_reason,
            usage=usage,
            model=model_name,
            provider=self.name,
            latency_ms=latency_ms
        )
    
    def _stream_chat(self, request_params: Dict[str, Any], start_time: float, model_name: str) -> Iterator[LLMResponse]:
        """Streaming chat completion"""
        stream = self.client.messages.create(**request_params)
        
        accumulated_content = ""
        accumulated_tool_calls = None
        current_tool_call = None
        
        for event in stream:
            if event.type == "message_start":
                # Message started
                continue
            
            elif event.type == "content_block_start":
                if event.content_block.type == "tool_use":
                    # Start of tool use block
                    current_tool_call = {
                        "id": event.content_block.id,
                        "type": "function",
                        "function": {
                            "name": event.content_block.name,
                            "arguments": ""
                        }
                    }
            
            elif event.type == "content_block_delta":
                if event.delta.type == "text_delta":
                    # Text content delta
                    content_delta = event.delta.text
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
                
                elif event.delta.type == "input_json_delta":
                    # Tool call arguments delta
                    if current_tool_call:
                        current_tool_call["function"]["arguments"] += event.delta.partial_json
            
            elif event.type == "content_block_stop":
                if current_tool_call:
                    # Finalize tool call
                    if not accumulated_tool_calls:
                        accumulated_tool_calls = []
                    accumulated_tool_calls.append(current_tool_call)
                    current_tool_call = None
            
            elif event.type == "message_delta":
                # Message metadata update
                continue
            
            elif event.type == "message_stop":
                # Final message with usage info
                latency_ms = (time.time() - start_time) * 1000
                
                usage = None
                if hasattr(event, 'usage') and event.usage:
                    usage = {
                        "prompt_tokens": event.usage.input_tokens,
                        "completion_tokens": event.usage.output_tokens,
                        "total_tokens": event.usage.input_tokens + event.usage.output_tokens
                    }
                
                yield LLMResponse(
                    content="",
                    tool_calls=accumulated_tool_calls,
                    finish_reason="stop",
                    usage=usage,
                    model=model_name,
                    provider=self.name,
                    latency_ms=latency_ms
                )
                break
    
    def count_tokens(self, messages: List[LLMMessage]) -> int:
        """Estimate token count (rough approximation)"""
        # Claude uses a different tokenizer, but we'll use a rough estimate
        # Claude tokens are roughly 3.5 characters per token
        total_chars = sum(len(msg.content) for msg in messages)
        return int(total_chars / 3.5)
    
    def is_available(self) -> bool:
        """Check if Claude API is available"""
        try:
            # Simple test request
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1,
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except Exception:
            return False
    
    def _convert_messages(self, messages: List[LLMMessage]) -> tuple[List[Dict[str, Any]], Optional[str]]:
        """Convert messages to Claude format"""
        claude_messages = []
        system_message = None
        
        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                # Claude uses separate system parameter
                if system_message:
                    system_message += "\n\n" + msg.content
                else:
                    system_message = msg.content
            
            elif msg.role == MessageRole.USER:
                claude_messages.append({
                    "role": "user",
                    "content": msg.content
                })
            
            elif msg.role == MessageRole.ASSISTANT:
                content = []
                
                # Add text content if present
                if msg.content:
                    content.append({
                        "type": "text",
                        "text": msg.content
                    })
                
                # Add tool calls if present
                if msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        if tool_call.get("type") == "function":
                            func = tool_call.get("function", {})
                            content.append({
                                "type": "tool_use",
                                "id": tool_call.get("id"),
                                "name": func.get("name"),
                                "input": json.loads(func.get("arguments", "{}"))
                            })
                
                claude_messages.append({
                    "role": "assistant",
                    "content": content
                })
            
            elif msg.role == MessageRole.TOOL:
                # Tool results are sent as user messages with tool_result content
                claude_messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": msg.tool_call_id,
                        "content": msg.content
                    }]
                })
        
        return claude_messages, system_message
    
    def _convert_tools(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert tools to Claude format"""
        claude_tools = []
        
        for tool in tools:
            if tool.get("type") == "function":
                func = tool.get("function", {})
                
                claude_tool = {
                    "name": func.get("name"),
                    "description": func.get("description", ""),
                    "input_schema": func.get("parameters", {})
                }
                
                claude_tools.append(claude_tool)
        
        return claude_tools