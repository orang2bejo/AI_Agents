"""Voice Input Module - Speech-to-Text dengan Whisper dan Voice Activity Detection

Module ini menyediakan fungsi untuk:
- Speech-to-Text menggunakan Whisper (offline)
- Voice Activity Detection (VAD)
- Push-to-talk functionality
- Audio recording dan preprocessing
"""

import asyncio
import threading
import time
from typing import Optional, Callable, Dict, Any
import logging

try:
    import sounddevice as sd
    import numpy as np
    import whisper
    import webrtcvad
except ImportError as e:
    logging.warning(f"Voice dependencies not installed: {e}")
    logging.warning("Install with: pip install sounddevice numpy openai-whisper webrtcvad")

class VoiceInput:
    """Voice Input handler dengan STT dan VAD"""
    
    def __init__(self, 
                 model_name: str = "base",
                 sample_rate: int = 16000,
                 chunk_duration: float = 0.03,  # 30ms chunks untuk VAD
                 vad_aggressiveness: int = 2,
                 silence_threshold: float = 2.0,  # detik silence sebelum stop
                 push_to_talk_key: str = "space"):
        """
        Initialize Voice Input
        
        Args:
            model_name: Whisper model (tiny, base, small, medium, large)
            sample_rate: Audio sample rate (16kHz optimal untuk Whisper)
            chunk_duration: Duration per audio chunk untuk VAD
            vad_aggressiveness: VAD aggressiveness (0-3, 3 = most aggressive)
            silence_threshold: Seconds of silence before stopping recording
            push_to_talk_key: Key untuk push-to-talk mode
        """
        self.model_name = model_name
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration
        self.chunk_size = int(sample_rate * chunk_duration)
        self.silence_threshold = silence_threshold
        self.push_to_talk_key = push_to_talk_key
        
        # Initialize components
        self.whisper_model = None
        self.vad = None
        self.is_recording = False
        self.audio_buffer = []
        self.last_speech_time = 0
        
        # Callbacks
        self.on_speech_start: Optional[Callable] = None
        self.on_speech_end: Optional[Callable] = None
        self.on_transcription: Optional[Callable[[str], None]] = None
        
        self._setup_components()
        
    def _setup_components(self):
        """Setup Whisper dan VAD components"""
        try:
            # Check if whisper is available
            if 'whisper' in globals():
                # Load Whisper model
                logging.info(f"Loading Whisper model: {self.model_name}")
                self.whisper_model = whisper.load_model(self.model_name)
            else:
                logging.warning("Whisper not available, voice recognition disabled")
                self.whisper_model = None
            
            # Setup VAD
            if 'webrtcvad' in globals():
                self.vad = webrtcvad.Vad()
                self.vad.set_mode(2)  # Aggressiveness mode
            else:
                logging.warning("WebRTC VAD not available, voice activity detection disabled")
                self.vad = None
            
            logging.info("Voice components initialized successfully")
            
        except Exception as e:
            logging.error(f"Failed to setup voice components: {e}")
            self.whisper_model = None
            self.vad = None
    
    def start_listening(self, mode: str = "vad") -> None:
        """Start listening untuk voice input
        
        Args:
            mode: "vad" untuk voice activity detection, "ptt" untuk push-to-talk
        """
        if mode == "vad":
            self._start_vad_listening()
        elif mode == "ptt":
            self._start_ptt_listening()
        else:
            raise ValueError("Mode must be 'vad' or 'ptt'")
    
    def _start_vad_listening(self):
        """Start VAD-based listening"""
        def audio_callback(indata, frames, time, status):
            if status:
                logging.warning(f"Audio callback status: {status}")
            
            # Convert to int16 untuk VAD
            audio_int16 = (indata[:, 0] * 32767).astype(np.int16)
            
            # Check voice activity
            is_speech = self.vad.is_speech(audio_int16.tobytes(), self.sample_rate)
            
            if is_speech:
                if not self.is_recording:
                    self.is_recording = True
                    self.audio_buffer = []
                    if self.on_speech_start:
                        self.on_speech_start()
                    logging.info("Speech detected, starting recording")
                
                self.audio_buffer.append(audio_int16)
                self.last_speech_time = time.time()
                
            elif self.is_recording:
                # Check if silence duration exceeded threshold
                silence_duration = time.time() - self.last_speech_time
                if silence_duration > self.silence_threshold:
                    self._process_recorded_audio()
        
        # Start audio stream
        logging.info("Starting VAD listening...")
        with sd.InputStream(callback=audio_callback,
                          channels=1,
                          samplerate=self.sample_rate,
                          blocksize=self.chunk_size):
            try:
                while True:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                logging.info("Stopping VAD listening")
    
    def _start_ptt_listening(self):
        """Start Push-to-Talk listening"""
        try:
            import keyboard
        except ImportError:
            logging.error("keyboard library required for PTT mode")
            logging.error("Install with: pip install keyboard")
            return
        
        def on_key_press():
            if not self.is_recording:
                self.is_recording = True
                self.audio_buffer = []
                if self.on_speech_start:
                    self.on_speech_start()
                logging.info("PTT activated, recording...")
                self._start_recording()
        
        def on_key_release():
            if self.is_recording:
                self._process_recorded_audio()
        
        # Setup keyboard hooks
        keyboard.on_press_key(self.push_to_talk_key, lambda _: on_key_press())
        keyboard.on_release_key(self.push_to_talk_key, lambda _: on_key_release())
        
        logging.info(f"PTT mode active. Hold '{self.push_to_talk_key}' to talk")
        keyboard.wait()  # Keep listening
    
    def _start_recording(self):
        """Start recording audio untuk PTT mode"""
        def audio_callback(indata, frames, time, status):
            if self.is_recording:
                audio_int16 = (indata[:, 0] * 32767).astype(np.int16)
                self.audio_buffer.append(audio_int16)
        
        self.stream = sd.InputStream(callback=audio_callback,
                                   channels=1,
                                   samplerate=self.sample_rate,
                                   blocksize=self.chunk_size)
        self.stream.start()
    
    def _process_recorded_audio(self):
        """Process recorded audio dengan Whisper STT"""
        if not self.audio_buffer:
            return
        
        self.is_recording = False
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
        
        if self.on_speech_end:
            self.on_speech_end()
        
        # Combine audio chunks
        audio_data = np.concatenate(self.audio_buffer)
        
        # Convert to float32 untuk Whisper
        audio_float32 = audio_data.astype(np.float32) / 32767.0
        
        # Transcribe dengan Whisper
        try:
            logging.info("Transcribing audio...")
            result = self.whisper_model.transcribe(audio_float32, language="id")
            text = result["text"].strip()
            
            if text:
                logging.info(f"Transcription: {text}")
                if self.on_transcription:
                    self.on_transcription(text)
            else:
                logging.info("No speech detected in audio")
                
        except Exception as e:
            logging.error(f"Transcription failed: {e}")
        
        # Clear buffer
        self.audio_buffer = []
    
    def stop_listening(self):
        """Stop voice input"""
        self.is_recording = False
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
        logging.info("Voice input stopped")
    
    def transcribe_file(self, audio_file_path: str) -> str:
        """Transcribe audio file
        
        Args:
            audio_file_path: Path ke audio file
            
        Returns:
            Transcribed text
        """
        try:
            result = self.whisper_model.transcribe(audio_file_path, language="id")
            return result["text"].strip()
        except Exception as e:
            logging.error(f"File transcription failed: {e}")
            return ""


# Example usage dan testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    def on_transcription(text: str):
        print(f"\n🎤 Transcription: {text}\n")
    
    def on_speech_start():
        print("🔴 Recording started...")
    
    def on_speech_end():
        print("⏹️ Recording stopped, processing...")
    
    # Initialize voice input
    voice = VoiceInput(model_name="base")
    voice.on_transcription = on_transcription
    voice.on_speech_start = on_speech_start
    voice.on_speech_end = on_speech_end
    
    print("Voice Input Test")
    print("1. VAD mode (automatic)")
    print("2. PTT mode (press space)")
    
    choice = input("Choose mode (1/2): ")
    
    try:
        if choice == "1":
            voice.start_listening("vad")
        elif choice == "2":
            voice.start_listening("ptt")
        else:
            print("Invalid choice")
    except KeyboardInterrupt:
        voice.stop_listening()
        print("\nVoice input stopped")