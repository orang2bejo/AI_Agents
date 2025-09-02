"""Screenshot Capture Module

Module ini menyediakan kemampuan untuk mengambil screenshot secara otomatis
untuk observability dan debugging. Mendukung berbagai mode capture dan
optimisasi untuk performa.

Features:
- Full screen capture
- Window-specific capture
- Region capture
- Automatic capture on events
- Image optimization
- Metadata embedding
- Privacy filtering
"""

import os
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum
import threading
from contextlib import contextmanager

try:
    from PIL import Image, ImageDraw, ImageFont
    from PIL.ExifTags import TAGS
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None
    ImageDraw = None
    ImageFont = None

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    pyautogui = None

try:
    import win32gui
    import win32ui
    import win32con
    import win32api
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    win32gui = None
    win32ui = None
    win32con = None
    win32api = None

class CaptureMode(Enum):
    """Screenshot capture modes"""
    FULL_SCREEN = "full_screen"
    ACTIVE_WINDOW = "active_window"
    SPECIFIC_WINDOW = "specific_window"
    REGION = "region"
    MULTI_MONITOR = "multi_monitor"

class TriggerEvent(Enum):
    """Events yang trigger screenshot"""
    MANUAL = "manual"
    ERROR_OCCURRED = "error_occurred"
    ACTION_EXECUTED = "action_executed"
    OFFICE_OPERATION = "office_operation"
    SECURITY_ALERT = "security_alert"
    USER_INTERACTION = "user_interaction"
    PERIODIC = "periodic"

@dataclass
class ScreenshotMetadata:
    """Metadata untuk screenshot"""
    timestamp: str
    session_id: str
    trigger_event: str
    capture_mode: str
    file_path: str
    file_size: int
    dimensions: Tuple[int, int]
    window_title: Optional[str] = None
    window_process: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    privacy_filtered: bool = False
    compression_ratio: Optional[float] = None
    capture_duration_ms: Optional[float] = None

