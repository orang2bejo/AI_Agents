"""LLM Router and Selection Logic

Intelligent routing of requests to appropriate LLM providers based on
task requirements, capabilities, and policies.
"""

from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
import time
import random

from .base import LLMProvider, LLMMessage, LLMResponse, LLMConfig
from .registry import ModelRegistry, MODEL_CATALOG


class TaskType(Enum):
    """Different types of tasks for routing decisions"""
    PLANNING = "planning"          # Quick planning and decision making
    EXECUTION = "execution"        # Tool calling and action execution
    REFLECTION = "reflection"      # Analysis and evaluation
    VISION = "vision"             # Image/screenshot analysis
    CONVERSATION = "conversation"  # General chat and Q&A
    REASONING = "reasoning"        # Complex reasoning tasks
    CODING = "coding"             # Code generation and analysis


class RoutingPolicy(Enum):
    """Routing policies for different scenarios"""
    OFFLINE_ONLY = "offline_only"      # Use only local models
    COST_OPTIMIZED = "cost_optimized"  # Minimize cost
    SPEED_OPTIMIZED = "speed_optimized" # Minimize latency
    QUALITY_OPTIMIZED = "quality_optimized" # Best quality regardless of cost
    BALANCED = "balanced"              # Balance cost, speed, and quality
    PRIVACY_FIRST = "privacy_first"    # Prefer local, fallback to privacy-focused cloud


@dataclass
class RoutingConfig:
    """Configuration for routing decisions"""
    policy: RoutingPolicy = RoutingPolicy.BALANCED
    max_cost_per_request: Optional[float] = None
    max_latency_ms: Optional[int] = None
    require_tools: bool = False
    require_vision: bool = False
    require_streaming: bool = False
    fallback_enabled: bool = True
    retry_attempts: int = 3
    preferred_providers: List[str] = None
    blocked_providers: List[str] = None


@dataclass
class RoutingResult:
    """Result of routing decision"""
    provider: LLMProvider
    model_name: str
    confidence: float
    reasoning: str
    fallback_options: List[Tuple[str, str]]  # (provider, model) pairs


