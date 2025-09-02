#!/usr/bin/env python3
"""
Unit Tests for Evolution Module

Tests for self-evolving AI engine, adaptive learning, and optimization components.

Author: Jarvis AI Team
Date: 2024
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json
import numpy as np

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from windows_use.evolution.evolution_engine import EvolutionEngine
    from windows_use.evolution.evaluator import PerformanceEvaluator
    from windows_use.evolution.reflector import SelfReflector
    from windows_use.evolution.mutator import StrategyMutator
    from windows_use.evolution.memory_store import MemoryStore
except ImportError as e:
    pytest.skip(f"Evolution modules not available: {e}", allow_module_level=True)


class TestEvolutionEngine:
    """Test cases for EvolutionEngine"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.engine = EvolutionEngine()
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_initialization(self):
        """Test EvolutionEngine initialization"""
        assert self.engine is not None
        assert hasattr(self.engine, 'evaluator')
        assert hasattr(self.engine, 'reflector')
        assert hasattr(self.engine, 'mutator')
        assert hasattr(self.engine, 'memory_store')
        assert hasattr(self.engine, 'generation_count')
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_component_integration(self):
        """Test integration of evolution components"""
        assert isinstance(self.engine.evaluator, PerformanceEvaluator)
        assert isinstance(self.engine.reflector, SelfReflector)
        assert isinstance(self.engine.mutator, StrategyMutator)
        assert isinstance(self.engine.memory_store, MemoryStore)
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_evolve_strategy(self):
        """Test strategy evolution process"""
        initial_strategy = {
            'approach': 'conservative',
            'parameters': {'temperature': 0.7, 'max_tokens': 1000},
            'performance_score': 0.75
        }
        
        with patch.object(self.engine.evaluator, 'evaluate_performance', return_value=0.85), \
             patch.object(self.engine.reflector, 'analyze_performance', return_value={'insights': 'good'}), \
             patch.object(self.engine.mutator, 'mutate_strategy', return_value=initial_strategy):
            
            evolved_strategy = self.engine.evolve_strategy(initial_strategy)
            
            assert evolved_strategy is not None
            assert 'approach' in evolved_strategy
            assert 'parameters' in evolved_strategy
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_fitness_evaluation(self):
        """Test fitness evaluation of strategies"""
        strategies = [
            {'id': 1, 'performance_score': 0.8},
            {'id': 2, 'performance_score': 0.6},
            {'id': 3, 'performance_score': 0.9}
        ]
        
        fitness_scores = self.engine.evaluate_fitness(strategies)
        
        assert len(fitness_scores) == 3
        assert max(fitness_scores) == 0.9  # Best strategy
        assert min(fitness_scores) == 0.6  # Worst strategy
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_selection_process(self):
        """Test strategy selection for evolution"""
        population = [
            {'id': 1, 'fitness': 0.8, 'strategy': 'A'},
            {'id': 2, 'fitness': 0.6, 'strategy': 'B'},
            {'id': 3, 'fitness': 0.9, 'strategy': 'C'},
            {'id': 4, 'fitness': 0.7, 'strategy': 'D'}
        ]
        
        selected = self.engine.select_strategies(population, selection_size=2)
        
        assert len(selected) == 2
        # Should select the best performing strategies
        selected_fitness = [s['fitness'] for s in selected]
        assert 0.9 in selected_fitness  # Best strategy should be selected
        assert 0.8 in selected_fitness  # Second best should be selected
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_crossover_operation(self):
        """Test strategy crossover for genetic algorithm"""
        parent1 = {
            'parameters': {'temperature': 0.7, 'max_tokens': 1000},
            'approach': 'aggressive'
        }
        parent2 = {
            'parameters': {'temperature': 0.3, 'max_tokens': 1500},
            'approach': 'conservative'
        }
        
        offspring = self.engine.crossover_strategies(parent1, parent2)
        
        assert offspring is not None
        assert 'parameters' in offspring
        assert 'approach' in offspring
        # Offspring should have characteristics from both parents
        temp = offspring['parameters']['temperature']
        assert 0.3 <= temp <= 0.7
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_mutation_operation(self):
        """Test strategy mutation"""
        original_strategy = {
            'parameters': {'temperature': 0.5, 'max_tokens': 1000},
            'approach': 'balanced'
        }
        
        with patch.object(self.engine.mutator, 'mutate_strategy') as mock_mutate:
            mock_mutated = {
                'parameters': {'temperature': 0.6, 'max_tokens': 1200},
                'approach': 'balanced'
            }
            mock_mutate.return_value = mock_mutated
            
            mutated_strategy = self.engine.mutate_strategy(original_strategy, mutation_rate=0.1)
            
            assert mutated_strategy != original_strategy
            mock_mutate.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_generation_advancement(self):
        """Test generation advancement"""
        initial_generation = self.engine.generation_count
        
        population = [
            {'id': 1, 'fitness': 0.8},
            {'id': 2, 'fitness': 0.7}
        ]
        
        self.engine.advance_generation(population)
        
        assert self.engine.generation_count == initial_generation + 1
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_convergence_detection(self):
        """Test convergence detection"""
        # Simulate converged population (similar fitness scores)
        converged_population = [
            {'fitness': 0.85},
            {'fitness': 0.84},
            {'fitness': 0.86},
            {'fitness': 0.85}
        ]
        
        is_converged = self.engine.check_convergence(converged_population, threshold=0.05)
        assert is_converged is True
        
        # Simulate diverse population
        diverse_population = [
            {'fitness': 0.9},
            {'fitness': 0.6},
            {'fitness': 0.8},
            {'fitness': 0.4}
        ]
        
        is_converged = self.engine.check_convergence(diverse_population, threshold=0.05)
        assert is_converged is False
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_best_strategy_tracking(self):
        """Test tracking of best performing strategy"""
        strategies = [
            {'id': 1, 'fitness': 0.7, 'strategy': 'A'},
            {'id': 2, 'fitness': 0.9, 'strategy': 'B'},
            {'id': 3, 'fitness': 0.6, 'strategy': 'C'}
        ]
        
        best_strategy = self.engine.get_best_strategy(strategies)
        
        assert best_strategy['id'] == 2
        assert best_strategy['fitness'] == 0.9
        assert best_strategy['strategy'] == 'B'


