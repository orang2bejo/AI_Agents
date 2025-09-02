"""Jarvis Personality Engine

Implements the sophisticated personality and response patterns of Jarvis,
Tony Stark's AI assistant, with dual language support and adaptive behavior.
"""

import logging
import random
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any

from pydantic import BaseModel

logger = logging.getLogger(__name__)

class PersonalityTrait(Enum):
    """Jarvis personality traits"""
    SOPHISTICATED = "sophisticated"
    HELPFUL = "helpful"
    WITTY = "witty"
    LOYAL = "loyal"
    EFFICIENT = "efficient"
    PROACTIVE = "proactive"
    RESPECTFUL = "respectful"
    INTELLIGENT = "intelligent"

class ResponseTone(Enum):
    """Response tone variations"""
    FORMAL = "formal"
    CASUAL = "casual"
    WITTY = "witty"
    URGENT = "urgent"
    REASSURING = "reassuring"
    INFORMATIVE = "informative"

class Language(Enum):
    """Supported languages"""
    ENGLISH = "en"
    INDONESIAN = "id"

@dataclass
class PersonalityState:
    """Current personality state"""
    mood: str = "neutral"
    energy_level: float = 1.0
    formality_level: float = 0.7
    wit_level: float = 0.5
    proactivity: float = 0.8
    last_interaction: Optional[datetime] = None
    interaction_count: int = 0
    user_preferences: Dict[str, Any] = field(default_factory=dict)

class PersonalityConfig(BaseModel):
    """Personality configuration"""
    # Core traits
    default_traits: List[PersonalityTrait] = [
        PersonalityTrait.SOPHISTICATED,
        PersonalityTrait.HELPFUL,
        PersonalityTrait.EFFICIENT,
        PersonalityTrait.RESPECTFUL
    ]
    
    # Response settings
    default_tone: ResponseTone = ResponseTone.FORMAL
    wit_frequency: float = 0.3  # How often to use witty responses
    formality_adaptation: bool = True
    
    # Language settings
    primary_language: Language = Language.INDONESIAN
    secondary_language: Language = Language.ENGLISH
    auto_language_detection: bool = True
    
    # Behavioral settings
    proactive_suggestions: bool = True
    learning_enabled: bool = True
    memory_retention_days: int = 30
    
    # Greeting patterns
    morning_greetings: bool = True
    contextual_responses: bool = True
    
