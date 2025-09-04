"""Hume AI EVI Audio Streamer.

This module provides audio streaming capabilities for EVI integration,
including real-time audio capture, processing, and voice activity detection.
"""

import asyncio
import logging
import threading
import time
import queue
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
import numpy as np

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False
    sd = None

try:
    import webrtcvad
    WEBRTCVAD_AVAILABLE = True
except ImportError:
    WEBRTCVAD_AVAILABLE = False
    webrtcvad = None

from .evi_config import EVIConfig
from ..utils.error_handling import handle_errors


@dataclass
class AudioChunk:
    """Represents an audio chunk."""
    data: np.ndarray
    timestamp: float
    sample_rate: int
    channels: int
    is_speech: bool = False
    volume_level: float = 0.0


class VoiceActivityDetector:
    """Voice Activity Detection using WebRTC VAD."""
    
    def __init__(self, sample_rate: int = 16000, aggressiveness: int = 2):
        """Initialize VAD.
        
        Args:
            sample_rate: Audio sample rate
            aggressiveness: VAD aggressiveness (0-3)
        """
        self.sample_rate = sample_rate
        self.aggressiveness = aggressiveness
        self.vad = None
        
        if WEBRTCVAD_AVAILABLE:
            self.vad = webrtcvad.Vad(aggressiveness)
        else:
            logging.warning("WebRTC VAD not available, using simple volume-based detection")
    
    def is_speech(self, audio_data: bytes, sample_rate: int) -> bool:
        """Detect if audio contains speech.
        
        Args:
            audio_data: Audio data bytes
            sample_rate: Sample rate
            
        Returns:
            True if speech detected
        """
        if self.vad and sample_rate in [8000, 16000, 32000, 48000]:
            try:
                # WebRTC VAD requires specific frame sizes
                frame_duration = 30  # ms
                frame_size = int(sample_rate * frame_duration / 1000)
                
                if len(audio_data) >= frame_size * 2:  # 2 bytes per sample
                    frame = audio_data[:frame_size * 2]
                    return self.vad.is_speech(frame, sample_rate)
            except Exception as e:
                logging.debug(f"VAD error: {e}")
        
        # Fallback to volume-based detection
        return self._volume_based_detection(audio_data)
    
    def _volume_based_detection(self, audio_data: bytes, threshold: float = 0.01) -> bool:
        """Simple volume-based speech detection.
        
        Args:
            audio_data: Audio data bytes
            threshold: Volume threshold
            
        Returns:
            True if volume above threshold
        """
        try:
            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            # Calculate RMS volume
            rms = np.sqrt(np.mean(audio_array.astype(np.float32) ** 2))
            normalized_rms = rms / 32768.0  # Normalize to 0-1
            
            return normalized_rms > threshold
        except Exception:
            return False


