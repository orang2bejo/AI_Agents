"""Base LLM Provider Interface

Defines the abstract base class and data structures for all LLM providers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Iterator, Union
from enum import Enum
import json


class MessageRole(Enum):
    """Standard message roles across all providers"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class LLMMessage:
    """Standardized message format"""
    role: MessageRole
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        result = {
            "role": self.role.value,
            "content": self.content
        }
        if self.tool_calls:
            result["tool_calls"] = self.tool_calls
        if self.tool_call_id:
            result["tool_call_id"] = self.tool_call_id
        if self.name:
            result["name"] = self.name
        return result


@dataclass
class LLMResponse:
    """Standardized response format"""
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    finish_reason: Optional[str] = None
    usage: Optional[Dict[str, int]] = None
    model: Optional[str] = None
    provider: Optional[str] = None
    latency_ms: Optional[float] = None
    
    def to_message(self) -> LLMMessage:
        """Convert response to message format"""
        return LLMMessage(
            role=MessageRole.ASSISTANT,
            content=self.content,
            tool_calls=self.tool_calls
        )


@dataclass
class ModelCapabilities:
    """Model capabilities and limitations"""
    max_context: int
    supports_tools: bool = False
    supports_vision: bool = False
    supports_json_mode: bool = False
    supports_streaming: bool = False
    supports_system_message: bool = True
    cost_per_1k_input: Optional[float] = None
    cost_per_1k_output: Optional[float] = None
    typical_latency_ms: Optional[int] = None


@dataclass
class LLMConfig:
    """Configuration for LLM requests"""
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: Optional[int] = None
    stream: bool = False
    json_mode: bool = False
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0


class LLMProvider(ABC):
    """Abstract base class for all LLM providers"""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        self.api_key = api_key
        self.config = kwargs
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name"""
        pass
    
    @property
    @abstractmethod
    def capabilities(self) -> ModelCapabilities:
        """Model capabilities"""
        pass
    
    @abstractmethod
    def chat(
        self,
        messages: List[LLMMessage],
        tools: Optional[List[Dict[str, Any]]] = None,
        config: Optional[LLMConfig] = None,
        **kwargs
    ) -> Union[LLMResponse, Iterator[LLMResponse]]:
        """Send chat completion request"""
        pass
    
    @abstractmethod
    def count_tokens(self, messages: List[LLMMessage]) -> int:
        """Count tokens in messages"""
        pass
    
    def is_available(self) -> bool:
        """Check if provider is available"""
        try:
            # Simple health check
            test_messages = [LLMMessage(role=MessageRole.USER, content="test")]
            response = self.chat(test_messages, config=LLMConfig(max_tokens=1))
            return True
        except Exception:
            return False
    
    def estimate_cost(
        self, 
        input_tokens: int, 
        output_tokens: int
    ) -> Optional[float]:
        """Estimate cost for token usage"""
        caps = self.capabilities
        if caps.cost_per_1k_input and caps.cost_per_1k_output:
            input_cost = (input_tokens / 1000) * caps.cost_per_1k_input
            output_cost = (output_tokens / 1000) * caps.cost_per_1k_output
            return input_cost + output_cost
        return None
    
    def validate_tools(self, tools: List[Dict[str, Any]]) -> bool:
        """Validate tool schema"""
        if not self.capabilities.supports_tools:
            return False
        
        for tool in tools:
            if not isinstance(tool, dict):
                return False
            if "type" not in tool or tool["type"] != "function":
                return False
            if "function" not in tool:
                return False
            func = tool["function"]
            if "name" not in func or "parameters" not in func:
                return False
        
        return True
    
    def truncate_messages(
        self, 
        messages: List[LLMMessage], 
        max_tokens: Optional[int] = None
    ) -> List[LLMMessage]:
        """Truncate messages to fit context window"""
        if not max_tokens:
            max_tokens = self.capabilities.max_context - 1000  # Reserve for response
        
        # Always keep system message and last user message
        system_msgs = [m for m in messages if m.role == MessageRole.SYSTEM]
        user_msgs = [m for m in messages if m.role == MessageRole.USER]
        other_msgs = [m for m in messages if m.role not in [MessageRole.SYSTEM, MessageRole.USER]]
        
        # Start with system and last user message
        result = system_msgs.copy()
        if user_msgs:
            result.append(user_msgs[-1])
        
        # Add other messages if space allows
        current_tokens = self.count_tokens(result)
        for msg in reversed(other_msgs):
            msg_tokens = self.count_tokens([msg])
            if current_tokens + msg_tokens <= max_tokens:
                result.insert(-1, msg)  # Insert before last user message
                current_tokens += msg_tokens
            else:
                break
        
        return result