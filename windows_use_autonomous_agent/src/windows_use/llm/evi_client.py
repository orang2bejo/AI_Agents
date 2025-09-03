"""Hume AI EVI Client Implementation.

This module provides the main client for communicating with Hume AI's
Empathic Voice Interface (EVI) API.
"""

import asyncio
import json
import logging
import time
from typing import Optional, Dict, Any, Callable, AsyncGenerator
from dataclasses import dataclass
import websockets
import base64
import numpy as np

from .evi_config import EVIConfig
from ..utils.error_handling import handle_errors


@dataclass
class EVIMessage:
    """Represents a message in EVI conversation."""
    type: str
    content: Any
    timestamp: float
    emotion_scores: Optional[Dict[str, float]] = None
    confidence: Optional[float] = None


class EVIClient:
    """Client for Hume AI Empathic Voice Interface."""
    
    def __init__(self, config: EVIConfig):
        """Initialize EVI client.
        
        Args:
            config: EVI configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.is_connected = False
        self.conversation_id: Optional[str] = None
        self.session_id: Optional[str] = None
        
        # Callbacks
        self.on_message: Optional[Callable[[EVIMessage], None]] = None
        self.on_audio: Optional[Callable[[bytes], None]] = None
        self.on_emotion: Optional[Callable[[Dict[str, float]], None]] = None
        self.on_error: Optional[Callable[[Exception], None]] = None
        
        # State management
        self._running = False
        self._audio_queue = asyncio.Queue()
        self._response_queue = asyncio.Queue()
    
    async def connect(self) -> bool:
        """Connect to Hume AI EVI API.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.config.validate()
            
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "X-Hume-Api-Key": self.config.api_key
            }
            
            self.logger.info(f"Connecting to Hume EVI at {self.config.base_url}")
            
            self.websocket = await websockets.connect(
                self.config.base_url,
                extra_headers=headers,
                timeout=self.config.connection_timeout
            )
            
            self.is_connected = True
            self.logger.info("Successfully connected to Hume EVI")
            
            # Send initial configuration
            await self._send_config()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Hume EVI: {e}")
            if self.on_error:
                self.on_error(e)
            return False
    
    async def disconnect(self):
        """Disconnect from Hume AI EVI API."""
        self._running = False
        
        if self.websocket and not self.websocket.closed:
            await self.websocket.close()
        
        self.is_connected = False
        self.websocket = None
        self.logger.info("Disconnected from Hume EVI")
    
    async def _send_config(self):
        """Send initial configuration to EVI."""
        config_message = {
            "type": "session_settings",
            "voice": {
                "provider": "hume",
                "voice_id": self.config.voice_id
            },
            "language": {
                "code": self.config.language
            },
            "audio": {
                "encoding": "linear16",
                "sample_rate": self.config.sample_rate,
                "channels": self.config.channels
            },
            "prosody": {
                "identify_speakers": False
            },
            "understanding": {
                "emotion_features": self.config.emotion_detection,
                "empathy_level": self.config.empathy_level
            },
            "personality": self.config.personality_traits
        }
        
        await self._send_message(config_message)
    
    async def _send_message(self, message: Dict[str, Any]):
        """Send message to EVI API.
        
        Args:
            message: Message to send
        """
        if not self.websocket or self.websocket.closed:
            raise ConnectionError("Not connected to EVI API")
        
        try:
            await self.websocket.send(json.dumps(message))
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            raise
    
    async def send_audio(self, audio_data: bytes):
        """Send audio data to EVI.
        
        Args:
            audio_data: Raw audio bytes
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to EVI API")
        
        # Convert audio to base64
        audio_b64 = base64.b64encode(audio_data).decode('utf-8')
        
        message = {
            "type": "audio_input",
            "data": audio_b64,
            "encoding": "linear16",
            "sample_rate": self.config.sample_rate
        }
        
        await self._send_message(message)
    
    async def send_text(self, text: str):
        """Send text message to EVI.
        
        Args:
            text: Text message to send
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to EVI API")
        
        message = {
            "type": "user_input",
            "text": text
        }
        
        await self._send_message(message)
    
    async def start_conversation(self) -> str:
        """Start a new conversation.
        
        Returns:
            Conversation ID
        """
        if not self.is_connected:
            await self.connect()
        
        message = {
            "type": "session_start"
        }
        
        await self._send_message(message)
        
        # Generate conversation ID
        self.conversation_id = f"conv_{int(time.time())}"
        self.session_id = f"sess_{int(time.time())}"
        
        self.logger.info(f"Started conversation: {self.conversation_id}")
        return self.conversation_id
    
    async def end_conversation(self):
        """End current conversation."""
        if self.conversation_id:
            message = {
                "type": "session_end",
                "conversation_id": self.conversation_id
            }
            
            await self._send_message(message)
            
            self.logger.info(f"Ended conversation: {self.conversation_id}")
            self.conversation_id = None
            self.session_id = None
    
    async def listen(self):
        """Listen for messages from EVI API."""
        if not self.websocket:
            raise ConnectionError("Not connected to EVI API")
        
        self._running = True
        
        try:
            async for message in self.websocket:
                if not self._running:
                    break
                
                await self._handle_message(message)
                
        except websockets.exceptions.ConnectionClosed:
            self.logger.info("EVI connection closed")
            self.is_connected = False
        except Exception as e:
            self.logger.error(f"Error in EVI listener: {e}")
            if self.on_error:
                self.on_error(e)
    
    async def _handle_message(self, raw_message: str):
        """Handle incoming message from EVI.
        
        Args:
            raw_message: Raw message string
        """
        try:
            data = json.loads(raw_message)
            message_type = data.get('type', 'unknown')
            
            evi_message = EVIMessage(
                type=message_type,
                content=data,
                timestamp=time.time(),
                emotion_scores=data.get('emotions'),
                confidence=data.get('confidence')
            )
            
            # Handle different message types
            if message_type == 'audio_output':
                await self._handle_audio_output(data)
            elif message_type == 'user_message':
                await self._handle_user_message(data)
            elif message_type == 'assistant_message':
                await self._handle_assistant_message(data)
            elif message_type == 'emotion_scores':
                await self._handle_emotion_scores(data)
            elif message_type == 'error':
                await self._handle_error_message(data)
            
            # Call general message callback
            if self.on_message:
                self.on_message(evi_message)
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse EVI message: {e}")
        except Exception as e:
            self.logger.error(f"Error handling EVI message: {e}")
    
    async def _handle_audio_output(self, data: Dict[str, Any]):
        """Handle audio output from EVI.
        
        Args:
            data: Audio output data
        """
        if 'data' in data:
            try:
                audio_data = base64.b64decode(data['data'])
                if self.on_audio:
                    self.on_audio(audio_data)
            except Exception as e:
                self.logger.error(f"Failed to decode audio data: {e}")
    
    async def _handle_user_message(self, data: Dict[str, Any]):
        """Handle user message from EVI.
        
        Args:
            data: User message data
        """
        self.logger.debug(f"User message: {data.get('message', {}).get('content', '')}")
    
    async def _handle_assistant_message(self, data: Dict[str, Any]):
        """Handle assistant message from EVI.
        
        Args:
            data: Assistant message data
        """
        self.logger.debug(f"Assistant message: {data.get('message', {}).get('content', '')}")
    
    async def _handle_emotion_scores(self, data: Dict[str, Any]):
        """Handle emotion scores from EVI.
        
        Args:
            data: Emotion scores data
        """
        emotions = data.get('emotions', {})
        if emotions and self.on_emotion:
            self.on_emotion(emotions)
    
    async def _handle_error_message(self, data: Dict[str, Any]):
        """Handle error message from EVI.
        
        Args:
            data: Error message data
        """
        error_msg = data.get('message', 'Unknown EVI error')
        error = Exception(f"EVI Error: {error_msg}")
        self.logger.error(error_msg)
        
        if self.on_error:
            self.on_error(error)
    
    def set_callbacks(
        self,
        on_message: Optional[Callable[[EVIMessage], None]] = None,
        on_audio: Optional[Callable[[bytes], None]] = None,
        on_emotion: Optional[Callable[[Dict[str, float]], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None
    ):
        """Set callback functions.
        
        Args:
            on_message: Callback for general messages
            on_audio: Callback for audio data
            on_emotion: Callback for emotion scores
            on_error: Callback for errors
        """
        if on_message:
            self.on_message = on_message
        if on_audio:
            self.on_audio = on_audio
        if on_emotion:
            self.on_emotion = on_emotion
        if on_error:
            self.on_error = on_error
    
    @property
    def status(self) -> Dict[str, Any]:
        """Get client status.
        
        Returns:
            Status dictionary
        """
        return {
            'connected': self.is_connected,
            'running': self._running,
            'conversation_id': self.conversation_id,
            'session_id': self.session_id,
            'websocket_state': 'open' if self.websocket and not self.websocket.closed else 'closed'
        }