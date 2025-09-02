"""Task Evaluator Module

Evaluates agent performance on various tasks and provides metrics for improvement.
"""

import time
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """Task execution status"""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    TIMEOUT = "timeout"
    ERROR = "error"

@dataclass
class PerformanceMetrics:
    """Performance metrics for task evaluation"""
    task_id: str
    task_type: str
    status: TaskStatus
    execution_time: float
    accuracy_score: float  # 0.0 to 1.0
    efficiency_score: float  # 0.0 to 1.0
    user_satisfaction: Optional[float] = None  # 0.0 to 1.0
    error_count: int = 0
    retry_count: int = 0
    resource_usage: Dict[str, float] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
        if self.resource_usage is None:
            self.resource_usage = {}
    
    def overall_score(self) -> float:
        """Calculate overall performance score"""
        base_score = (self.accuracy_score + self.efficiency_score) / 2
        
        # Penalty for errors and retries
        error_penalty = min(0.1 * self.error_count, 0.5)
        retry_penalty = min(0.05 * self.retry_count, 0.3)
        
        # Bonus for user satisfaction if available
        satisfaction_bonus = 0
        if self.user_satisfaction is not None:
            satisfaction_bonus = (self.user_satisfaction - 0.5) * 0.2
        
        return max(0.0, min(1.0, base_score - error_penalty - retry_penalty + satisfaction_bonus))

