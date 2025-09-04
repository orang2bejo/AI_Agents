#!/usr/bin/env python3
"""
Unit Tests for LLM Module

Tests for LLM providers, model registry, and routing functionality.

Author: Jarvis AI Team
Date: 2024
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import asyncio

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from windows_use.llm.base import BaseLLMProvider
    from windows_use.llm.manager import LLMManager
    from windows_use.llm.router import LLMRouter
    from windows_use.llm.registry import ModelRegistry
except ImportError as e:
    pytest.skip(f"LLM modules not available: {e}", allow_module_level=True)


class TestBaseLLMProvider:
    """Test cases for BaseLLMProvider"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.provider = BaseLLMProvider()
    
    @pytest.mark.unit
    @pytest.mark.llm
    def test_initialization(self):
        """Test BaseLLMProvider initialization"""
        assert self.provider is not None
        assert hasattr(self.provider, 'name')
        assert hasattr(self.provider, 'models')
    
    @pytest.mark.unit
    @pytest.mark.llm
    def test_abstract_methods(self):
        """Test that abstract methods raise NotImplementedError"""
        with pytest.raises(NotImplementedError):
            self.provider.generate_response("test prompt")
        
        with pytest.raises(NotImplementedError):
            asyncio.run(self.provider.generate_response_async("test prompt"))
    
    @pytest.mark.unit
    @pytest.mark.llm
    def test_model_validation(self):
        """Test model validation functionality"""
        # Mock some models
        self.provider.models = ["gpt-3.5-turbo", "gpt-4", "claude-3"]
        
        # Test valid model
        assert self.provider.is_model_supported("gpt-3.5-turbo")
        
        # Test invalid model
        assert not self.provider.is_model_supported("invalid-model")


class TestLLMManager:
    """Test cases for LLMManager"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.manager = LLMManager()
    
    @pytest.mark.unit
    @pytest.mark.llm
    def test_initialization(self):
        """Test LLMManager initialization"""
        assert self.manager is not None
        assert hasattr(self.manager, 'providers')
        assert hasattr(self.manager, 'default_provider')
    
    @pytest.mark.unit
    @pytest.mark.llm
    def test_provider_registration(self):
        """Test provider registration"""
        # Create a mock provider
        mock_provider = Mock(spec=BaseLLMProvider)
        mock_provider.name = "test_provider"
        mock_provider.models = ["test-model-1", "test-model-2"]
        
        # Register the provider
        self.manager.register_provider("test", mock_provider)
        
        # Verify registration
        assert "test" in self.manager.providers
        assert self.manager.providers["test"] == mock_provider
    
    @pytest.mark.unit
    @pytest.mark.llm
    def test_provider_selection(self):
        """Test provider selection logic"""
        # Register multiple mock providers
        provider1 = Mock(spec=BaseLLMProvider)
        provider1.name = "provider1"
        provider1.models = ["model1", "model2"]
        provider1.is_model_supported.return_value = True
        
        provider2 = Mock(spec=BaseLLMProvider)
        provider2.name = "provider2"
        provider2.models = ["model3", "model4"]
        provider2.is_model_supported.return_value = False
        
        self.manager.register_provider("p1", provider1)
        self.manager.register_provider("p2", provider2)
        
        # Test provider selection
        selected = self.manager.get_provider_for_model("model1")
        assert selected == provider1
    
    @pytest.mark.unit
    @pytest.mark.llm
    @patch('windows_use.llm.manager.LLMManager._load_config')
    def test_config_loading(self, mock_load_config):
        """Test configuration loading"""
        mock_config = {
            'default_provider': 'openai',
            'providers': {
                'openai': {
                    'api_key': 'test_key',
                    'models': ['gpt-3.5-turbo', 'gpt-4']
                }
            }
        }
        mock_load_config.return_value = mock_config
        
        manager = LLMManager()
        assert manager.default_provider == 'openai'


class TestLLMRouter:
    """Test cases for LLMRouter"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.router = LLMRouter()
    
    @pytest.mark.unit
    @pytest.mark.llm
    def test_initialization(self):
        """Test LLMRouter initialization"""
        assert self.router is not None
        assert hasattr(self.router, 'routing_rules')
        assert hasattr(self.router, 'fallback_provider')
    
    @pytest.mark.unit
    @pytest.mark.llm
    def test_route_by_task_type(self):
        """Test routing based on task type"""
        # Mock routing rules
        self.router.routing_rules = {
            'code_generation': 'openai',
            'text_analysis': 'anthropic',
            'general_chat': 'openai'
        }
        
        # Test routing
        assert self.router.route_request('code_generation') == 'openai'
        assert self.router.route_request('text_analysis') == 'anthropic'
        assert self.router.route_request('unknown_task') == self.router.fallback_provider
    
    @pytest.mark.unit
    @pytest.mark.llm
    def test_route_by_model_preference(self):
        """Test routing based on model preference"""
        # Test explicit model routing
        result = self.router.route_by_model('gpt-4')
        assert 'openai' in result.lower() or 'gpt' in result.lower()
        
        result = self.router.route_by_model('claude-3')
        assert 'anthropic' in result.lower() or 'claude' in result.lower()
    
    @pytest.mark.unit
    @pytest.mark.llm
    def test_load_balancing(self):
        """Test load balancing functionality"""
        # Mock multiple providers for the same capability
        providers = ['provider1', 'provider2', 'provider3']
        
        # Test round-robin or weighted selection
        selections = []
        for _ in range(10):
            selected = self.router.select_provider_with_load_balancing(providers)
            selections.append(selected)
        
        # Should distribute across providers
        unique_selections = set(selections)
        assert len(unique_selections) > 1  # Should use multiple providers


