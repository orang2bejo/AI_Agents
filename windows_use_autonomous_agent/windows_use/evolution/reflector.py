"""Agent Reflector Module

Analyzes agent performance and generates insights for improvement.
"""

import time
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from collections import defaultdict, Counter

from .evaluator import PerformanceMetrics, TaskStatus

logger = logging.getLogger(__name__)

class ReflectionType(Enum):
    """Types of reflection analysis"""
    FAILURE_ANALYSIS = "failure_analysis"
    SUCCESS_PATTERN = "success_pattern"
    PERFORMANCE_TREND = "performance_trend"
    ERROR_PATTERN = "error_pattern"
    USER_FEEDBACK = "user_feedback"

@dataclass
class ReflectionResult:
    """Result of reflection analysis"""
    reflection_type: ReflectionType
    insights: List[str]
    recommendations: List[str]
    confidence_score: float  # 0.0 to 1.0
    supporting_data: Dict[str, Any]
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

class AgentReflector:
    """Analyzes agent performance and generates improvement insights"""
    
    def __init__(self):
        self.reflection_history: List[ReflectionResult] = []
        self.error_patterns: Dict[str, List[str]] = defaultdict(list)
        self.success_patterns: Dict[str, List[str]] = defaultdict(list)
    
    def reflect_on_metrics(self, metrics: List[PerformanceMetrics]) -> List[ReflectionResult]:
        """Perform comprehensive reflection on performance metrics"""
        reflections = []
        
        if not metrics:
            return reflections
        
        # Analyze failures
        failure_reflection = self._analyze_failures(metrics)
        if failure_reflection:
            reflections.append(failure_reflection)
        
        # Analyze success patterns
        success_reflection = self._analyze_success_patterns(metrics)
        if success_reflection:
            reflections.append(success_reflection)
        
        # Analyze performance trends
        trend_reflection = self._analyze_performance_trends(metrics)
        if trend_reflection:
            reflections.append(trend_reflection)
        
        # Analyze error patterns
        error_reflection = self._analyze_error_patterns(metrics)
        if error_reflection:
            reflections.append(error_reflection)
        
        # Store reflections
        self.reflection_history.extend(reflections)
        
        logger.info(f"Generated {len(reflections)} reflection insights")
        return reflections
    
    def _analyze_failures(self, metrics: List[PerformanceMetrics]) -> Optional[ReflectionResult]:
        """Analyze failure patterns and causes"""
        failures = [m for m in metrics if m.status in [TaskStatus.FAILURE, TaskStatus.ERROR]]
        
        if not failures:
            return None
        
        insights = []
        recommendations = []
        supporting_data = {}
        
        # Failure rate by task type
        task_failures = defaultdict(int)
        task_totals = defaultdict(int)
        
        for metric in metrics:
            task_totals[metric.task_type] += 1
            if metric.status in [TaskStatus.FAILURE, TaskStatus.ERROR]:
                task_failures[metric.task_type] += 1
        
        failure_rates = {
            task_type: task_failures[task_type] / task_totals[task_type]
            for task_type in task_totals
        }
        
        supporting_data['failure_rates'] = failure_rates
        
        # Identify problematic task types
        high_failure_tasks = [task for task, rate in failure_rates.items() if rate > 0.2]
        
        if high_failure_tasks:
            insights.append(f"High failure rate detected in: {', '.join(high_failure_tasks)}")
            recommendations.append(f"Focus improvement efforts on {high_failure_tasks[0]} tasks")
        
        # Analyze common failure characteristics
        avg_execution_time = sum(f.execution_time for f in failures) / len(failures)
        avg_retries = sum(f.retry_count for f in failures) / len(failures)
        
        if avg_execution_time > 10.0:
            insights.append("Failed tasks tend to have long execution times")
            recommendations.append("Implement timeout mechanisms and task optimization")
        
        if avg_retries > 2:
            insights.append("Failed tasks often require multiple retries")
            recommendations.append("Improve initial task execution reliability")
        
        # Recent failure trend
        recent_failures = [f for f in failures if f.timestamp > time.time() - 3600]  # Last hour
        if len(recent_failures) > len(failures) * 0.5:
            insights.append("Failure rate has increased recently")
            recommendations.append("Investigate recent changes or environmental factors")
        
        confidence_score = min(1.0, len(failures) / 10)  # More failures = higher confidence
        
        return ReflectionResult(
            reflection_type=ReflectionType.FAILURE_ANALYSIS,
            insights=insights,
            recommendations=recommendations,
            confidence_score=confidence_score,
            supporting_data=supporting_data
        )
    
    def _analyze_success_patterns(self, metrics: List[PerformanceMetrics]) -> Optional[ReflectionResult]:
        """Analyze patterns in successful tasks"""
        successes = [m for m in metrics if m.status == TaskStatus.SUCCESS and m.overall_score() > 0.8]
        
        if len(successes) < 3:
            return None
        
        insights = []
        recommendations = []
        supporting_data = {}
        
        # Success characteristics
        avg_execution_time = sum(s.execution_time for s in successes) / len(successes)
        avg_accuracy = sum(s.accuracy_score for s in successes) / len(successes)
        avg_efficiency = sum(s.efficiency_score for s in successes) / len(successes)
        
        supporting_data['success_characteristics'] = {
            'avg_execution_time': avg_execution_time,
            'avg_accuracy': avg_accuracy,
            'avg_efficiency': avg_efficiency
        }
        
        # Task type success rates
        task_successes = defaultdict(int)
        task_totals = defaultdict(int)
        
        for metric in metrics:
            task_totals[metric.task_type] += 1
            if metric.status == TaskStatus.SUCCESS:
                task_successes[metric.task_type] += 1
        
        success_rates = {
            task_type: task_successes[task_type] / task_totals[task_type]
            for task_type in task_totals
        }
        
        best_performing_task = max(success_rates.items(), key=lambda x: x[1])
        
        insights.append(f"Best performing task type: {best_performing_task[0]} ({best_performing_task[1]:.1%} success rate)")
        insights.append(f"Successful tasks average {avg_execution_time:.1f}s execution time")
        
        # Identify optimal execution patterns
        fast_successes = [s for s in successes if s.execution_time < avg_execution_time]
        if fast_successes:
            fast_avg_accuracy = sum(s.accuracy_score for s in fast_successes) / len(fast_successes)
            if fast_avg_accuracy > avg_accuracy:
                insights.append("Faster execution often correlates with higher accuracy")
                recommendations.append("Optimize for speed without sacrificing accuracy")
        
        # Zero-retry successes
        no_retry_successes = [s for s in successes if s.retry_count == 0]
        if len(no_retry_successes) > len(successes) * 0.7:
            insights.append("Most successful tasks complete on first attempt")
            recommendations.append("Focus on improving first-attempt success rate")
        
        confidence_score = min(1.0, len(successes) / 20)
        
        return ReflectionResult(
            reflection_type=ReflectionType.SUCCESS_PATTERN,
            insights=insights,
            recommendations=recommendations,
            confidence_score=confidence_score,
            supporting_data=supporting_data
        )
    
    def _analyze_performance_trends(self, metrics: List[PerformanceMetrics]) -> Optional[ReflectionResult]:
        """Analyze performance trends over time"""
        if len(metrics) < 5:
            return None
        
        # Sort by timestamp
        sorted_metrics = sorted(metrics, key=lambda m: m.timestamp)
        
        insights = []
        recommendations = []
        supporting_data = {}
        
        # Calculate moving averages
        window_size = min(5, len(sorted_metrics) // 2)
        recent_metrics = sorted_metrics[-window_size:]
        earlier_metrics = sorted_metrics[:window_size]
        
        recent_avg_score = sum(m.overall_score() for m in recent_metrics) / len(recent_metrics)
        earlier_avg_score = sum(m.overall_score() for m in earlier_metrics) / len(earlier_metrics)
        
        score_trend = recent_avg_score - earlier_avg_score
        
        supporting_data['performance_trend'] = {
            'recent_avg_score': recent_avg_score,
            'earlier_avg_score': earlier_avg_score,
            'trend': score_trend
        }
        
        if score_trend > 0.1:
            insights.append(f"Performance is improving (trend: +{score_trend:.2f})")
            recommendations.append("Continue current optimization strategies")
        elif score_trend < -0.1:
            insights.append(f"Performance is declining (trend: {score_trend:.2f})")
            recommendations.append("Investigate recent changes and implement corrective measures")
        else:
            insights.append("Performance is stable")
            recommendations.append("Consider new optimization strategies for breakthrough improvements")
        
        # Execution time trend
        recent_avg_time = sum(m.execution_time for m in recent_metrics) / len(recent_metrics)
        earlier_avg_time = sum(m.execution_time for m in earlier_metrics) / len(earlier_metrics)
        time_trend = recent_avg_time - earlier_avg_time
        
        if time_trend > 1.0:
            insights.append("Execution times are increasing")
            recommendations.append("Investigate performance bottlenecks")
        elif time_trend < -1.0:
            insights.append("Execution times are improving")
            recommendations.append("Document and replicate speed optimizations")
        
        confidence_score = min(1.0, len(metrics) / 15)
        
        return ReflectionResult(
            reflection_type=ReflectionType.PERFORMANCE_TREND,
            insights=insights,
            recommendations=recommendations,
            confidence_score=confidence_score,
            supporting_data=supporting_data
        )
    
    def _analyze_error_patterns(self, metrics: List[PerformanceMetrics]) -> Optional[ReflectionResult]:
        """Analyze error patterns and frequencies"""
        error_metrics = [m for m in metrics if m.error_count > 0]
        
        if not error_metrics:
            return None
        
        insights = []
        recommendations = []
        supporting_data = {}
        
        # Error frequency by task type
        task_errors = defaultdict(int)
        for metric in error_metrics:
            task_errors[metric.task_type] += metric.error_count
        
        supporting_data['error_frequency'] = dict(task_errors)
        
        if task_errors:
            most_error_prone = max(task_errors.items(), key=lambda x: x[1])
            insights.append(f"Most error-prone task type: {most_error_prone[0]} ({most_error_prone[1]} errors)")
            recommendations.append(f"Implement additional error handling for {most_error_prone[0]} tasks")
        
        # Error clustering
        total_errors = sum(task_errors.values())
        avg_errors_per_task = total_errors / len(error_metrics)
        
        if avg_errors_per_task > 2:
            insights.append("High error density detected")
            recommendations.append("Implement comprehensive error prevention strategies")
        
        # Recent error spike detection
        recent_errors = [m for m in error_metrics if m.timestamp > time.time() - 1800]  # Last 30 minutes
        if len(recent_errors) > len(error_metrics) * 0.6:
            insights.append("Recent spike in errors detected")
            recommendations.append("Investigate immediate environmental or system issues")
        
        confidence_score = min(1.0, len(error_metrics) / 8)
        
        return ReflectionResult(
            reflection_type=ReflectionType.ERROR_PATTERN,
            insights=insights,
            recommendations=recommendations,
            confidence_score=confidence_score,
            supporting_data=supporting_data
        )
    
    def get_top_insights(self, limit: int = 5) -> List[str]:
        """Get top insights from recent reflections"""
        if not self.reflection_history:
            return []
        
        # Sort by confidence score and recency
        recent_reflections = sorted(
            self.reflection_history[-20:],  # Last 20 reflections
            key=lambda r: (r.confidence_score, r.timestamp),
            reverse=True
        )
        
        insights = []
        for reflection in recent_reflections:
            insights.extend(reflection.insights)
            if len(insights) >= limit:
                break
        
        return insights[:limit]
    
    def get_top_recommendations(self, limit: int = 3) -> List[str]:
        """Get top recommendations from recent reflections"""
        if not self.reflection_history:
            return []
        
        # Sort by confidence score and recency
        recent_reflections = sorted(
            self.reflection_history[-15:],  # Last 15 reflections
            key=lambda r: (r.confidence_score, r.timestamp),
            reverse=True
        )
        
        recommendations = []
        seen_recommendations = set()
        
        for reflection in recent_reflections:
            for rec in reflection.recommendations:
                if rec not in seen_recommendations:
                    recommendations.append(rec)
                    seen_recommendations.add(rec)
                    if len(recommendations) >= limit:
                        return recommendations
        
        return recommendations
    
    def export_reflections(self, filepath: str):
        """Export reflection history to JSON file"""
        data = {
            'reflections': [asdict(r) for r in self.reflection_history],
            'export_timestamp': time.time()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Reflections exported to {filepath}")
    
    def load_reflections(self, filepath: str):
        """Load reflection history from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.reflection_history = [
                ReflectionResult(**r) for r in data.get('reflections', [])
            ]
            
            logger.info(f"Reflections loaded from {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to load reflections: {e}")