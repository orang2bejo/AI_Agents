"""Windows Use Tools Module.

This module provides various tools and utilities for Windows automation,
including voice input, TTS, system tools, and security features.
"""

# Voice and Audio
from .voice_input import VoiceInput
from .tts_piper import TTSPiper

# Indonesian Language Processing
from .grammar_id import IndonesianGrammar
from .router import CommandRouter

# Windows System Tools
from .winget import WingetManager
from .ps_shell import PowerShellManager
from .process import ProcessManager, ProcessInfo, ProcessAction
from .net import NetworkManager

# Security and Safety
from .guardrails import GuardrailsEngine
from .hitl import HITLManager

# Observability
from .logger import setup_logger, get_logger
from .screenshot import ScreenshotManager

__all__ = [
    # Voice and Audio
    'VoiceInput',
    'TTSPiper',
    
    # Indonesian Language Processing
    'IndonesianGrammar',
    'CommandRouter',
    
    # Windows System Tools
    'WingetManager',
    'PowerShellManager',
    'ProcessManager',
    'ProcessInfo',
    'ProcessAction',
    'NetworkManager',
    
    # Security and Safety
    'GuardrailsEngine',
    'HITLManager',
    
    # Observability
    'setup_logger',
    'get_logger',
    'ScreenshotManager',
]

__version__ = '1.0.0'
__author__ = 'Windows Use Team'
__description__ = 'Comprehensive Windows automation tools with AI integration'