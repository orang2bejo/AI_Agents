"""Task Coordinator Module

Coordinates and manages tasks within the Jarvis AI system,
including task scheduling, execution, monitoring, and dependency management.
"""

import asyncio
import logging
import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union, Set
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, Future

from pydantic import BaseModel

logger = logging.getLogger(__name__)

class TaskType(Enum):
    """Types of tasks"""
    VOICE_COMMAND = "voice_command"
    OFFICE_AUTOMATION = "office_automation"
    WEB_SEARCH = "web_search"
    SYSTEM_OPERATION = "system_operation"
    FILE_OPERATION = "file_operation"
    SCHEDULED = "scheduled"
    BACKGROUND = "background"
    USER_INTERACTION = "user_interaction"

class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5

class ExecutionMode(Enum):
    """Task execution modes"""
    SYNCHRONOUS = "sync"
    ASYNCHRONOUS = "async"
    BACKGROUND = "background"
    SCHEDULED = "scheduled"

@dataclass
class TaskResult:
    """Task execution result"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

@dataclass
class TaskDependency:
    """Task dependency definition"""
    task_id: str
    dependency_type: str = "completion"  # completion, data, condition
    condition: Optional[Callable] = None
    timeout: Optional[float] = None

class TaskConfig(BaseModel):
    """Task configuration"""
    # Execution settings
    max_concurrent_tasks: int = 10
    default_timeout: float = 300.0  # 5 minutes
    retry_attempts: int = 3
    retry_delay: float = 1.0
    
    # Queue settings
    max_queue_size: int = 1000
    priority_queue_enabled: bool = True
    
    # Monitoring
    enable_monitoring: bool = True
    log_task_details: bool = True
    performance_tracking: bool = True
    
    # Cleanup
    cleanup_completed_tasks: bool = True
    cleanup_interval: float = 3600.0  # 1 hour
    max_completed_history: int = 100

class Task:
    """Individual task representation"""
    
    def __init__(
        self,
        task_id: str = None,
        name: str = "",
        task_type: TaskType = TaskType.USER_INTERACTION,
        priority: TaskPriority = TaskPriority.NORMAL,
        execution_mode: ExecutionMode = ExecutionMode.SYNCHRONOUS,
        timeout: float = None,
        max_retries: int = 3,
        dependencies: List[TaskDependency] = None,
        metadata: Dict[str, Any] = None
    ):
        self.task_id = task_id or str(uuid.uuid4())
        self.name = name or f"Task_{self.task_id[:8]}"
        self.task_type = task_type
        self.priority = priority
        self.execution_mode = execution_mode
        self.timeout = timeout
        self.max_retries = max_retries
        self.dependencies = dependencies or []
        self.metadata = metadata or {}
        
        # Execution state
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.last_updated = datetime.now()
        
        # Execution details
        self.executor: Optional[Callable] = None
        self.args: tuple = ()
        self.kwargs: Dict[str, Any] = {}
        self.result: Optional[TaskResult] = None
        self.error: Optional[Exception] = None
        self.retry_count = 0
        
        # Progress tracking
        self.progress = 0.0  # 0.0 to 1.0
        self.progress_message = ""
        
        # Callbacks
        self.on_start: Optional[Callable] = None
        self.on_progress: Optional[Callable] = None
        self.on_complete: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        
        # Execution context
        self.execution_thread: Optional[threading.Thread] = None
        self.future: Optional[Future] = None
        self.cancel_event = threading.Event()
    
    def set_executor(self, executor: Callable, *args, **kwargs):
        """Set task executor function"""
        self.executor = executor
        self.args = args
        self.kwargs = kwargs
    
    def update_progress(self, progress: float, message: str = ""):
        """Update task progress"""
        self.progress = max(0.0, min(1.0, progress))
        self.progress_message = message
        self.last_updated = datetime.now()
        
        if self.on_progress:
            try:
                self.on_progress(self, progress, message)
            except Exception as e:
                logger.error(f"Error in progress callback for task {self.task_id}: {e}")
    
    def cancel(self):
        """Cancel task execution"""
        self.cancel_event.set()
        
        if self.future and not self.future.done():
            self.future.cancel()
        
        if self.status in [TaskStatus.PENDING, TaskStatus.QUEUED, TaskStatus.RUNNING]:
            self.status = TaskStatus.CANCELLED
            self.completed_at = datetime.now()
            self.last_updated = datetime.now()
    
    def is_ready_to_execute(self, completed_tasks: Set[str]) -> bool:
        """Check if task dependencies are satisfied"""
        for dependency in self.dependencies:
            if dependency.task_id not in completed_tasks:
                return False
            
            # Check condition if specified
            if dependency.condition and not dependency.condition():
                return False
        
        return True
    
    def get_execution_time(self) -> Optional[float]:
        """Get task execution time in seconds"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            'task_id': self.task_id,
            'name': self.name,
            'task_type': self.task_type.value,
            'priority': self.priority.value,
            'execution_mode': self.execution_mode.value,
            'status': self.status.value,
            'progress': self.progress,
            'progress_message': self.progress_message,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'execution_time': self.get_execution_time(),
            'retry_count': self.retry_count,
            'metadata': self.metadata,
            'result': self.result.__dict__ if self.result else None,
            'error': str(self.error) if self.error else None
        }

