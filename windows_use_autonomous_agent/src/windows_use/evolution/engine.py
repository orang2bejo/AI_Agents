"""Evolution Engine - Orchestrates the self-evolving agent system.

This module coordinates the evaluation, reflection, mutation, and memory components
to create a self-improving agent system.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .evaluator import TaskEvaluator, PerformanceMetrics, TaskStatus
from .reflector import AgentReflector, ReflectionResult, ReflectionType
from .mutator import BehaviorMutator, MutationType
from .memory import MemoryStore, Experience, ExperienceType


@dataclass
class EvolutionConfig:
    """Configuration for the evolution engine."""
    evaluation_interval: int = 3600  # seconds
    reflection_threshold: int = 10  # minimum experiences before reflection
    mutation_threshold: float = 0.7  # performance threshold for mutations
    memory_retention_days: int = 30
    max_mutations_per_cycle: int = 3
    enable_auto_evolution: bool = True


class EvolutionEngine:
    """Main engine that orchestrates the self-evolving agent system."""
    
    def __init__(self, config: Optional[EvolutionConfig] = None):
        self.config = config or EvolutionConfig()
        self.evaluator = TaskEvaluator()
        self.reflector = AgentReflector()
        self.mutator = BehaviorMutator()
        self.memory = MemoryStore()
        
        self.logger = logging.getLogger(__name__)
        self.is_running = False
        self.last_evolution_time = datetime.now()
        
    async def start(self):
        """Start the evolution engine."""
        if self.is_running:
            self.logger.warning("Evolution engine is already running")
            return
            
        self.is_running = True
        self.logger.info("Starting evolution engine")
        
        if self.config.enable_auto_evolution:
            asyncio.create_task(self._evolution_loop())
    
    async def stop(self):
        """Stop the evolution engine."""
        self.is_running = False
        self.logger.info("Stopping evolution engine")
    
    async def record_experience(self, 
                              experience_type: ExperienceType,
                              context: str,
                              action: str,
                              outcome: str,
                              success: bool,
                              confidence: float = 0.5,
                              tags: Optional[List[str]] = None) -> str:
        """Record a new experience in the memory store."""
        experience = Experience(
            type=experience_type,
            context=context,
            action=action,
            outcome=outcome,
            success=success,
            confidence=confidence,
            tags=tags or [],
            timestamp=datetime.now()
        )
        
        experience_id = await self.memory.store_experience(experience)
        self.logger.debug(f"Recorded experience: {experience_id}")
        
        # Trigger evaluation if enough experiences accumulated
        if await self._should_trigger_evolution():
            await self.evolve()
            
        return experience_id
    
    async def evaluate_performance(self, 
                                 task_id: str,
                                 expected_outcome: str,
                                 actual_outcome: str,
                                 execution_time: float,
                                 success: bool) -> PerformanceMetrics:
        """Evaluate task performance."""
        status = TaskStatus.SUCCESS if success else TaskStatus.FAILED
        
        metrics = await self.evaluator.evaluate_task(
            task_id=task_id,
            expected_outcome=expected_outcome,
            actual_outcome=actual_outcome,
            execution_time=execution_time,
            status=status
        )
        
        # Record as experience
        await self.record_experience(
            experience_type=ExperienceType.TASK_EXECUTION,
            context=f"Task: {task_id}",
            action=f"Expected: {expected_outcome}",
            outcome=f"Actual: {actual_outcome} (Time: {execution_time}s)",
            success=success,
            confidence=metrics.accuracy,
            tags=["task_evaluation"]
        )
        
        return metrics
    
    async def evolve(self) -> Dict[str, Any]:
        """Trigger evolution cycle: reflect, mutate, and adapt."""
        self.logger.info("Starting evolution cycle")
        evolution_results = {
            "timestamp": datetime.now().isoformat(),
            "reflections": [],
            "mutations": [],
            "performance_summary": None
        }
        
        try:
            # 1. Reflect on recent experiences
            reflections = await self._reflect_on_experiences()
            evolution_results["reflections"] = [
                {
                    "type": r.type.value,
                    "insight": r.insight,
                    "confidence": r.confidence,
                    "recommendations": r.recommendations
                } for r in reflections
            ]
            
            # 2. Generate and apply mutations based on reflections
            mutations = await self._apply_mutations(reflections)
            evolution_results["mutations"] = [
                {
                    "type": m["type"],
                    "description": m["description"],
                    "success": m["success"]
                } for m in mutations
            ]
            
            # 3. Update performance summary
            performance = await self.evaluator.get_performance_summary()
            evolution_results["performance_summary"] = {
                "total_tasks": performance.total_tasks,
                "success_rate": performance.success_rate,
                "avg_execution_time": performance.avg_execution_time,
                "accuracy": performance.accuracy,
                "efficiency": performance.efficiency
            }
            
            # 4. Clean up old data
            await self._cleanup_old_data()
            
            self.last_evolution_time = datetime.now()
            self.logger.info(f"Evolution cycle completed. Applied {len(mutations)} mutations")
            
        except Exception as e:
            self.logger.error(f"Evolution cycle failed: {e}")
            evolution_results["error"] = str(e)
        
        return evolution_results
    
    async def get_insights(self) -> Dict[str, Any]:
        """Get current insights and recommendations."""
        insights = await self.reflector.get_top_insights(limit=10)
        recommendations = await self.reflector.get_recommendations()
        performance = await self.evaluator.get_performance_summary()
        
        return {
            "performance": {
                "success_rate": performance.success_rate,
                "accuracy": performance.accuracy,
                "efficiency": performance.efficiency,
                "total_tasks": performance.total_tasks
            },
            "insights": [
                {
                    "type": insight.type.value,
                    "insight": insight.insight,
                    "confidence": insight.confidence,
                    "impact_score": insight.impact_score
                } for insight in insights
            ],
            "recommendations": recommendations,
            "last_evolution": self.last_evolution_time.isoformat()
        }
    
    async def _evolution_loop(self):
        """Main evolution loop that runs periodically."""
        while self.is_running:
            try:
                await asyncio.sleep(self.config.evaluation_interval)
                
                if await self._should_trigger_evolution():
                    await self.evolve()
                    
            except Exception as e:
                self.logger.error(f"Evolution loop error: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _should_trigger_evolution(self) -> bool:
        """Check if evolution should be triggered."""
        # Check if enough time has passed
        time_threshold = datetime.now() - timedelta(seconds=self.config.evaluation_interval)
        if self.last_evolution_time < time_threshold:
            return True
        
        # Check if enough experiences accumulated
        recent_experiences = await self.memory.get_experiences(
            limit=self.config.reflection_threshold
        )
        
        return len(recent_experiences) >= self.config.reflection_threshold
    
    async def _reflect_on_experiences(self) -> List[ReflectionResult]:
        """Analyze recent experiences and generate insights."""
        # Get recent experiences
        experiences = await self.memory.get_experiences(limit=100)
        
        if not experiences:
            return []
        
        reflections = []
        
        # Analyze failures
        failed_experiences = [e for e in experiences if not e.success]
        if failed_experiences:
            failure_reflection = await self.reflector.analyze_failures(failed_experiences)
            if failure_reflection:
                reflections.append(failure_reflection)
        
        # Analyze success patterns
        successful_experiences = [e for e in experiences if e.success]
        if successful_experiences:
            success_reflection = await self.reflector.analyze_success_patterns(successful_experiences)
            if success_reflection:
                reflections.append(success_reflection)
        
        # Analyze performance trends
        performance_metrics = await self.evaluator.get_recent_metrics(days=7)
        if performance_metrics:
            trend_reflection = await self.reflector.analyze_performance_trends(performance_metrics)
            if trend_reflection:
                reflections.append(trend_reflection)
        
        return reflections
    
    async def _apply_mutations(self, reflections: List[ReflectionResult]) -> List[Dict[str, Any]]:
        """Apply mutations based on reflection insights."""
        mutations = []
        applied_count = 0
        
        for reflection in reflections:
            if applied_count >= self.config.max_mutations_per_cycle:
                break
                
            for recommendation in reflection.recommendations:
                if applied_count >= self.config.max_mutations_per_cycle:
                    break
                
                try:
                    # Generate mutation based on recommendation
                    mutation_result = await self.mutator.generate_mutation(
                        mutation_type=self._recommendation_to_mutation_type(recommendation),
                        context=reflection.insight,
                        target_improvement=recommendation
                    )
                    
                    if mutation_result:
                        # Apply the mutation
                        success = await self.mutator.apply_mutation(mutation_result["id"])
                        
                        mutations.append({
                            "type": mutation_result["type"],
                            "description": mutation_result["description"],
                            "success": success
                        })
                        
                        if success:
                            applied_count += 1
                            
                except Exception as e:
                    self.logger.error(f"Failed to apply mutation: {e}")
        
        return mutations
    
    def _recommendation_to_mutation_type(self, recommendation: str) -> MutationType:
        """Convert recommendation text to mutation type."""
        recommendation_lower = recommendation.lower()
        
        if "timeout" in recommendation_lower or "time" in recommendation_lower:
            return MutationType.TIMEOUT_ADJUSTMENT
        elif "retry" in recommendation_lower:
            return MutationType.RETRY_POLICY
        elif "parameter" in recommendation_lower or "config" in recommendation_lower:
            return MutationType.PARAMETER_ADJUSTMENT
        elif "strategy" in recommendation_lower or "approach" in recommendation_lower:
            return MutationType.STRATEGY_CHANGE
        elif "prompt" in recommendation_lower or "instruction" in recommendation_lower:
            return MutationType.PROMPT_OPTIMIZATION
        elif "workflow" in recommendation_lower or "order" in recommendation_lower:
            return MutationType.WORKFLOW_REORDER
        else:
            return MutationType.PARAMETER_ADJUSTMENT
    
    async def _cleanup_old_data(self):
        """Clean up old data from memory and evaluation stores."""
        cutoff_date = datetime.now() - timedelta(days=self.config.memory_retention_days)
        
        # Clean up old experiences
        await self.memory.cleanup_old_experiences(cutoff_date)
        
        # Clean up old evaluation data
        await self.evaluator.cleanup_old_metrics(cutoff_date)
        
        # Clean up old reflection data
        await self.reflector.cleanup_old_reflections(cutoff_date)