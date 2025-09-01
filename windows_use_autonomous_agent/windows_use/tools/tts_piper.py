"""TTS Piper Module - Text-to-Speech menggunakan Piper (offline)

Module ini menyediakan fungsi untuk:
- Text-to-Speech menggunakan Piper (ringan dan cepat)
- Voice synthesis dalam bahasa Indonesia
- Audio playback dan file output
- Voice configuration dan customization
"""

import asyncio
import logging
import os
import tempfile
import threading
from pathlib import Path
from typing import Optional, Dict, Any, List

import numpy as np

try:
    import sounddevice as sd
    import wave
except ImportError as e:
    logging.warning(f"Audio dependencies not installed: {e}")
    logging.warning("Install with: pip install sounddevice numpy")

try:
    # Piper TTS - install dengan: pip install piper-tts
    from piper import PiperVoice
except ImportError:
    logging.warning("Piper TTS not installed")
    logging.warning("Install with: pip install piper-tts")
    PiperVoice = None

class TTSPiper:
    """Text-to-Speech menggunakan Piper"""
    
    def __init__(self, 
                 voice_model: str = "id_ID-fajri-medium",
                 sample_rate: int = 22050,
                 speed: float = 1.0,
                 volume: float = 0.8):
        """
        Initialize TTS Piper
        
        Args:
            voice_model: Piper voice model untuk bahasa Indonesia
            sample_rate: Audio sample rate
            speed: Speech speed multiplier (0.5-2.0)
            volume: Audio volume (0.0-1.0)
        """
        self.voice_model = voice_model
        self.sample_rate = sample_rate
        self.speed = speed
        self.volume = volume
        
        self.voice = None
        self.is_speaking = False
        
        # Voice models yang tersedia untuk bahasa Indonesia
        self.available_voices = {
            "id_ID-fajri-medium": "Suara pria Indonesia (medium quality)",
            "id_ID-fajri-low": "Suara pria Indonesia (low quality, faster)",
            # Tambah voice models lain jika tersedia
        }
        
        self._setup_voice()
    
    def _setup_voice(self):
        """Setup Piper voice model"""
        if PiperVoice is None:
            logging.error("Piper TTS not available")
            return
        
        try:
            # Download dan load voice model jika belum ada
            model_path = self._get_or_download_model()
            if model_path:
                self.voice = PiperVoice.load(model_path)
                logging.info(f"Piper voice loaded: {self.voice_model}")
            else:
                logging.error(f"Failed to load voice model: {self.voice_model}")
                
        except Exception as e:
            logging.error(f"Failed to setup Piper voice: {e}")
    
    def _get_or_download_model(self) -> Optional[str]:
        """Get atau download voice model
        
        Returns:
            Path ke model file atau None jika gagal
        """
        # Implementasi sederhana - dalam production, ini bisa download dari Piper repository
        models_dir = Path.home() / ".piper" / "voices"
        models_dir.mkdir(parents=True, exist_ok=True)
        
        model_file = models_dir / f"{self.voice_model}.onnx"
        config_file = models_dir / f"{self.voice_model}.onnx.json"
        
        if model_file.exists() and config_file.exists():
            return str(model_file)
        
        # Fallback: gunakan voice model default jika ada
        logging.warning(f"Voice model {self.voice_model} not found")
        logging.warning("Please download Piper voice models manually")
        logging.warning("See: https://github.com/rhasspy/piper/releases")
        
        return None
    
    def speak(self, text: str, blocking: bool = True) -> bool:
        """Speak text menggunakan TTS
        
        Args:
            text: Text yang akan diucapkan
            blocking: Jika True, tunggu sampai selesai bicara
            
        Returns:
            True jika berhasil, False jika gagal
        """
        if not self.voice:
            logging.error("Voice model not loaded")
            return False
        
        if not text.strip():
            return False
        
        if blocking:
            return self._speak_sync(text)
        else:
            thread = threading.Thread(target=self._speak_sync, args=(text,))
            thread.daemon = True
            thread.start()
            return True
    
    def _speak_sync(self, text: str) -> bool:
        """Synchronous speech synthesis dan playback"""
        try:
            self.is_speaking = True
            
            # Generate audio dari text
            audio_data = self._synthesize_audio(text)
            if audio_data is None:
                return False
            
            # Play audio
            self._play_audio(audio_data)
            
            return True
            
        except Exception as e:
            logging.error(f"Speech synthesis failed: {e}")
            return False
        finally:
            self.is_speaking = False
    
    def _synthesize_audio(self, text: str) -> Optional[np.ndarray]:
        """Synthesize audio dari text
        
        Args:
            text: Input text
            
        Returns:
            Audio data sebagai numpy array atau None jika gagal
        """
        try:
            # Preprocess text
            text = self._preprocess_text(text)
            
            # Generate audio dengan Piper
            audio_stream = self.voice.synthesize(text)
            
            # Convert ke numpy array
            audio_data = np.array(list(audio_stream), dtype=np.float32)
            
            # Apply speed dan volume adjustments
            if self.speed != 1.0:
                audio_data = self._adjust_speed(audio_data)
            
            audio_data = audio_data * self.volume
            
            return audio_data
            
        except Exception as e:
            logging.error(f"Audio synthesis failed: {e}")
            return None
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text untuk TTS
        
        Args:
            text: Raw text
            
        Returns:
            Processed text
        """
        # Normalisasi text untuk bahasa Indonesia
        text = text.strip()
        
        # Replace common abbreviations
        replacements = {
            "&": "dan",
            "%": "persen",
            "@": "at",
            "#": "hashtag",
            "$": "dollar",
            "€": "euro",
            "£": "pound",
            "¥": "yen",
            "₹": "rupee",
            "Rp": "rupiah",
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def _adjust_speed(self, audio_data: np.ndarray) -> np.ndarray:
        """Adjust speech speed
        
        Args:
            audio_data: Original audio data
            
        Returns:
            Speed-adjusted audio data
        """
        # Simple speed adjustment dengan resampling
        # Untuk implementasi yang lebih baik, gunakan librosa atau similar
        if self.speed == 1.0:
            return audio_data
        
        # Resample untuk mengubah speed
        new_length = int(len(audio_data) / self.speed)
        indices = np.linspace(0, len(audio_data) - 1, new_length)
        return np.interp(indices, np.arange(len(audio_data)), audio_data)
    
    def _play_audio(self, audio_data: np.ndarray):
        """Play audio data
        
        Args:
            audio_data: Audio data untuk diplay
        """
        try:
            # Play audio menggunakan sounddevice
            sd.play(audio_data, samplerate=self.sample_rate)
            sd.wait()  # Wait sampai selesai
            
        except Exception as e:
            logging.error(f"Audio playback failed: {e}")
    
    def save_to_file(self, text: str, output_path: str) -> bool:
        """Save synthesized speech ke file
        
        Args:
            text: Text yang akan di-synthesize
            output_path: Path output file (.wav)
            
        Returns:
            True jika berhasil, False jika gagal
        """
        try:
            audio_data = self._synthesize_audio(text)
            if audio_data is None:
                return False
            
            # Convert ke int16 untuk WAV file
            audio_int16 = (audio_data * 32767).astype(np.int16)
            
            # Save ke WAV file
            with wave.open(output_path, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(audio_int16.tobytes())
            
            logging.info(f"Audio saved to: {output_path}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to save audio: {e}")
            return False
    
    def stop_speaking(self):
        """Stop current speech"""
        try:
            sd.stop()
            self.is_speaking = False
            logging.info("Speech stopped")
        except Exception as e:
            logging.error(f"Failed to stop speech: {e}")
    
    def set_voice(self, voice_model: str) -> bool:
        """Change voice model
        
        Args:
            voice_model: New voice model name
            
        Returns:
            True jika berhasil, False jika gagal
        """
        if voice_model == self.voice_model:
            return True
        
        old_model = self.voice_model
        self.voice_model = voice_model
        
        try:
            self._setup_voice()
            if self.voice:
                logging.info(f"Voice changed from {old_model} to {voice_model}")
                return True
            else:
                # Rollback jika gagal
                self.voice_model = old_model
                self._setup_voice()
                return False
                
        except Exception as e:
            logging.error(f"Failed to change voice: {e}")
            # Rollback
            self.voice_model = old_model
            self._setup_voice()
            return False
    
    def get_available_voices(self) -> Dict[str, str]:
        """Get list voice models yang tersedia
        
        Returns:
            Dictionary voice models dan descriptions
        """
        return self.available_voices.copy()
    
    def is_voice_available(self) -> bool:
        """Check apakah voice model tersedia
        
        Returns:
            True jika voice tersedia
        """
        return self.voice is not None


# Fallback TTS menggunakan Windows SAPI jika Piper tidak tersedia
class TTSFallback:
    """Fallback TTS menggunakan Windows SAPI"""
    
    def __init__(self, rate: int = 0, volume: float = 0.8):
        self.rate = rate  # -10 to 10
        self.volume = volume  # 0.0 to 1.0
        self.is_speaking = False
        
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150 + (rate * 25))
            self.engine.setProperty('volume', volume)
            
            # Set Indonesian voice jika tersedia
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if 'indonesia' in voice.name.lower() or 'id' in voice.id.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
                    
        except ImportError:
            logging.error("pyttsx3 not installed. Install with: pip install pyttsx3")
            self.engine = None
    
    def speak(self, text: str, blocking: bool = True) -> bool:
        if not self.engine or not text.strip():
            return False
        
        try:
            self.is_speaking = True
            if blocking:
                self.engine.say(text)
                self.engine.runAndWait()
            else:
                thread = threading.Thread(target=self._speak_async, args=(text,))
                thread.daemon = True
                thread.start()
            return True
        except Exception as e:
            logging.error(f"Fallback TTS failed: {e}")
            return False
        finally:
            if blocking:
                self.is_speaking = False
    
    def _speak_async(self, text: str):
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        finally:
            self.is_speaking = False
    
    def stop_speaking(self):
        if self.engine:
            self.engine.stop()
            self.is_speaking = False


# Factory function untuk create TTS instance
def create_tts(prefer_piper: bool = True, **kwargs) -> Any:
    """Create TTS instance
    
    Args:
        prefer_piper: Prefer Piper over fallback TTS
        **kwargs: Arguments untuk TTS constructor
        
    Returns:
        TTS instance (TTSPiper atau TTSFallback)
    """
    if prefer_piper and PiperVoice is not None:
        tts = TTSPiper(**kwargs)
        if tts.is_voice_available():
            return tts
    
    # Fallback ke Windows SAPI
    logging.info("Using fallback TTS (Windows SAPI)")
    return TTSFallback(**kwargs)


# Example usage dan testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("TTS Piper Test")
    print("1. Piper TTS (preferred)")
    print("2. Fallback TTS (Windows SAPI)")
    
    choice = input("Choose TTS engine (1/2): ")
    
    if choice == "1":
        tts = TTSPiper()
    elif choice == "2":
        tts = TTSFallback()
    else:
        tts = create_tts()
    
    # Test speech
    test_texts = [
        "Halo, saya adalah asisten suara Windows.",
        "Saya dapat membantu Anda mengendalikan komputer dengan suara.",
        "Silakan berikan perintah Anda."
    ]
    
    for text in test_texts:
        print(f"Speaking: {text}")
        success = tts.speak(text, blocking=True)
        if not success:
            print("Failed to speak")
            break
        
        import time
        time.sleep(0.5)
    
    print("TTS test completed")