class TaskQueue:
    """Priority-based task queue"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.tasks: List[Task] = []
        self.lock = threading.RLock()
    
    def add_task(self, task: Task) -> bool:
        """Add task to queue"""
        with self.lock:
            if len(self.tasks) >= self.max_size:
                logger.warning(f"Task queue is full ({self.max_size}), rejecting task {task.task_id}")
                return False
            
            # Insert task based on priority
            inserted = False
            for i, existing_task in enumerate(self.tasks):
                if task.priority.value > existing_task.priority.value:
                    self.tasks.insert(i, task)
                    inserted = True
                    break
            
            if not inserted:
                self.tasks.append(task)
            
            task.status = TaskStatus.QUEUED
            task.last_updated = datetime.now()
            
            logger.debug(f"Task {task.task_id} added to queue (priority: {task.priority.value})")
            return True
    
    def get_next_task(self, completed_tasks: Set[str]) -> Optional[Task]:
        """Get next ready task from queue"""
        with self.lock:
            for i, task in enumerate(self.tasks):
                if task.is_ready_to_execute(completed_tasks):
                    return self.tasks.pop(i)
            return None
    
    def remove_task(self, task_id: str) -> bool:
        """Remove task from queue"""
        with self.lock:
            for i, task in enumerate(self.tasks):
                if task.task_id == task_id:
                    self.tasks.pop(i)
                    return True
            return False
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get tasks by status"""
        with self.lock:
            return [task for task in self.tasks if task.status == status]
    
    def get_queue_size(self) -> int:
        """Get current queue size"""
        with self.lock:
            return len(self.tasks)
    
    def clear(self):
        """Clear all tasks from queue"""
        with self.lock:
            self.tasks.clear()