class LLMRouter:
    """Intelligent router for LLM requests"""
    
    def __init__(self, registry: ModelRegistry):
        self.registry = registry
        self.performance_history: Dict[str, List[float]] = {}  # Track latencies
        self.failure_counts: Dict[str, int] = {}  # Track failures
        
        # Default routing preferences by task type
        self.task_preferences = {
            TaskType.PLANNING: {
                'preferred_models': ['groq/llama-3.1-8b', 'ollama/llama3.2:3b', 'claude-3.5-haiku'],
                'max_latency_ms': 1000,
                'require_tools': True
            },
            TaskType.EXECUTION: {
                'preferred_models': ['groq/llama-3.1-70b', 'claude-3.5-sonnet', 'gemini-1.5-flash'],
                'max_latency_ms': 2000,
                'require_tools': True
            },
            TaskType.REFLECTION: {
                'preferred_models': ['claude-3.5-sonnet', 'deepseek-r1', 'qwen2.5-72b-instruct'],
                'max_latency_ms': 5000,
                'require_tools': False
            },
            TaskType.VISION: {
                'preferred_models': ['gemini-1.5-flash', 'claude-3.5-sonnet', 'ollama/llama3.2-vision:11b'],
                'require_vision': True
            },
            TaskType.CONVERSATION: {
                'preferred_models': ['ollama/llama3.2:3b', 'groq/llama-3.1-8b', 'claude-3.5-haiku'],
                'max_latency_ms': 1500
            },
            TaskType.REASONING: {
                'preferred_models': ['deepseek-r1', 'claude-3.5-sonnet', 'qwen2.5-72b-instruct'],
                'max_latency_ms': 10000
            },
            TaskType.CODING: {
                'preferred_models': ['claude-3.5-sonnet', 'deepseek-chat', 'qwen2.5-72b-instruct'],
                'max_latency_ms': 5000,
                'require_tools': True
            }
        }
    
    def route(
        self, 
        task_type: TaskType,
        messages: List[LLMMessage],
        config: Optional[RoutingConfig] = None
    ) -> RoutingResult:
        """Route request to appropriate provider"""
        if not config:
            config = RoutingConfig()
        
        # Get task preferences
        task_prefs = self.task_preferences.get(task_type, {})
        
        # Build requirements
        requirements = {
            'require_tools': config.require_tools or task_prefs.get('require_tools', False),
            'require_vision': config.require_vision or task_prefs.get('require_vision', False),
            'require_streaming': config.require_streaming,
            'max_latency_ms': config.max_latency_ms or task_prefs.get('max_latency_ms'),
            'max_cost_per_request': config.max_cost_per_request
        }
        
        # Get candidate models
        candidates = self._get_candidates(config, task_prefs, requirements)
        
        if not candidates:
            raise RuntimeError(f"No suitable models found for task {task_type}")
        
        # Score and rank candidates
        scored_candidates = self._score_candidates(
            candidates, config, requirements, messages
        )
        
        # Select best candidate
        best_model, best_score, reasoning = scored_candidates[0]
        provider_name = self._get_provider_name(best_model)
        provider = self.registry.get_provider(provider_name)
        
        if not provider:
            raise RuntimeError(f"Provider {provider_name} not available")
        
        # Prepare fallback options
        fallback_options = []
        for model, score, _ in scored_candidates[1:3]:  # Top 2 alternatives
            fallback_provider = self._get_provider_name(model)
            fallback_options.append((fallback_provider, model))
        
        return RoutingResult(
            provider=provider,
            model_name=best_model,
            confidence=best_score,
            reasoning=reasoning,
            fallback_options=fallback_options
        )
    
    def chat_with_routing(
        self,
        task_type: TaskType,
        messages: List[LLMMessage],
        tools: Optional[List[Dict[str, Any]]] = None,
        routing_config: Optional[RoutingConfig] = None,
        llm_config: Optional[LLMConfig] = None
    ) -> LLMResponse:
        """Chat with automatic routing and fallback"""
        if not routing_config:
            routing_config = RoutingConfig()
        if not llm_config:
            llm_config = LLMConfig()
        
        # Route to best provider
        routing_result = self.route(task_type, messages, routing_config)
        
        # Try primary provider
        start_time = time.time()
        try:
            response = routing_result.provider.chat(
                messages=messages,
                tools=tools,
                config=llm_config
            )
            
            # Record success
            latency = (time.time() - start_time) * 1000
            self._record_performance(routing_result.model_name, latency, True)
            
            # Add metadata to response
            if isinstance(response, LLMResponse):
                response.model = routing_result.model_name
                response.provider = routing_result.provider.name
                response.latency_ms = latency
            
            return response
            
        except Exception as e:
            # Record failure
            self._record_performance(routing_result.model_name, None, False)
            
            # Try fallback if enabled
            if routing_config.fallback_enabled and routing_result.fallback_options:
                for provider_name, model_name in routing_result.fallback_options:
                    try:
                        fallback_provider = self.registry.get_provider(provider_name)
                        if fallback_provider:
                            response = fallback_provider.chat(
                                messages=messages,
                                tools=tools,
                                config=llm_config
                            )
                            
                            # Add metadata
                            if isinstance(response, LLMResponse):
                                response.model = model_name
                                response.provider = provider_name
                                response.latency_ms = (time.time() - start_time) * 1000
                            
                            return response
                    except Exception:
                        continue
            
            # All options failed
            raise RuntimeError(f"All providers failed. Last error: {e}")
    
    def _get_candidates(
        self, 
        config: RoutingConfig, 
        task_prefs: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> List[str]:
        """Get candidate models based on requirements"""
        candidates = []
        
        # Start with preferred models from task preferences
        preferred = task_prefs.get('preferred_models', [])
        
        # Add models from routing config
        if config.preferred_providers:
            for provider in config.preferred_providers:
                provider_models = [m for m in MODEL_CATALOG.keys() 
                                 if m.startswith(provider + '/') or 
                                    self._get_provider_name(m) == provider]
                preferred.extend(provider_models)
        
        # Filter by policy
        if config.policy == RoutingPolicy.OFFLINE_ONLY:
            preferred = [m for m in preferred if m.startswith('ollama/')]
        elif config.policy == RoutingPolicy.PRIVACY_FIRST:
            # Prefer local, then privacy-focused providers
            local_models = [m for m in preferred if m.startswith('ollama/')]
            other_models = [m for m in preferred if not m.startswith('ollama/')]
            preferred = local_models + other_models
        
        # Filter by capabilities
        for model in preferred:
            if model not in MODEL_CATALOG:
                continue
            
            caps = MODEL_CATALOG[model]
            
            # Check requirements
            if requirements.get('require_tools') and not caps.supports_tools:
                continue
            if requirements.get('require_vision') and not caps.supports_vision:
                continue
            if requirements.get('require_streaming') and not caps.supports_streaming:
                continue
            
            # Check blocked providers
            if config.blocked_providers:
                provider_name = self._get_provider_name(model)
                if provider_name in config.blocked_providers:
                    continue
            
            candidates.append(model)
        
        # If no preferred candidates, fall back to all compatible models
        if not candidates:
            for model, caps in MODEL_CATALOG.items():
                if requirements.get('require_tools') and not caps.supports_tools:
                    continue
                if requirements.get('require_vision') and not caps.supports_vision:
                    continue
                if requirements.get('require_streaming') and not caps.supports_streaming:
                    continue
                
                candidates.append(model)
        
        return candidates
    
    def _score_candidates(
        self, 
        candidates: List[str], 
        config: RoutingConfig,
        requirements: Dict[str, Any],
        messages: List[LLMMessage]
    ) -> List[Tuple[str, float, str]]:
        """Score and rank candidate models"""
        scored = []
        
        for model in candidates:
            caps = MODEL_CATALOG[model]
            score = 0.0
            reasoning_parts = []
            
            # Base availability score
            provider_name = self._get_provider_name(model)
            provider = self.registry.get_provider(provider_name)
            if not provider or not provider.is_available():
                continue
            
            score += 10.0  # Base score for availability
            
            # Policy-based scoring
            if config.policy == RoutingPolicy.COST_OPTIMIZED:
                if caps.cost_per_1k_output == 0:  # Local models
                    score += 20.0
                    reasoning_parts.append("free local model")
                elif caps.cost_per_1k_output and caps.cost_per_1k_output < 1.0:
                    score += 15.0
                    reasoning_parts.append("low cost")
                elif caps.cost_per_1k_output and caps.cost_per_1k_output < 5.0:
                    score += 10.0
                    reasoning_parts.append("moderate cost")
            
            elif config.policy == RoutingPolicy.SPEED_OPTIMIZED:
                if caps.typical_latency_ms and caps.typical_latency_ms < 500:
                    score += 20.0
                    reasoning_parts.append("very fast")
                elif caps.typical_latency_ms and caps.typical_latency_ms < 1000:
                    score += 15.0
                    reasoning_parts.append("fast")
                elif caps.typical_latency_ms and caps.typical_latency_ms < 2000:
                    score += 10.0
                    reasoning_parts.append("moderate speed")
            
            elif config.policy == RoutingPolicy.QUALITY_OPTIMIZED:
                # Prefer larger, more capable models
                if "70b" in model or "72b" in model or "sonnet" in model:
                    score += 20.0
                    reasoning_parts.append("high quality model")
                elif "8b" in model or "7b" in model or "haiku" in model:
                    score += 10.0
                    reasoning_parts.append("good quality model")
            
            elif config.policy == RoutingPolicy.OFFLINE_ONLY:
                if model.startswith('ollama/'):
                    score += 20.0
                    reasoning_parts.append("local model")
                else:
                    score -= 50.0  # Heavily penalize cloud models
            
            # Performance history bonus
            if model in self.performance_history:
                avg_latency = sum(self.performance_history[model]) / len(self.performance_history[model])
                if avg_latency < 1000:
                    score += 5.0
                    reasoning_parts.append("good historical performance")
            
            # Failure penalty
            if model in self.failure_counts and self.failure_counts[model] > 2:
                score -= 10.0
                reasoning_parts.append("recent failures")
            
            # Context length bonus for long conversations
            total_tokens = sum(len(msg.content) for msg in messages) // 4  # Rough estimate
            if total_tokens > caps.max_context * 0.7:
                score -= 20.0  # Penalize if close to limit
                reasoning_parts.append("near context limit")
            elif caps.max_context > 100000:
                score += 5.0
                reasoning_parts.append("large context window")
            
            reasoning = ", ".join(reasoning_parts) if reasoning_parts else "basic compatibility"
            scored.append((model, score, reasoning))
        
        # Sort by score (descending)
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored
    
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
    
    def _record_performance(self, model_name: str, latency: Optional[float], success: bool):
        """Record performance metrics"""
        if success and latency is not None:
            if model_name not in self.performance_history:
                self.performance_history[model_name] = []
            self.performance_history[model_name].append(latency)
            
            # Keep only last 10 measurements
            if len(self.performance_history[model_name]) > 10:
                self.performance_history[model_name] = self.performance_history[model_name][-10:]
        
        if not success:
            self.failure_counts[model_name] = self.failure_counts.get(model_name, 0) + 1
    
    def get_performance_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get performance statistics for all models"""
        stats = {}
        
        for model in MODEL_CATALOG.keys():
            model_stats = {
                'avg_latency_ms': None,
                'failure_count': self.failure_counts.get(model, 0),
                'total_requests': 0
            }
            
            if model in self.performance_history:
                latencies = self.performance_history[model]
                model_stats['avg_latency_ms'] = sum(latencies) / len(latencies)
                model_stats['total_requests'] = len(latencies)
            
            stats[model] = model_stats
        
        return stats