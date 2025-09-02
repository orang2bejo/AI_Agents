"""Google Gemini Provider Adapter

Adapter for Google Gemini API.
"""

import json
import time
from typing import List, Dict, Any, Optional, Iterator, Union

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

from ..base import LLMProvider, LLMMessage, LLMResponse, LLMConfig, ModelCapabilities, MessageRole
from ..registry import MODEL_CATALOG


class GeminiProvider(LLMProvider):
    """Google Gemini provider"""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai package not installed. Install with: pip install google-generativeai")
        
        super().__init__(api_key=api_key, **kwargs)
        
        if not api_key:
            raise ValueError("Gemini API key is required")
        
        genai.configure(api_key=api_key)
        
        # Safety settings - allow most content for agent use
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
    
    @property
    def name(self) -> str:
        return "gemini"
    
    @property
    def capabilities(self) -> ModelCapabilities:
        # Return default capabilities for Gemini Flash
        return MODEL_CATALOG.get("gemini-1.5-flash", ModelCapabilities(
            max_context=1048576,
            supports_tools=True,
            supports_vision=True,
            supports_json_mode=True,
            supports_streaming=True,
            cost_per_1k_input=0.075,
            cost_per_1k_output=0.30,
            typical_latency_ms=800
        ))
    
    def chat(
        self,
        messages: List[LLMMessage],
        tools: Optional[List[Dict[str, Any]]] = None,
        config: Optional[LLMConfig] = None,
        model: str = "gemini-1.5-flash",
        **kwargs
    ) -> Union[LLMResponse, Iterator[LLMResponse]]:
        """Send chat completion request to Gemini"""
        if not config:
            config = LLMConfig()
        
        # Initialize model
        generation_config = {
            "temperature": config.temperature,
            "top_p": config.top_p,
            "max_output_tokens": config.max_tokens or 8192,
        }
        
        # Add JSON mode if requested
        if config.json_mode:
            generation_config["response_mime_type"] = "application/json"
        
        # Convert tools to Gemini format
        gemini_tools = None
        if tools:
            gemini_tools = self._convert_tools(tools)
        
        try:
            model_instance = genai.GenerativeModel(
                model_name=model,
                generation_config=generation_config,
                safety_settings=self.safety_settings,
                tools=gemini_tools
            )
            
            # Convert messages to Gemini format
            gemini_messages = self._convert_messages(messages)
            
            start_time = time.time()
            
            if config.stream:
                return self._stream_chat(model_instance, gemini_messages, start_time, model)
            else:
                return self._sync_chat(model_instance, gemini_messages, start_time, model)
        
        except Exception as e:
            raise RuntimeError(f"Gemini request failed: {e}")
    
    def _sync_chat(self, model_instance, messages: List[Dict[str, Any]], start_time: float, model_name: str) -> LLMResponse:
        """Synchronous chat completion"""
        response = model_instance.generate_content(
            messages,
            stream=False
        )
        
        latency_ms = (time.time() - start_time) * 1000
        
        # Extract content
        content = ""
        tool_calls = None
        
        if response.candidates:
            candidate = response.candidates[0]
            
            # Extract text content
            if candidate.content and candidate.content.parts:
                for part in candidate.content.parts:
                    if hasattr(part, 'text') and part.text:
                        content += part.text
                    elif hasattr(part, 'function_call') and part.function_call:
                        # Handle function calls
                        if not tool_calls:
                            tool_calls = []
                        
                        tool_call = {
                            "id": f"call_{int(time.time() * 1000)}",
                            "type": "function",
                            "function": {
                                "name": part.function_call.name,
                                "arguments": json.dumps(dict(part.function_call.args))
                            }
                        }
                        tool_calls.append(tool_call)
        
        # Extract usage information
        usage = None
        if hasattr(response, 'usage_metadata') and response.usage_metadata:
            usage = {
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "completion_tokens": response.usage_metadata.candidates_token_count,
                "total_tokens": response.usage_metadata.total_token_count
            }
        
        # Determine finish reason
        finish_reason = None
        if response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'finish_reason'):
                finish_reason = str(candidate.finish_reason)
        
        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            finish_reason=finish_reason,
            usage=usage,
            model=model_name,
            provider=self.name,
            latency_ms=latency_ms
        )
    
    def _stream_chat(self, model_instance, messages: List[Dict[str, Any]], start_time: float, model_name: str) -> Iterator[LLMResponse]:
        """Streaming chat completion"""
        response = model_instance.generate_content(
            messages,
            stream=True
        )
        
        accumulated_content = ""
        accumulated_tool_calls = None
        
        for chunk in response:
            if chunk.candidates:
                candidate = chunk.candidates[0]
                
                # Extract content delta
                content_delta = ""
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            content_delta += part.text
                        elif hasattr(part, 'function_call') and part.function_call:
                            # Handle function calls
                            if not accumulated_tool_calls:
                                accumulated_tool_calls = []
                            
                            tool_call = {
                                "id": f"call_{int(time.time() * 1000)}",
                                "type": "function",
                                "function": {
                                    "name": part.function_call.name,
                                    "arguments": json.dumps(dict(part.function_call.args))
                                }
                            }
                            accumulated_tool_calls.append(tool_call)
                
                accumulated_content += content_delta
                
                # Calculate latency
                latency_ms = (time.time() - start_time) * 1000
                
                # Determine if this is the final chunk
                is_final = hasattr(candidate, 'finish_reason') and candidate.finish_reason
                
                yield LLMResponse(
                    content=content_delta,
                    tool_calls=accumulated_tool_calls if is_final else None,
                    finish_reason=str(candidate.finish_reason) if is_final else None,
                    usage=self._extract_usage(chunk) if is_final else None,
                    model=model_name,
                    provider=self.name,
                    latency_ms=latency_ms if is_final else None
                )
    
    def count_tokens(self, messages: List[LLMMessage]) -> int:
        """Count tokens using Gemini's tokenizer"""
        try:
            # Use Gemini's count_tokens method
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Convert messages to text for counting
            text_content = "\n".join([f"{msg.role.value}: {msg.content}" for msg in messages])
            
            result = model.count_tokens(text_content)
            return result.total_tokens
        
        except Exception:
            # Fallback to rough estimation
            total_chars = sum(len(msg.content) for msg in messages)
            return total_chars // 4
    
    def is_available(self) -> bool:
        """Check if Gemini API is available"""
        try:
            # Try to list models as a health check
            models = list(genai.list_models())
            return len(models) > 0
        except Exception:
            return False
    
    def _convert_messages(self, messages: List[LLMMessage]) -> List[Dict[str, Any]]:
        """Convert messages to Gemini format"""
        gemini_messages = []
        
        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                # Gemini doesn't have system role, prepend to first user message
                if gemini_messages and gemini_messages[-1].get("role") == "user":
                    gemini_messages[-1]["parts"][0]["text"] = f"{msg.content}\n\n{gemini_messages[-1]['parts'][0]['text']}"
                else:
                    # Create a user message with system content
                    gemini_messages.append({
                        "role": "user",
                        "parts": [{"text": msg.content}]
                    })
            
            elif msg.role == MessageRole.USER:
                gemini_messages.append({
                    "role": "user",
                    "parts": [{"text": msg.content}]
                })
            
            elif msg.role == MessageRole.ASSISTANT:
                parts = [{"text": msg.content}] if msg.content else []
                
                # Add function calls if present
                if msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        if tool_call.get("type") == "function":
                            func = tool_call.get("function", {})
                            parts.append({
                                "function_call": {
                                    "name": func.get("name"),
                                    "args": json.loads(func.get("arguments", "{}"))
                                }
                            })
                
                gemini_messages.append({
                    "role": "model",
                    "parts": parts
                })
            
            elif msg.role == MessageRole.TOOL:
                # Tool responses are handled as user messages in Gemini
                gemini_messages.append({
                    "role": "user",
                    "parts": [{"text": f"Tool result: {msg.content}"}]
                })
        
        return gemini_messages
    
    def _convert_tools(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert tools to Gemini format"""
        gemini_tools = []
        
        for tool in tools:
            if tool.get("type") == "function":
                func = tool.get("function", {})
                
                gemini_tool = {
                    "function_declarations": [{
                        "name": func.get("name"),
                        "description": func.get("description", ""),
                        "parameters": func.get("parameters", {})
                    }]
                }
                
                gemini_tools.append(gemini_tool)
        
        return gemini_tools
    
    def _extract_usage(self, chunk) -> Optional[Dict[str, int]]:
        """Extract usage information from response chunk"""
        if hasattr(chunk, 'usage_metadata') and chunk.usage_metadata:
            return {
                "prompt_tokens": chunk.usage_metadata.prompt_token_count,
                "completion_tokens": chunk.usage_metadata.candidates_token_count,
                "total_tokens": chunk.usage_metadata.total_token_count
            }
        return None