"""Ollama Provider Adapter

Adapter for Ollama local LLM server.
"""

import json
import requests
import time
from typing import List, Dict, Any, Optional, Iterator, Union

from ..base import LLMProvider, LLMMessage, LLMResponse, LLMConfig, ModelCapabilities, MessageRole
from ..registry import MODEL_CATALOG


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider"""
    
    def __init__(self, base_url: str = "http://localhost:11434", **kwargs):
        super().__init__(**kwargs)
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 30
    
    @property
    def name(self) -> str:
        return "ollama"
    
    @property
    def capabilities(self) -> ModelCapabilities:
        # Return default capabilities - will be overridden by specific model
        return ModelCapabilities(
            max_context=131072,
            supports_tools=True,
            supports_vision=False,
            supports_json_mode=True,
            supports_streaming=True,
            cost_per_1k_input=0.0,
            cost_per_1k_output=0.0,
            typical_latency_ms=2000
        )
    
    def chat(
        self,
        messages: List[LLMMessage],
        tools: Optional[List[Dict[str, Any]]] = None,
        config: Optional[LLMConfig] = None,
        model: str = "llama3.2:3b",
        **kwargs
    ) -> Union[LLMResponse, Iterator[LLMResponse]]:
        """Send chat completion request to Ollama"""
        if not config:
            config = LLMConfig()
        
        # Convert messages to Ollama format
        ollama_messages = self._convert_messages(messages)
        
        # Build request payload
        payload = {
            "model": model,
            "messages": ollama_messages,
            "stream": config.stream,
            "options": {
                "temperature": config.temperature,
                "top_p": config.top_p,
                "num_predict": config.max_tokens or -1
            }
        }
        
        # Add JSON mode if requested
        if config.json_mode:
            payload["format"] = "json"
        
        # Add tools if provided
        if tools and self._model_supports_tools(model):
            payload["tools"] = self._convert_tools(tools)
        
        start_time = time.time()
        
        try:
            if config.stream:
                return self._stream_chat(payload, start_time)
            else:
                return self._sync_chat(payload, start_time)
        
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama request failed: {e}")
    
    def _sync_chat(self, payload: Dict[str, Any], start_time: float) -> LLMResponse:
        """Synchronous chat completion"""
        response = self.session.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        
        result = response.json()
        latency_ms = (time.time() - start_time) * 1000
        
        # Extract response content
        content = result.get("message", {}).get("content", "")
        tool_calls = None
        
        # Handle tool calls if present
        if "tool_calls" in result.get("message", {}):
            tool_calls = result["message"]["tool_calls"]
        
        # Extract usage information
        usage = None
        if "prompt_eval_count" in result or "eval_count" in result:
            usage = {
                "prompt_tokens": result.get("prompt_eval_count", 0),
                "completion_tokens": result.get("eval_count", 0),
                "total_tokens": result.get("prompt_eval_count", 0) + result.get("eval_count", 0)
            }
        
        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            finish_reason=result.get("done_reason"),
            usage=usage,
            model=payload["model"],
            provider=self.name,
            latency_ms=latency_ms
        )
    
    def _stream_chat(self, payload: Dict[str, Any], start_time: float) -> Iterator[LLMResponse]:
        """Streaming chat completion"""
        response = self.session.post(
            f"{self.base_url}/api/chat",
            json=payload,
            stream=True,
            timeout=60
        )
        response.raise_for_status()
        
        accumulated_content = ""
        accumulated_tool_calls = None
        
        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line.decode('utf-8'))
                    
                    # Extract content from chunk
                    message = chunk.get("message", {})
                    content_delta = message.get("content", "")
                    accumulated_content += content_delta
                    
                    # Handle tool calls
                    if "tool_calls" in message:
                        accumulated_tool_calls = message["tool_calls"]
                    
                    # Calculate latency
                    latency_ms = (time.time() - start_time) * 1000
                    
                    # Yield chunk response
                    yield LLMResponse(
                        content=content_delta,
                        tool_calls=accumulated_tool_calls if chunk.get("done") else None,
                        finish_reason=chunk.get("done_reason") if chunk.get("done") else None,
                        usage=self._extract_usage(chunk) if chunk.get("done") else None,
                        model=payload["model"],
                        provider=self.name,
                        latency_ms=latency_ms if chunk.get("done") else None
                    )
                    
                    if chunk.get("done"):
                        break
                        
                except json.JSONDecodeError:
                    continue
    
    def count_tokens(self, messages: List[LLMMessage]) -> int:
        """Estimate token count (rough approximation)"""
        # Simple approximation: ~4 characters per token
        total_chars = sum(len(msg.content) for msg in messages)
        return total_chars // 4
    
    def is_available(self) -> bool:
        """Check if Ollama server is available"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def list_models(self) -> List[str]:
        """List available models on Ollama server"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            
            result = response.json()
            models = []
            
            for model in result.get("models", []):
                model_name = model.get("name", "")
                if model_name:
                    models.append(f"ollama/{model_name}")
            
            return models
        
        except Exception:
            return []
    
    def pull_model(self, model: str) -> bool:
        """Pull a model to Ollama server"""
        try:
            # Remove ollama/ prefix if present
            if model.startswith("ollama/"):
                model = model[7:]
            
            payload = {"name": model}
            response = self.session.post(
                f"{self.base_url}/api/pull",
                json=payload,
                timeout=300  # 5 minutes for model download
            )
            response.raise_for_status()
            return True
        
        except Exception:
            return False
    
    def _convert_messages(self, messages: List[LLMMessage]) -> List[Dict[str, Any]]:
        """Convert messages to Ollama format"""
        ollama_messages = []
        
        for msg in messages:
            ollama_msg = {
                "role": msg.role.value,
                "content": msg.content
            }
            
            # Add tool calls if present
            if msg.tool_calls:
                ollama_msg["tool_calls"] = msg.tool_calls
            
            # Add tool call ID if present
            if msg.tool_call_id:
                ollama_msg["tool_call_id"] = msg.tool_call_id
            
            ollama_messages.append(ollama_msg)
        
        return ollama_messages
    
    def _convert_tools(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert tools to Ollama format"""
        # Ollama uses OpenAI-compatible tool format
        return tools
    
    def _model_supports_tools(self, model: str) -> bool:
        """Check if model supports tool calling"""
        # Remove ollama/ prefix for lookup
        lookup_name = f"ollama/{model}" if not model.startswith("ollama/") else model
        
        if lookup_name in MODEL_CATALOG:
            return MODEL_CATALOG[lookup_name].supports_tools
        
        # Default assumption for unknown models
        return "llama" in model.lower() or "qwen" in model.lower()
    
    def _extract_usage(self, chunk: Dict[str, Any]) -> Optional[Dict[str, int]]:
        """Extract usage information from response chunk"""
        if "prompt_eval_count" in chunk or "eval_count" in chunk:
            return {
                "prompt_tokens": chunk.get("prompt_eval_count", 0),
                "completion_tokens": chunk.get("eval_count", 0),
                "total_tokens": chunk.get("prompt_eval_count", 0) + chunk.get("eval_count", 0)
            }
        return None
    
    def get_model_info(self, model: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a model"""
        try:
            # Remove ollama/ prefix if present
            if model.startswith("ollama/"):
                model = model[7:]
            
            response = self.session.post(
                f"{self.base_url}/api/show",
                json={"name": model}
            )
            response.raise_for_status()
            return response.json()
        
        except Exception:
            return None