class TaskCoordinator:
    """Main task coordination and management system"""
    
    def __init__(self, config: TaskConfig = None):
        self.config = config or TaskConfig()
        
        # Task storage
        self.tasks: Dict[str, Task] = {}
        self.task_queue = TaskQueue(self.config.max_queue_size)
        self.completed_tasks: Set[str] = set()
        
        # Execution management
        self.executor = ThreadPoolExecutor(max_workers=self.config.max_concurrent_tasks)
        self.running_tasks: Dict[str, Task] = {}
        self.scheduled_tasks: Dict[str, Task] = {}
        
        # Control
        self.is_running = False
        self.coordinator_thread: Optional[threading.Thread] = None
        self.scheduler_thread: Optional[threading.Thread] = None
        self.cleanup_thread: Optional[threading.Thread] = None
        
        # Callbacks
        self.on_task_start: Optional[Callable[[Task], None]] = None
        self.on_task_complete: Optional[Callable[[Task], None]] = None
        self.on_task_error: Optional[Callable[[Task, Exception], None]] = None
        
        # Statistics
        self.stats = {
            'tasks_created': 0,
            'tasks_completed': 0,
            'tasks_failed': 0,
            'tasks_cancelled': 0,
            'total_execution_time': 0.0,
            'average_execution_time': 0.0
        }
        
        # Locks
        self.tasks_lock = threading.RLock()
        
        logger.info("Task Coordinator initialized")
    
    def start(self):
        """Start task coordinator"""
        if self.is_running:
            logger.warning("Task coordinator is already running")
            return
        
        self.is_running = True
        
        # Start coordinator thread
        self.coordinator_thread = threading.Thread(target=self._coordinator_loop, daemon=True)
        self.coordinator_thread.start()
        
        # Start scheduler thread
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        # Start cleanup thread
        if self.config.cleanup_completed_tasks:
            self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
            self.cleanup_thread.start()
        
        logger.info("Task Coordinator started")
    
    def stop(self):
        """Stop task coordinator"""
        if not self.is_running:
            return
        
        logger.info("Stopping Task Coordinator...")
        
        self.is_running = False
        
        # Cancel all running tasks
        with self.tasks_lock:
            for task in self.running_tasks.values():
                task.cancel()
        
        # Wait for threads to finish
        threads = [self.coordinator_thread, self.scheduler_thread, self.cleanup_thread]
        for thread in threads:
            if thread and thread.is_alive():
                thread.join(timeout=5.0)
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("Task Coordinator stopped")
    
    def create_task(
        self,
        name: str,
        executor: Callable,
        *args,
        task_type: TaskType = TaskType.USER_INTERACTION,
        priority: TaskPriority = TaskPriority.NORMAL,
        execution_mode: ExecutionMode = ExecutionMode.SYNCHRONOUS,
        timeout: float = None,
        dependencies: List[TaskDependency] = None,
        metadata: Dict[str, Any] = None,
        **kwargs
    ) -> Task:
        """Create a new task"""
        task = Task(
            name=name,
            task_type=task_type,
            priority=priority,
            execution_mode=execution_mode,
            timeout=timeout or self.config.default_timeout,
            dependencies=dependencies,
            metadata=metadata
        )
        
        task.set_executor(executor, *args, **kwargs)
        
        with self.tasks_lock:
            self.tasks[task.task_id] = task
            self.stats['tasks_created'] += 1
        
        logger.info(f"Task created: {task.name} ({task.task_id})")
        return task
    
    def submit_task(self, task: Task) -> bool:
        """Submit task for execution"""
        if not self.is_running:
            logger.error("Task coordinator is not running")
            return False
        
        if task.execution_mode == ExecutionMode.SCHEDULED:
            # Add to scheduled tasks
            with self.tasks_lock:
                self.scheduled_tasks[task.task_id] = task
            logger.info(f"Task scheduled: {task.name} ({task.task_id})")
            return True
        else:
            # Add to execution queue
            success = self.task_queue.add_task(task)
            if success:
                logger.info(f"Task queued: {task.name} ({task.task_id})")
            return success
    
    def execute_task_sync(self, task: Task) -> TaskResult:
        """Execute task synchronously"""
        if not task.executor:
            error_msg = f"No executor set for task {task.task_id}"
            logger.error(error_msg)
            return TaskResult(success=False, error=error_msg)
        
        try:
            # Update task status
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            task.last_updated = datetime.now()
            
            # Call start callback
            if task.on_start:
                task.on_start(task)
            if self.on_task_start:
                self.on_task_start(task)
            
            start_time = time.time()
            
            # Execute task
            if asyncio.iscoroutinefunction(task.executor):
                # Async executor
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result_data = loop.run_until_complete(
                        asyncio.wait_for(
                            task.executor(*task.args, **task.kwargs),
                            timeout=task.timeout
                        )
                    )
                finally:
                    loop.close()
            else:
                # Sync executor
                result_data = task.executor(*task.args, **task.kwargs)
            
            execution_time = time.time() - start_time
            
            # Create result
            result = TaskResult(
                success=True,
                data=result_data,
                execution_time=execution_time
            )
            
            # Update task
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.last_updated = datetime.now()
            task.progress = 1.0
            
            # Update statistics
            with self.tasks_lock:
                self.stats['tasks_completed'] += 1
                self.stats['total_execution_time'] += execution_time
                self.stats['average_execution_time'] = (
                    self.stats['total_execution_time'] / self.stats['tasks_completed']
                )
                self.completed_tasks.add(task.task_id)
            
            # Call completion callbacks
            if task.on_complete:
                task.on_complete(task)
            if self.on_task_complete:
                self.on_task_complete(task)
            
            logger.info(f"Task completed: {task.name} ({execution_time:.2f}s)")
            return result
            
        except asyncio.TimeoutError:
            error_msg = f"Task {task.task_id} timed out after {task.timeout}s"
            logger.error(error_msg)
            
            task.status = TaskStatus.TIMEOUT
            task.completed_at = datetime.now()
            task.last_updated = datetime.now()
            task.error = TimeoutError(error_msg)
            
            result = TaskResult(success=False, error=error_msg)
            task.result = result
            
            with self.tasks_lock:
                self.stats['tasks_failed'] += 1
            
            return result
            
        except Exception as e:
            error_msg = f"Task {task.task_id} failed: {str(e)}"
            logger.error(error_msg)
            
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now()
            task.last_updated = datetime.now()
            task.error = e
            
            result = TaskResult(success=False, error=str(e))
            task.result = result
            
            # Call error callbacks
            if task.on_error:
                task.on_error(task, e)
            if self.on_task_error:
                self.on_task_error(task, e)
            
            with self.tasks_lock:
                self.stats['tasks_failed'] += 1
            
            return result
    
    def _coordinator_loop(self):
        """Main coordinator loop"""
        logger.info("Task coordinator loop started")
        
        while self.is_running:
            try:
                # Get next ready task
                task = self.task_queue.get_next_task(self.completed_tasks)
                
                if task:
                    # Check if we can run more tasks
                    if len(self.running_tasks) < self.config.max_concurrent_tasks:
                        self._execute_task_async(task)
                    else:
                        # Put task back in queue
                        self.task_queue.add_task(task)
                
                # Clean up completed async tasks
                self._cleanup_completed_async_tasks()
                
                time.sleep(0.1)  # Small delay to prevent excessive CPU usage
                
            except Exception as e:
                logger.error(f"Error in coordinator loop: {e}")
                time.sleep(1.0)
        
        logger.info("Task coordinator loop stopped")
    
    def _execute_task_async(self, task: Task):
        """Execute task asynchronously"""
        with self.tasks_lock:
            self.running_tasks[task.task_id] = task
        
        # Submit to thread pool
        future = self.executor.submit(self._execute_task_wrapper, task)
        task.future = future
        
        logger.debug(f"Task submitted for async execution: {task.name}")
    
    def _execute_task_wrapper(self, task: Task):
        """Wrapper for task execution with error handling"""
        try:
            return self.execute_task_sync(task)
        except Exception as e:
            logger.error(f"Unexpected error in task execution wrapper: {e}")
            task.status = TaskStatus.FAILED
            task.error = e
            return TaskResult(success=False, error=str(e))
        finally:
            # Remove from running tasks
            with self.tasks_lock:
                self.running_tasks.pop(task.task_id, None)
    
    def _cleanup_completed_async_tasks(self):
        """Clean up completed async tasks"""
        completed_task_ids = []
        
        with self.tasks_lock:
            for task_id, task in self.running_tasks.items():
                if task.future and task.future.done():
                    completed_task_ids.append(task_id)
        
        for task_id in completed_task_ids:
            with self.tasks_lock:
                task = self.running_tasks.pop(task_id, None)
                if task:
                    self.completed_tasks.add(task_id)
    
    def _scheduler_loop(self):
        """Scheduled tasks loop"""
        logger.info("Task scheduler loop started")
        
        while self.is_running:
            try:
                current_time = datetime.now()
                tasks_to_execute = []
                
                with self.tasks_lock:
                    for task_id, task in list(self.scheduled_tasks.items()):
                        # Check if task should be executed
                        # This is a simplified check - real implementation would
                        # handle various scheduling criteria
                        if self._should_execute_scheduled_task(task, current_time):
                            tasks_to_execute.append(task)
                            del self.scheduled_tasks[task_id]
                
                # Submit scheduled tasks
                for task in tasks_to_execute:
                    self.task_queue.add_task(task)
                
                time.sleep(1.0)  # Check every second
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(5.0)
        
        logger.info("Task scheduler loop stopped")
    
    def _should_execute_scheduled_task(self, task: Task, current_time: datetime) -> bool:
        """Check if scheduled task should be executed"""
        # Simplified scheduling logic
        # Real implementation would check cron expressions, intervals, etc.
        
        # For now, just check if task has a 'scheduled_time' in metadata
        scheduled_time = task.metadata.get('scheduled_time')
        if scheduled_time and isinstance(scheduled_time, datetime):
            return current_time >= scheduled_time
        
        return False
    
    def _cleanup_loop(self):
        """Cleanup completed tasks loop"""
        logger.info("Task cleanup loop started")
        
        while self.is_running:
            try:
                self._cleanup_completed_tasks()
                time.sleep(self.config.cleanup_interval)
                
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                time.sleep(60.0)
        
        logger.info("Task cleanup loop stopped")
    
    def _cleanup_completed_tasks(self):
        """Clean up old completed tasks"""
        with self.tasks_lock:
            completed_tasks = [
                task for task in self.tasks.values()
                if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
            ]
            
            # Sort by completion time
            completed_tasks.sort(key=lambda t: t.completed_at or datetime.min)
            
            # Keep only the most recent tasks
            if len(completed_tasks) > self.config.max_completed_history:
                tasks_to_remove = completed_tasks[:-self.config.max_completed_history]
                
                for task in tasks_to_remove:
                    self.tasks.pop(task.task_id, None)
                    self.completed_tasks.discard(task.task_id)
                
                logger.info(f"Cleaned up {len(tasks_to_remove)} old completed tasks")
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        with self.tasks_lock:
            return self.tasks.get(task_id)
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get tasks by status"""
        with self.tasks_lock:
            return [task for task in self.tasks.values() if task.status == status]
    
    def get_tasks_by_type(self, task_type: TaskType) -> List[Task]:
        """Get tasks by type"""
        with self.tasks_lock:
            return [task for task in self.tasks.values() if task.task_type == task_type]
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task"""
        with self.tasks_lock:
            task = self.tasks.get(task_id)
            if not task:
                return False
            
            task.cancel()
            
            # Remove from queue if queued
            self.task_queue.remove_task(task_id)
            
            # Remove from running tasks
            self.running_tasks.pop(task_id, None)
            
            # Remove from scheduled tasks
            self.scheduled_tasks.pop(task_id, None)
            
            self.stats['tasks_cancelled'] += 1
            
            logger.info(f"Task cancelled: {task.name} ({task_id})")
            return True
    
    def pause_task(self, task_id: str) -> bool:
        """Pause a task (if supported)"""
        with self.tasks_lock:
            task = self.tasks.get(task_id)
            if not task or task.status != TaskStatus.RUNNING:
                return False
            
            task.status = TaskStatus.PAUSED
            task.last_updated = datetime.now()
            
            logger.info(f"Task paused: {task.name} ({task_id})")
            return True
    
    def resume_task(self, task_id: str) -> bool:
        """Resume a paused task"""
        with self.tasks_lock:
            task = self.tasks.get(task_id)
            if not task or task.status != TaskStatus.PAUSED:
                return False
            
            # Re-queue the task
            task.status = TaskStatus.PENDING
            task.last_updated = datetime.now()
            
            success = self.task_queue.add_task(task)
            if success:
                logger.info(f"Task resumed: {task.name} ({task_id})")
            
            return success
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get task coordinator statistics"""
        with self.tasks_lock:
            queue_size = self.task_queue.get_queue_size()
            running_count = len(self.running_tasks)
            scheduled_count = len(self.scheduled_tasks)
            
            return {
                **self.stats,
                'queue_size': queue_size,
                'running_tasks': running_count,
                'scheduled_tasks': scheduled_count,
                'total_tasks': len(self.tasks),
                'completed_tasks_count': len(self.completed_tasks),
                'is_running': self.is_running
            }
    
    def get_task_summary(self) -> Dict[str, Any]:
        """Get summary of all tasks"""
        with self.tasks_lock:
            summary = {
                'total': len(self.tasks),
                'by_status': {},
                'by_type': {},
                'by_priority': {}
            }
            
            for task in self.tasks.values():
                # Count by status
                status = task.status.value
                summary['by_status'][status] = summary['by_status'].get(status, 0) + 1
                
                # Count by type
                task_type = task.task_type.value
                summary['by_type'][task_type] = summary['by_type'].get(task_type, 0) + 1
                
                # Count by priority
                priority = task.priority.value
                summary['by_priority'][priority] = summary['by_priority'].get(priority, 0) + 1
            
            return summary
    
    def export_tasks(self, include_completed: bool = True) -> List[Dict[str, Any]]:
        """Export tasks data"""
        with self.tasks_lock:
            tasks_data = []
            
            for task in self.tasks.values():
                if not include_completed and task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                    continue
                
                tasks_data.append(task.to_dict())
            
            return tasks_data
    
    def clear_completed_tasks(self):
        """Clear all completed tasks"""
        with self.tasks_lock:
            completed_task_ids = [
                task_id for task_id, task in self.tasks.items()
                if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
            ]
            
            for task_id in completed_task_ids:
                self.tasks.pop(task_id, None)
                self.completed_tasks.discard(task_id)
            
            logger.info(f"Cleared {len(completed_task_ids)} completed tasks")

# Utility functions for common task patterns
def create_voice_command_task(
    coordinator: TaskCoordinator,
    command_text: str,
    handler: Callable,
    priority: TaskPriority = TaskPriority.HIGH
) -> Task:
    """Create a voice command task"""
    return coordinator.create_task(
        name=f"Voice Command: {command_text[:50]}",
        executor=handler,
        task_type=TaskType.VOICE_COMMAND,
        priority=priority,
        metadata={'command_text': command_text}
    )

def create_scheduled_task(
    coordinator: TaskCoordinator,
    name: str,
    executor: Callable,
    scheduled_time: datetime,
    *args,
    **kwargs
) -> Task:
    """Create a scheduled task"""
    task = coordinator.create_task(
        name=name,
        executor=executor,
        *args,
        task_type=TaskType.SCHEDULED,
        execution_mode=ExecutionMode.SCHEDULED,
        metadata={'scheduled_time': scheduled_time},
        **kwargs
    )
    return task

def create_background_task(
    coordinator: TaskCoordinator,
    name: str,
    executor: Callable,
    *args,
    **kwargs
) -> Task:
    """Create a background task"""
    return coordinator.create_task(
        name=name,
        executor=executor,
        *args,
        task_type=TaskType.BACKGROUND,
        execution_mode=ExecutionMode.BACKGROUND,
        priority=TaskPriority.LOW,
        **kwargs
    )

# Example usage
if __name__ == "__main__":
    import random
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create task coordinator
    coordinator = TaskCoordinator()
    coordinator.start()
    
    # Example task functions
    def example_task(name: str, duration: float = 1.0):
        """Example task that simulates work"""
        logger.info(f"Starting task: {name}")
        time.sleep(duration)
        result = f"Task {name} completed after {duration}s"
        logger.info(result)
        return result
    
    async def example_async_task(name: str, duration: float = 1.0):
        """Example async task"""
        logger.info(f"Starting async task: {name}")
        await asyncio.sleep(duration)
        result = f"Async task {name} completed after {duration}s"
        logger.info(result)
        return result
    
    def failing_task(name: str):
        """Example task that fails"""
        logger.info(f"Starting failing task: {name}")
        raise Exception(f"Task {name} failed intentionally")
    
    try:
        # Create and submit various tasks
        tasks = []
        
        # Regular tasks
        for i in range(5):
            task = coordinator.create_task(
                name=f"task_{i+1}",
                executor=example_task,
                delay=random.uniform(0.5, 2.0),
                priority=TaskPriority(random.randint(1, 3))
            )
            tasks.append(task)
            coordinator.submit_task(task)
        
        # Async tasks
        for i in range(3):
            task = coordinator.create_task(
                name=f"async_task_{i+1}",
                executor=example_async_task,
                delay=random.uniform(0.5, 1.5),
                priority=TaskPriority.HIGH
            )
            tasks.append(task)
            coordinator.submit_task(task)
        
        # Failing task
        failing_task_obj = coordinator.create_task(
            name="Failing Task",
            executor=failing_task,
            priority=TaskPriority.NORMAL
        )
        tasks.append(failing_task_obj)
        coordinator.submit_task(failing_task_obj)
        
        # Wait for tasks to complete
        time.sleep(10)
        
        # Print statistics
        stats = coordinator.get_statistics()
        print("\nTask Coordinator Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Print task summary
        summary = coordinator.get_task_summary()
        print("\nTask Summary:")
        for category, data in summary.items():
            print(f"  {category}: {data}")
        
    finally:
        # Stop coordinator
        coordinator.stop()