"""Hume AI EVI Handler - High-level interface for EVI integration.

This module provides a high-level handler for managing EVI conversations
and integrating with the Jarvis AI system.
"""

import asyncio
import logging
import threading
import time
from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass, field
from enum import Enum

from .evi_client import EVIClient, EVIMessage
from .evi_config import EVIConfig
from .evi_streamer import EVIStreamer
from ..utils.error_handler import handle_errors


class ConversationState(Enum):
    """Conversation state enumeration."""
    IDLE = "idle"
    CONNECTING = "connecting"
    ACTIVE = "active"
    LISTENING = "listening"
    SPEAKING = "speaking"
    PROCESSING = "processing"
    ERROR = "error"
    DISCONNECTED = "disconnected"


@dataclass
class ConversationMetrics:
    """Metrics for EVI conversation."""
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    total_messages: int = 0
    audio_messages: int = 0
    text_messages: int = 0
    emotion_detections: int = 0
    average_response_time: float = 0.0
    response_times: List[float] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    @property
    def duration(self) -> float:
        """Get conversation duration."""
        end = self.end_time or time.time()
        return end - self.start_time
    
    def add_response_time(self, response_time: float):
        """Add response time measurement."""
        self.response_times.append(response_time)
        self.average_response_time = sum(self.response_times) / len(self.response_times)


