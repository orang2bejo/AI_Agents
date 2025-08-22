"""Evolution Engine Module

Integrates evaluator, reflector, mutator, and memory store for self-evolving agent.
"""

import time
import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
import logging
from pathlib import Path

from .evaluator import TaskEvaluator, PerformanceMetrics, TaskStatus
from .reflector import AgentReflector, ReflectionResult, ReflectionType
from .mutator import BehaviorMutator, MutationStrategy, MutationType
from .memory import MemoryStore, Experience, ExperienceType

logger = logging.getLogger(__name__)

@dataclass
class EvolutionCycle:
    """Represents one evolution cycle"""
    cycle_id: str
    start_time: float
    end_time: Optional[float] = None
    metrics_analyzed: int = 0
    reflections_generated: int = 0
    mutations_applied: int = 0
    experiences_stored: int = 0
    performance_improvement: float = 0.0
    success: bool = False
    
class EvolutionEngine:
    """Main engine that orchestrates the self-evolution process"""
    
    def __init__(self, 
                 memory_db_path: str = "agent_memory.db",
                 evolution_config: Optional[Dict[str, Any]] = None):
        
        # Initialize components
        self.evaluator = TaskEvaluator()
        self.reflector = AgentReflector()
        self.mutator = BehaviorMutator()
        self.memory_store = MemoryStore(memory_db_path)
        
        # Evolution configuration
        self.config = evolution_config or {
            'evolution_interval': 300,  # 5 minutes
            'min_metrics_for_evolution': 5,
            'max_mutations_per_cycle': 3,
            'mutation_confidence_threshold': 0.6,
            'performance_improvement_threshold': 0.05,
            'auto_rollback_enabled': True,
            'rollback_performance_threshold': -0.1
        }
        
        # Evolution state
        self.evolution_cycles: List[EvolutionCycle] = []
        self.last_evolution_time = 0
        self.baseline_performance = 0.0
        self.is_evolving = False
        
        # Callbacks
        self.on_evolution_start: Optional[Callable] = None
        self.on_evolution_complete: Optional[Callable] = None
        self.on_mutation_applied: Optional[Callable] = None
        self.on_rollback_triggered: Optional[Callable] = None
        
        logger.info("Evolution engine initialized")
    
    def should_evolve(self) -> bool:
        """Check if evolution should be triggered"""
        current_time = time.time()
        time_since_last = current_time - self.last_evolution_time
        
        # Check time interval
        if time_since_last < self.config['evolution_interval']:
            return False
        
        # Check if we have enough metrics
        recent_metrics = self.evaluator.metrics_history[-50:]  # Last 50 tasks
        if len(recent_metrics) < self.config['min_metrics_for_evolution']:
            return False
        
        # Check if we're already evolving
        if self.is_evolving:
            return False
        
        return True
    
    async def evolve(self) -> EvolutionCycle:
        """Execute one evolution cycle"""
        if not self.should_evolve():
            logger.debug("Evolution conditions not met")
            return None
        
        self.is_evolving = True
        cycle_id = f"evolution_{int(time.time())}"
        cycle = EvolutionCycle(cycle_id=cycle_id, start_time=time.time())
        
        try:
            logger.info(f"Starting evolution cycle: {cycle_id}")
            
            if self.on_evolution_start:
                self.on_evolution_start(cycle)
            
            # Step 1: Analyze recent performance
            recent_metrics = self.evaluator.metrics_history[-50:]
            cycle.metrics_analyzed = len(recent_metrics)
            
            # Step 2: Generate reflections
            reflections = self.reflector.reflect_on_metrics(recent_metrics)
            cycle.reflections_generated = len(reflections)
            
            # Step 3: Extract insights and recommendations
            insights = []
            recommendations = []
            
            for reflection in reflections:
                insights.extend(reflection.insights)
                recommendations.extend(reflection.recommendations)
            
            # Step 4: Generate mutations
            mutations = self.mutator.generate_mutations(insights, recommendations)
            
            # Filter mutations by confidence threshold
            viable_mutations = [
                m for m in mutations 
                if m.confidence >= self.config['mutation_confidence_threshold']
            ]
            
            # Step 5: Apply mutations (limited by max_mutations_per_cycle)
            max_mutations = self.config['max_mutations_per_cycle']
            mutations_to_apply = viable_mutations[:max_mutations]
            
            applied_mutations = []
            for mutation in mutations_to_apply:
                if self.mutator.apply_mutation(mutation):
                    applied_mutations.append(mutation)
                    
                    if self.on_mutation_applied:
                        self.on_mutation_applied(mutation)
            
            cycle.mutations_applied = len(applied_mutations)
            
            # Step 6: Store evolution experience
            evolution_experience = Experience(
                experience_id="",
                experience_type=ExperienceType.PERFORMANCE_OPTIMIZATION,
                context={
                    'cycle_id': cycle_id,
                    'metrics_count': cycle.metrics_analyzed,
                    'reflections_count': cycle.reflections_generated,
                    'mutations_applied': [asdict(m) for m in applied_mutations]
                },
                action_taken=f"Applied {len(applied_mutations)} mutations",
                outcome={
                    'mutations': [m.mutation_type.value for m in applied_mutations],
                    'expected_improvements': [m.expected_improvement for m in applied_mutations]
                },
                success=len(applied_mutations) > 0,
                confidence=sum(m.confidence for m in applied_mutations) / len(applied_mutations) if applied_mutations else 0.0,
                tags=['evolution', 'optimization', cycle_id]
            )
            
            self.memory_store.store_experience(evolution_experience)
            cycle.experiences_stored = 1
            
            # Step 7: Calculate baseline for future comparison
            if recent_metrics:
                current_performance = sum(m.overall_score() for m in recent_metrics) / len(recent_metrics)
                if self.baseline_performance > 0:
                    cycle.performance_improvement = current_performance - self.baseline_performance
                self.baseline_performance = current_performance
            
            cycle.success = True
            cycle.end_time = time.time()
            self.last_evolution_time = cycle.end_time
            
            self.evolution_cycles.append(cycle)
            
            logger.info(f"Evolution cycle completed: {cycle_id} - Applied {cycle.mutations_applied} mutations")
            
            if self.on_evolution_complete:
                self.on_evolution_complete(cycle)
            
            return cycle
            
        except Exception as e:
            logger.error(f"Evolution cycle failed: {e}")
            cycle.success = False
            cycle.end_time = time.time()
            return cycle
            
        finally:
            self.is_evolving = False
    
    def check_and_rollback(self) -> bool:
        """Check if rollback is needed based on performance degradation"""
        if not self.config['auto_rollback_enabled']:
            return False
        
        recent_metrics = self.evaluator.metrics_history[-20:]  # Last 20 tasks
        if len(recent_metrics) < 10:
            return False
        
        current_performance = sum(m.overall_score() for m in recent_metrics) / len(recent_metrics)
        performance_change = current_performance - self.baseline_performance
        
        if performance_change < self.config['rollback_performance_threshold']:
            logger.warning(f"Performance degradation detected: {performance_change:.3f}")
            
            # Rollback recent mutations
            rollback_count = 0
            for mutation_key in list(self.mutator.active_mutations.keys()):
                if self.mutator.rollback_mutation(mutation_key):
                    rollback_count += 1
            
            if rollback_count > 0:
                logger.info(f"Rolled back {rollback_count} mutations")
                
                # Store rollback experience
                rollback_experience = Experience(
                    experience_id="",
                    experience_type=ExperienceType.ERROR_RECOVERY,
                    context={
                        'performance_change': performance_change,
                        'threshold': self.config['rollback_performance_threshold'],
                        'rollback_count': rollback_count
                    },
                    action_taken=f"Rolled back {rollback_count} mutations due to performance degradation",
                    outcome={
                        'rollback_successful': True,
                        'mutations_rolled_back': rollback_count
                    },
                    success=True,
                    confidence=0.9,
                    tags=['rollback', 'performance_recovery', 'auto_correction']
                )
                
                self.memory_store.store_experience(rollback_experience)
                
                if self.on_rollback_triggered:
                    self.on_rollback_triggered(rollback_count, performance_change)
                
                return True
        
        return False
    
    def get_evolution_status(self) -> Dict[str, Any]:
        """Get current evolution status"""
        recent_cycle = self.evolution_cycles[-1] if self.evolution_cycles else None
        
        status = {
            'is_evolving': self.is_evolving,
            'last_evolution_time': self.last_evolution_time,
            'time_until_next_evolution': max(0, self.config['evolution_interval'] - (time.time() - self.last_evolution_time)),
            'total_cycles': len(self.evolution_cycles),
            'baseline_performance': self.baseline_performance,
            'active_mutations': len(self.mutator.active_mutations),
            'recent_cycle': asdict(recent_cycle) if recent_cycle else None,
            'memory_stats': self.memory_store.get_memory_stats()
        }
        
        return status
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights from learning history"""
        insights = {
            'top_insights': self.reflector.get_top_insights(limit=5),
            'top_recommendations': self.reflector.get_top_recommendations(limit=3),
            'success_patterns': self.memory_store.get_success_patterns(),
            'failure_patterns': self.memory_store.get_failure_patterns(),
            'performance_summary': self.evaluator.get_performance_summary(last_n_tasks=50),
            'improvement_areas': self.evaluator.identify_improvement_areas()
        }
        
        return insights
    
    def force_evolution(self) -> EvolutionCycle:
        """Force an evolution cycle regardless of conditions"""
        logger.info("Forcing evolution cycle")
        self.last_evolution_time = 0  # Reset to allow evolution
        return asyncio.run(self.evolve())
    
    def reset_evolution(self):
        """Reset evolution state (for testing or recovery)"""
        logger.warning("Resetting evolution state")
        
        # Rollback all active mutations
        for mutation_key in list(self.mutator.active_mutations.keys()):
            self.mutator.rollback_mutation(mutation_key)
        
        # Reset state
        self.evolution_cycles.clear()
        self.last_evolution_time = 0
        self.baseline_performance = 0.0
        self.is_evolving = False
        
        logger.info("Evolution state reset complete")
    
    def export_evolution_data(self, directory: str):
        """Export all evolution data for analysis"""
        export_dir = Path(directory)
        export_dir.mkdir(exist_ok=True)
        
        timestamp = int(time.time())
        
        # Export metrics
        metrics_file = export_dir / f"metrics_{timestamp}.json"
        self.evaluator.export_metrics(str(metrics_file))
        
        # Export reflections
        reflections_file = export_dir / f"reflections_{timestamp}.json"
        self.reflector.export_reflections(str(reflections_file))
        
        # Export mutations
        mutations_file = export_dir / f"mutations_{timestamp}.json"
        self.mutator.export_mutations(str(mutations_file))
        
        # Export experiences
        experiences_file = export_dir / f"experiences_{timestamp}.json"
        self.memory_store.export_experiences(str(experiences_file))
        
        # Export evolution cycles
        cycles_file = export_dir / f"evolution_cycles_{timestamp}.json"
        cycles_data = {
            'cycles': [asdict(cycle) for cycle in self.evolution_cycles],
            'config': self.config,
            'status': self.get_evolution_status(),
            'export_timestamp': time.time()
        }
        
        with open(cycles_file, 'w', encoding='utf-8') as f:
            json.dump(cycles_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Evolution data exported to {export_dir}")
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old evolution data"""
        # Clean up old experiences
        deleted_experiences = self.memory_store.cleanup_old_experiences(days_to_keep)
        
        # Clean up old evolution cycles
        cutoff_time = time.time() - (days_to_keep * 24 * 3600)
        old_cycles = [c for c in self.evolution_cycles if c.start_time < cutoff_time]
        self.evolution_cycles = [c for c in self.evolution_cycles if c.start_time >= cutoff_time]
        
        logger.info(f"Cleaned up {deleted_experiences} experiences and {len(old_cycles)} evolution cycles")
    
    def close(self):
        """Close evolution engine and cleanup resources"""
        self.memory_store.close()
        logger.info("Evolution engine closed")