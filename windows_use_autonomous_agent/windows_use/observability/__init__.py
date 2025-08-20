"""Observability Package

Package ini menyediakan sistem observability lengkap untuk Windows Use Autonomous Agent.
Termasuk structured logging, screenshot capture, dan monitoring untuk debugging dan analisis.

Modules:
- logger: Structured JSON logging dengan context tracking
- screenshot: Screenshot capture dengan berbagai mode dan optimisasi

Features:
- JSON structured logging
- Automatic screenshot capture
- Performance metrics
- Context tracking
- Error monitoring
- Session management

Usage:
    from windows_use.observability import get_logger, get_screenshot_capture
    from windows_use.observability import LogLevel, EventType, CaptureMode, TriggerEvent
    
    # Initialize components
    logger = get_logger()
    capture = get_screenshot_capture()
    
    # Log events
    logger.log_event(
        EventType.ACTION_EXECUTED,
        "File operation completed",
        LogLevel.INFO,
        {"file_path": "document.txt", "operation": "read"}
    )
    
    # Capture screenshots
    metadata = capture.capture_screenshot(
        mode=CaptureMode.ACTIVE_WINDOW,
        trigger_event=TriggerEvent.ACTION_EXECUTED,
        context={"operation": "file_read"}
    )
    
    # Use context managers for automatic tracking
    with logger.operation_timer("file_processing"):
        with capture.capture_context("file_operation"):
            # do work
            pass
"""

from typing import Dict, Any, Optional, List
import logging

try:
    from .logger import (
        StructuredLogger,
        LogEntry,
        LogLevel,
        EventType,
        get_logger,
        set_global_logger,
        close_global_logger
    )
    LOGGER_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Logger module not available: {e}")
    LOGGER_AVAILABLE = False
    
    # Create dummy classes for graceful degradation
    class StructuredLogger:
        def __init__(self, *args, **kwargs):
            raise ImportError("Logger dependencies not available")
    
    LogEntry = None
    LogLevel = None
    EventType = None
    get_logger = None
    set_global_logger = None
    close_global_logger = None

try:
    from .screenshot import (
        ScreenshotCapture,
        ScreenshotMetadata,
        CaptureMode,
        TriggerEvent,
        get_screenshot_capture,
        set_global_capture,
        get_capture_capabilities
    )
    SCREENSHOT_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Screenshot module not available: {e}")
    SCREENSHOT_AVAILABLE = False
    
    # Create dummy classes for graceful degradation
    class ScreenshotCapture:
        def __init__(self, *args, **kwargs):
            raise ImportError("Screenshot dependencies not available")
    
    ScreenshotMetadata = None
    CaptureMode = None
    TriggerEvent = None
    get_screenshot_capture = None
    set_global_capture = None
    get_capture_capabilities = None