class TestPerformanceEvaluator:
    """Test cases for PerformanceEvaluator"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.evaluator = PerformanceEvaluator()
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_initialization(self):
        """Test PerformanceEvaluator initialization"""
        assert self.evaluator is not None
        assert hasattr(self.evaluator, 'metrics')
        assert hasattr(self.evaluator, 'benchmarks')
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_response_quality_evaluation(self):
        """Test response quality evaluation"""
        response_data = {
            'response': 'This is a high-quality response with relevant information.',
            'relevance_score': 0.9,
            'coherence_score': 0.85,
            'completeness_score': 0.8
        }
        
        quality_score = self.evaluator.evaluate_response_quality(response_data)
        
        assert 0.0 <= quality_score <= 1.0
        assert quality_score > 0.8  # Should be high for good response
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_efficiency_evaluation(self):
        """Test efficiency evaluation"""
        performance_data = {
            'response_time': 2.5,  # seconds
            'token_count': 150,
            'api_calls': 3,
            'memory_usage': 512  # MB
        }
        
        efficiency_score = self.evaluator.evaluate_efficiency(performance_data)
        
        assert 0.0 <= efficiency_score <= 1.0
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_accuracy_evaluation(self):
        """Test accuracy evaluation"""
        test_cases = [
            {'expected': 'correct answer', 'actual': 'correct answer', 'correct': True},
            {'expected': 'another answer', 'actual': 'wrong answer', 'correct': False},
            {'expected': 'third answer', 'actual': 'third answer', 'correct': True}
        ]
        
        accuracy_score = self.evaluator.evaluate_accuracy(test_cases)
        
        assert accuracy_score == 2/3  # 2 out of 3 correct
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_user_satisfaction_evaluation(self):
        """Test user satisfaction evaluation"""
        feedback_data = {
            'ratings': [4, 5, 3, 5, 4],  # Out of 5
            'positive_feedback': 4,
            'negative_feedback': 1,
            'total_interactions': 5
        }
        
        satisfaction_score = self.evaluator.evaluate_user_satisfaction(feedback_data)
        
        assert 0.0 <= satisfaction_score <= 1.0
        assert satisfaction_score > 0.7  # Should be high for good feedback
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_comprehensive_evaluation(self):
        """Test comprehensive performance evaluation"""
        strategy_data = {
            'response_quality': 0.85,
            'efficiency': 0.75,
            'accuracy': 0.9,
            'user_satisfaction': 0.8
        }
        
        overall_score = self.evaluator.evaluate_performance(strategy_data)
        
        assert 0.0 <= overall_score <= 1.0
        assert overall_score > 0.7  # Should be high for good overall performance
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_benchmark_comparison(self):
        """Test benchmark comparison"""
        current_performance = {
            'response_time': 2.0,
            'accuracy': 0.85,
            'user_rating': 4.2
        }
        
        benchmark_performance = {
            'response_time': 3.0,
            'accuracy': 0.8,
            'user_rating': 4.0
        }
        
        comparison = self.evaluator.compare_to_benchmark(current_performance, benchmark_performance)
        
        assert comparison['response_time_improvement'] > 0  # Faster is better
        assert comparison['accuracy_improvement'] > 0  # Higher accuracy is better
        assert comparison['user_rating_improvement'] > 0  # Higher rating is better


class TestSelfReflector:
    """Test cases for SelfReflector"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.reflector = SelfReflector()
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_initialization(self):
        """Test SelfReflector initialization"""
        assert self.reflector is not None
        assert hasattr(self.reflector, 'analysis_history')
        assert hasattr(self.reflector, 'insight_patterns')
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_performance_analysis(self):
        """Test performance analysis"""
        performance_data = {
            'success_rate': 0.85,
            'failure_patterns': ['timeout', 'invalid_input'],
            'response_times': [1.2, 2.1, 1.8, 3.0, 1.5],
            'user_feedback': ['good', 'excellent', 'poor', 'good', 'excellent']
        }
        
        analysis = self.reflector.analyze_performance(performance_data)
        
        assert 'insights' in analysis
        assert 'recommendations' in analysis
        assert 'patterns' in analysis
        assert isinstance(analysis['insights'], list)
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_failure_pattern_detection(self):
        """Test failure pattern detection"""
        failure_data = [
            {'type': 'timeout', 'context': 'large_file_processing', 'timestamp': '2024-01-01T10:00:00'},
            {'type': 'timeout', 'context': 'large_file_processing', 'timestamp': '2024-01-01T11:00:00'},
            {'type': 'invalid_input', 'context': 'user_query', 'timestamp': '2024-01-01T12:00:00'},
            {'type': 'timeout', 'context': 'large_file_processing', 'timestamp': '2024-01-01T13:00:00'}
        ]
        
        patterns = self.reflector.detect_failure_patterns(failure_data)
        
        assert 'timeout' in patterns
        assert patterns['timeout']['frequency'] == 3
        assert 'large_file_processing' in patterns['timeout']['contexts']
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_success_factor_identification(self):
        """Test success factor identification"""
        success_data = [
            {'strategy': 'conservative', 'outcome': 'success', 'score': 0.9},
            {'strategy': 'aggressive', 'outcome': 'failure', 'score': 0.3},
            {'strategy': 'conservative', 'outcome': 'success', 'score': 0.85},
            {'strategy': 'balanced', 'outcome': 'success', 'score': 0.8}
        ]
        
        success_factors = self.reflector.identify_success_factors(success_data)
        
        assert 'conservative' in success_factors
        assert success_factors['conservative']['success_rate'] > 0.8
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_improvement_recommendations(self):
        """Test improvement recommendations"""
        analysis_data = {
            'weak_areas': ['response_time', 'error_handling'],
            'strong_areas': ['accuracy', 'user_satisfaction'],
            'trends': {'response_time': 'increasing', 'accuracy': 'stable'}
        }
        
        recommendations = self.reflector.generate_recommendations(analysis_data)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert any('response_time' in rec.lower() for rec in recommendations)
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_insight_extraction(self):
        """Test insight extraction from data"""
        interaction_data = {
            'successful_interactions': 85,
            'failed_interactions': 15,
            'average_response_time': 2.3,
            'user_satisfaction': 4.1,
            'common_queries': ['weather', 'news', 'calculation']
        }
        
        insights = self.reflector.extract_insights(interaction_data)
        
        assert isinstance(insights, dict)
        assert 'success_rate' in insights
        assert 'performance_summary' in insights
        assert insights['success_rate'] == 0.85


