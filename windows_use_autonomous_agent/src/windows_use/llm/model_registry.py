#!/usr/bin/env python3
"""
Model Registry Module for Windows Use Autonomous Agent

Centralized registry for managing LLM models and their capabilities.

Author: Jarvis AI Team
Date: 2024
"""

import logging
import json
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class ModelCapability(Enum):
    """Model capabilities"""
    TEXT_GENERATION = "text_generation"
    CODE_GENERATION = "code_generation"
    FUNCTION_CALLING = "function_calling"
    TOOL_USE = "tool_use"
    VISION = "vision"
    AUDIO = "audio"
    MULTIMODAL = "multimodal"
    REASONING = "reasoning"
    MATH = "math"
    CREATIVE_WRITING = "creative_writing"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    QUESTION_ANSWERING = "question_answering"
    CONVERSATION = "conversation"
    ANALYSIS = "analysis"
    EMBEDDING = "embedding"
    CLASSIFICATION = "classification"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    ENTITY_EXTRACTION = "entity_extraction"

class ModelTier(Enum):
    """Model performance tiers"""
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class ModelStatus(Enum):
    """Model availability status"""
    AVAILABLE = "available"
    DEPRECATED = "deprecated"
    BETA = "beta"
    EXPERIMENTAL = "experimental"
    MAINTENANCE = "maintenance"
    UNAVAILABLE = "unavailable"

@dataclass
class ModelPricing:
    """Model pricing information"""
    input_cost_per_1k: float  # Cost per 1K input tokens
    output_cost_per_1k: float  # Cost per 1K output tokens
    currency: str = "USD"
    billing_unit: str = "tokens"
    free_tier_limit: Optional[int] = None
    rate_limit_rpm: Optional[int] = None  # Requests per minute
    rate_limit_tpm: Optional[int] = None  # Tokens per minute

@dataclass
class ModelLimits:
    """Model technical limits"""
    max_input_tokens: int
    max_output_tokens: int
    context_window: int
    max_batch_size: Optional[int] = None
    max_concurrent_requests: Optional[int] = None
    timeout_seconds: int = 60

