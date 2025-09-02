"""Behavior Mutator Module

Mutates agent behavior based on performance insights and recommendations.
"""

import time
import json
import random
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from copy import deepcopy

logger = logging.getLogger(__name__)

class MutationType(Enum):
    """Types of behavior mutations"""
    PARAMETER_ADJUSTMENT = "parameter_adjustment"
    STRATEGY_CHANGE = "strategy_change"
    TIMEOUT_MODIFICATION = "timeout_modification"
    RETRY_POLICY = "retry_policy"
    PROMPT_OPTIMIZATION = "prompt_optimization"
    WORKFLOW_REORDER = "workflow_reorder"
    FEATURE_TOGGLE = "feature_toggle"

@dataclass
class MutationStrategy:
    """Strategy for behavior mutation"""
    mutation_type: MutationType
    target_component: str
    parameter_name: str
    current_value: Any
    proposed_value: Any
    confidence: float  # 0.0 to 1.0
    rationale: str
    expected_improvement: str
    rollback_condition: str
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

class BehaviorMutator:
    """Mutates agent behavior based on performance analysis"""
    
    def __init__(self):
        self.mutation_history: List[MutationStrategy] = []
        self.active_mutations: Dict[str, MutationStrategy] = {}
        self.rollback_stack: List[Dict[str, Any]] = []
        
        # Default behavior parameters
        self.behavior_config = {
            'voice_input': {
                'timeout': 5.0,
                'confidence_threshold': 0.7,
                'retry_attempts': 2,
                'vad_sensitivity': 0.5
            },
            'office_automation': {
                'timeout': 30.0,
                'save_frequency': 'auto',
                'error_recovery': True,
                'backup_enabled': True
            },
            'system_operations': {
                'timeout': 10.0,
                'safety_checks': True,
                'confirmation_required': True,
                'max_retries': 1
            },
            'web_search': {
                'timeout': 15.0,
                'max_results': 5,
                'retry_attempts': 3,
                'result_filtering': True
            },
            'general': {
                'response_delay': 0.5,
                'logging_level': 'INFO',
                'performance_monitoring': True,
                'auto_optimization': True
            }
        }
    
    def generate_mutations(self, insights: List[str], recommendations: List[str]) -> List[MutationStrategy]:
        """Generate mutation strategies based on insights and recommendations"""
        mutations = []
        
        for recommendation in recommendations:
            mutation_strategies = self._analyze_recommendation(recommendation)
            mutations.extend(mutation_strategies)
        
        for insight in insights:
            mutation_strategies = self._analyze_insight(insight)
            mutations.extend(mutation_strategies)
        
        # Sort by confidence score
        mutations.sort(key=lambda m: m.confidence, reverse=True)
        
        logger.info(f"Generated {len(mutations)} mutation strategies")
        return mutations
    
    def _analyze_recommendation(self, recommendation: str) -> List[MutationStrategy]:
        """Analyze recommendation and generate corresponding mutations"""
        mutations = []
        rec_lower = recommendation.lower()
        
        # Timeout-related recommendations
        if 'timeout' in rec_lower or 'speed' in rec_lower:
            if 'increase' in rec_lower or 'longer' in rec_lower:
                mutations.extend(self._generate_timeout_mutations(increase=True))
            elif 'decrease' in rec_lower or 'faster' in rec_lower:
                mutations.extend(self._generate_timeout_mutations(increase=False))
        
        # Retry-related recommendations
        if 'retry' in rec_lower or 'attempt' in rec_lower:
            if 'more' in rec_lower or 'increase' in rec_lower:
                mutations.extend(self._generate_retry_mutations(increase=True))
            elif 'fewer' in rec_lower or 'reduce' in rec_lower:
                mutations.extend(self._generate_retry_mutations(increase=False))
        
        # Accuracy-related recommendations
        if 'accuracy' in rec_lower or 'precision' in rec_lower:
            mutations.extend(self._generate_accuracy_mutations())
        
        # Error handling recommendations
        if 'error' in rec_lower and 'handling' in rec_lower:
            mutations.extend(self._generate_error_handling_mutations())
        
        # Performance optimization
        if 'optimize' in rec_lower or 'performance' in rec_lower:
            mutations.extend(self._generate_performance_mutations())
        
        return mutations
    
    def _analyze_insight(self, insight: str) -> List[MutationStrategy]:
        """Analyze insight and generate corresponding mutations"""
        mutations = []
        insight_lower = insight.lower()
        
        # High failure rate insights
        if 'failure rate' in insight_lower and 'high' in insight_lower:
            mutations.extend(self._generate_reliability_mutations())
        
        # Execution time insights
        if 'execution time' in insight_lower:
            if 'long' in insight_lower or 'slow' in insight_lower:
                mutations.extend(self._generate_speed_mutations())
        
        # Success pattern insights
        if 'successful' in insight_lower and 'fast' in insight_lower:
            mutations.extend(self._generate_speed_optimization_mutations())
        
        return mutations
    
    def _generate_timeout_mutations(self, increase: bool) -> List[MutationStrategy]:
        """Generate timeout-related mutations"""
        mutations = []
        
        for component, config in self.behavior_config.items():
            if 'timeout' in config:
                current_timeout = config['timeout']
                
                if increase:
                    new_timeout = min(current_timeout * 1.5, 60.0)  # Max 60 seconds
                    rationale = "Increase timeout to reduce timeout-related failures"
                    improvement = "Reduced timeout failures, potentially slower response"
                else:
                    new_timeout = max(current_timeout * 0.7, 1.0)  # Min 1 second
                    rationale = "Decrease timeout to improve response speed"
                    improvement = "Faster response times, potential increase in timeouts"
                
                if new_timeout != current_timeout:
                    mutations.append(MutationStrategy(
                        mutation_type=MutationType.TIMEOUT_MODIFICATION,
                        target_component=component,
                        parameter_name='timeout',
                        current_value=current_timeout,
                        proposed_value=new_timeout,
                        confidence=0.8,
                        rationale=rationale,
                        expected_improvement=improvement,
                        rollback_condition="Performance degrades by >20%"
                    ))
        
        return mutations
    
    def _generate_retry_mutations(self, increase: bool) -> List[MutationStrategy]:
        """Generate retry-related mutations"""
        mutations = []
        
        for component, config in self.behavior_config.items():
            retry_key = 'retry_attempts' if 'retry_attempts' in config else 'max_retries'
            
            if retry_key in config:
                current_retries = config[retry_key]
                
                if increase:
                    new_retries = min(current_retries + 1, 5)  # Max 5 retries
                    rationale = "Increase retry attempts to improve success rate"
                    improvement = "Higher success rate, potentially slower response"
                else:
                    new_retries = max(current_retries - 1, 0)  # Min 0 retries
                    rationale = "Decrease retry attempts to improve speed"
                    improvement = "Faster failure detection, potentially lower success rate"
                
                if new_retries != current_retries:
                    mutations.append(MutationStrategy(
                        mutation_type=MutationType.RETRY_POLICY,
                        target_component=component,
                        parameter_name=retry_key,
                        current_value=current_retries,
                        proposed_value=new_retries,
                        confidence=0.7,
                        rationale=rationale,
                        expected_improvement=improvement,
                        rollback_condition="Success rate drops by >15%"
                    ))
        
        return mutations
    
    def _generate_accuracy_mutations(self) -> List[MutationStrategy]:
        """Generate accuracy-related mutations"""
        mutations = []
        
        # Voice input confidence threshold
        if 'voice_input' in self.behavior_config:
            current_threshold = self.behavior_config['voice_input']['confidence_threshold']
            new_threshold = min(current_threshold + 0.1, 0.95)
            
            if new_threshold != current_threshold:
                mutations.append(MutationStrategy(
                    mutation_type=MutationType.PARAMETER_ADJUSTMENT,
                    target_component='voice_input',
                    parameter_name='confidence_threshold',
                    current_value=current_threshold,
                    proposed_value=new_threshold,
                    confidence=0.8,
                    rationale="Increase confidence threshold to improve accuracy",
                    expected_improvement="Higher accuracy, potentially more rejections",
                    rollback_condition="Rejection rate increases by >30%"
                ))
        
        return mutations
    
    def _generate_error_handling_mutations(self) -> List[MutationStrategy]:
        """Generate error handling mutations"""
        mutations = []
        
        # Enable error recovery for office automation
        if not self.behavior_config['office_automation']['error_recovery']:
            mutations.append(MutationStrategy(
                mutation_type=MutationType.FEATURE_TOGGLE,
                target_component='office_automation',
                parameter_name='error_recovery',
                current_value=False,
                proposed_value=True,
                confidence=0.9,
                rationale="Enable error recovery to handle office automation failures",
                expected_improvement="Better error handling, potential slight performance overhead",
                rollback_condition="Performance degrades by >10%"
            ))
        
        # Enable safety checks for system operations
        if not self.behavior_config['system_operations']['safety_checks']:
            mutations.append(MutationStrategy(
                mutation_type=MutationType.FEATURE_TOGGLE,
                target_component='system_operations',
                parameter_name='safety_checks',
                current_value=False,
                proposed_value=True,
                confidence=0.95,
                rationale="Enable safety checks to prevent dangerous operations",
                expected_improvement="Improved safety, slight performance overhead",
                rollback_condition="User complaints about excessive confirmations"
            ))
        
        return mutations
    
    def _generate_performance_mutations(self) -> List[MutationStrategy]:
        """Generate performance optimization mutations"""
        mutations = []
        
        # Reduce response delay
        current_delay = self.behavior_config['general']['response_delay']
        new_delay = max(current_delay * 0.5, 0.1)
        
        if new_delay != current_delay:
            mutations.append(MutationStrategy(
                mutation_type=MutationType.PARAMETER_ADJUSTMENT,
                target_component='general',
                parameter_name='response_delay',
                current_value=current_delay,
                proposed_value=new_delay,
                confidence=0.7,
                rationale="Reduce response delay to improve perceived performance",
                expected_improvement="Faster response feel, potential stability issues",
                rollback_condition="Error rate increases by >10%"
            ))
        
        return mutations
    
    def _generate_reliability_mutations(self) -> List[MutationStrategy]:
        """Generate reliability improvement mutations"""
        mutations = []
        
        # Enable backup for office automation
        if not self.behavior_config['office_automation']['backup_enabled']:
            mutations.append(MutationStrategy(
                mutation_type=MutationType.FEATURE_TOGGLE,
                target_component='office_automation',
                parameter_name='backup_enabled',
                current_value=False,
                proposed_value=True,
                confidence=0.85,
                rationale="Enable backup to prevent data loss",
                expected_improvement="Better data protection, slight performance overhead",
                rollback_condition="Storage usage increases by >50%"
            ))
        
        return mutations
    
    def _generate_speed_mutations(self) -> List[MutationStrategy]:
        """Generate speed improvement mutations"""
        mutations = []
        
        # Reduce web search results for faster processing
        current_results = self.behavior_config['web_search']['max_results']
        new_results = max(current_results - 1, 3)
        
        if new_results != current_results:
            mutations.append(MutationStrategy(
                mutation_type=MutationType.PARAMETER_ADJUSTMENT,
                target_component='web_search',
                parameter_name='max_results',
                current_value=current_results,
                proposed_value=new_results,
                confidence=0.6,
                rationale="Reduce search results to improve speed",
                expected_improvement="Faster search processing, potentially less comprehensive results",
                rollback_condition="Search quality drops significantly"
            ))
        
        return mutations
    
    def _generate_speed_optimization_mutations(self) -> List[MutationStrategy]:
        """Generate mutations based on successful speed patterns"""
        mutations = []
        
        # Optimize save frequency for office automation
        if self.behavior_config['office_automation']['save_frequency'] != 'manual':
            mutations.append(MutationStrategy(
                mutation_type=MutationType.STRATEGY_CHANGE,
                target_component='office_automation',
                parameter_name='save_frequency',
                current_value=self.behavior_config['office_automation']['save_frequency'],
                proposed_value='manual',
                confidence=0.5,
                rationale="Switch to manual save for speed optimization",
                expected_improvement="Faster operations, potential data loss risk",
                rollback_condition="User reports data loss"
            ))
        
        return mutations
    
    def apply_mutation(self, mutation: MutationStrategy) -> bool:
        """Apply a mutation to the behavior configuration"""
        try:
            # Store current state for rollback
            self.rollback_stack.append(deepcopy(self.behavior_config))
            
            # Apply the mutation
            if mutation.target_component in self.behavior_config:
                if mutation.parameter_name in self.behavior_config[mutation.target_component]:
                    self.behavior_config[mutation.target_component][mutation.parameter_name] = mutation.proposed_value
                    
                    # Track active mutation
                    mutation_key = f"{mutation.target_component}.{mutation.parameter_name}"
                    self.active_mutations[mutation_key] = mutation
                    
                    # Add to history
                    self.mutation_history.append(mutation)
                    
                    logger.info(f"Applied mutation: {mutation.target_component}.{mutation.parameter_name} = {mutation.proposed_value}")
                    return True
            
            logger.warning(f"Failed to apply mutation: invalid target or parameter")
            return False
            
        except Exception as e:
            logger.error(f"Error applying mutation: {e}")
            return False
    
    def rollback_mutation(self, mutation_key: str) -> bool:
        """Rollback a specific mutation"""
        try:
            if mutation_key in self.active_mutations and self.rollback_stack:
                # Restore previous state
                self.behavior_config = self.rollback_stack.pop()
                
                # Remove from active mutations
                del self.active_mutations[mutation_key]
                
                logger.info(f"Rolled back mutation: {mutation_key}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error rolling back mutation: {e}")
            return False
    
    def get_current_config(self) -> Dict[str, Any]:
        """Get current behavior configuration"""
        return deepcopy(self.behavior_config)
    
    def export_mutations(self, filepath: str):
        """Export mutation history to JSON file"""
        data = {
            'mutations': [asdict(m) for m in self.mutation_history],
            'active_mutations': {k: asdict(v) for k, v in self.active_mutations.items()},
            'current_config': self.behavior_config,
            'export_timestamp': time.time()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Mutations exported to {filepath}")
    
    def load_mutations(self, filepath: str):
        """Load mutation history from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'mutations' in data:
                self.mutation_history = [
                    MutationStrategy(**m) for m in data['mutations']
                ]
            
            if 'current_config' in data:
                self.behavior_config = data['current_config']
            
            logger.info(f"Mutations loaded from {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to load mutations: {e}")