class ScreenshotCapture:
    """Screenshot capture engine dengan berbagai mode dan optimisasi"""
    
    def __init__(self, output_dir: str = "screenshots",
                 max_file_size: int = 2 * 1024 * 1024,  # 2MB
                 quality: int = 85,
                 auto_cleanup_days: int = 7,
                 privacy_mode: bool = False):
        """
        Args:
            output_dir: Directory untuk menyimpan screenshots
            max_file_size: Maximum file size dalam bytes
            quality: JPEG quality (1-100)
            auto_cleanup_days: Days to keep screenshots
            privacy_mode: Enable privacy filtering
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.max_file_size = max_file_size
        self.quality = quality
        self.auto_cleanup_days = auto_cleanup_days
        self.privacy_mode = privacy_mode
        
        # Check dependencies
        self.capabilities = self._check_capabilities()
        
        # Screenshot history
        self.screenshot_history: List[ScreenshotMetadata] = []
        self._lock = threading.Lock()
        
        # Privacy filters (sensitive window titles)
        self.privacy_filters = [
            "password", "login", "credential", "secret", "private",
            "bank", "payment", "credit card", "ssn", "social security"
        ]
        
        # Auto-capture settings
        self.auto_capture_enabled = False
        self.auto_capture_events = set()
        
        # Performance metrics
        self.metrics = {
            "total_captures": 0,
            "failed_captures": 0,
            "total_size_bytes": 0,
            "average_capture_time_ms": 0,
            "captures_by_mode": {},
            "captures_by_event": {}
        }
    
    def _check_capabilities(self) -> Dict[str, bool]:
        """Check available screenshot capabilities"""
        return {
            "pil_available": PIL_AVAILABLE,
            "pyautogui_available": PYAUTOGUI_AVAILABLE,
            "win32_available": WIN32_AVAILABLE,
            "can_capture_screen": PIL_AVAILABLE and (PYAUTOGUI_AVAILABLE or WIN32_AVAILABLE),
            "can_capture_windows": WIN32_AVAILABLE,
            "can_optimize_images": PIL_AVAILABLE
        }
    
    def capture_screenshot(self, mode: CaptureMode = CaptureMode.FULL_SCREEN,
                          trigger_event: TriggerEvent = TriggerEvent.MANUAL,
                          context: Optional[Dict[str, Any]] = None,
                          window_title: Optional[str] = None,
                          region: Optional[Tuple[int, int, int, int]] = None,
                          session_id: Optional[str] = None) -> Optional[ScreenshotMetadata]:
        """Capture screenshot dengan mode yang ditentukan
        
        Args:
            mode: Capture mode
            trigger_event: Event yang trigger capture
            context: Additional context
            window_title: Specific window title (untuk SPECIFIC_WINDOW mode)
            region: Region coordinates (x, y, width, height)
            session_id: Session ID
            
        Returns:
            ScreenshotMetadata jika berhasil, None jika gagal
        """
        if not self.capabilities["can_capture_screen"]:
            return None
        
        start_time = time.time()
        
        try:
            with self._lock:
                # Generate filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                filename = f"screenshot_{timestamp}_{mode.value}.png"
                file_path = self.output_dir / filename
                
                # Check privacy mode
                if self.privacy_mode and self._should_filter_privacy(window_title):
                    return self._create_privacy_placeholder(file_path, trigger_event, context, session_id)
                
                # Capture based on mode
                image = None
                window_info = None
                
                if mode == CaptureMode.FULL_SCREEN:
                    image = self._capture_full_screen()
                elif mode == CaptureMode.ACTIVE_WINDOW:
                    image, window_info = self._capture_active_window()
                elif mode == CaptureMode.SPECIFIC_WINDOW:
                    image, window_info = self._capture_specific_window(window_title)
                elif mode == CaptureMode.REGION:
                    image = self._capture_region(region)
                elif mode == CaptureMode.MULTI_MONITOR:
                    image = self._capture_multi_monitor()
                
                if image is None:
                    self.metrics["failed_captures"] += 1
                    return None
                
                # Optimize and save
                optimized_image = self._optimize_image(image)
                optimized_image.save(file_path, "PNG", optimize=True)
                
                # Calculate metrics
                end_time = time.time()
                capture_duration_ms = (end_time - start_time) * 1000
                file_size = file_path.stat().st_size
                
                # Create metadata
                metadata = ScreenshotMetadata(
                    timestamp=datetime.utcnow().isoformat() + "Z",
                    session_id=session_id or "unknown",
                    trigger_event=trigger_event.value,
                    capture_mode=mode.value,
                    file_path=str(file_path),
                    file_size=file_size,
                    dimensions=(optimized_image.width, optimized_image.height),
                    window_title=window_info.get("title") if window_info else None,
                    window_process=window_info.get("process") if window_info else None,
                    context=context,
                    privacy_filtered=False,
                    compression_ratio=None,
                    capture_duration_ms=capture_duration_ms
                )
                
                # Update metrics
                self._update_metrics(mode, trigger_event, file_size, capture_duration_ms)
                
                # Add to history
                self.screenshot_history.append(metadata)
                
                return metadata
                
        except Exception as e:
            self.metrics["failed_captures"] += 1
            # Log error (would integrate with logger)
            return None
    
    def _capture_full_screen(self) -> Optional[Image.Image]:
        """Capture full screen"""
        if PYAUTOGUI_AVAILABLE:
            try:
                screenshot = pyautogui.screenshot()
                return screenshot
            except Exception:
                pass
        
        if WIN32_AVAILABLE:
            try:
                return self._win32_capture_screen()
            except Exception:
                pass
        
        return None
    
    def _capture_active_window(self) -> Tuple[Optional[Image.Image], Optional[Dict[str, str]]]:
        """Capture active window"""
        if not WIN32_AVAILABLE:
            return None, None
        
        try:
            hwnd = win32gui.GetForegroundWindow()
            return self._capture_window_by_handle(hwnd)
        except Exception:
            return None, None
    
    def _capture_specific_window(self, window_title: str) -> Tuple[Optional[Image.Image], Optional[Dict[str, str]]]:
        """Capture specific window by title"""
        if not WIN32_AVAILABLE or not window_title:
            return None, None
        
        try:
            hwnd = win32gui.FindWindow(None, window_title)
            if hwnd:
                return self._capture_window_by_handle(hwnd)
        except Exception:
            pass
        
        return None, None
    
    def _capture_window_by_handle(self, hwnd) -> Tuple[Optional[Image.Image], Optional[Dict[str, str]]]:
        """Capture window by handle"""
        try:
            # Get window info
            window_title = win32gui.GetWindowText(hwnd)
            _, pid = win32gui.GetWindowThreadProcessId(hwnd)
            
            try:
                process_handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, False, pid)
                process_name = win32api.GetModuleFileNameEx(process_handle, 0)
                win32api.CloseHandle(process_handle)
            except:
                process_name = "unknown"
            
            # Get window rect
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bottom - top
            
            # Capture window
            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()
            
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)
            
            result = saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)
            
            if result:
                # Convert to PIL Image
                bmpinfo = saveBitMap.GetInfo()
                bmpstr = saveBitMap.GetBitmapBits(True)
                
                image = Image.frombuffer(
                    'RGB',
                    (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                    bmpstr, 'raw', 'BGRX', 0, 1
                )
                
                window_info = {
                    "title": window_title,
                    "process": os.path.basename(process_name)
                }
                
                # Cleanup
                win32gui.DeleteObject(saveBitMap.GetHandle())
                saveDC.DeleteDC()
                mfcDC.DeleteDC()
                win32gui.ReleaseDC(hwnd, hwndDC)
                
                return image, window_info
            
        except Exception:
            pass
        
        return None, None
    
    def _capture_region(self, region: Optional[Tuple[int, int, int, int]]) -> Optional[Image.Image]:
        """Capture specific region"""
        if not region or not PYAUTOGUI_AVAILABLE:
            return None
        
        try:
            x, y, width, height = region
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            return screenshot
        except Exception:
            return None
    
    def _capture_multi_monitor(self) -> Optional[Image.Image]:
        """Capture all monitors"""
        # For now, just capture primary screen
        return self._capture_full_screen()
    
    def _win32_capture_screen(self) -> Optional[Image.Image]:
        """Capture screen using Win32 API"""
        try:
            hdesktop = win32gui.GetDesktopWindow()
            width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
            height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
            left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
            top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
            
            desktop_dc = win32gui.GetWindowDC(hdesktop)
            img_dc = win32ui.CreateDCFromHandle(desktop_dc)
            mem_dc = img_dc.CreateCompatibleDC()
            
            screenshot = win32ui.CreateBitmap()
            screenshot.CreateCompatibleBitmap(img_dc, width, height)
            mem_dc.SelectObject(screenshot)
            mem_dc.BitBlt((0, 0), (width, height), img_dc, (left, top), win32con.SRCCOPY)
            
            bmpinfo = screenshot.GetInfo()
            bmpstr = screenshot.GetBitmapBits(True)
            
            image = Image.frombuffer(
                'RGB',
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'BGRX', 0, 1
            )
            
            # Cleanup
            mem_dc.DeleteDC()
            win32gui.DeleteObject(screenshot.GetHandle())
            img_dc.DeleteDC()
            win32gui.ReleaseDC(hdesktop, desktop_dc)
            
            return image
            
        except Exception:
            return None
    
    def _optimize_image(self, image: Image.Image) -> Image.Image:
        """Optimize image untuk size dan quality"""
        if not PIL_AVAILABLE:
            return image
        
        try:
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too large
            max_dimension = 1920  # Max width or height
            if image.width > max_dimension or image.height > max_dimension:
                ratio = min(max_dimension / image.width, max_dimension / image.height)
                new_size = (int(image.width * ratio), int(image.height * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            return image
            
        except Exception:
            return image
    
    def _should_filter_privacy(self, window_title: Optional[str]) -> bool:
        """Check if window should be filtered for privacy"""
        if not window_title:
            return False
        
        window_title_lower = window_title.lower()
        return any(filter_term in window_title_lower for filter_term in self.privacy_filters)
    
    def _create_privacy_placeholder(self, file_path: Path, trigger_event: TriggerEvent,
                                  context: Optional[Dict[str, Any]], 
                                  session_id: Optional[str]) -> ScreenshotMetadata:
        """Create privacy placeholder image"""
        if PIL_AVAILABLE:
            # Create placeholder image
            placeholder = Image.new('RGB', (800, 600), color='gray')
            draw = ImageDraw.Draw(placeholder)
            
            try:
                font = ImageFont.load_default()
            except:
                font = None
            
            text = "Screenshot blocked for privacy"
            if font:
                draw.text((400, 300), text, fill='white', font=font, anchor='mm')
            
            placeholder.save(file_path, "PNG")
            file_size = file_path.stat().st_size
        else:
            # Create empty file
            file_path.touch()
            file_size = 0
        
        return ScreenshotMetadata(
            timestamp=datetime.utcnow().isoformat() + "Z",
            session_id=session_id or "unknown",
            trigger_event=trigger_event.value,
            capture_mode="privacy_filtered",
            file_path=str(file_path),
            file_size=file_size,
            dimensions=(800, 600) if PIL_AVAILABLE else (0, 0),
            privacy_filtered=True,
            context=context
        )
    
    def _update_metrics(self, mode: CaptureMode, trigger_event: TriggerEvent,
                       file_size: int, capture_duration_ms: float):
        """Update performance metrics"""
        self.metrics["total_captures"] += 1
        self.metrics["total_size_bytes"] += file_size
        
        # Update average capture time
        total_time = self.metrics["average_capture_time_ms"] * (self.metrics["total_captures"] - 1)
        self.metrics["average_capture_time_ms"] = (total_time + capture_duration_ms) / self.metrics["total_captures"]
        
        # Count by mode
        mode_key = mode.value
        self.metrics["captures_by_mode"][mode_key] = \
            self.metrics["captures_by_mode"].get(mode_key, 0) + 1
        
        # Count by event
        event_key = trigger_event.value
        self.metrics["captures_by_event"][event_key] = \
            self.metrics["captures_by_event"].get(event_key, 0) + 1
    
    def enable_auto_capture(self, events: List[TriggerEvent]):
        """Enable automatic screenshot capture untuk events tertentu
        
        Args:
            events: List of events yang akan trigger auto capture
        """
        self.auto_capture_enabled = True
        self.auto_capture_events = set(events)
    
    def disable_auto_capture(self):
        """Disable automatic screenshot capture"""
        self.auto_capture_enabled = False
        self.auto_capture_events.clear()
    
    def should_auto_capture(self, event: TriggerEvent) -> bool:
        """Check if event should trigger auto capture
        
        Args:
            event: Trigger event
            
        Returns:
            True if should capture
        """
        return self.auto_capture_enabled and event in self.auto_capture_events
    
    @contextmanager
    def capture_context(self, context_name: str, 
                       mode: CaptureMode = CaptureMode.FULL_SCREEN,
                       capture_on_enter: bool = True,
                       capture_on_exit: bool = True,
                       capture_on_error: bool = True,
                       session_id: Optional[str] = None):
        """Context manager untuk automatic screenshot capture
        
        Usage:
            with capture.capture_context("file_operation"):
                # do work
                pass
        """
        context_id = str(uuid.uuid4())
        context_data = {
            "context_name": context_name,
            "context_id": context_id
        }
        
        # Capture on enter
        if capture_on_enter:
            self.capture_screenshot(
                mode=mode,
                trigger_event=TriggerEvent.USER_INTERACTION,
                context={**context_data, "phase": "enter"},
                session_id=session_id
            )
        
        try:
            yield context_id
        except Exception as e:
            # Capture on error
            if capture_on_error:
                self.capture_screenshot(
                    mode=mode,
                    trigger_event=TriggerEvent.ERROR_OCCURRED,
                    context={**context_data, "phase": "error", "error": str(e)},
                    session_id=session_id
                )
            raise
        finally:
            # Capture on exit
            if capture_on_exit:
                self.capture_screenshot(
                    mode=mode,
                    trigger_event=TriggerEvent.USER_INTERACTION,
                    context={**context_data, "phase": "exit"},
                    session_id=session_id
                )
    
    def get_recent_screenshots(self, limit: int = 10) -> List[ScreenshotMetadata]:
        """Get recent screenshots
        
        Args:
            limit: Maximum number of screenshots
            
        Returns:
            List of recent screenshot metadata
        """
        with self._lock:
            return self.screenshot_history[-limit:] if self.screenshot_history else []
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get capture metrics
        
        Returns:
            Dictionary dengan metrics
        """
        return {
            **self.metrics,
            "capabilities": self.capabilities,
            "auto_capture_enabled": self.auto_capture_enabled,
            "auto_capture_events": list(self.auto_capture_events),
            "privacy_mode": self.privacy_mode,
            "total_screenshots": len(self.screenshot_history)
        }
    
    def cleanup_old_screenshots(self):
        """Cleanup old screenshots berdasarkan auto_cleanup_days"""
        if self.auto_cleanup_days <= 0:
            return
        
        cutoff_time = time.time() - (self.auto_cleanup_days * 24 * 60 * 60)
        cleaned_count = 0
        
        for screenshot_file in self.output_dir.glob("*.png"):
            if screenshot_file.stat().st_mtime < cutoff_time:
                try:
                    screenshot_file.unlink()
                    cleaned_count += 1
                except Exception:
                    pass
        
        # Remove from history
        cutoff_timestamp = datetime.fromtimestamp(cutoff_time).isoformat() + "Z"
        with self._lock:
            self.screenshot_history = [
                meta for meta in self.screenshot_history 
                if meta.timestamp >= cutoff_timestamp
            ]
        
        return cleaned_count
    
    def export_metadata(self) -> List[Dict[str, Any]]:
        """Export screenshot metadata
        
        Returns:
            List of metadata dictionaries
        """
        with self._lock:
            return [{
                "timestamp": meta.timestamp,
                "session_id": meta.session_id,
                "trigger_event": meta.trigger_event,
                "capture_mode": meta.capture_mode,
                "file_path": meta.file_path,
                "file_size": meta.file_size,
                "dimensions": meta.dimensions,
                "window_title": meta.window_title,
                "window_process": meta.window_process,
                "context": meta.context,
                "privacy_filtered": meta.privacy_filtered,
                "capture_duration_ms": meta.capture_duration_ms
            } for meta in self.screenshot_history]

