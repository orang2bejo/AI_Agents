"""Hume AI EVI Configuration Management.

This module handles configuration for Hume AI's Empathic Voice Interface (EVI).
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
from pydantic import BaseModel, Field


@dataclass
class EVIConfig:
    """Configuration for Hume AI EVI."""
    
    # API Configuration
    api_key: str = ""
    base_url: str = "wss://api.hume.ai/v0/evi/chat"
    
    # Voice Configuration
    voice_id: str = "default"  # Hume AI voice model ID
    language: str = "en"  # Language code
    
    # Audio Configuration
    sample_rate: int = 16000  # Audio sample rate
    channels: int = 1  # Mono audio
    chunk_size: int = 1024  # Audio chunk size for streaming
    
    # Conversation Configuration
    max_duration: int = 300  # Maximum conversation duration in seconds
    silence_timeout: int = 3  # Silence timeout in seconds
    
    # Emotional Intelligence Configuration
    emotion_detection: bool = True
    empathy_level: str = "medium"  # low, medium, high
    personality_traits: Dict[str, float] = None
    
    # Performance Configuration
    enable_streaming: bool = True
    buffer_size: int = 4096
    connection_timeout: int = 30
    
    def __post_init__(self):
        """Initialize default values after dataclass creation."""
        if self.personality_traits is None:
            self.personality_traits = {
                "warmth": 0.7,
                "enthusiasm": 0.6,
                "curiosity": 0.8,
                "helpfulness": 0.9
            }
    
    @classmethod
    def from_env(cls) -> 'EVIConfig':
        """Create configuration from environment variables."""
        return cls(
            api_key=os.getenv('HUME_API_KEY', ''),
            voice_id=os.getenv('HUME_VOICE_ID', 'default'),
            language=os.getenv('HUME_LANGUAGE', 'en'),
            sample_rate=int(os.getenv('HUME_SAMPLE_RATE', '16000')),
            emotion_detection=os.getenv('HUME_EMOTION_DETECTION', 'true').lower() == 'true',
            empathy_level=os.getenv('HUME_EMPATHY_LEVEL', 'medium')
        )
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'EVIConfig':
        """Create configuration from dictionary."""
        return cls(**config_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'api_key': self.api_key,
            'base_url': self.base_url,
            'voice_id': self.voice_id,
            'language': self.language,
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'chunk_size': self.chunk_size,
            'max_duration': self.max_duration,
            'silence_timeout': self.silence_timeout,
            'emotion_detection': self.emotion_detection,
            'empathy_level': self.empathy_level,
            'personality_traits': self.personality_traits,
            'enable_streaming': self.enable_streaming,
            'buffer_size': self.buffer_size,
            'connection_timeout': self.connection_timeout
        }
    
    def validate(self) -> bool:
        """Validate configuration."""
        if not self.api_key:
            raise ValueError("Hume API key is required")
        
        if self.empathy_level not in ['low', 'medium', 'high']:
            raise ValueError("Empathy level must be 'low', 'medium', or 'high'")
        
        if self.sample_rate not in [8000, 16000, 22050, 44100, 48000]:
            raise ValueError("Invalid sample rate")
        
        return True


class EVIConfigModel(BaseModel):
    """Pydantic model for EVI configuration validation."""
    
    api_key: str = Field(..., description="Hume AI API key")
    base_url: str = Field(default="wss://api.hume.ai/v0/evi/chat", description="EVI WebSocket URL")
    voice_id: str = Field(default="default", description="Voice model ID")
    language: str = Field(default="en", description="Language code")
    sample_rate: int = Field(default=16000, description="Audio sample rate")
    channels: int = Field(default=1, description="Audio channels")
    chunk_size: int = Field(default=1024, description="Audio chunk size")
    max_duration: int = Field(default=300, description="Max conversation duration")
    silence_timeout: int = Field(default=3, description="Silence timeout")
    emotion_detection: bool = Field(default=True, description="Enable emotion detection")
    empathy_level: str = Field(default="medium", description="Empathy level")
    personality_traits: Dict[str, float] = Field(
        default_factory=lambda: {
            "warmth": 0.7,
            "enthusiasm": 0.6,
            "curiosity": 0.8,
            "helpfulness": 0.9
        },
        description="Personality traits"
    )
    enable_streaming: bool = Field(default=True, description="Enable streaming")
    buffer_size: int = Field(default=4096, description="Buffer size")
    connection_timeout: int = Field(default=30, description="Connection timeout")
    
    class Config:
        """Pydantic configuration."""
        extra = "forbid"
        validate_assignment = True