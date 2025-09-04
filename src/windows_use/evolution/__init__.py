"""Self-Evolving Agent Module

This module implements a self-evolving agent system that can:
- Evaluate its own performance
- Reflect on failures and successes
- Mutate its behavior based on learning
- Store and retrieve memories for continuous improvement
"""

from .evaluator import TaskEvaluator, PerformanceMetrics
from .reflector import AgentReflector, ReflectionResult
from .mutator import BehaviorMutator, MutationStrategy
from .memory import MemoryStore, Experience
from .evolution_engine import EvolutionEngine

__all__ = [
    'TaskEvaluator',
    'PerformanceMetrics', 
    'AgentReflector',
    'ReflectionResult',
    'BehaviorMutator',
    'MutationStrategy',
    'MemoryStore',
    'Experience',
    'EvolutionEngine'
]

__version__ = '1.0.0'