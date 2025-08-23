"""Voice Interface Module

Manages voice input/output interface for the Jarvis AI system,
integrating STT, TTS, and voice activity detection.
"""

import asyncio
import logging
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union, Tuple

import numpy as np
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class VoiceState(Enum):
    """Voice interface states"""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    ERROR = "error"
    DISABLED = "disabled"

class InputMode(Enum):
    """Voice input modes"""
    PUSH_TO_TALK = "push_to_talk"
    VOICE_ACTIVATION = "voice_activation"
    CONTINUOUS = "continuous"
    MANUAL = "manual"

class TTSEngine(Enum):
    """Text-to-Speech engines"""
    PIPER = "piper"
    PYTTSX3 = "pyttsx3"
    SYSTEM = "system"

class STTEngine(Enum):
    """Speech-to-Text engines"""
    WHISPER = "whisper"
    VOSK = "vosk"
    SYSTEM = "system"

class Language(Enum):
    """Supported languages"""
    ENGLISH = "en"
    INDONESIAN = "id"

@dataclass
class VoiceCommand:
    """Voice command data"""
    text: str
    confidence: float
    language: Language
    timestamp: float = field(default_factory=time.time)
    audio_duration: Optional[float] = None
    processing_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class VoiceResponse:
    """Voice response data"""
    text: str
    language: Language
    audio_file: Optional[str] = None
    duration: Optional[float] = None
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

class VoiceConfig(BaseModel):
    """Voice interface configuration"""
    # Input settings
    input_mode: InputMode = InputMode.VOICE_ACTIVATION
    stt_engine: STTEngine = STTEngine.WHISPER
    push_to_talk_key: str = "ctrl+space"
    
    # Output settings
    tts_engine: TTSEngine = TTSEngine.PIPER
    voice_enabled: bool = True
    speech_rate: float = 1.0
    speech_volume: float = 0.8
    
    # Audio settings
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024
    
    # VAD settings
    vad_enabled: bool = True
    vad_threshold: float = 0.5
    silence_timeout: float = 2.0
    min_speech_duration: float = 0.5
    
    # Language settings
    default_language: Language = Language.INDONESIAN
    auto_language_detection: bool = True
    
    # Processing settings
    max_recording_duration: float = 30.0
    audio_buffer_size: int = 5
    
