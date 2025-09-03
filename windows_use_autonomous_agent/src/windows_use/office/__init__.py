"""Office Automation Package

Package ini menyediakan handler untuk mengotomatisasi aplikasi Microsoft Office
melalui COM (Component Object Model) menggunakan pywin32.

Modules:
- excel_handler: Excel automation
- word_handler: Word automation  
- powerpoint_handler: PowerPoint automation

Usage:
    from . import ExcelHandler, WordHandler, PowerPointHandler
    
    # Excel
    with ExcelHandler() as excel:
        excel.open_workbook("data.xlsx")
        excel.write_cell("A1", "Hello World")
    
    # Word
    with WordHandler() as word:
        word.open_document("report.docx")
        word.write_text("New content")
    
    # PowerPoint
    with PowerPointHandler() as ppt:
        ppt.create_presentation()
        ppt.edit_slide_title("My Presentation")
"""

from typing import Dict, Any, Optional
import logging

try:
    from .excel_handler import ExcelHandler, ExcelResult
    from .word_handler import WordHandler, WordResult
    from .powerpoint_handler import PowerPointHandler, PowerPointResult
    
    OFFICE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Office handlers not available: {e}")
    OFFICE_AVAILABLE = False
    
    # Create dummy classes for graceful degradation
    class ExcelHandler:
        def __init__(self, *args, **kwargs):
            raise ImportError("pywin32 required for Excel automation")
    
    class WordHandler:
        def __init__(self, *args, **kwargs):
            raise ImportError("pywin32 required for Word automation")
    
    class PowerPointHandler:
        def __init__(self, *args, **kwargs):
            raise ImportError("pywin32 required for PowerPoint automation")
    
    ExcelResult = None
    WordResult = None
    PowerPointResult = None

# Office application types
OFFICE_APPS = {
    "excel": ExcelHandler,
    "word": WordHandler,
    "powerpoint": PowerPointHandler,
    "ppt": PowerPointHandler  # Alias
}

def create_office_handler(app_type: str, **kwargs) -> Any:
    """Factory function untuk membuat office handler
    
    Args:
        app_type: Tipe aplikasi ('excel', 'word', 'powerpoint')
        **kwargs: Arguments untuk handler
        
    Returns:
        Office handler instance
        
    Raises:
        ValueError: Jika app_type tidak didukung
        ImportError: Jika pywin32 tidak tersedia
    """
    if not OFFICE_AVAILABLE:
        raise ImportError("pywin32 required for Office automation")
    
    app_type = app_type.lower()
    if app_type not in OFFICE_APPS:
        raise ValueError(f"Unsupported office app: {app_type}. Supported: {list(OFFICE_APPS.keys())}")
    
    handler_class = OFFICE_APPS[app_type]
    return handler_class(**kwargs)

def get_office_capabilities() -> Dict[str, Any]:
    """Get informasi kemampuan office automation
    
    Returns:
        Dictionary dengan informasi capabilities
    """
    return {
        "available": OFFICE_AVAILABLE,
        "supported_apps": list(OFFICE_APPS.keys()) if OFFICE_AVAILABLE else [],
        "excel_features": [
            "open/close workbooks",
            "read/write cells", 
            "worksheet management",
            "chart creation",
            "formula calculation",
            "export to PDF"
        ] if OFFICE_AVAILABLE else [],
        "word_features": [
            "open/close documents",
            "text manipulation",
            "formatting", 
            "find/replace",
            "export to PDF",
            "heading management"
        ] if OFFICE_AVAILABLE else [],
        "powerpoint_features": [
            "open/close presentations",
            "slide management",
            "content editing",
            "image insertion",
            "export to PDF",
            "template support"
        ] if OFFICE_AVAILABLE else []
    }

# Export all public classes and functions
__all__ = [
    "ExcelHandler",
    "WordHandler", 
    "PowerPointHandler",
    "ExcelResult",
    "WordResult",
    "PowerPointResult",
    "create_office_handler",
    "get_office_capabilities",
    "OFFICE_AVAILABLE",
    "OFFICE_APPS"
]

# Package metadata
__version__ = "1.0.0"
__author__ = "Windows Use Autonomous Agent"
__description__ = "Office automation via COM for Excel, Word, and PowerPoint"