class EVIHandler:
    """High-level handler for Hume AI EVI integration."""
    
    def __init__(self, config: EVIConfig):
        """Initialize EVI handler.
        
        Args:
            config: EVI configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.client = EVIClient(config)
        self.streamer = EVIStreamer(config)
        
        # State management
        self.state = ConversationState.IDLE
        self.conversation_id: Optional[str] = None
        self.metrics = ConversationMetrics()
        
        # Threading
        self._event_loop: Optional[asyncio.AbstractEventLoop] = None
        self._background_thread: Optional[threading.Thread] = None
        self._running = False
        
        # Callbacks
        self.on_state_change: Optional[Callable[[ConversationState], None]] = None
        self.on_response: Optional[Callable[[str, Dict[str, Any]], None]] = None
        self.on_audio_response: Optional[Callable[[bytes], None]] = None
        self.on_emotion_detected: Optional[Callable[[Dict[str, float]], None]] = None
        self.on_error: Optional[Callable[[Exception], None]] = None
        
        # Setup client callbacks
        self._setup_client_callbacks()
    
    def _setup_client_callbacks(self):
        """Setup callbacks for EVI client."""
        self.client.set_callbacks(
            on_message=self._handle_client_message,
            on_audio=self._handle_client_audio,
            on_emotion=self._handle_client_emotion,
            on_error=self._handle_client_error
        )
    
    def _handle_client_message(self, message: EVIMessage):
        """Handle message from EVI client.
        
        Args:
            message: EVI message
        """
        self.metrics.total_messages += 1
        
        if message.type == 'assistant_message':
            content = message.content.get('message', {}).get('content', '')
            if content and self.on_response:
                self.on_response(content, message.content)
        
        self.logger.debug(f"Received EVI message: {message.type}")
    
    def _handle_client_audio(self, audio_data: bytes):
        """Handle audio from EVI client.
        
        Args:
            audio_data: Audio data bytes
        """
        self.metrics.audio_messages += 1
        
        if self.on_audio_response:
            self.on_audio_response(audio_data)
        
        # Update state
        if self.state != ConversationState.SPEAKING:
            self._set_state(ConversationState.SPEAKING)
    
    def _handle_client_emotion(self, emotions: Dict[str, float]):
        """Handle emotion detection from EVI client.
        
        Args:
            emotions: Emotion scores
        """
        self.metrics.emotion_detections += 1
        
        if self.on_emotion_detected:
            self.on_emotion_detected(emotions)
        
        self.logger.debug(f"Detected emotions: {emotions}")
    
    def _handle_client_error(self, error: Exception):
        """Handle error from EVI client.
        
        Args:
            error: Exception that occurred
        """
        self.metrics.errors.append(str(error))
        self._set_state(ConversationState.ERROR)
        
        if self.on_error:
            self.on_error(error)
        
        self.logger.error(f"EVI client error: {error}")
    
    def _set_state(self, new_state: ConversationState):
        """Set conversation state.
        
        Args:
            new_state: New conversation state
        """
        if self.state != new_state:
            old_state = self.state
            self.state = new_state
            
            self.logger.info(f"State changed: {old_state.value} -> {new_state.value}")
            
            if self.on_state_change:
                self.on_state_change(new_state)
    
    async def start_conversation(self) -> str:
        """Start a new EVI conversation.
        
        Returns:
            Conversation ID
        """
        try:
            self._set_state(ConversationState.CONNECTING)
            
            # Connect to EVI
            if not await self.client.connect():
                raise ConnectionError("Failed to connect to Hume EVI")
            
            # Start conversation
            self.conversation_id = await self.client.start_conversation()
            
            # Reset metrics
            self.metrics = ConversationMetrics()
            
            # Start listening
            asyncio.create_task(self.client.listen())
            
            self._set_state(ConversationState.ACTIVE)
            
            self.logger.info(f"Started EVI conversation: {self.conversation_id}")
            return self.conversation_id
            
        except Exception as e:
            self._set_state(ConversationState.ERROR)
            self.logger.error(f"Failed to start conversation: {e}")
            raise
    
    async def end_conversation(self):
        """End current EVI conversation."""
        try:
            if self.conversation_id:
                await self.client.end_conversation()
                
                # Update metrics
                self.metrics.end_time = time.time()
                
                self.logger.info(f"Ended EVI conversation: {self.conversation_id}")
                self.conversation_id = None
            
            await self.client.disconnect()
            self._set_state(ConversationState.IDLE)
            
        except Exception as e:
            self.logger.error(f"Error ending conversation: {e}")
            self._set_state(ConversationState.ERROR)
            raise
    
    async def send_text(self, text: str) -> bool:
        """Send text message to EVI.
        
        Args:
            text: Text message to send
            
        Returns:
            True if sent successfully
        """
        try:
            if self.state not in [ConversationState.ACTIVE, ConversationState.LISTENING]:
                raise RuntimeError(f"Cannot send text in state: {self.state.value}")
            
            start_time = time.time()
            
            await self.client.send_text(text)
            
            # Update metrics
            self.metrics.text_messages += 1
            response_time = time.time() - start_time
            self.metrics.add_response_time(response_time)
            
            self._set_state(ConversationState.PROCESSING)
            
            self.logger.debug(f"Sent text to EVI: {text[:50]}...")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send text: {e}")
            self._set_state(ConversationState.ERROR)
            return False
    
    async def send_audio(self, audio_data: bytes) -> bool:
        """Send audio data to EVI.
        
        Args:
            audio_data: Audio data bytes
            
        Returns:
            True if sent successfully
        """
        try:
            if self.state not in [ConversationState.ACTIVE, ConversationState.LISTENING]:
                raise RuntimeError(f"Cannot send audio in state: {self.state.value}")
            
            start_time = time.time()
            
            await self.client.send_audio(audio_data)
            
            # Update metrics
            self.metrics.audio_messages += 1
            response_time = time.time() - start_time
            self.metrics.add_response_time(response_time)
            
            self._set_state(ConversationState.PROCESSING)
            
            self.logger.debug(f"Sent audio to EVI: {len(audio_data)} bytes")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send audio: {e}")
            self._set_state(ConversationState.ERROR)
            return False
    
    def start_audio_streaming(self) -> bool:
        """Start audio streaming.
        
        Returns:
            True if started successfully
        """
        try:
            if not self.streamer.start_streaming():
                return False
            
            # Setup audio callback
            self.streamer.set_audio_callback(self._handle_streamed_audio)
            
            self._set_state(ConversationState.LISTENING)
            
            self.logger.info("Started audio streaming")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start audio streaming: {e}")
            return False
    
    def stop_audio_streaming(self):
        """Stop audio streaming."""
        try:
            self.streamer.stop_streaming()
            
            if self.state == ConversationState.LISTENING:
                self._set_state(ConversationState.ACTIVE)
            
            self.logger.info("Stopped audio streaming")
            
        except Exception as e:
            self.logger.error(f"Failed to stop audio streaming: {e}")
    
    def _handle_streamed_audio(self, audio_data: bytes):
        """Handle streamed audio data.
        
        Args:
            audio_data: Audio data from streamer
        """
        if self.state == ConversationState.LISTENING:
            # Send audio to EVI asynchronously
            if self._event_loop:
                asyncio.run_coroutine_threadsafe(
                    self.send_audio(audio_data),
                    self._event_loop
                )
    
    def set_callbacks(
        self,
        on_state_change: Optional[Callable[[ConversationState], None]] = None,
        on_response: Optional[Callable[[str, Dict[str, Any]], None]] = None,
        on_audio_response: Optional[Callable[[bytes], None]] = None,
        on_emotion_detected: Optional[Callable[[Dict[str, float]], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None
    ):
        """Set callback functions.
        
        Args:
            on_state_change: Callback for state changes
            on_response: Callback for text responses
            on_audio_response: Callback for audio responses
            on_emotion_detected: Callback for emotion detection
            on_error: Callback for errors
        """
        if on_state_change:
            self.on_state_change = on_state_change
        if on_response:
            self.on_response = on_response
        if on_audio_response:
            self.on_audio_response = on_audio_response
        if on_emotion_detected:
            self.on_emotion_detected = on_emotion_detected
        if on_error:
            self.on_error = on_error
    
    def get_metrics(self) -> ConversationMetrics:
        """Get conversation metrics.
        
        Returns:
            Current conversation metrics
        """
        return self.metrics
    
    def get_status(self) -> Dict[str, Any]:
        """Get handler status.
        
        Returns:
            Status dictionary
        """
        return {
            'state': self.state.value,
            'conversation_id': self.conversation_id,
            'client_status': self.client.status,
            'streamer_status': self.streamer.get_status(),
            'metrics': {
                'duration': self.metrics.duration,
                'total_messages': self.metrics.total_messages,
                'audio_messages': self.metrics.audio_messages,
                'text_messages': self.metrics.text_messages,
                'emotion_detections': self.metrics.emotion_detections,
                'average_response_time': self.metrics.average_response_time,
                'errors': len(self.metrics.errors)
            }
        }
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.conversation_id:
            # Run cleanup in event loop if available
            if self._event_loop and self._event_loop.is_running():
                asyncio.run_coroutine_threadsafe(
                    self.end_conversation(),
                    self._event_loop
                )
            else:
                # Create new event loop for cleanup
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(self.end_conversation())
                finally:
                    loop.close()