class EVIStreamer:
    """Audio streamer for EVI integration."""
    
    def __init__(self, config: EVIConfig):
        """Initialize EVI streamer.
        
        Args:
            config: EVI configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Audio settings
        self.sample_rate = config.sample_rate
        self.channels = config.channels
        self.chunk_size = config.chunk_size
        
        # Components
        self.vad = VoiceActivityDetector(self.sample_rate)
        
        # State
        self.is_streaming = False
        self.is_recording = False
        
        # Threading
        self._stream_thread: Optional[threading.Thread] = None
        self._audio_queue = queue.Queue(maxsize=100)
        
        # Callbacks
        self.audio_callback: Optional[Callable[[bytes], None]] = None
        self.speech_start_callback: Optional[Callable[[], None]] = None
        self.speech_end_callback: Optional[Callable[[], None]] = None
        
        # Audio stream
        self._input_stream: Optional[sd.InputStream] = None
        
        # Speech detection state
        self._speech_active = False
        self._silence_start = None
        self._speech_buffer = []
        
        # Check audio availability
        if not SOUNDDEVICE_AVAILABLE:
            self.logger.warning("sounddevice not available, audio streaming disabled")
    
    def start_streaming(self) -> bool:
        """Start audio streaming.
        
        Returns:
            True if started successfully
        """
        if not SOUNDDEVICE_AVAILABLE:
            self.logger.error("Cannot start streaming: sounddevice not available")
            return False
        
        if self.is_streaming:
            self.logger.warning("Streaming already active")
            return True
        
        try:
            # Create audio stream
            self._input_stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.int16,
                blocksize=self.chunk_size,
                callback=self._audio_callback
            )
            
            # Start stream
            self._input_stream.start()
            
            # Start processing thread
            self.is_streaming = True
            self._stream_thread = threading.Thread(
                target=self._process_audio_stream,
                daemon=True
            )
            self._stream_thread.start()
            
            self.logger.info("Started audio streaming")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start streaming: {e}")
            return False
    
    def stop_streaming(self):
        """Stop audio streaming."""
        self.is_streaming = False
        
        if self._input_stream:
            try:
                self._input_stream.stop()
                self._input_stream.close()
            except Exception as e:
                self.logger.error(f"Error stopping audio stream: {e}")
            finally:
                self._input_stream = None
        
        if self._stream_thread and self._stream_thread.is_alive():
            self._stream_thread.join(timeout=1.0)
        
        # Clear queue
        while not self._audio_queue.empty():
            try:
                self._audio_queue.get_nowait()
            except queue.Empty:
                break
        
        self.logger.info("Stopped audio streaming")
    
    def _audio_callback(self, indata: np.ndarray, frames: int, time_info, status):
        """Audio input callback.
        
        Args:
            indata: Input audio data
            frames: Number of frames
            time_info: Timing information
            status: Stream status
        """
        if status:
            self.logger.warning(f"Audio callback status: {status}")
        
        if not self.is_streaming:
            return
        
        try:
            # Create audio chunk
            chunk = AudioChunk(
                data=indata.copy(),
                timestamp=time.time(),
                sample_rate=self.sample_rate,
                channels=self.channels
            )
            
            # Calculate volume level
            chunk.volume_level = np.sqrt(np.mean(indata.astype(np.float32) ** 2))
            
            # Add to queue
            if not self._audio_queue.full():
                self._audio_queue.put(chunk)
            else:
                self.logger.warning("Audio queue full, dropping chunk")
                
        except Exception as e:
            self.logger.error(f"Error in audio callback: {e}")
    
    def _process_audio_stream(self):
        """Process audio stream in background thread."""
        self.logger.info("Started audio processing thread")
        
        while self.is_streaming:
            try:
                # Get audio chunk with timeout
                chunk = self._audio_queue.get(timeout=0.1)
                
                # Process chunk
                self._process_audio_chunk(chunk)
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error processing audio: {e}")
        
        self.logger.info("Audio processing thread stopped")
    
    def _process_audio_chunk(self, chunk: AudioChunk):
        """Process individual audio chunk.
        
        Args:
            chunk: Audio chunk to process
        """
        # Convert to bytes
        audio_bytes = chunk.data.astype(np.int16).tobytes()
        
        # Detect speech
        chunk.is_speech = self.vad.is_speech(audio_bytes, chunk.sample_rate)
        
        # Handle speech detection
        self._handle_speech_detection(chunk)
        
        # Send audio if callback is set
        if self.audio_callback and chunk.is_speech:
            self.audio_callback(audio_bytes)
    
    def _handle_speech_detection(self, chunk: AudioChunk):
        """Handle speech detection logic.
        
        Args:
            chunk: Audio chunk with speech detection
        """
        current_time = chunk.timestamp
        
        if chunk.is_speech:
            # Speech detected
            if not self._speech_active:
                # Speech started
                self._speech_active = True
                self._silence_start = None
                
                if self.speech_start_callback:
                    self.speech_start_callback()
                
                self.logger.debug("Speech started")
            
            # Add to speech buffer
            self._speech_buffer.append(chunk)
            
            # Limit buffer size
            if len(self._speech_buffer) > 100:  # Keep last 100 chunks
                self._speech_buffer.pop(0)
        
        else:
            # No speech detected
            if self._speech_active:
                # Start silence timer
                if self._silence_start is None:
                    self._silence_start = current_time
                
                # Check if silence timeout reached
                elif current_time - self._silence_start > self.config.silence_timeout:
                    # Speech ended
                    self._speech_active = False
                    self._silence_start = None
                    
                    if self.speech_end_callback:
                        self.speech_end_callback()
                    
                    self.logger.debug("Speech ended")
                    
                    # Clear speech buffer
                    self._speech_buffer.clear()
    
    def set_audio_callback(self, callback: Callable[[bytes], None]):
        """Set audio data callback.
        
        Args:
            callback: Function to call with audio data
        """
        self.audio_callback = callback
    
    def set_speech_callbacks(
        self,
        on_speech_start: Optional[Callable[[], None]] = None,
        on_speech_end: Optional[Callable[[], None]] = None
    ):
        """Set speech detection callbacks.
        
        Args:
            on_speech_start: Callback for speech start
            on_speech_end: Callback for speech end
        """
        if on_speech_start:
            self.speech_start_callback = on_speech_start
        if on_speech_end:
            self.speech_end_callback = on_speech_end
    
    def get_audio_devices(self) -> Dict[str, Any]:
        """Get available audio devices.
        
        Returns:
            Dictionary of available devices
        """
        if not SOUNDDEVICE_AVAILABLE:
            return {"error": "sounddevice not available"}
        
        try:
            devices = sd.query_devices()
            return {
                "devices": devices,
                "default_input": sd.default.device[0],
                "default_output": sd.default.device[1]
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """Get streamer status.
        
        Returns:
            Status dictionary
        """
        return {
            "streaming": self.is_streaming,
            "recording": self.is_recording,
            "speech_active": self._speech_active,
            "queue_size": self._audio_queue.qsize(),
            "buffer_size": len(self._speech_buffer),
            "sounddevice_available": SOUNDDEVICE_AVAILABLE,
            "webrtcvad_available": WEBRTCVAD_AVAILABLE,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "chunk_size": self.chunk_size
        }
    
    def __del__(self):
        """Cleanup on destruction."""
        if self.is_streaming:
            self.stop_streaming()