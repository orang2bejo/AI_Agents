#!/usr/bin/env python3
"""
Agent Manager Module for Windows Use Autonomous Agent

Integrated AI agent management system for coordinating various AI agents
and task execution within the Jarvis AI ecosystem.

Author: Jarvis AI Team
Date: 2024
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class AgentType(Enum):
    """Types of AI agents"""
    VOICE_ASSISTANT = "voice_assistant"
    TASK_EXECUTOR = "task_executor"
    WEB_AUTOMATION = "web_automation"
    OFFICE_AUTOMATION = "office_automation"
    SYSTEM_MONITOR = "system_monitor"
    SECURITY_AGENT = "security_agent"
    LEARNING_AGENT = "learning_agent"
    CONVERSATION_AGENT = "conversation_agent"
    DECISION_MAKER = "decision_maker"
    COORDINATOR = "coordinator"

class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    INITIALIZING = "initializing"
    RUNNING = "running"
    BUSY = "busy"
    PAUSED = "paused"
    ERROR = "error"
    STOPPED = "stopped"
    MAINTENANCE = "maintenance"

class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5

class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

@dataclass
class AgentTask:
    """Task assigned to an agent"""
    task_id: str
    agent_type: AgentType
    task_type: str
    parameters: Dict[str, Any]
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    assigned_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    timeout_seconds: int = 300
    retry_count: int = 0
    max_retries: int = 3
    result: Optional[Any] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentCapability:
    """Agent capability definition"""
    name: str
    description: str
    input_types: List[str]
    output_types: List[str]
    required_permissions: List[str] = field(default_factory=list)
    estimated_duration: Optional[int] = None  # seconds
    resource_requirements: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentMetrics:
    """Agent performance metrics"""
    tasks_completed: int = 0
    tasks_failed: int = 0
    average_execution_time: float = 0.0
    success_rate: float = 0.0
    last_activity: Optional[datetime] = None
    uptime_seconds: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0

class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, agent_id: str, agent_type: AgentType, name: str, 
                 capabilities: List[AgentCapability] = None):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.name = name
        self.capabilities = capabilities or []
        self.status = AgentStatus.IDLE
        self.current_task: Optional[AgentTask] = None
        self.metrics = AgentMetrics()
        self.logger = logging.getLogger(f"{__name__}.{self.name}")
        self.created_at = datetime.now()
        self.config: Dict[str, Any] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
        
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the agent"""
        pass
    
    @abstractmethod
    async def execute_task(self, task: AgentTask) -> Any:
        """Execute a task"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> bool:
        """Cleanup agent resources"""
        pass
    
    def can_handle_task(self, task: AgentTask) -> bool:
        """Check if agent can handle the task"""
        if task.agent_type != self.agent_type:
            return False
        
        # Check capabilities
        for capability in self.capabilities:
            if capability.name == task.task_type:
                return True
        
        return False
    
    def add_event_handler(self, event: str, handler: Callable):
        """Add event handler"""
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)
    
    def emit_event(self, event: str, data: Any = None):
        """Emit event to handlers"""
        if event in self.event_handlers:
            for handler in self.event_handlers[event]:
                try:
                    handler(self, event, data)
                except Exception as e:
                    self.logger.error(f"Event handler error: {e}")
    
    def update_metrics(self, task_result: Any, execution_time: float, success: bool):
        """Update agent metrics"""
        if success:
            self.metrics.tasks_completed += 1
        else:
            self.metrics.tasks_failed += 1
        
        # Update average execution time
        total_tasks = self.metrics.tasks_completed + self.metrics.tasks_failed
        if total_tasks > 0:
            self.metrics.average_execution_time = (
                (self.metrics.average_execution_time * (total_tasks - 1) + execution_time) / total_tasks
            )
            self.metrics.success_rate = self.metrics.tasks_completed / total_tasks
        
        self.metrics.last_activity = datetime.now()
    
    def get_status_info(self) -> Dict[str, Any]:
        """Get agent status information"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "type": self.agent_type.value,
            "status": self.status.value,
            "current_task": self.current_task.task_id if self.current_task else None,
            "capabilities": [cap.name for cap in self.capabilities],
            "metrics": {
                "tasks_completed": self.metrics.tasks_completed,
                "tasks_failed": self.metrics.tasks_failed,
                "success_rate": self.metrics.success_rate,
                "average_execution_time": self.metrics.average_execution_time,
                "last_activity": self.metrics.last_activity.isoformat() if self.metrics.last_activity else None
            },
            "created_at": self.created_at.isoformat(),
            "uptime_seconds": (datetime.now() - self.created_at).total_seconds()
        }