@dataclass
class ModelInfo:
    """Comprehensive model information"""
    id: str
    name: str
    provider: str
    description: str
    capabilities: Set[ModelCapability]
    tier: ModelTier
    status: ModelStatus
    limits: ModelLimits
    pricing: Optional[ModelPricing] = None
    version: str = "1.0"
    release_date: Optional[datetime] = None
    deprecation_date: Optional[datetime] = None
    supported_languages: List[str] = field(default_factory=lambda: ["en"])
    training_data_cutoff: Optional[str] = None
    fine_tuning_available: bool = False
    api_endpoint: Optional[str] = None
    documentation_url: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class ModelRegistry:
    """Registry for managing LLM models"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.models: Dict[str, ModelInfo] = {}
        self.providers: Dict[str, List[str]] = {}
        self.capabilities_index: Dict[ModelCapability, List[str]] = {}
        self.tier_index: Dict[ModelTier, List[str]] = {}
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
        
        # Initialize with default models
        self._initialize_default_models()
        
        # Load from config if provided
        if config_path and config_path.exists():
            self.load_from_config(config_path)
    
    def _initialize_default_models(self):
        """Initialize registry with default model configurations"""
        default_models = [
            # OpenAI Models
            ModelInfo(
                id="gpt-4-turbo",
                name="GPT-4 Turbo",
                provider="openai",
                description="Most capable GPT-4 model with improved instruction following",
                capabilities={
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.CODE_GENERATION,
                    ModelCapability.FUNCTION_CALLING,
                    ModelCapability.TOOL_USE,
                    ModelCapability.REASONING,
                    ModelCapability.MATH,
                    ModelCapability.CREATIVE_WRITING,
                    ModelCapability.ANALYSIS
                },
                tier=ModelTier.PREMIUM,
                status=ModelStatus.AVAILABLE,
                limits=ModelLimits(
                    max_input_tokens=128000,
                    max_output_tokens=4096,
                    context_window=128000
                ),
                pricing=ModelPricing(
                    input_cost_per_1k=0.01,
                    output_cost_per_1k=0.03
                ),
                training_data_cutoff="2024-04"
            ),
            ModelInfo(
                id="gpt-3.5-turbo",
                name="GPT-3.5 Turbo",
                provider="openai",
                description="Fast and efficient model for most tasks",
                capabilities={
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.CODE_GENERATION,
                    ModelCapability.FUNCTION_CALLING,
                    ModelCapability.CONVERSATION,
                    ModelCapability.SUMMARIZATION
                },
                tier=ModelTier.STANDARD,
                status=ModelStatus.AVAILABLE,
                limits=ModelLimits(
                    max_input_tokens=16385,
                    max_output_tokens=4096,
                    context_window=16385
                ),
                pricing=ModelPricing(
                    input_cost_per_1k=0.0005,
                    output_cost_per_1k=0.0015
                ),
                training_data_cutoff="2021-09"
            ),
            
            # Anthropic Models
            ModelInfo(
                id="claude-3-opus-20240229",
                name="Claude 3 Opus",
                provider="anthropic",
                description="Most powerful Claude model for complex tasks",
                capabilities={
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.CODE_GENERATION,
                    ModelCapability.REASONING,
                    ModelCapability.MATH,
                    ModelCapability.CREATIVE_WRITING,
                    ModelCapability.ANALYSIS,
                    ModelCapability.VISION
                },
                tier=ModelTier.PREMIUM,
                status=ModelStatus.AVAILABLE,
                limits=ModelLimits(
                    max_input_tokens=200000,
                    max_output_tokens=4096,
                    context_window=200000
                ),
                pricing=ModelPricing(
                    input_cost_per_1k=0.015,
                    output_cost_per_1k=0.075
                ),
                training_data_cutoff="2023-08"
            ),
            ModelInfo(
                id="claude-3-sonnet-20240229",
                name="Claude 3 Sonnet",
                provider="anthropic",
                description="Balanced Claude model for most use cases",
                capabilities={
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.CODE_GENERATION,
                    ModelCapability.REASONING,
                    ModelCapability.CONVERSATION,
                    ModelCapability.ANALYSIS,
                    ModelCapability.VISION
                },
                tier=ModelTier.ADVANCED,
                status=ModelStatus.AVAILABLE,
                limits=ModelLimits(
                    max_input_tokens=200000,
                    max_output_tokens=4096,
                    context_window=200000
                ),
                pricing=ModelPricing(
                    input_cost_per_1k=0.003,
                    output_cost_per_1k=0.015
                ),
                training_data_cutoff="2023-08"
            ),
            
            # Google Models
            ModelInfo(
                id="gemini-pro",
                name="Gemini Pro",
                provider="google",
                description="Google's advanced multimodal model",
                capabilities={
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.CODE_GENERATION,
                    ModelCapability.MULTIMODAL,
                    ModelCapability.VISION,
                    ModelCapability.REASONING,
                    ModelCapability.MATH
                },
                tier=ModelTier.ADVANCED,
                status=ModelStatus.AVAILABLE,
                limits=ModelLimits(
                    max_input_tokens=30720,
                    max_output_tokens=2048,
                    context_window=32768
                ),
                pricing=ModelPricing(
                    input_cost_per_1k=0.00025,
                    output_cost_per_1k=0.0005
                )
            ),
            
            # Ollama Models (Local)
            ModelInfo(
                id="llama2",
                name="Llama 2",
                provider="ollama",
                description="Meta's open-source language model",
                capabilities={
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.CODE_GENERATION,
                    ModelCapability.CONVERSATION,
                    ModelCapability.REASONING
                },
                tier=ModelTier.STANDARD,
                status=ModelStatus.AVAILABLE,
                limits=ModelLimits(
                    max_input_tokens=4096,
                    max_output_tokens=2048,
                    context_window=4096
                ),
                pricing=None  # Local model, no API costs
            ),
            ModelInfo(
                id="codellama",
                name="Code Llama",
                provider="ollama",
                description="Specialized model for code generation",
                capabilities={
                    ModelCapability.CODE_GENERATION,
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.REASONING
                },
                tier=ModelTier.STANDARD,
                status=ModelStatus.AVAILABLE,
                limits=ModelLimits(
                    max_input_tokens=16384,
                    max_output_tokens=4096,
                    context_window=16384
                ),
                pricing=None
            )
        ]
        
        for model in default_models:
            self.register_model(model)
    
    def register_model(self, model: ModelInfo):
        """Register a new model in the registry"""
        self.models[model.id] = model
        
        # Update provider index
        if model.provider not in self.providers:
            self.providers[model.provider] = []
        self.providers[model.provider].append(model.id)
        
        # Update capabilities index
        for capability in model.capabilities:
            if capability not in self.capabilities_index:
                self.capabilities_index[capability] = []
            self.capabilities_index[capability].append(model.id)
        
        # Update tier index
        if model.tier not in self.tier_index:
            self.tier_index[model.tier] = []
        self.tier_index[model.tier].append(model.id)
        
        self.logger.info(f"Registered model: {model.id}")
    
    def unregister_model(self, model_id: str):
        """Remove a model from the registry"""
        if model_id not in self.models:
            return
        
        model = self.models[model_id]
        
        # Remove from provider index
        if model.provider in self.providers:
            self.providers[model.provider].remove(model_id)
            if not self.providers[model.provider]:
                del self.providers[model.provider]
        
        # Remove from capabilities index
        for capability in model.capabilities:
            if capability in self.capabilities_index:
                self.capabilities_index[capability].remove(model_id)
                if not self.capabilities_index[capability]:
                    del self.capabilities_index[capability]
        
        # Remove from tier index
        if model.tier in self.tier_index:
            self.tier_index[model.tier].remove(model_id)
            if not self.tier_index[model.tier]:
                del self.tier_index[model.tier]
        
        # Remove model
        del self.models[model_id]
        
        self.logger.info(f"Unregistered model: {model_id}")
    
    def get_model(self, model_id: str) -> Optional[ModelInfo]:
        """Get model information by ID"""
        return self.models.get(model_id)
    
    def list_models(self, provider: Optional[str] = None, 
                   capability: Optional[ModelCapability] = None,
                   tier: Optional[ModelTier] = None,
                   status: Optional[ModelStatus] = None) -> List[ModelInfo]:
        """List models with optional filters"""
        models = list(self.models.values())
        
        if provider:
            models = [m for m in models if m.provider == provider]
        
        if capability:
            models = [m for m in models if capability in m.capabilities]
        
        if tier:
            models = [m for m in models if m.tier == tier]
        
        if status:
            models = [m for m in models if m.status == status]
        
        return models
    
    def find_models_by_capability(self, capabilities: List[ModelCapability],
                                 require_all: bool = True) -> List[ModelInfo]:
        """Find models that have specified capabilities"""
        if require_all:
            # Models must have ALL specified capabilities
            candidate_models = None
            for capability in capabilities:
                model_ids = set(self.capabilities_index.get(capability, []))
                if candidate_models is None:
                    candidate_models = model_ids
                else:
                    candidate_models &= model_ids
            
            if candidate_models:
                return [self.models[model_id] for model_id in candidate_models]
            return []
        else:
            # Models must have ANY of the specified capabilities
            model_ids = set()
            for capability in capabilities:
                model_ids.update(self.capabilities_index.get(capability, []))
            
            return [self.models[model_id] for model_id in model_ids]
    
    def get_providers(self) -> List[str]:
        """Get list of available providers"""
        return list(self.providers.keys())
    
    def get_models_by_provider(self, provider: str) -> List[ModelInfo]:
        """Get all models from a specific provider"""
        model_ids = self.providers.get(provider, [])
        return [self.models[model_id] for model_id in model_ids]
    
    def get_best_model_for_task(self, capabilities: List[ModelCapability],
                               tier_preference: Optional[ModelTier] = None,
                               provider_preference: Optional[str] = None) -> Optional[ModelInfo]:
        """Get the best model for a specific task"""
        candidates = self.find_models_by_capability(capabilities, require_all=True)
        
        # Filter by status (only available models)
        candidates = [m for m in candidates if m.status == ModelStatus.AVAILABLE]
        
        if not candidates:
            return None
        
        # Apply preferences
        if provider_preference:
            preferred = [m for m in candidates if m.provider == provider_preference]
            if preferred:
                candidates = preferred
        
        if tier_preference:
            preferred = [m for m in candidates if m.tier == tier_preference]
            if preferred:
                candidates = preferred
        
        # Sort by tier (premium first) and then by context window
        tier_order = {
            ModelTier.ENTERPRISE: 5,
            ModelTier.PREMIUM: 4,
            ModelTier.ADVANCED: 3,
            ModelTier.STANDARD: 2,
            ModelTier.BASIC: 1
        }
        
        candidates.sort(
            key=lambda m: (tier_order.get(m.tier, 0), m.limits.context_window),
            reverse=True
        )
        
        return candidates[0]
    
    def estimate_cost(self, model_id: str, input_tokens: int, 
                     output_tokens: int) -> Optional[float]:
        """Estimate cost for using a model"""
        model = self.get_model(model_id)
        if not model or not model.pricing:
            return None
        
        input_cost = (input_tokens / 1000) * model.pricing.input_cost_per_1k
        output_cost = (output_tokens / 1000) * model.pricing.output_cost_per_1k
        
        return input_cost + output_cost
    
    def get_model_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        total_models = len(self.models)
        providers_count = len(self.providers)
        
        status_counts = {}
        tier_counts = {}
        capability_counts = {}
        
        for model in self.models.values():
            # Count by status
            status_counts[model.status.value] = status_counts.get(model.status.value, 0) + 1
            
            # Count by tier
            tier_counts[model.tier.value] = tier_counts.get(model.tier.value, 0) + 1
            
            # Count by capabilities
            for capability in model.capabilities:
                capability_counts[capability.value] = capability_counts.get(capability.value, 0) + 1
        
        return {
            "total_models": total_models,
            "providers_count": providers_count,
            "providers": list(self.providers.keys()),
            "status_distribution": status_counts,
            "tier_distribution": tier_counts,
            "capability_distribution": capability_counts
        }
    
    def save_to_config(self, config_path: Path):
        """Save registry to configuration file"""
        config_data = {
            "models": {},
            "metadata": {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "total_models": len(self.models)
            }
        }
        
        for model_id, model in self.models.items():
            config_data["models"][model_id] = {
                "id": model.id,
                "name": model.name,
                "provider": model.provider,
                "description": model.description,
                "capabilities": [cap.value for cap in model.capabilities],
                "tier": model.tier.value,
                "status": model.status.value,
                "limits": {
                    "max_input_tokens": model.limits.max_input_tokens,
                    "max_output_tokens": model.limits.max_output_tokens,
                    "context_window": model.limits.context_window,
                    "max_batch_size": model.limits.max_batch_size,
                    "max_concurrent_requests": model.limits.max_concurrent_requests,
                    "timeout_seconds": model.limits.timeout_seconds
                },
                "pricing": {
                    "input_cost_per_1k": model.pricing.input_cost_per_1k,
                    "output_cost_per_1k": model.pricing.output_cost_per_1k,
                    "currency": model.pricing.currency,
                    "billing_unit": model.pricing.billing_unit,
                    "free_tier_limit": model.pricing.free_tier_limit,
                    "rate_limit_rpm": model.pricing.rate_limit_rpm,
                    "rate_limit_tpm": model.pricing.rate_limit_tpm
                } if model.pricing else None,
                "version": model.version,
                "release_date": model.release_date.isoformat() if model.release_date else None,
                "deprecation_date": model.deprecation_date.isoformat() if model.deprecation_date else None,
                "supported_languages": model.supported_languages,
                "training_data_cutoff": model.training_data_cutoff,
                "fine_tuning_available": model.fine_tuning_available,
                "api_endpoint": model.api_endpoint,
                "documentation_url": model.documentation_url,
                "tags": model.tags,
                "metadata": model.metadata
            }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Registry saved to {config_path}")
    
    def load_from_config(self, config_path: Path):
        """Load registry from configuration file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            models_data = config_data.get("models", {})
            
            for model_id, model_data in models_data.items():
                # Parse capabilities
                capabilities = {ModelCapability(cap) for cap in model_data.get("capabilities", [])}
                
                # Parse limits
                limits_data = model_data.get("limits", {})
                limits = ModelLimits(
                    max_input_tokens=limits_data.get("max_input_tokens", 4096),
                    max_output_tokens=limits_data.get("max_output_tokens", 2048),
                    context_window=limits_data.get("context_window", 4096),
                    max_batch_size=limits_data.get("max_batch_size"),
                    max_concurrent_requests=limits_data.get("max_concurrent_requests"),
                    timeout_seconds=limits_data.get("timeout_seconds", 60)
                )
                
                # Parse pricing
                pricing = None
                pricing_data = model_data.get("pricing")
                if pricing_data:
                    pricing = ModelPricing(
                        input_cost_per_1k=pricing_data.get("input_cost_per_1k", 0.0),
                        output_cost_per_1k=pricing_data.get("output_cost_per_1k", 0.0),
                        currency=pricing_data.get("currency", "USD"),
                        billing_unit=pricing_data.get("billing_unit", "tokens"),
                        free_tier_limit=pricing_data.get("free_tier_limit"),
                        rate_limit_rpm=pricing_data.get("rate_limit_rpm"),
                        rate_limit_tpm=pricing_data.get("rate_limit_tpm")
                    )
                
                # Create model info
                model = ModelInfo(
                    id=model_data.get("id", model_id),
                    name=model_data.get("name", ""),
                    provider=model_data.get("provider", ""),
                    description=model_data.get("description", ""),
                    capabilities=capabilities,
                    tier=ModelTier(model_data.get("tier", "standard")),
                    status=ModelStatus(model_data.get("status", "available")),
                    limits=limits,
                    pricing=pricing,
                    version=model_data.get("version", "1.0"),
                    release_date=datetime.fromisoformat(model_data["release_date"]) if model_data.get("release_date") else None,
                    deprecation_date=datetime.fromisoformat(model_data["deprecation_date"]) if model_data.get("deprecation_date") else None,
                    supported_languages=model_data.get("supported_languages", ["en"]),
                    training_data_cutoff=model_data.get("training_data_cutoff"),
                    fine_tuning_available=model_data.get("fine_tuning_available", False),
                    api_endpoint=model_data.get("api_endpoint"),
                    documentation_url=model_data.get("documentation_url"),
                    tags=model_data.get("tags", []),
                    metadata=model_data.get("metadata", {})
                )
                
                self.register_model(model)
            
            self.logger.info(f"Registry loaded from {config_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to load registry from {config_path}: {e}")
            raise

# Create default registry instance
MODEL_CATALOG = ModelRegistry()

# Export main classes
__all__ = [
    'ModelRegistry',
    'ModelInfo',
    'ModelCapability',
    'ModelTier',
    'ModelStatus',
    'ModelPricing',
    'ModelLimits',
    'MODEL_CATALOG'
]