class TaskEvaluator:
    """Evaluates agent performance on various tasks"""
    
    def __init__(self):
        self.metrics_history: List[PerformanceMetrics] = []
        self.task_benchmarks: Dict[str, Dict[str, float]] = {
            'voice_command': {
                'target_accuracy': 0.9,
                'target_response_time': 2.0,
                'max_retries': 2
            },
            'office_automation': {
                'target_accuracy': 0.95,
                'target_response_time': 5.0,
                'max_retries': 1
            },
            'system_operation': {
                'target_accuracy': 0.98,
                'target_response_time': 3.0,
                'max_retries': 0
            },
            'web_search': {
                'target_accuracy': 0.85,
                'target_response_time': 10.0,
                'max_retries': 3
            }
        }
    
    def evaluate_task(self, 
                     task_id: str,
                     task_type: str,
                     start_time: float,
                     end_time: float,
                     expected_output: Any,
                     actual_output: Any,
                     error_count: int = 0,
                     retry_count: int = 0,
                     user_feedback: Optional[float] = None) -> PerformanceMetrics:
        """Evaluate a completed task"""
        
        execution_time = end_time - start_time
        
        # Determine task status
        status = self._determine_status(actual_output, error_count)
        
        # Calculate accuracy score
        accuracy_score = self._calculate_accuracy(expected_output, actual_output, task_type)
        
        # Calculate efficiency score
        efficiency_score = self._calculate_efficiency(task_type, execution_time, retry_count)
        
        metrics = PerformanceMetrics(
            task_id=task_id,
            task_type=task_type,
            status=status,
            execution_time=execution_time,
            accuracy_score=accuracy_score,
            efficiency_score=efficiency_score,
            user_satisfaction=user_feedback,
            error_count=error_count,
            retry_count=retry_count
        )
        
        self.metrics_history.append(metrics)
        logger.info(f"Task {task_id} evaluated: {metrics.overall_score():.2f}")
        
        return metrics
    
    def _determine_status(self, actual_output: Any, error_count: int) -> TaskStatus:
        """Determine task execution status"""
        if error_count > 0:
            if actual_output is None:
                return TaskStatus.FAILURE
            else:
                return TaskStatus.PARTIAL
        elif actual_output is not None:
            return TaskStatus.SUCCESS
        else:
            return TaskStatus.FAILURE
    
    def _calculate_accuracy(self, expected: Any, actual: Any, task_type: str) -> float:
        """Calculate accuracy score based on expected vs actual output"""
        if expected is None or actual is None:
            return 0.0
        
        if task_type == 'voice_command':
            # For voice commands, check if the action was performed correctly
            if isinstance(expected, dict) and isinstance(actual, dict):
                matches = sum(1 for k, v in expected.items() if actual.get(k) == v)
                return matches / len(expected) if expected else 0.0
        
        elif task_type == 'office_automation':
            # For office tasks, check if files were created/modified correctly
            if isinstance(expected, str) and isinstance(actual, str):
                return 1.0 if expected.lower() in actual.lower() else 0.0
        
        elif task_type == 'system_operation':
            # For system operations, check if the operation succeeded
            return 1.0 if str(actual).lower() in ['success', 'completed', 'done'] else 0.0
        
        # Default string similarity
        if isinstance(expected, str) and isinstance(actual, str):
            return self._string_similarity(expected, actual)
        
        return 1.0 if expected == actual else 0.0
    
    def _calculate_efficiency(self, task_type: str, execution_time: float, retry_count: int) -> float:
        """Calculate efficiency score based on execution time and retries"""
        benchmark = self.task_benchmarks.get(task_type, {
            'target_response_time': 5.0,
            'max_retries': 2
        })
        
        # Time efficiency (inverse relationship)
        target_time = benchmark['target_response_time']
        time_score = min(1.0, target_time / max(execution_time, 0.1))
        
        # Retry penalty
        max_retries = benchmark['max_retries']
        retry_penalty = min(0.5, retry_count / max(max_retries, 1)) if max_retries > 0 else retry_count * 0.2
        
        return max(0.0, time_score - retry_penalty)
    
    def _string_similarity(self, s1: str, s2: str) -> float:
        """Calculate simple string similarity"""
        if not s1 or not s2:
            return 0.0
        
        s1_words = set(s1.lower().split())
        s2_words = set(s2.lower().split())
        
        if not s1_words or not s2_words:
            return 0.0
        
        intersection = s1_words.intersection(s2_words)
        union = s1_words.union(s2_words)
        
        return len(intersection) / len(union)
    
    def get_performance_summary(self, task_type: Optional[str] = None, 
                              last_n_tasks: Optional[int] = None) -> Dict[str, float]:
        """Get performance summary statistics"""
        metrics = self.metrics_history
        
        if task_type:
            metrics = [m for m in metrics if m.task_type == task_type]
        
        if last_n_tasks:
            metrics = metrics[-last_n_tasks:]
        
        if not metrics:
            return {}
        
        return {
            'avg_accuracy': sum(m.accuracy_score for m in metrics) / len(metrics),
            'avg_efficiency': sum(m.efficiency_score for m in metrics) / len(metrics),
            'avg_overall_score': sum(m.overall_score() for m in metrics) / len(metrics),
            'success_rate': sum(1 for m in metrics if m.status == TaskStatus.SUCCESS) / len(metrics),
            'avg_execution_time': sum(m.execution_time for m in metrics) / len(metrics),
            'total_tasks': len(metrics)
        }
    
    def identify_improvement_areas(self) -> List[Dict[str, Any]]:
        """Identify areas that need improvement"""
        improvements = []
        
        for task_type in self.task_benchmarks.keys():
            summary = self.get_performance_summary(task_type=task_type, last_n_tasks=10)
            
            if not summary:
                continue
            
            benchmark = self.task_benchmarks[task_type]
            
            if summary['avg_accuracy'] < benchmark['target_accuracy']:
                improvements.append({
                    'area': 'accuracy',
                    'task_type': task_type,
                    'current': summary['avg_accuracy'],
                    'target': benchmark['target_accuracy'],
                    'priority': 'high' if summary['avg_accuracy'] < 0.7 else 'medium'
                })
            
            if summary['avg_execution_time'] > benchmark['target_response_time']:
                improvements.append({
                    'area': 'speed',
                    'task_type': task_type,
                    'current': summary['avg_execution_time'],
                    'target': benchmark['target_response_time'],
                    'priority': 'medium'
                })
        
        return improvements
    
    def export_metrics(self, filepath: str):
        """Export metrics to JSON file"""
        data = {
            'metrics': [asdict(m) for m in self.metrics_history],
            'benchmarks': self.task_benchmarks,
            'export_timestamp': time.time()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Metrics exported to {filepath}")
    
    def load_metrics(self, filepath: str):
        """Load metrics from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.metrics_history = [
                PerformanceMetrics(**m) for m in data.get('metrics', [])
            ]
            
            if 'benchmarks' in data:
                self.task_benchmarks.update(data['benchmarks'])
            
            logger.info(f"Metrics loaded from {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to load metrics: {e}")