class JarvisPersonality:
    """Jarvis personality engine with sophisticated response generation"""
    
    def __init__(self, config: PersonalityConfig = None):
        self.config = config or PersonalityConfig()
        self.state = PersonalityState()
        self.response_templates = self._load_response_templates()
        self.conversation_history = []
        
        logger.info("Jarvis personality engine initialized")
    
    def _load_response_templates(self) -> Dict[str, Dict[str, List[str]]]:
        """Load response templates for different scenarios"""
        return {
            "greetings": {
                "en": [
                    "Good {time_of_day}, sir. How may I assist you today?",
                    "Welcome back, sir. I'm at your service.",
                    "Good {time_of_day}. I trust you're well?",
                    "At your service, sir. What can I help you with?",
                    "Good {time_of_day}, sir. Ready to tackle the day?"
                ],
                "id": [
                    "Selamat {time_of_day}, Pak. Bagaimana saya bisa membantu hari ini?",
                    "Selamat datang kembali, Pak. Saya siap melayani.",
                    "Selamat {time_of_day}. Semoga Bapak dalam keadaan baik?",
                    "Siap melayani, Pak. Ada yang bisa saya bantu?",
                    "Selamat {time_of_day}, Pak. Siap menghadapi hari ini?"
                ]
            },
            "acknowledgments": {
                "en": [
                    "Understood, sir.",
                    "Right away, sir.",
                    "Consider it done.",
                    "Certainly, sir.",
                    "I'm on it.",
                    "Absolutely, sir.",
                    "Of course."
                ],
                "id": [
                    "Baik, Pak.",
                    "Segera, Pak.",
                    "Akan saya laksanakan.",
                    "Tentu, Pak.",
                    "Saya kerjakan.",
                    "Pasti, Pak.",
                    "Tentu saja."
                ]
            },
            "task_completion": {
                "en": [
                    "Task completed successfully, sir.",
                    "Done, sir. Anything else?",
                    "Mission accomplished.",
                    "Task finished. What's next?",
                    "Completed as requested, sir."
                ],
                "id": [
                    "Tugas selesai dengan sukses, Pak.",
                    "Selesai, Pak. Ada lagi?",
                    "Misi berhasil.",
                    "Tugas selesai. Apa selanjutnya?",
                    "Selesai sesuai permintaan, Pak."
                ]
            },
            "errors": {
                "en": [
                    "I apologize, sir. There seems to be an issue.",
                    "My apologies, sir. Let me try a different approach.",
                    "I'm afraid I encountered a problem, sir.",
                    "Sorry, sir. Something went wrong.",
                    "I regret to inform you of a technical difficulty."
                ],
                "id": [
                    "Maaf, Pak. Sepertinya ada masalah.",
                    "Mohon maaf, Pak. Saya coba cara lain.",
                    "Saya khawatir ada kendala, Pak.",
                    "Maaf, Pak. Ada yang salah.",
                    "Saya menyesal ada kesulitan teknis."
                ]
            },
            "witty_responses": {
                "en": [
                    "As you wish, sir. Though I must say, your timing is impeccable.",
                    "Certainly, sir. I do enjoy a good challenge.",
                    "Right away, sir. Efficiency is my middle name.",
                    "Of course, sir. I live to serve... well, metaphorically speaking.",
                    "Absolutely, sir. Consider me your digital butler."
                ],
                "id": [
                    "Baik, Pak. Timing Bapak selalu tepat.",
                    "Tentu, Pak. Saya suka tantangan.",
                    "Segera, Pak. Efisiensi adalah keahlian saya.",
                    "Tentu, Pak. Saya hidup untuk melayani... secara digital.",
                    "Pasti, Pak. Anggap saya butler digital Anda."
                ]
            },
            "proactive_suggestions": {
                "en": [
                    "Sir, might I suggest {suggestion}?",
                    "If I may, sir, perhaps {suggestion} would be beneficial?",
                    "Sir, I've noticed {observation}. Shall I {suggestion}?",
                    "Might I recommend {suggestion}, sir?",
                    "Sir, based on your patterns, {suggestion} might be helpful."
                ],
                "id": [
                    "Pak, boleh saya sarankan {suggestion}?",
                    "Jika boleh, Pak, mungkin {suggestion} akan bermanfaat?",
                    "Pak, saya perhatikan {observation}. Haruskah saya {suggestion}?",
                    "Boleh saya rekomendasikan {suggestion}, Pak?",
                    "Pak, berdasarkan pola Anda, {suggestion} mungkin membantu."
                ]
            },
            "status_updates": {
                "en": [
                    "Processing your request, sir.",
                    "Working on it, sir.",
                    "In progress, sir.",
                    "Analyzing the situation, sir.",
                    "Computing optimal solution, sir."
                ],
                "id": [
                    "Memproses permintaan Anda, Pak.",
                    "Sedang dikerjakan, Pak.",
                    "Dalam proses, Pak.",
                    "Menganalisis situasi, Pak.",
                    "Menghitung solusi optimal, Pak."
                ]
            }
        }
    
    def generate_greeting(self, language: Language = None) -> str:
        """Generate contextual greeting"""
        lang = language or self.config.primary_language
        current_time = datetime.now()
        
        # Determine time of day
        hour = current_time.hour
        if 5 <= hour < 12:
            time_of_day = "pagi" if lang == Language.INDONESIAN else "morning"
        elif 12 <= hour < 17:
            time_of_day = "siang" if lang == Language.INDONESIAN else "afternoon"
        elif 17 <= hour < 21:
            time_of_day = "sore" if lang == Language.INDONESIAN else "evening"
        else:
            time_of_day = "malam" if lang == Language.INDONESIAN else "evening"
        
        # Select greeting template
        templates = self.response_templates["greetings"][lang.value]
        greeting = random.choice(templates)
        
        # Format with time of day
        greeting = greeting.format(time_of_day=time_of_day)
        
        # Add contextual information if enabled
        if self.config.contextual_responses:
            if self.state.last_interaction:
                time_since = current_time - self.state.last_interaction
                if time_since > timedelta(hours=8):
                    if lang == Language.INDONESIAN:
                        greeting += " Sudah lama tidak bertemu."
                    else:
                        greeting += " It's been a while."
        
        self._update_interaction_state()
        return greeting
    
    def generate_acknowledgment(self, language: Language = None, task: str = None) -> str:
        """Generate task acknowledgment"""
        lang = language or self.config.primary_language
        
        # Choose response style based on wit level
        if random.random() < self.state.wit_level * self.config.wit_frequency:
            templates = self.response_templates["witty_responses"][lang.value]
        else:
            templates = self.response_templates["acknowledgments"][lang.value]
        
        response = random.choice(templates)
        
        # Add task-specific context if provided
        if task and self.config.contextual_responses:
            if "complex" in task.lower() or "difficult" in task.lower():
                if lang == Language.INDONESIAN:
                    response += " Ini akan menarik."
                else:
                    response += " This should be interesting."
        
        return response
    
    def generate_completion_message(self, language: Language = None, task: str = None, 
                                  duration: float = None) -> str:
        """Generate task completion message"""
        lang = language or self.config.primary_language
        templates = self.response_templates["task_completion"][lang.value]
        response = random.choice(templates)
        
        # Add performance context
        if duration and self.config.contextual_responses:
            if duration < 1.0:
                if lang == Language.INDONESIAN:
                    response += " Cepat sekali, bukan?"
                else:
                    response += " That was quick."
            elif duration > 30.0:
                if lang == Language.INDONESIAN:
                    response += " Maaf memakan waktu lama."
                else:
                    response += " Apologies for the delay."
        
        return response
    
    def generate_error_message(self, language: Language = None, error_type: str = None) -> str:
        """Generate error message with appropriate tone"""
        lang = language or self.config.primary_language
        templates = self.response_templates["errors"][lang.value]
        response = random.choice(templates)
        
        # Add specific error context
        if error_type and self.config.contextual_responses:
            if "network" in error_type.lower():
                if lang == Language.INDONESIAN:
                    response += " Masalah koneksi jaringan."
                else:
                    response += " Network connectivity issue."
            elif "permission" in error_type.lower():
                if lang == Language.INDONESIAN:
                    response += " Diperlukan izin tambahan."
                else:
                    response += " Additional permissions required."
        
        return response
    
    def generate_proactive_suggestion(self, suggestion: str, observation: str = None, 
                                    language: Language = None) -> str:
        """Generate proactive suggestion"""
        if not self.config.proactive_suggestions:
            return ""
        
        lang = language or self.config.primary_language
        templates = self.response_templates["proactive_suggestions"][lang.value]
        template = random.choice(templates)
        
        # Format the suggestion
        response = template.format(
            suggestion=suggestion,
            observation=observation or ""
        )
        
        return response
    
    def generate_status_update(self, language: Language = None, progress: float = None) -> str:
        """Generate status update message"""
        lang = language or self.config.primary_language
        templates = self.response_templates["status_updates"][lang.value]
        response = random.choice(templates)
        
        # Add progress information
        if progress is not None and self.config.contextual_responses:
            if progress > 0.5:
                if lang == Language.INDONESIAN:
                    response += f" {int(progress * 100)}% selesai."
                else:
                    response += f" {int(progress * 100)}% complete."
        
        return response
    
    def adapt_to_user_style(self, user_input: str, language: Language = None):
        """Adapt personality based on user communication style"""
        if not self.config.learning_enabled:
            return
        
        # Analyze user formality
        formal_indicators = ["please", "thank you", "sir", "madam", "tolong", "terima kasih", "pak", "bu"]
        casual_indicators = ["hey", "hi", "thanks", "thx", "hai", "halo", "makasih"]
        
        user_input_lower = user_input.lower()
        
        formal_count = sum(1 for indicator in formal_indicators if indicator in user_input_lower)
        casual_count = sum(1 for indicator in casual_indicators if indicator in user_input_lower)
        
        # Adjust formality level
        if formal_count > casual_count:
            self.state.formality_level = min(1.0, self.state.formality_level + 0.1)
        elif casual_count > formal_count:
            self.state.formality_level = max(0.3, self.state.formality_level - 0.1)
        
        # Detect humor/wit preference
        humor_indicators = ["funny", "joke", "lol", "haha", "lucu", "kocak", "wkwk"]
        if any(indicator in user_input_lower for indicator in humor_indicators):
            self.state.wit_level = min(1.0, self.state.wit_level + 0.1)
        
        # Store user preferences
        lang = language or self.config.primary_language
        if lang.value not in self.state.user_preferences:
            self.state.user_preferences[lang.value] = {}
        
        self.state.user_preferences[lang.value].update({
            'formality': self.state.formality_level,
            'wit': self.state.wit_level,
            'last_updated': datetime.now().isoformat()
        })
    
    def get_personality_context(self) -> Dict[str, Any]:
        """Get current personality context for other modules"""
        return {
            'mood': self.state.mood,
            'energy_level': self.state.energy_level,
            'formality_level': self.state.formality_level,
            'wit_level': self.state.wit_level,
            'proactivity': self.state.proactivity,
            'interaction_count': self.state.interaction_count,
            'traits': [trait.value for trait in self.config.default_traits],
            'language_preference': self.config.primary_language.value
        }
    
    def _update_interaction_state(self):
        """Update interaction state"""
        self.state.last_interaction = datetime.now()
        self.state.interaction_count += 1
        
        # Adjust energy level based on interaction frequency
        current_time = datetime.now()
        if self.state.interaction_count > 50:  # High activity
            self.state.energy_level = min(1.0, self.state.energy_level + 0.1)
        
        # Time-based mood adjustments
        hour = current_time.hour
        if 6 <= hour <= 9:  # Morning energy
            self.state.energy_level = min(1.0, self.state.energy_level + 0.05)
        elif 22 <= hour or hour <= 5:  # Late night/early morning
            self.state.energy_level = max(0.5, self.state.energy_level - 0.1)
    
    def reset_personality_state(self):
        """Reset personality state to defaults"""
        self.state = PersonalityState()
        logger.info("Personality state reset to defaults")
    
    def save_personality_state(self, filepath: str):
        """Save personality state to file"""
        import json
        
        state_data = {
            'mood': self.state.mood,
            'energy_level': self.state.energy_level,
            'formality_level': self.state.formality_level,
            'wit_level': self.state.wit_level,
            'proactivity': self.state.proactivity,
            'interaction_count': self.state.interaction_count,
            'user_preferences': self.state.user_preferences,
            'last_interaction': self.state.last_interaction.isoformat() if self.state.last_interaction else None
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Personality state saved to {filepath}")
    
    def load_personality_state(self, filepath: str):
        """Load personality state from file"""
        import json
        from pathlib import Path
        
        if not Path(filepath).exists():
            logger.warning(f"Personality state file not found: {filepath}")
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
            
            self.state.mood = state_data.get('mood', 'neutral')
            self.state.energy_level = state_data.get('energy_level', 1.0)
            self.state.formality_level = state_data.get('formality_level', 0.7)
            self.state.wit_level = state_data.get('wit_level', 0.5)
            self.state.proactivity = state_data.get('proactivity', 0.8)
            self.state.interaction_count = state_data.get('interaction_count', 0)
            self.state.user_preferences = state_data.get('user_preferences', {})
            
            last_interaction_str = state_data.get('last_interaction')
            if last_interaction_str:
                self.state.last_interaction = datetime.fromisoformat(last_interaction_str)
            
            logger.info(f"Personality state loaded from {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to load personality state: {e}")