class TestStrategyMutator:
    """Test cases for StrategyMutator"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mutator = StrategyMutator()
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_initialization(self):
        """Test StrategyMutator initialization"""
        assert self.mutator is not None
        assert hasattr(self.mutator, 'mutation_operators')
        assert hasattr(self.mutator, 'mutation_rate')
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_parameter_mutation(self):
        """Test parameter mutation"""
        original_params = {
            'temperature': 0.7,
            'max_tokens': 1000,
            'top_p': 0.9
        }
        
        mutated_params = self.mutator.mutate_parameters(original_params, mutation_rate=0.1)
        
        assert isinstance(mutated_params, dict)
        assert 'temperature' in mutated_params
        assert 'max_tokens' in mutated_params
        assert 'top_p' in mutated_params
        
        # At least one parameter should be different (with high probability)
        differences = sum(1 for key in original_params 
                         if original_params[key] != mutated_params[key])
        # Note: Due to randomness, this might occasionally fail, but very unlikely
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_strategy_approach_mutation(self):
        """Test strategy approach mutation"""
        original_strategy = {
            'approach': 'conservative',
            'risk_tolerance': 0.3,
            'exploration_factor': 0.2
        }
        
        mutated_strategy = self.mutator.mutate_approach(original_strategy)
        
        assert 'approach' in mutated_strategy
        assert 'risk_tolerance' in mutated_strategy
        assert 'exploration_factor' in mutated_strategy
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_gaussian_mutation(self):
        """Test Gaussian mutation operator"""
        original_value = 0.5
        mutation_strength = 0.1
        
        mutated_value = self.mutator.gaussian_mutation(original_value, mutation_strength)
        
        assert isinstance(mutated_value, float)
        # Value should be within reasonable bounds
        assert abs(mutated_value - original_value) <= 1.0
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_uniform_mutation(self):
        """Test uniform mutation operator"""
        original_value = 100
        min_value = 50
        max_value = 200
        
        mutated_value = self.mutator.uniform_mutation(original_value, min_value, max_value)
        
        assert min_value <= mutated_value <= max_value
        assert isinstance(mutated_value, (int, float))
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_adaptive_mutation_rate(self):
        """Test adaptive mutation rate"""
        performance_history = [0.7, 0.75, 0.73, 0.72, 0.71]  # Declining performance
        
        adaptive_rate = self.mutator.calculate_adaptive_mutation_rate(performance_history)
        
        assert 0.0 <= adaptive_rate <= 1.0
        # Should increase mutation rate when performance is declining
        assert adaptive_rate > self.mutator.base_mutation_rate
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_constraint_preservation(self):
        """Test constraint preservation during mutation"""
        strategy = {
            'temperature': 0.8,
            'max_tokens': 1500
        }
        
        constraints = {
            'temperature': (0.0, 1.0),
            'max_tokens': (100, 2000)
        }
        
        mutated_strategy = self.mutator.mutate_with_constraints(strategy, constraints)
        
        assert 0.0 <= mutated_strategy['temperature'] <= 1.0
        assert 100 <= mutated_strategy['max_tokens'] <= 2000


class TestMemoryStore:
    """Test cases for MemoryStore"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.memory_store = MemoryStore()
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_initialization(self):
        """Test MemoryStore initialization"""
        assert self.memory_store is not None
        assert hasattr(self.memory_store, 'strategies')
        assert hasattr(self.memory_store, 'performance_history')
        assert hasattr(self.memory_store, 'insights')
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_store_strategy(self):
        """Test strategy storage"""
        strategy = {
            'id': 'strategy_001',
            'parameters': {'temperature': 0.7},
            'performance': 0.85,
            'generation': 1
        }
        
        self.memory_store.store_strategy(strategy)
        
        assert 'strategy_001' in self.memory_store.strategies
        stored_strategy = self.memory_store.strategies['strategy_001']
        assert stored_strategy['performance'] == 0.85
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_retrieve_strategy(self):
        """Test strategy retrieval"""
        strategy = {
            'id': 'strategy_002',
            'parameters': {'temperature': 0.5},
            'performance': 0.9
        }
        
        self.memory_store.store_strategy(strategy)
        retrieved_strategy = self.memory_store.retrieve_strategy('strategy_002')
        
        assert retrieved_strategy is not None
        assert retrieved_strategy['performance'] == 0.9
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_get_best_strategies(self):
        """Test retrieval of best performing strategies"""
        strategies = [
            {'id': 'strategy_1', 'performance': 0.7},
            {'id': 'strategy_2', 'performance': 0.9},
            {'id': 'strategy_3', 'performance': 0.8},
            {'id': 'strategy_4', 'performance': 0.6}
        ]
        
        for strategy in strategies:
            self.memory_store.store_strategy(strategy)
        
        best_strategies = self.memory_store.get_best_strategies(top_k=2)
        
        assert len(best_strategies) == 2
        assert best_strategies[0]['performance'] == 0.9
        assert best_strategies[1]['performance'] == 0.8
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_store_performance_data(self):
        """Test performance data storage"""
        performance_data = {
            'strategy_id': 'strategy_001',
            'timestamp': '2024-01-01T12:00:00',
            'metrics': {
                'accuracy': 0.85,
                'response_time': 2.1,
                'user_satisfaction': 4.2
            }
        }
        
        self.memory_store.store_performance_data(performance_data)
        
        assert len(self.memory_store.performance_history) == 1
        stored_data = self.memory_store.performance_history[0]
        assert stored_data['strategy_id'] == 'strategy_001'
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_get_performance_trends(self):
        """Test performance trend analysis"""
        performance_data = [
            {'strategy_id': 'strategy_001', 'timestamp': '2024-01-01T10:00:00', 'metrics': {'accuracy': 0.8}},
            {'strategy_id': 'strategy_001', 'timestamp': '2024-01-01T11:00:00', 'metrics': {'accuracy': 0.85}},
            {'strategy_id': 'strategy_001', 'timestamp': '2024-01-01T12:00:00', 'metrics': {'accuracy': 0.9}}
        ]
        
        for data in performance_data:
            self.memory_store.store_performance_data(data)
        
        trends = self.memory_store.get_performance_trends('strategy_001', metric='accuracy')
        
        assert len(trends) == 3
        assert trends[-1] == 0.9  # Latest value
        assert trends[0] == 0.8   # Earliest value
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_store_insights(self):
        """Test insight storage"""
        insight = {
            'id': 'insight_001',
            'type': 'performance_pattern',
            'description': 'Conservative strategies perform better in complex tasks',
            'confidence': 0.85,
            'supporting_data': ['strategy_001', 'strategy_003']
        }
        
        self.memory_store.store_insight(insight)
        
        assert 'insight_001' in self.memory_store.insights
        stored_insight = self.memory_store.insights['insight_001']
        assert stored_insight['confidence'] == 0.85
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_query_insights(self):
        """Test insight querying"""
        insights = [
            {'id': 'insight_1', 'type': 'performance_pattern', 'confidence': 0.9},
            {'id': 'insight_2', 'type': 'failure_pattern', 'confidence': 0.7},
            {'id': 'insight_3', 'type': 'performance_pattern', 'confidence': 0.8}
        ]
        
        for insight in insights:
            self.memory_store.store_insight(insight)
        
        performance_insights = self.memory_store.query_insights(insight_type='performance_pattern')
        
        assert len(performance_insights) == 2
        assert all(insight['type'] == 'performance_pattern' for insight in performance_insights)
    
    @pytest.mark.unit
    @pytest.mark.evolution
    def test_memory_cleanup(self):
        """Test memory cleanup functionality"""
        # Add old strategies
        old_strategies = [
            {'id': f'old_strategy_{i}', 'generation': 1, 'performance': 0.5}
            for i in range(10)
        ]
        
        for strategy in old_strategies:
            self.memory_store.store_strategy(strategy)
        
        # Add recent strategies
        recent_strategies = [
            {'id': f'recent_strategy_{i}', 'generation': 10, 'performance': 0.8}
            for i in range(5)
        ]
        
        for strategy in recent_strategies:
            self.memory_store.store_strategy(strategy)
        
        # Cleanup old strategies
        self.memory_store.cleanup_old_strategies(max_age_generations=5)
        
        # Should keep recent strategies and remove old ones
        remaining_strategies = list(self.memory_store.strategies.keys())
        assert len(remaining_strategies) == 5
        assert all('recent_strategy' in strategy_id for strategy_id in remaining_strategies)