class TestModelRegistry:
    """Test cases for ModelRegistry"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.registry = ModelRegistry()
    
    @pytest.mark.unit
    @pytest.mark.llm
    def test_initialization(self):
        """Test ModelRegistry initialization"""
        assert self.registry is not None
        assert hasattr(self.registry, 'models')
        assert hasattr(self.registry, 'providers')
    
    @pytest.mark.unit
    @pytest.mark.llm
    def test_model_registration(self):
        """Test model registration"""
        model_info = {
            'name': 'test-model',
            'provider': 'test-provider',
            'capabilities': ['text_generation', 'code_completion'],
            'context_length': 4096,
            'cost_per_token': 0.0001
        }
        
        self.registry.register_model('test-model', model_info)
        
        # Verify registration
        assert 'test-model' in self.registry.models
        assert self.registry.models['test-model'] == model_info
    
    @pytest.mark.unit
    @pytest.mark.llm
    def test_model_lookup(self):
        """Test model lookup functionality"""
        # Register test models
        models = {
            'gpt-3.5-turbo': {
                'provider': 'openai',
                'capabilities': ['text_generation', 'chat'],
                'context_length': 4096
            },
            'claude-3-sonnet': {
                'provider': 'anthropic',
                'capabilities': ['text_generation', 'analysis'],
                'context_length': 200000
            }
        }
        
        for name, info in models.items():
            self.registry.register_model(name, info)
        
        # Test lookup by capability
        text_gen_models = self.registry.get_models_by_capability('text_generation')
        assert len(text_gen_models) == 2
        
        # Test lookup by provider
        openai_models = self.registry.get_models_by_provider('openai')
        assert 'gpt-3.5-turbo' in openai_models
    
    @pytest.mark.unit
    @pytest.mark.llm
    def test_model_comparison(self):
        """Test model comparison functionality"""
        # Register models with different specs
        self.registry.register_model('fast-model', {
            'context_length': 2048,
            'cost_per_token': 0.0001,
            'speed_tokens_per_second': 100
        })
        
        self.registry.register_model('large-model', {
            'context_length': 32768,
            'cost_per_token': 0.001,
            'speed_tokens_per_second': 50
        })
        
        # Test comparison
        fastest = self.registry.get_fastest_model(['fast-model', 'large-model'])
        assert fastest == 'fast-model'
        
        cheapest = self.registry.get_cheapest_model(['fast-model', 'large-model'])
        assert cheapest == 'fast-model'
        
        largest_context = self.registry.get_largest_context_model(['fast-model', 'large-model'])
        assert largest_context == 'large-model'


@pytest.mark.integration
@pytest.mark.llm
class TestLLMIntegration:
    """Integration tests for LLM components"""
    
    def setup_method(self):
        """Set up integration test fixtures"""
        self.manager = LLMManager()
        self.router = LLMRouter()
        self.registry = ModelRegistry()
    
    def test_end_to_end_request_routing(self):
        """Test end-to-end request routing"""
        # Mock a complete request flow
        task_type = 'code_generation'
        prompt = "Write a Python function to calculate fibonacci numbers"
        
        # Step 1: Route the request
        provider_name = self.router.route_request(task_type)
        assert provider_name is not None
        
        # Step 2: Get the provider
        provider = self.manager.get_provider(provider_name)
        # Provider might be None if not registered, which is expected in tests
    
    @pytest.mark.slow
    def test_provider_failover(self):
        """Test provider failover mechanism"""
        # Mock a scenario where primary provider fails
        primary_provider = Mock(spec=BaseLLMProvider)
        primary_provider.generate_response.side_effect = Exception("Provider unavailable")
        
        fallback_provider = Mock(spec=BaseLLMProvider)
        fallback_provider.generate_response.return_value = "Fallback response"
        
        self.manager.register_provider("primary", primary_provider)
        self.manager.register_provider("fallback", fallback_provider)
        
        # Test failover logic
        response = self.manager.generate_with_failover("test prompt", ["primary", "fallback"])
        assert response == "Fallback response"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])