class AgentManager:
    """Manager for coordinating multiple AI agents"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.agents: Dict[str, BaseAgent] = {}
        self.task_queue: List[AgentTask] = []
        self.completed_tasks: List[AgentTask] = []
        self.failed_tasks: List[AgentTask] = []
        self.logger = logging.getLogger(__name__)
        self.is_running = False
        self.task_assignment_lock = asyncio.Lock()
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # Configuration
        self.max_concurrent_tasks = self.config.get("max_concurrent_tasks", 10)
        self.task_timeout_default = self.config.get("task_timeout_default", 300)
        self.cleanup_interval = self.config.get("cleanup_interval", 3600)  # 1 hour
        self.metrics_update_interval = self.config.get("metrics_update_interval", 60)  # 1 minute
        
        # Start background tasks
        self._background_tasks: List[asyncio.Task] = []
    
    async def start(self):
        """Start the agent manager"""
        if self.is_running:
            return
        
        self.is_running = True
        self.logger.info("Starting Agent Manager")
        
        # Start background tasks
        self._background_tasks = [
            asyncio.create_task(self._task_assignment_loop()),
            asyncio.create_task(self._cleanup_loop()),
            asyncio.create_task(self._metrics_update_loop())
        ]
        
        # Initialize all agents
        for agent in self.agents.values():
            try:
                await agent.initialize()
                agent.status = AgentStatus.IDLE
                self.logger.info(f"Agent {agent.name} initialized successfully")
            except Exception as e:
                agent.status = AgentStatus.ERROR
                self.logger.error(f"Failed to initialize agent {agent.name}: {e}")
    
    async def stop(self):
        """Stop the agent manager"""
        if not self.is_running:
            return
        
        self.is_running = False
        self.logger.info("Stopping Agent Manager")
        
        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self._background_tasks, return_exceptions=True)
        
        # Cleanup all agents
        for agent in self.agents.values():
            try:
                await agent.cleanup()
                agent.status = AgentStatus.STOPPED
                self.logger.info(f"Agent {agent.name} stopped successfully")
            except Exception as e:
                self.logger.error(f"Failed to stop agent {agent.name}: {e}")
    
    def register_agent(self, agent: BaseAgent) -> bool:
        """Register a new agent"""
        if agent.agent_id in self.agents:
            self.logger.warning(f"Agent {agent.agent_id} already registered")
            return False
        
        self.agents[agent.agent_id] = agent
        
        # Add event handlers
        agent.add_event_handler("task_started", self._on_agent_task_started)
        agent.add_event_handler("task_completed", self._on_agent_task_completed)
        agent.add_event_handler("task_failed", self._on_agent_task_failed)
        agent.add_event_handler("status_changed", self._on_agent_status_changed)
        
        self.logger.info(f"Agent {agent.name} registered successfully")
        return True
    
    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent"""
        if agent_id not in self.agents:
            return False
        
        agent = self.agents[agent_id]
        
        # Cancel current task if any
        if agent.current_task:
            agent.current_task.status = TaskStatus.CANCELLED
            self.failed_tasks.append(agent.current_task)
        
        del self.agents[agent_id]
        self.logger.info(f"Agent {agent.name} unregistered")
        return True
    
    async def assign_task(self, task: AgentTask) -> bool:
        """Assign a task to an appropriate agent"""
        async with self.task_assignment_lock:
            # Find available agent that can handle the task
            suitable_agents = [
                agent for agent in self.agents.values()
                if (agent.status == AgentStatus.IDLE and 
                    agent.can_handle_task(task))
            ]
            
            if not suitable_agents:
                # Add to queue if no suitable agent available
                self.task_queue.append(task)
                self.logger.info(f"Task {task.task_id} queued (no available agents)")
                return False
            
            # Select best agent (simple strategy: least loaded)
            best_agent = min(suitable_agents, 
                           key=lambda a: a.metrics.tasks_completed + a.metrics.tasks_failed)
            
            # Assign task
            task.assigned_at = datetime.now()
            task.status = TaskStatus.ASSIGNED
            best_agent.current_task = task
            best_agent.status = AgentStatus.BUSY
            
            # Execute task in background
            asyncio.create_task(self._execute_agent_task(best_agent, task))
            
            self.logger.info(f"Task {task.task_id} assigned to agent {best_agent.name}")
            return True
    
    async def _execute_agent_task(self, agent: BaseAgent, task: AgentTask):
        """Execute task on agent"""
        start_time = datetime.now()
        task.started_at = start_time
        task.status = TaskStatus.IN_PROGRESS
        
        agent.emit_event("task_started", task)
        
        try:
            # Set timeout
            result = await asyncio.wait_for(
                agent.execute_task(task),
                timeout=task.timeout_seconds
            )
            
            # Task completed successfully
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            
            execution_time = (task.completed_at - start_time).total_seconds()
            agent.update_metrics(result, execution_time, True)
            
            self.completed_tasks.append(task)
            agent.emit_event("task_completed", task)
            
            self.logger.info(f"Task {task.task_id} completed successfully")
            
        except asyncio.TimeoutError:
            task.status = TaskStatus.TIMEOUT
            task.error_message = "Task execution timeout"
            task.completed_at = datetime.now()
            
            execution_time = (task.completed_at - start_time).total_seconds()
            agent.update_metrics(None, execution_time, False)
            
            self.failed_tasks.append(task)
            agent.emit_event("task_failed", task)
            
            self.logger.warning(f"Task {task.task_id} timed out")
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.now()
            
            execution_time = (task.completed_at - start_time).total_seconds()
            agent.update_metrics(None, execution_time, False)
            
            self.failed_tasks.append(task)
            agent.emit_event("task_failed", task)
            
            self.logger.error(f"Task {task.task_id} failed: {e}")
        
        finally:
            # Reset agent status
            agent.current_task = None
            agent.status = AgentStatus.IDLE
            agent.emit_event("status_changed", agent.status)
    
    async def _task_assignment_loop(self):
        """Background loop for task assignment"""
        while self.is_running:
            try:
                if self.task_queue:
                    # Try to assign queued tasks
                    tasks_to_remove = []
                    for task in self.task_queue:
                        if await self.assign_task(task):
                            tasks_to_remove.append(task)
                    
                    # Remove assigned tasks from queue
                    for task in tasks_to_remove:
                        self.task_queue.remove(task)
                
                await asyncio.sleep(1)  # Check every second
                
            except Exception as e:
                self.logger.error(f"Task assignment loop error: {e}")
                await asyncio.sleep(5)
    
    async def _cleanup_loop(self):
        """Background loop for cleanup"""
        while self.is_running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                
                # Cleanup old completed/failed tasks
                cutoff_time = datetime.now() - timedelta(hours=24)
                
                self.completed_tasks = [
                    task for task in self.completed_tasks
                    if task.completed_at and task.completed_at > cutoff_time
                ]
                
                self.failed_tasks = [
                    task for task in self.failed_tasks
                    if task.completed_at and task.completed_at > cutoff_time
                ]
                
                self.logger.info("Cleanup completed")
                
            except Exception as e:
                self.logger.error(f"Cleanup loop error: {e}")
    
    async def _metrics_update_loop(self):
        """Background loop for metrics updates"""
        while self.is_running:
            try:
                await asyncio.sleep(self.metrics_update_interval)
                
                # Update system metrics for all agents
                for agent in self.agents.values():
                    # Update uptime
                    agent.metrics.uptime_seconds = (
                        datetime.now() - agent.created_at
                    ).total_seconds()
                
                # Emit metrics update event
                self.emit_event("metrics_updated", self.get_system_metrics())
                
            except Exception as e:
                self.logger.error(f"Metrics update loop error: {e}")
    
    def create_task(self, agent_type: AgentType, task_type: str, 
                   parameters: Dict[str, Any], priority: TaskPriority = TaskPriority.NORMAL,
                   timeout_seconds: int = None) -> AgentTask:
        """Create a new task"""
        task = AgentTask(
            task_id=str(uuid.uuid4()),
            agent_type=agent_type,
            task_type=task_type,
            parameters=parameters,
            priority=priority,
            timeout_seconds=timeout_seconds or self.task_timeout_default
        )
        
        return task
    
    async def submit_task(self, agent_type: AgentType, task_type: str,
                         parameters: Dict[str, Any], priority: TaskPriority = TaskPriority.NORMAL,
                         timeout_seconds: int = None) -> str:
        """Submit a task for execution"""
        task = self.create_task(agent_type, task_type, parameters, priority, timeout_seconds)
        
        # Try immediate assignment
        if not await self.assign_task(task):
            # Task was queued
            pass
        
        return task.task_id
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status"""
        # Check all task lists
        all_tasks = (
            self.task_queue + 
            [agent.current_task for agent in self.agents.values() if agent.current_task] +
            self.completed_tasks + 
            self.failed_tasks
        )
        
        for task in all_tasks:
            if task and task.task_id == task_id:
                return {
                    "task_id": task.task_id,
                    "status": task.status.value,
                    "agent_type": task.agent_type.value,
                    "task_type": task.task_type,
                    "priority": task.priority.value,
                    "created_at": task.created_at.isoformat(),
                    "assigned_at": task.assigned_at.isoformat() if task.assigned_at else None,
                    "started_at": task.started_at.isoformat() if task.started_at else None,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                    "result": task.result,
                    "error_message": task.error_message,
                    "retry_count": task.retry_count
                }
        
        return None
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics"""
        total_agents = len(self.agents)
        active_agents = len([a for a in self.agents.values() if a.status == AgentStatus.BUSY])
        idle_agents = len([a for a in self.agents.values() if a.status == AgentStatus.IDLE])
        error_agents = len([a for a in self.agents.values() if a.status == AgentStatus.ERROR])
        
        total_completed = len(self.completed_tasks)
        total_failed = len(self.failed_tasks)
        total_queued = len(self.task_queue)
        
        return {
            "agents": {
                "total": total_agents,
                "active": active_agents,
                "idle": idle_agents,
                "error": error_agents
            },
            "tasks": {
                "completed": total_completed,
                "failed": total_failed,
                "queued": total_queued,
                "success_rate": total_completed / (total_completed + total_failed) if (total_completed + total_failed) > 0 else 0
            },
            "system": {
                "is_running": self.is_running,
                "uptime_seconds": (datetime.now() - self.created_at).total_seconds() if hasattr(self, 'created_at') else 0
            }
        }
    
    def add_event_handler(self, event: str, handler: Callable):
        """Add system event handler"""
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)
    
    def emit_event(self, event: str, data: Any = None):
        """Emit system event"""
        if event in self.event_handlers:
            for handler in self.event_handlers[event]:
                try:
                    handler(self, event, data)
                except Exception as e:
                    self.logger.error(f"Event handler error: {e}")
    
    def _on_agent_task_started(self, agent: BaseAgent, event: str, task: AgentTask):
        """Handle agent task started event"""
        self.emit_event("agent_task_started", {"agent": agent, "task": task})
    
    def _on_agent_task_completed(self, agent: BaseAgent, event: str, task: AgentTask):
        """Handle agent task completed event"""
        self.emit_event("agent_task_completed", {"agent": agent, "task": task})
    
    def _on_agent_task_failed(self, agent: BaseAgent, event: str, task: AgentTask):
        """Handle agent task failed event"""
        self.emit_event("agent_task_failed", {"agent": agent, "task": task})
    
    def _on_agent_status_changed(self, agent: BaseAgent, event: str, status: AgentStatus):
        """Handle agent status changed event"""
        self.emit_event("agent_status_changed", {"agent": agent, "status": status})
    
    def get_agent_list(self) -> List[Dict[str, Any]]:
        """Get list of all agents with their status"""
        return [agent.get_status_info() for agent in self.agents.values()]
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)

# Export main classes
__all__ = [
    'AgentManager',
    'BaseAgent',
    'AgentTask',
    'AgentCapability',
    'AgentMetrics',
    'AgentType',
    'AgentStatus',
    'TaskPriority',
    'TaskStatus'
]