@pytest.mark.integration
@pytest.mark.evolution
class TestEvolutionIntegration:
    """Integration tests for evolution components"""
    
    def setup_method(self):
        """Set up integration test fixtures"""
        self.engine = EvolutionEngine()
    
    @pytest.mark.slow
    def test_full_evolution_cycle(self):
        """Test complete evolution cycle"""
        # Initial population
        initial_strategies = [
            {'id': 1, 'parameters': {'temperature': 0.7}, 'performance': 0.6},
            {'id': 2, 'parameters': {'temperature': 0.5}, 'performance': 0.8},
            {'id': 3, 'parameters': {'temperature': 0.9}, 'performance': 0.4}
        ]
        
        # Mock the evaluation process
        with patch.object(self.engine.evaluator, 'evaluate_performance') as mock_eval, \
             patch.object(self.engine.reflector, 'analyze_performance') as mock_reflect, \
             patch.object(self.engine.mutator, 'mutate_strategy') as mock_mutate:
            
            mock_eval.return_value = 0.85
            mock_reflect.return_value = {'insights': ['good performance']}
            mock_mutate.side_effect = lambda x, **kwargs: x  # Return unchanged for simplicity
            
            # Run evolution cycle
            evolved_population = self.engine.evolve_population(initial_strategies, generations=3)
            
            assert len(evolved_population) > 0
            assert self.engine.generation_count >= 3
    
    def test_memory_integration(self):
        """Test integration with memory store"""
        strategy = {
            'id': 'test_strategy',
            'parameters': {'temperature': 0.6},
            'performance': 0.75
        }
        
        # Store strategy
        self.engine.memory_store.store_strategy(strategy)
        
        # Retrieve and verify
        retrieved = self.engine.memory_store.retrieve_strategy('test_strategy')
        assert retrieved['performance'] == 0.75
        
        # Test performance tracking
        performance_data = {
            'strategy_id': 'test_strategy',
            'timestamp': '2024-01-01T12:00:00',
            'metrics': {'accuracy': 0.8}
        }
        
        self.engine.memory_store.store_performance_data(performance_data)
        trends = self.engine.memory_store.get_performance_trends('test_strategy', 'accuracy')
        assert len(trends) == 1
        assert trends[0] == 0.8


if __name__ == "__main__":
    pytest.main([__file__, "-v"])