"""Structured JSON Logger

Module ini menyediakan sistem logging terstruktur dengan format JSON
untuk observability dan debugging yang lebih baik.

Features:
- JSON structured logging
- Multiple log levels
- Context tracking
- Performance metrics
- Error tracking
- Session management
"""

import json
import logging
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum
import traceback
import threading
from contextlib import contextmanager

class LogLevel(Enum):
    """Log levels untuk structured logging"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class EventType(Enum):
    """Types of events yang bisa di-log"""
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"
    VOICE_INPUT = "voice_input"
    INTENT_PARSED = "intent_parsed"
    ACTION_EXECUTED = "action_executed"
    OFFICE_OPERATION = "office_operation"
    SECURITY_CHECK = "security_check"
    ERROR_OCCURRED = "error_occurred"
    PERFORMANCE_METRIC = "performance_metric"
    USER_INTERACTION = "user_interaction"
    SYSTEM_COMMAND = "system_command"
    FILE_OPERATION = "file_operation"

@dataclass
class LogEntry:
    """Structured log entry"""
    timestamp: str
    session_id: str
    event_type: str
    level: str
    message: str
    context: Dict[str, Any]
    duration_ms: Optional[float] = None
    error_details: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    component: Optional[str] = None
    trace_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=None)

class StructuredLogger:
    """Structured JSON logger dengan context tracking"""
    
    def __init__(self, log_dir: str = "logs", 
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5,
                 session_id: Optional[str] = None):
        """
        Args:
            log_dir: Directory untuk menyimpan log files
            max_file_size: Maximum size per log file
            backup_count: Number of backup files to keep
            session_id: Session ID, auto-generated if None
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.session_id = session_id or str(uuid.uuid4())
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        
        # Thread-local storage untuk context
        self._local = threading.local()
        
        # Setup file handlers
        self._setup_file_handlers()
        
        # Performance tracking
        self._operation_stack = []
        self._metrics = {
            "total_events": 0,
            "events_by_type": {},
            "events_by_level": {},
            "session_start": time.time()
        }
        
        # Log session start
        self.log_event(
            EventType.SYSTEM_START,
            "Structured logger initialized",
            LogLevel.INFO,
            {"session_id": self.session_id}
        )
    
    def _setup_file_handlers(self):
        """Setup rotating file handlers"""
        from logging.handlers import RotatingFileHandler
        
        # Main log file
        self.main_log_file = self.log_dir / f"agent_{datetime.now().strftime('%Y%m%d')}.jsonl"
        
        # Error log file
        self.error_log_file = self.log_dir / f"errors_{datetime.now().strftime('%Y%m%d')}.jsonl"
        
        # Performance log file
        self.perf_log_file = self.log_dir / f"performance_{datetime.now().strftime('%Y%m%d')}.jsonl"
    
    def _get_context(self) -> Dict[str, Any]:
        """Get current thread context"""
        if not hasattr(self._local, 'context'):
            self._local.context = {}
        return self._local.context
    
    def set_context(self, key: str, value: Any):
        """Set context value untuk current thread"""
        context = self._get_context()
        context[key] = value
    
    def clear_context(self):
        """Clear context untuk current thread"""
        if hasattr(self._local, 'context'):
            self._local.context = {}
    
    def log_event(self, event_type: EventType, message: str, 
                  level: LogLevel = LogLevel.INFO,
                  context: Optional[Dict[str, Any]] = None,
                  duration_ms: Optional[float] = None,
                  error_details: Optional[Dict[str, Any]] = None,
                  user_id: Optional[str] = None,
                  component: Optional[str] = None,
                  trace_id: Optional[str] = None):
        """Log structured event
        
        Args:
            event_type: Type of event
            message: Human-readable message
            level: Log level
            context: Additional context data
            duration_ms: Operation duration in milliseconds
            error_details: Error details if applicable
            user_id: User ID if applicable
            component: Component name
            trace_id: Trace ID for request tracking
        """
        # Merge context
        merged_context = self._get_context().copy()
        if context:
            merged_context.update(context)
        
        # Create log entry
        entry = LogEntry(
            timestamp=datetime.utcnow().isoformat() + "Z",
            session_id=self.session_id,
            event_type=event_type.value,
            level=level.value,
            message=message,
            context=merged_context,
            duration_ms=duration_ms,
            error_details=error_details,
            user_id=user_id,
            component=component,
            trace_id=trace_id
        )
        
        # Write to appropriate log files
        self._write_log_entry(entry)
        
        # Update metrics
        self._update_metrics(event_type, level)
    
    def _write_log_entry(self, entry: LogEntry):
        """Write log entry to files"""
        json_line = entry.to_json() + "\n"
        
        # Write to main log
        with open(self.main_log_file, "a", encoding="utf-8") as f:
            f.write(json_line)
        
        # Write to error log if error level
        if entry.level in ["error", "critical"]:
            with open(self.error_log_file, "a", encoding="utf-8") as f:
                f.write(json_line)
        
        # Write to performance log if has duration
        if entry.duration_ms is not None:
            with open(self.perf_log_file, "a", encoding="utf-8") as f:
                f.write(json_line)
    
    def _update_metrics(self, event_type: EventType, level: LogLevel):
        """Update internal metrics"""
        self._metrics["total_events"] += 1
        
        # Count by type
        type_key = event_type.value
        self._metrics["events_by_type"][type_key] = \
            self._metrics["events_by_type"].get(type_key, 0) + 1
        
        # Count by level
        level_key = level.value
        self._metrics["events_by_level"][level_key] = \
            self._metrics["events_by_level"].get(level_key, 0) + 1
    
    @contextmanager
    def operation_timer(self, operation_name: str, 
                       event_type: EventType = EventType.PERFORMANCE_METRIC,
                       context: Optional[Dict[str, Any]] = None):
        """Context manager untuk timing operations
        
        Usage:
            with logger.operation_timer("file_processing"):
                # do work
                pass
        """
        start_time = time.time()
        operation_id = str(uuid.uuid4())
        
        # Set trace context
        self.set_context("operation_id", operation_id)
        self.set_context("operation_name", operation_name)
        
        self._operation_stack.append({
            "name": operation_name,
            "start_time": start_time,
            "operation_id": operation_id
        })
        
        try:
            yield operation_id
        except Exception as e:
            # Log error with timing
            duration_ms = (time.time() - start_time) * 1000
            self.log_error(
                f"Operation '{operation_name}' failed",
                e,
                context={"operation_name": operation_name, "operation_id": operation_id},
                duration_ms=duration_ms
            )
            raise
        finally:
            # Log completion
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            
            if self._operation_stack:
                self._operation_stack.pop()
            
            merged_context = {"operation_name": operation_name, "operation_id": operation_id}
            if context:
                merged_context.update(context)
            
            self.log_event(
                event_type,
                f"Operation '{operation_name}' completed",
                LogLevel.INFO,
                context=merged_context,
                duration_ms=duration_ms
            )
    
    def log_voice_input(self, text: str, confidence: float, 
                       duration_ms: float, method: str = "whisper"):
        """Log voice input event"""
        self.log_event(
            EventType.VOICE_INPUT,
            f"Voice input received: '{text[:50]}...' (confidence: {confidence:.2f})",
            LogLevel.INFO,
            {
                "text": text,
                "confidence": confidence,
                "method": method,
                "text_length": len(text)
            },
            duration_ms=duration_ms
        )
    
    def log_intent_parsed(self, intent_type: str, confidence: float,
                         parameters: Dict[str, Any], raw_text: str):
        """Log intent parsing event"""
        self.log_event(
            EventType.INTENT_PARSED,
            f"Intent parsed: {intent_type} (confidence: {confidence:.2f})",
            LogLevel.INFO,
            {
                "intent_type": intent_type,
                "confidence": confidence,
                "parameters": parameters,
                "raw_text": raw_text
            }
        )
    
    def log_action_executed(self, action_type: str, success: bool,
                           parameters: Dict[str, Any], 
                           result: Optional[Dict[str, Any]] = None,
                           duration_ms: Optional[float] = None):
        """Log action execution event"""
        level = LogLevel.INFO if success else LogLevel.ERROR
        status = "success" if success else "failed"
        
        self.log_event(
            EventType.ACTION_EXECUTED,
            f"Action {action_type} {status}",
            level,
            {
                "action_type": action_type,
                "success": success,
                "parameters": parameters,
                "result": result
            },
            duration_ms=duration_ms
        )
    
    def log_office_operation(self, app: str, operation: str, 
                           file_path: Optional[str] = None,
                           success: bool = True,
                           duration_ms: Optional[float] = None):
        """Log Office automation event"""
        level = LogLevel.INFO if success else LogLevel.ERROR
        
        self.log_event(
            EventType.OFFICE_OPERATION,
            f"Office {app} operation: {operation}",
            level,
            {
                "application": app,
                "operation": operation,
                "file_path": file_path,
                "success": success
            },
            duration_ms=duration_ms
        )
    
    def log_security_check(self, action_type: str, allowed: bool,
                          reason: str, security_level: str,
                          parameters: Dict[str, Any]):
        """Log security check event"""
        level = LogLevel.WARNING if not allowed else LogLevel.INFO
        
        self.log_event(
            EventType.SECURITY_CHECK,
            f"Security check: {action_type} {'allowed' if allowed else 'blocked'}",
            level,
            {
                "action_type": action_type,
                "allowed": allowed,
                "reason": reason,
                "security_level": security_level,
                "parameters": parameters
            }
        )
    
    def log_error(self, message: str, exception: Exception,
                  context: Optional[Dict[str, Any]] = None,
                  duration_ms: Optional[float] = None):
        """Log error dengan exception details"""
        error_details = {
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
            "traceback": traceback.format_exc()
        }
        
        self.log_event(
            EventType.ERROR_OCCURRED,
            message,
            LogLevel.ERROR,
            context=context,
            duration_ms=duration_ms,
            error_details=error_details
        )
    
    def log_user_interaction(self, interaction_type: str, 
                           details: Dict[str, Any]):
        """Log user interaction event"""
        self.log_event(
            EventType.USER_INTERACTION,
            f"User interaction: {interaction_type}",
            LogLevel.INFO,
            {
                "interaction_type": interaction_type,
                "details": details
            }
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        session_duration = time.time() - self._metrics["session_start"]
        
        return {
            **self._metrics,
            "session_duration_seconds": session_duration,
            "events_per_minute": self._metrics["total_events"] / (session_duration / 60) if session_duration > 0 else 0,
            "current_operations": [op["name"] for op in self._operation_stack]
        }
    
    def export_logs(self, start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None,
                   event_types: Optional[List[str]] = None,
                   levels: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Export logs dengan filtering
        
        Args:
            start_time: Filter start time
            end_time: Filter end time
            event_types: Filter by event types
            levels: Filter by log levels
            
        Returns:
            List of log entries
        """
        logs = []
        
        try:
            with open(self.main_log_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        
                        # Apply filters
                        if start_time and entry["timestamp"] < start_time.isoformat():
                            continue
                        if end_time and entry["timestamp"] > end_time.isoformat():
                            continue
                        if event_types and entry["event_type"] not in event_types:
                            continue
                        if levels and entry["level"] not in levels:
                            continue
                        
                        logs.append(entry)
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            pass
        
        return logs
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """Cleanup old log files
        
        Args:
            days_to_keep: Number of days to keep logs
        """
        cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
        
        for log_file in self.log_dir.glob("*.jsonl"):
            if log_file.stat().st_mtime < cutoff_time:
                log_file.unlink()
                self.log_event(
                    EventType.SYSTEM_START,
                    f"Cleaned up old log file: {log_file.name}",
                    LogLevel.INFO
                )
    
    def close(self):
        """Close logger dan log session end"""
        self.log_event(
            EventType.SYSTEM_STOP,
            "Structured logger closing",
            LogLevel.INFO,
            self.get_metrics()
        )

# Global logger instance
_global_logger: Optional[StructuredLogger] = None

def get_logger(log_dir: str = "logs") -> StructuredLogger:
    """Get global logger instance
    
    Args:
        log_dir: Directory untuk logs
        
    Returns:
        StructuredLogger instance
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = StructuredLogger(log_dir)
    return _global_logger

def set_global_logger(logger: StructuredLogger):
    """Set global logger instance
    
    Args:
        logger: StructuredLogger instance
    """
    global _global_logger
    _global_logger = logger

def close_global_logger():
    """Close global logger"""
    global _global_logger
    if _global_logger:
        _global_logger.close()
        _global_logger = None