class ObservabilityManager:
    """Unified observability manager yang menggabungkan logging dan screenshot"""
    
    def __init__(self, log_dir: str = "logs", 
                 screenshot_dir: str = "screenshots",
                 session_id: Optional[str] = None,
                 enable_auto_screenshot: bool = True,
                 screenshot_events: Optional[List[str]] = None):
        """
        Args:
            log_dir: Directory untuk log files
            screenshot_dir: Directory untuk screenshots
            session_id: Session ID untuk tracking
            enable_auto_screenshot: Enable automatic screenshot capture
            screenshot_events: Events yang trigger auto screenshot
        """
        if not LOGGER_AVAILABLE:
            raise ImportError("Logger dependencies not available")
        
        self.session_id = session_id
        
        # Initialize logger
        self.logger = StructuredLogger(
            log_dir=log_dir,
            session_id=session_id
        )
        
        # Initialize screenshot capture if available
        self.screenshot_capture = None
        if SCREENSHOT_AVAILABLE:
            try:
                self.screenshot_capture = ScreenshotCapture(
                    output_dir=screenshot_dir
                )
                
                # Enable auto capture if requested
                if enable_auto_screenshot and screenshot_events:
                    events = []
                    for event_name in screenshot_events:
                        try:
                            event = TriggerEvent(event_name)
                            events.append(event)
                        except ValueError:
                            continue
                    
                    if events:
                        self.screenshot_capture.enable_auto_capture(events)
                        
            except Exception as e:
                logging.warning(f"Failed to initialize screenshot capture: {e}")
                self.screenshot_capture = None
        
        # Observability statistics
        self.stats = {
            "session_start": self.logger._metrics["session_start"],
            "total_operations": 0,
            "operations_with_screenshots": 0,
            "errors_captured": 0
        }
    
    def log_and_capture(self, event_type: EventType, message: str,
                       level: LogLevel = LogLevel.INFO,
                       context: Optional[Dict[str, Any]] = None,
                       capture_screenshot: bool = False,
                       capture_mode: Optional[CaptureMode] = None,
                       duration_ms: Optional[float] = None,
                       error_details: Optional[Dict[str, Any]] = None):
        """Log event dan capture screenshot jika diperlukan
        
        Args:
            event_type: Type of event
            message: Log message
            level: Log level
            context: Additional context
            capture_screenshot: Whether to capture screenshot
            capture_mode: Screenshot capture mode
            duration_ms: Operation duration
            error_details: Error details if applicable
        """
        # Log event
        self.logger.log_event(
            event_type=event_type,
            message=message,
            level=level,
            context=context,
            duration_ms=duration_ms,
            error_details=error_details,
            user_id=None,
            component=None,
            trace_id=None
        )
        
        # Capture screenshot if requested and available
        screenshot_metadata = None
        if capture_screenshot and self.screenshot_capture:
            try:
                # Map event type to trigger event
                trigger_event = self._map_event_to_trigger(event_type)
                
                screenshot_metadata = self.screenshot_capture.capture_screenshot(
                    mode=capture_mode or CaptureMode.FULL_SCREEN,
                    trigger_event=trigger_event,
                    context=context,
                    session_id=self.session_id
                )
                
                if screenshot_metadata:
                    self.stats["operations_with_screenshots"] += 1
                    
            except Exception as e:
                self.logger.log_error(
                    "Failed to capture screenshot",
                    e,
                    context={"original_event": event_type.value}
                )
        
        # Update stats
        self.stats["total_operations"] += 1
        if level in [LogLevel.ERROR, LogLevel.CRITICAL]:
            self.stats["errors_captured"] += 1
        
        return screenshot_metadata
    
    def _map_event_to_trigger(self, event_type: EventType) -> TriggerEvent:
        """Map EventType to TriggerEvent"""
        mapping = {
            EventType.ERROR_OCCURRED: TriggerEvent.ERROR_OCCURRED,
            EventType.ACTION_EXECUTED: TriggerEvent.ACTION_EXECUTED,
            EventType.OFFICE_OPERATION: TriggerEvent.OFFICE_OPERATION,
            EventType.SECURITY_CHECK: TriggerEvent.SECURITY_ALERT,
            EventType.USER_INTERACTION: TriggerEvent.USER_INTERACTION,
            EventType.SYSTEM_COMMAND: TriggerEvent.ACTION_EXECUTED,
            EventType.FILE_OPERATION: TriggerEvent.ACTION_EXECUTED
        }
        return mapping.get(event_type, TriggerEvent.MANUAL)
    
    def log_voice_input(self, text: str, confidence: float, 
                       duration_ms: float, method: str = "whisper",
                       capture_screenshot: bool = False):
        """Log voice input dengan optional screenshot"""
        self.logger.log_voice_input(text, confidence, duration_ms, method)
        
        if capture_screenshot and self.screenshot_capture:
            self.screenshot_capture.capture_screenshot(
                mode=CaptureMode.ACTIVE_WINDOW,
                trigger_event=TriggerEvent.USER_INTERACTION,
                context={
                    "voice_text": text[:100],  # Limit text length
                    "confidence": confidence,
                    "method": method
                },
                session_id=self.session_id
            )
    
    def log_intent_parsed(self, intent_type: str, confidence: float,
                         parameters: Dict[str, Any], raw_text: str,
                         capture_screenshot: bool = False):
        """Log intent parsing dengan optional screenshot"""
        self.logger.log_intent_parsed(intent_type, confidence, parameters, raw_text)
        
        if capture_screenshot and self.screenshot_capture:
            self.screenshot_capture.capture_screenshot(
                mode=CaptureMode.ACTIVE_WINDOW,
                trigger_event=TriggerEvent.USER_INTERACTION,
                context={
                    "intent_type": intent_type,
                    "confidence": confidence,
                    "raw_text": raw_text[:100]
                },
                session_id=self.session_id
            )
    
    def log_action_executed(self, action_type: str, success: bool,
                           parameters: Dict[str, Any], 
                           result: Optional[Dict[str, Any]] = None,
                           duration_ms: Optional[float] = None,
                           capture_screenshot: bool = True):
        """Log action execution dengan automatic screenshot"""
        self.logger.log_action_executed(
            action_type, success, parameters, result, duration_ms
        )
        
        # Auto capture for action execution
        if capture_screenshot and self.screenshot_capture:
            self.screenshot_capture.capture_screenshot(
                mode=CaptureMode.ACTIVE_WINDOW,
                trigger_event=TriggerEvent.ACTION_EXECUTED,
                context={
                    "action_type": action_type,
                    "success": success,
                    "parameters": parameters
                },
                session_id=self.session_id
            )
    
    def log_office_operation(self, app: str, operation: str, 
                           file_path: Optional[str] = None,
                           success: bool = True,
                           duration_ms: Optional[float] = None,
                           capture_screenshot: bool = True):
        """Log Office operation dengan automatic screenshot"""
        self.logger.log_office_operation(
            app, operation, file_path, success, duration_ms
        )
        
        # Auto capture for Office operations
        if capture_screenshot and self.screenshot_capture:
            self.screenshot_capture.capture_screenshot(
                mode=CaptureMode.ACTIVE_WINDOW,
                trigger_event=TriggerEvent.OFFICE_OPERATION,
                context={
                    "application": app,
                    "operation": operation,
                    "file_path": file_path
                },
                session_id=self.session_id
            )
    
    def log_error_with_screenshot(self, message: str, exception: Exception,
                                 context: Optional[Dict[str, Any]] = None,
                                 duration_ms: Optional[float] = None):
        """Log error dengan automatic screenshot capture"""
        self.logger.log_error(message, exception, context, duration_ms)
        
        # Always capture screenshot on errors
        if self.screenshot_capture:
            self.screenshot_capture.capture_screenshot(
                mode=CaptureMode.FULL_SCREEN,
                trigger_event=TriggerEvent.ERROR_OCCURRED,
                context={
                    "error_message": message,
                    "exception_type": type(exception).__name__,
                    "exception_message": str(exception),
                    **(context or {})
                },
                session_id=self.session_id
            )
    
    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive observability status
        
        Returns:
            Dictionary dengan status lengkap
        """
        status = {
            "session_id": self.session_id,
            "logger_available": LOGGER_AVAILABLE,
            "screenshot_available": SCREENSHOT_AVAILABLE,
            "statistics": self.stats
        }
        
        if LOGGER_AVAILABLE:
            status["logger_metrics"] = self.logger.get_metrics()
        
        if SCREENSHOT_AVAILABLE and self.screenshot_capture:
            status["screenshot_metrics"] = self.screenshot_capture.get_metrics()
            status["recent_screenshots"] = [
                meta.file_path for meta in 
                self.screenshot_capture.get_recent_screenshots(5)
            ]
        
        return status
    
    def export_session_data(self, include_screenshots: bool = True) -> Dict[str, Any]:
        """Export complete session data untuk analysis
        
        Args:
            include_screenshots: Include screenshot metadata
            
        Returns:
            Dictionary dengan session data lengkap
        """
        data = {
            "session_id": self.session_id,
            "statistics": self.stats,
            "logs": [],
            "screenshots": []
        }
        
        # Export logs
        if LOGGER_AVAILABLE:
            try:
                data["logs"] = self.logger.export_logs()
            except Exception:
                pass
        
        # Export screenshots
        if include_screenshots and SCREENSHOT_AVAILABLE and self.screenshot_capture:
            try:
                data["screenshots"] = self.screenshot_capture.export_metadata()
            except Exception:
                pass
        
        return data
    
    def cleanup_old_data(self, days_to_keep: int = 7):
        """Cleanup old logs dan screenshots
        
        Args:
            days_to_keep: Number of days to keep data
        """
        cleaned_logs = 0
        cleaned_screenshots = 0
        
        # Cleanup logs
        if LOGGER_AVAILABLE:
            try:
                self.logger.cleanup_old_logs(days_to_keep)
                cleaned_logs = 1  # Simplified count
            except Exception:
                pass
        
        # Cleanup screenshots
        if SCREENSHOT_AVAILABLE and self.screenshot_capture:
            try:
                cleaned_screenshots = self.screenshot_capture.cleanup_old_screenshots()
            except Exception:
                pass
        
        return {
            "cleaned_logs": cleaned_logs,
            "cleaned_screenshots": cleaned_screenshots
        }
    
    def close(self):
        """Close observability manager"""
        if LOGGER_AVAILABLE:
            self.logger.close()

def create_observability_manager(log_dir: str = "logs",
                                screenshot_dir: str = "screenshots",
                                session_id: Optional[str] = None,
                                enable_auto_screenshot: bool = True) -> ObservabilityManager:
    """Factory function untuk membuat ObservabilityManager
    
    Args:
        log_dir: Directory untuk logs
        screenshot_dir: Directory untuk screenshots
        session_id: Session ID
        enable_auto_screenshot: Enable automatic screenshots
        
    Returns:
        ObservabilityManager instance
        
    Raises:
        ImportError: Jika logger dependencies tidak tersedia
    """
    if not LOGGER_AVAILABLE:
        raise ImportError("Logger dependencies not available")
    
    # Default screenshot events
    screenshot_events = [
        "error_occurred",
        "action_executed", 
        "office_operation",
        "security_alert"
    ] if enable_auto_screenshot else []
    
    return ObservabilityManager(
        log_dir=log_dir,
        screenshot_dir=screenshot_dir,
        session_id=session_id,
        enable_auto_screenshot=enable_auto_screenshot,
        screenshot_events=screenshot_events
    )

def get_observability_capabilities() -> Dict[str, Any]:
    """Get informasi kemampuan observability system
    
    Returns:
        Dictionary dengan informasi capabilities
    """
    capabilities = {
        "logger_available": LOGGER_AVAILABLE,
        "screenshot_available": SCREENSHOT_AVAILABLE,
        "unified_manager_available": LOGGER_AVAILABLE
    }
    
    if LOGGER_AVAILABLE:
        capabilities["logger_features"] = [
            "JSON structured logging",
            "Context tracking",
            "Performance metrics",
            "Operation timing",
            "Error tracking",
            "Session management",
            "Log export",
            "Auto cleanup"
        ]
    
    if SCREENSHOT_AVAILABLE:
        try:
            capabilities["screenshot_features"] = get_capture_capabilities()
        except:
            capabilities["screenshot_features"] = []
    
    return capabilities

# Global observability manager instance
_global_observability: Optional[ObservabilityManager] = None

def get_observability_manager(log_dir: str = "logs",
                             screenshot_dir: str = "screenshots") -> ObservabilityManager:
    """Get global observability manager instance
    
    Args:
        log_dir: Directory untuk logs
        screenshot_dir: Directory untuk screenshots
        
    Returns:
        ObservabilityManager instance
    """
    global _global_observability
    if _global_observability is None:
        _global_observability = create_observability_manager(
            log_dir=log_dir,
            screenshot_dir=screenshot_dir
        )
    return _global_observability

def set_global_observability(manager: ObservabilityManager):
    """Set global observability manager instance
    
    Args:
        manager: ObservabilityManager instance
    """
    global _global_observability
    _global_observability = manager

def close_global_observability():
    """Close global observability manager"""
    global _global_observability
    if _global_observability:
        _global_observability.close()
        _global_observability = None

# Export all public classes and functions
__all__ = [
    # Logger exports
    "StructuredLogger",
    "LogEntry", 
    "LogLevel",
    "EventType",
    "get_logger",
    "set_global_logger",
    "close_global_logger",
    
    # Screenshot exports
    "ScreenshotCapture",
    "ScreenshotMetadata",
    "CaptureMode",
    "TriggerEvent",
    "get_screenshot_capture",
    "set_global_capture",
    "get_capture_capabilities",
    
    # Unified manager exports
    "ObservabilityManager",
    "create_observability_manager",
    "get_observability_manager",
    "set_global_observability",
    "close_global_observability",
    "get_observability_capabilities",
    
    # Availability flags
    "LOGGER_AVAILABLE",
    "SCREENSHOT_AVAILABLE"
]

# Package metadata
__version__ = "1.0.0"
__author__ = "Windows Use Autonomous Agent"
__description__ = "Comprehensive observability system with logging and screenshot capture"