class VoiceInterface:
    """Main voice interface for Jarvis AI"""
    
    def __init__(self, config: VoiceConfig = None):
        self.config = config or VoiceConfig()
        self.state = VoiceState.IDLE
        
        # Audio components
        self.audio_recorder = None
        self.audio_player = None
        self.vad_detector = None
        
        # STT/TTS engines
        self.stt_engine = None
        self.tts_engine = None
        
        # Threading and async
        self.audio_thread = None
        self.processing_thread = None
        self.is_running = False
        
        # Callbacks
        self.on_command_received: Optional[Callable[[VoiceCommand], None]] = None
        self.on_state_changed: Optional[Callable[[VoiceState], None]] = None
        self.on_error: Optional[Callable[[Exception], None]] = None
        
        # Audio buffer
        self.audio_buffer = []
        self.recording_start_time = None
        
        # Statistics
        self.stats = {
            'commands_processed': 0,
            'responses_generated': 0,
            'total_recording_time': 0.0,
            'total_processing_time': 0.0,
            'errors': 0
        }
        
        logger.info("Voice interface initialized")
    
    async def initialize(self):
        """Initialize voice interface components"""
        try:
            # Initialize audio components
            await self._initialize_audio()
            
            # Initialize STT engine
            await self._initialize_stt()
            
            # Initialize TTS engine
            await self._initialize_tts()
            
            # Initialize VAD if enabled
            if self.config.vad_enabled:
                await self._initialize_vad()
            
            logger.info("Voice interface components initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize voice interface: {e}")
            self.state = VoiceState.ERROR
            if self.on_error:
                self.on_error(e)
            raise
    
    async def _initialize_audio(self):
        """Initialize audio recording and playback"""
        try:
            import pyaudio
            
            self.audio = pyaudio.PyAudio()
            
            # Find suitable audio devices
            self.input_device = self._find_input_device()
            self.output_device = self._find_output_device()
            
            logger.info(f"Audio initialized - Input: {self.input_device}, Output: {self.output_device}")
            
        except ImportError:
            logger.warning("PyAudio not available, using alternative audio backend")
            # Fallback to alternative audio backend
            await self._initialize_alternative_audio()
    
    async def _initialize_alternative_audio(self):
        """Initialize alternative audio backend"""
        try:
            import sounddevice as sd
            self.audio_backend = 'sounddevice'
            logger.info("Using sounddevice as audio backend")
        except ImportError:
            logger.error("No suitable audio backend available")
            raise RuntimeError("No audio backend available")
    
    async def _initialize_stt(self):
        """Initialize Speech-to-Text engine"""
        if self.config.stt_engine == STTEngine.WHISPER:
            await self._initialize_whisper()
        elif self.config.stt_engine == STTEngine.VOSK:
            await self._initialize_vosk()
        else:
            await self._initialize_system_stt()
    
    async def _initialize_whisper(self):
        """Initialize Whisper STT engine"""
        try:
            import whisper
            
            # Load Whisper model
            model_size = "base"  # Can be configured
            self.whisper_model = whisper.load_model(model_size)
            
            logger.info(f"Whisper model '{model_size}' loaded")
            
        except ImportError:
            logger.error("Whisper not available")
            raise
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    async def _initialize_vosk(self):
        """Initialize Vosk STT engine"""
        try:
            import vosk
            import json
            
            # Load Vosk model (path should be configured)
            model_path = "models/vosk-model-small-id-0.22"  # Indonesian model
            if not os.path.exists(model_path):
                model_path = "models/vosk-model-small-en-us-0.15"  # English fallback
            
            self.vosk_model = vosk.Model(model_path)
            self.vosk_recognizer = vosk.KaldiRecognizer(self.vosk_model, self.config.sample_rate)
            
            logger.info(f"Vosk model loaded from {model_path}")
            
        except ImportError:
            logger.error("Vosk not available")
            raise
        except Exception as e:
            logger.error(f"Failed to load Vosk model: {e}")
            raise
    
    async def _initialize_system_stt(self):
        """Initialize system STT engine"""
        try:
            import speech_recognition as sr
            
            self.sr_recognizer = sr.Recognizer()
            self.sr_microphone = sr.Microphone()
            
            # Adjust for ambient noise
            with self.sr_microphone as source:
                self.sr_recognizer.adjust_for_ambient_noise(source)
            
            logger.info("System STT engine initialized")
            
        except ImportError:
            logger.error("SpeechRecognition not available")
            raise
    
    async def _initialize_tts(self):
        """Initialize Text-to-Speech engine"""
        if self.config.tts_engine == TTSEngine.PIPER:
            await self._initialize_piper()
        elif self.config.tts_engine == TTSEngine.PYTTSX3:
            await self._initialize_pyttsx3()
        else:
            await self._initialize_system_tts()
    
    async def _initialize_piper(self):
        """Initialize Piper TTS engine"""
        try:
            # Piper TTS initialization
            # This would typically involve loading Piper models
            self.piper_models = {
                Language.ENGLISH: "models/piper/en_US-lessac-medium.onnx",
                Language.INDONESIAN: "models/piper/id_ID-fajri-medium.onnx"
            }
            
            logger.info("Piper TTS engine initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Piper TTS: {e}")
            # Fallback to pyttsx3
            await self._initialize_pyttsx3()
    
    async def _initialize_pyttsx3(self):
        """Initialize pyttsx3 TTS engine"""
        try:
            import pyttsx3
            
            self.tts_engine_obj = pyttsx3.init()
            
            # Configure voice settings
            voices = self.tts_engine_obj.getProperty('voices')
            if voices:
                # Try to find appropriate voice for language
                for voice in voices:
                    if self.config.default_language == Language.INDONESIAN:
                        if 'indonesia' in voice.name.lower() or 'id' in voice.id.lower():
                            self.tts_engine_obj.setProperty('voice', voice.id)
                            break
                    else:
                        if 'english' in voice.name.lower() or 'en' in voice.id.lower():
                            self.tts_engine_obj.setProperty('voice', voice.id)
                            break
            
            # Set rate and volume
            self.tts_engine_obj.setProperty('rate', int(200 * self.config.speech_rate))
            self.tts_engine_obj.setProperty('volume', self.config.speech_volume)
            
            logger.info("pyttsx3 TTS engine initialized")
            
        except ImportError:
            logger.error("pyttsx3 not available")
            raise
    
    async def _initialize_system_tts(self):
        """Initialize system TTS engine"""
        # Platform-specific TTS initialization
        import platform
        
        if platform.system() == "Windows":
            await self._initialize_windows_tts()
        else:
            logger.warning("System TTS not supported on this platform")
            await self._initialize_pyttsx3()  # Fallback
    
    async def _initialize_windows_tts(self):
        """Initialize Windows SAPI TTS"""
        try:
            import win32com.client
            
            self.sapi_voice = win32com.client.Dispatch("SAPI.SpVoice")
            
            # Configure voice
            voices = self.sapi_voice.GetVoices()
            for voice in voices:
                voice_info = voice.GetDescription()
                if self.config.default_language == Language.INDONESIAN:
                    if 'indonesia' in voice_info.lower():
                        self.sapi_voice.Voice = voice
                        break
                else:
                    if 'english' in voice_info.lower():
                        self.sapi_voice.Voice = voice
                        break
            
            # Set rate and volume
            self.sapi_voice.Rate = int(self.config.speech_rate * 5)  # SAPI uses -10 to 10
            self.sapi_voice.Volume = int(self.config.speech_volume * 100)
            
            logger.info("Windows SAPI TTS initialized")
            
        except ImportError:
            logger.error("Windows SAPI not available")
            raise
    
    async def _initialize_vad(self):
        """Initialize Voice Activity Detection"""
        try:
            import webrtcvad
            
            self.vad = webrtcvad.Vad()
            self.vad.set_mode(2)  # Moderate aggressiveness
            
            logger.info("WebRTC VAD initialized")
            
        except ImportError:
            logger.warning("WebRTC VAD not available, using energy-based VAD")
            self.vad = None
    
    def _find_input_device(self) -> Optional[int]:
        """Find suitable input audio device"""
        try:
            import pyaudio
            
            for i in range(self.audio.get_device_count()):
                device_info = self.audio.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    return i
            return None
        except:
            return None
    
    def _find_output_device(self) -> Optional[int]:
        """Find suitable output audio device"""
        try:
            import pyaudio
            
            for i in range(self.audio.get_device_count()):
                device_info = self.audio.get_device_info_by_index(i)
                if device_info['maxOutputChannels'] > 0:
                    return i
            return None
        except:
            return None
    
    async def start_listening(self):
        """Start voice input listening"""
        if self.state in [VoiceState.ERROR, VoiceState.DISABLED]:
            logger.warning(f"Cannot start listening in state: {self.state}")
            return
        
        self.is_running = True
        self._change_state(VoiceState.LISTENING)
        
        if self.config.input_mode == InputMode.PUSH_TO_TALK:
            await self._start_push_to_talk_listening()
        elif self.config.input_mode == InputMode.VOICE_ACTIVATION:
            await self._start_voice_activation_listening()
        elif self.config.input_mode == InputMode.CONTINUOUS:
            await self._start_continuous_listening()
        
        logger.info(f"Started listening in {self.config.input_mode.value} mode")
    
    async def _start_push_to_talk_listening(self):
        """Start push-to-talk listening mode"""
        import keyboard
        
        def on_key_press():
            if self.state == VoiceState.LISTENING:
                asyncio.create_task(self._start_recording())
        
        def on_key_release():
            if self.state == VoiceState.LISTENING:
                asyncio.create_task(self._stop_recording())
        
        keyboard.on_press_key(self.config.push_to_talk_key, lambda _: on_key_press())
        keyboard.on_release_key(self.config.push_to_talk_key, lambda _: on_key_release())
    
    async def _start_voice_activation_listening(self):
        """Start voice activation listening mode"""
        self.audio_thread = threading.Thread(target=self._voice_activation_loop, daemon=True)
        self.audio_thread.start()
    
    async def _start_continuous_listening(self):
        """Start continuous listening mode"""
        self.audio_thread = threading.Thread(target=self._continuous_listening_loop, daemon=True)
        self.audio_thread.start()
    
    def _voice_activation_loop(self):
        """Voice activation detection loop"""
        import pyaudio
        
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=self.config.channels,
            rate=self.config.sample_rate,
            input=True,
            input_device_index=self.input_device,
            frames_per_buffer=self.config.chunk_size
        )
        
        silence_start = None
        is_speaking = False
        
        try:
            while self.is_running:
                data = stream.read(self.config.chunk_size, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.int16)
                
                # Voice activity detection
                is_voice = self._detect_voice_activity(audio_data)
                
                if is_voice and not is_speaking:
                    # Start of speech detected
                    is_speaking = True
                    silence_start = None
                    asyncio.run_coroutine_threadsafe(
                        self._start_recording(), 
                        asyncio.get_event_loop()
                    )
                
                elif not is_voice and is_speaking:
                    # Potential end of speech
                    if silence_start is None:
                        silence_start = time.time()
                    elif time.time() - silence_start > self.config.silence_timeout:
                        # End of speech confirmed
                        is_speaking = False
                        silence_start = None
                        asyncio.run_coroutine_threadsafe(
                            self._stop_recording(),
                            asyncio.get_event_loop()
                        )
                
                elif is_voice and is_speaking:
                    # Continue recording
                    silence_start = None
                    self.audio_buffer.append(audio_data)
                
                time.sleep(0.01)  # Small delay to prevent excessive CPU usage
        
        finally:
            stream.stop_stream()
            stream.close()
    
    def _continuous_listening_loop(self):
        """Continuous listening loop"""
        # Similar to voice activation but without VAD
        # Records continuously and processes in chunks
        pass
    
    def _detect_voice_activity(self, audio_data: np.ndarray) -> bool:
        """Detect voice activity in audio data"""
        if self.vad:
            # Use WebRTC VAD
            try:
                # Convert to bytes for WebRTC VAD
                audio_bytes = audio_data.tobytes()
                return self.vad.is_speech(audio_bytes, self.config.sample_rate)
            except:
                pass
        
        # Fallback to energy-based VAD
        energy = np.sqrt(np.mean(audio_data.astype(np.float32) ** 2))
        return energy > self.config.vad_threshold
    
    async def _start_recording(self):
        """Start audio recording"""
        self.recording_start_time = time.time()
        self.audio_buffer.clear()
        logger.debug("Started recording")
    
    async def _stop_recording(self):
        """Stop audio recording and process"""
        if not self.recording_start_time:
            return
        
        recording_duration = time.time() - self.recording_start_time
        
        if recording_duration < self.config.min_speech_duration:
            logger.debug("Recording too short, ignoring")
            return
        
        self._change_state(VoiceState.PROCESSING)
        
        # Process audio in background
        self.processing_thread = threading.Thread(
            target=self._process_audio_async,
            args=(self.audio_buffer.copy(), recording_duration),
            daemon=True
        )
        self.processing_thread.start()
        
        logger.debug(f"Stopped recording, duration: {recording_duration:.2f}s")
    
    def _process_audio_async(self, audio_data: List[np.ndarray], duration: float):
        """Process audio data asynchronously"""
        try:
            start_time = time.time()
            
            # Combine audio chunks
            if audio_data:
                combined_audio = np.concatenate(audio_data)
            else:
                logger.warning("No audio data to process")
                return
            
            # Perform STT
            text, confidence, language = self._perform_stt(combined_audio)
            
            processing_time = time.time() - start_time
            
            if text and text.strip():
                # Create voice command
                command = VoiceCommand(
                    text=text.strip(),
                    confidence=confidence,
                    language=language,
                    audio_duration=duration,
                    processing_time=processing_time
                )
                
                # Update statistics
                self.stats['commands_processed'] += 1
                self.stats['total_recording_time'] += duration
                self.stats['total_processing_time'] += processing_time
                
                # Notify callback
                if self.on_command_received:
                    self.on_command_received(command)
                
                logger.info(f"Command received: '{text}' (confidence: {confidence:.2f})")
            
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            self.stats['errors'] += 1
            if self.on_error:
                self.on_error(e)
        
        finally:
            self._change_state(VoiceState.LISTENING)
    
    def _perform_stt(self, audio_data: np.ndarray) -> Tuple[str, float, Language]:
        """Perform speech-to-text conversion"""
        if self.config.stt_engine == STTEngine.WHISPER:
            return self._whisper_stt(audio_data)
        elif self.config.stt_engine == STTEngine.VOSK:
            return self._vosk_stt(audio_data)
        else:
            return self._system_stt(audio_data)
    
    def _whisper_stt(self, audio_data: np.ndarray) -> Tuple[str, float, Language]:
        """Perform STT using Whisper"""
        try:
            # Convert to float32 and normalize
            audio_float = audio_data.astype(np.float32) / 32768.0
            
            # Perform transcription
            result = self.whisper_model.transcribe(
                audio_float,
                language=self.config.default_language.value if not self.config.auto_language_detection else None
            )
            
            text = result['text']
            confidence = 1.0  # Whisper doesn't provide confidence scores
            
            # Detect language
            detected_language = Language(result.get('language', self.config.default_language.value))
            
            return text, confidence, detected_language
            
        except Exception as e:
            logger.error(f"Whisper STT error: {e}")
            return "", 0.0, self.config.default_language
    
    def _vosk_stt(self, audio_data: np.ndarray) -> Tuple[str, float, Language]:
        """Perform STT using Vosk"""
        try:
            import json
            
            # Convert to bytes
            audio_bytes = audio_data.tobytes()
            
            # Process with Vosk
            if self.vosk_recognizer.AcceptWaveform(audio_bytes):
                result = json.loads(self.vosk_recognizer.Result())
                text = result.get('text', '')
                confidence = result.get('confidence', 0.0)
            else:
                partial_result = json.loads(self.vosk_recognizer.PartialResult())
                text = partial_result.get('partial', '')
                confidence = 0.5  # Lower confidence for partial results
            
            return text, confidence, self.config.default_language
            
        except Exception as e:
            logger.error(f"Vosk STT error: {e}")
            return "", 0.0, self.config.default_language
    
    def _system_stt(self, audio_data: np.ndarray) -> Tuple[str, float, Language]:
        """Perform STT using system recognition"""
        try:
            import speech_recognition as sr
            import io
            import wave
            
            # Convert numpy array to audio file in memory
            audio_buffer = io.BytesIO()
            with wave.open(audio_buffer, 'wb') as wav_file:
                wav_file.setnchannels(self.config.channels)
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(self.config.sample_rate)
                wav_file.writeframes(audio_data.tobytes())
            
            audio_buffer.seek(0)
            
            # Create AudioFile from buffer
            with sr.AudioFile(audio_buffer) as source:
                audio = self.sr_recognizer.record(source)
            
            # Perform recognition
            text = self.sr_recognizer.recognize_google(
                audio, 
                language=self.config.default_language.value
            )
            
            return text, 0.8, self.config.default_language  # Assume good confidence
            
        except sr.UnknownValueError:
            logger.debug("System STT could not understand audio")
            return "", 0.0, self.config.default_language
        except Exception as e:
            logger.error(f"System STT error: {e}")
            return "", 0.0, self.config.default_language
    
    async def speak(self, text: str, language: Language = None) -> VoiceResponse:
        """Generate speech from text"""
        if not self.config.voice_enabled:
            return VoiceResponse(text=text, language=language or self.config.default_language)
        
        language = language or self.config.default_language
        
        self._change_state(VoiceState.SPEAKING)
        
        try:
            start_time = time.time()
            
            if self.config.tts_engine == TTSEngine.PIPER:
                audio_file = await self._piper_tts(text, language)
            elif self.config.tts_engine == TTSEngine.PYTTSX3:
                audio_file = await self._pyttsx3_tts(text, language)
            else:
                audio_file = await self._system_tts(text, language)
            
            duration = time.time() - start_time
            
            response = VoiceResponse(
                text=text,
                language=language,
                audio_file=audio_file,
                duration=duration
            )
            
            self.stats['responses_generated'] += 1
            
            logger.info(f"Speech generated: '{text[:50]}...' (duration: {duration:.2f}s)")
            
            return response
            
        except Exception as e:
            logger.error(f"TTS error: {e}")
            self.stats['errors'] += 1
            if self.on_error:
                self.on_error(e)
            
            return VoiceResponse(text=text, language=language)
        
        finally:
            self._change_state(VoiceState.LISTENING if self.is_running else VoiceState.IDLE)
    
    async def _piper_tts(self, text: str, language: Language) -> Optional[str]:
        """Generate speech using Piper TTS"""
        try:
            # Piper TTS implementation
            # This would involve calling Piper with the appropriate model
            model_path = self.piper_models.get(language)
            if not model_path:
                logger.warning(f"No Piper model for language {language.value}")
                return None
            
            # Generate audio file
            output_file = f"temp_audio_{int(time.time())}.wav"
            
            # Piper command would be executed here
            # For now, return placeholder
            return output_file
            
        except Exception as e:
            logger.error(f"Piper TTS error: {e}")
            return None
    
    async def _pyttsx3_tts(self, text: str, language: Language) -> Optional[str]:
        """Generate speech using pyttsx3"""
        try:
            # Save to file
            output_file = f"temp_audio_{int(time.time())}.wav"
            self.tts_engine_obj.save_to_file(text, output_file)
            self.tts_engine_obj.runAndWait()
            
            return output_file
            
        except Exception as e:
            logger.error(f"pyttsx3 TTS error: {e}")
            return None
    
    async def _system_tts(self, text: str, language: Language) -> Optional[str]:
        """Generate speech using system TTS"""
        try:
            if hasattr(self, 'sapi_voice'):
                # Windows SAPI
                output_file = f"temp_audio_{int(time.time())}.wav"
                file_stream = win32com.client.Dispatch("SAPI.SpFileStream")
                file_stream.Open(output_file, 3)
                self.sapi_voice.AudioOutputStream = file_stream
                self.sapi_voice.Speak(text)
                file_stream.Close()
                return output_file
            
            return None
            
        except Exception as e:
            logger.error(f"System TTS error: {e}")
            return None
    
    def _change_state(self, new_state: VoiceState):
        """Change voice interface state"""
        if self.state != new_state:
            old_state = self.state
            self.state = new_state
            
            logger.debug(f"Voice state changed: {old_state.value} -> {new_state.value}")
            
            if self.on_state_changed:
                self.on_state_changed(new_state)
    
    async def stop_listening(self):
        """Stop voice input listening"""
        self.is_running = False
        
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(timeout=2.0)
        
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=2.0)
        
        self._change_state(VoiceState.IDLE)
        logger.info("Stopped listening")
    
    async def shutdown(self):
        """Shutdown voice interface"""
        await self.stop_listening()
        
        # Cleanup audio resources
        if hasattr(self, 'audio'):
            self.audio.terminate()
        
        self._change_state(VoiceState.DISABLED)
        logger.info("Voice interface shutdown")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get voice interface statistics"""
        return {
            **self.stats,
            'current_state': self.state.value,
            'is_running': self.is_running,
            'config': {
                'input_mode': self.config.input_mode.value,
                'stt_engine': self.config.stt_engine.value,
                'tts_engine': self.config.tts_engine.value,
                'language': self.config.default_language.value
            }
        }
    
    def update_config(self, **kwargs):
        """Update voice interface configuration"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                logger.info(f"Config updated: {key} = {value}")