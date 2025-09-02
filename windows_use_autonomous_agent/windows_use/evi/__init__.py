"""Hume AI EVI (Empathic Voice Interface) Integration Module.

This module provides integration with Hume AI's Empathic Voice Interface (EVI)
for advanced speech-to-speech capabilities with emotional intelligence.

Features:
- Real-time speech-to-speech conversation
- Emotional intelligence and empathy
- Voice activity detection
- Streaming audio processing
- WebSocket-based communication
- Configurable voice models

Components:
- EVIClient: Main client for EVI API
- EVIConfig: Configuration management
- EVIHandler: High-level interface handler
- EVIStreamer: Audio streaming utilities
"""

from .evi_client import EVIClient
from .evi_config import EVIConfig
from .evi_handler import EVIHandler
from .evi_streamer import EVIStreamer

__all__ = [
    'EVIClient',
    'EVIConfig', 
    'EVIHandler',
    'EVIStreamer'
]

__version__ = '1.0.0'