# Global screenshot capture instance
_global_capture: Optional[ScreenshotCapture] = None

def get_screenshot_capture(output_dir: str = "screenshots") -> ScreenshotCapture:
    """Get global screenshot capture instance
    
    Args:
        output_dir: Directory untuk screenshots
        
    Returns:
        ScreenshotCapture instance
    """
    global _global_capture
    if _global_capture is None:
        _global_capture = ScreenshotCapture(output_dir)
    return _global_capture

def set_global_capture(capture: ScreenshotCapture):
    """Set global screenshot capture instance
    
    Args:
        capture: ScreenshotCapture instance
    """
    global _global_capture
    _global_capture = capture

def get_capture_capabilities() -> Dict[str, Any]:
    """Get screenshot capture capabilities
    
    Returns:
        Dictionary dengan informasi capabilities
    """
    return {
        "pil_available": PIL_AVAILABLE,
        "pyautogui_available": PYAUTOGUI_AVAILABLE,
        "win32_available": WIN32_AVAILABLE,
        "supported_modes": [
            "full_screen", "active_window", "specific_window", 
            "region", "multi_monitor"
        ] if PIL_AVAILABLE and (PYAUTOGUI_AVAILABLE or WIN32_AVAILABLE) else [],
        "supported_events": [
            "manual", "error_occurred", "action_executed",
            "office_operation", "security_alert", "user_interaction", "periodic"
        ],
        "features": [
            "Auto capture", "Privacy filtering", "Image optimization",
            "Metadata tracking", "Auto cleanup", "Context management"
        ]
    }