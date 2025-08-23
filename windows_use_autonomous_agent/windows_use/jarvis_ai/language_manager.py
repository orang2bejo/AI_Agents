"""Language Management Module

Manages dual language support (Indonesian/English) for the Jarvis AI system,
including language detection, translation, and localized responses.
"""

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Union

from pydantic import BaseModel

logger = logging.getLogger(__name__)

class Language(Enum):
    """Supported languages"""
    ENGLISH = "en"
    INDONESIAN = "id"

class LanguageConfidence(Enum):
    """Language detection confidence levels"""
    HIGH = "high"      # > 0.8
    MEDIUM = "medium"  # 0.5 - 0.8
    LOW = "low"        # < 0.5

@dataclass
class LanguageDetectionResult:
    """Result of language detection"""
    language: Language
    confidence: float
    confidence_level: LanguageConfidence
    detected_words: List[str] = field(default_factory=list)
    mixed_language: bool = False
    
@dataclass
class TranslationResult:
    """Result of translation"""
    original_text: str
    translated_text: str
    source_language: Language
    target_language: Language
    confidence: float = 1.0
    
class LanguageConfig(BaseModel):
    """Language management configuration"""
    # Default settings
    default_language: Language = Language.INDONESIAN
    auto_detection_enabled: bool = True
    translation_enabled: bool = True
    
    # Detection settings
    detection_threshold: float = 0.6
    mixed_language_threshold: float = 0.3
    
    # Response settings
    maintain_user_language: bool = True
    fallback_to_default: bool = True
    
    # Localization
    use_local_phrases: bool = True
    formal_tone: bool = False
    
class LanguageManager:
    """Manages dual language support for Jarvis AI"""
    
    def __init__(self, config: LanguageConfig = None):
        self.config = config or LanguageConfig()
        
        # Language detection patterns
        self.language_patterns = self._load_language_patterns()
        self.common_words = self._load_common_words()
        self.greeting_patterns = self._load_greeting_patterns()
        
        # Localized responses
        self.localized_responses = self._load_localized_responses()
        self.system_messages = self._load_system_messages()
        
        # Translation mappings (simple rule-based)
        self.translation_mappings = self._load_translation_mappings()
        
        logger.info("Language manager initialized")
    
    def _load_language_patterns(self) -> Dict[Language, List[str]]:
        """Load language-specific patterns for detection"""
        return {
            Language.INDONESIAN: [
                # Common Indonesian words
                'dan', 'atau', 'yang', 'ini', 'itu', 'dengan', 'untuk', 'dari', 'ke', 'di', 'pada',
                'adalah', 'akan', 'sudah', 'belum', 'tidak', 'bukan', 'juga', 'saja', 'hanya',
                'bisa', 'dapat', 'mau', 'ingin', 'perlu', 'harus', 'boleh', 'jangan',
                'saya', 'anda', 'kamu', 'dia', 'mereka', 'kita', 'kami',
                'apa', 'siapa', 'kapan', 'dimana', 'mengapa', 'bagaimana',
                'tolong', 'mohon', 'silakan', 'terima kasih', 'maaf', 'permisi',
                # Indonesian-specific suffixes
                'kan', 'lah', 'kah', 'nya', 'mu', 'ku',
                # Common Indonesian verbs
                'buat', 'bikin', 'buka', 'tutup', 'cari', 'temukan', 'lihat', 'dengar',
                'kirim', 'terima', 'simpan', 'hapus', 'ubah', 'ganti'
            ],
            Language.ENGLISH: [
                # Common English words
                'and', 'or', 'the', 'this', 'that', 'with', 'for', 'from', 'to', 'in', 'on', 'at',
                'is', 'are', 'was', 'were', 'will', 'would', 'could', 'should', 'can', 'may',
                'have', 'has', 'had', 'do', 'does', 'did', 'get', 'got', 'make', 'made',
                'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
                'what', 'who', 'when', 'where', 'why', 'how', 'which',
                'please', 'thank', 'sorry', 'excuse', 'welcome',
                # Common English verbs
                'create', 'make', 'open', 'close', 'search', 'find', 'look', 'see', 'hear',
                'send', 'receive', 'save', 'delete', 'change', 'modify'
            ]
        }
    
    def _load_common_words(self) -> Dict[Language, Dict[str, float]]:
        """Load common words with frequency weights"""
        return {
            Language.INDONESIAN: {
                'dan': 0.9, 'yang': 0.9, 'ini': 0.8, 'itu': 0.8, 'dengan': 0.8,
                'untuk': 0.8, 'dari': 0.8, 'ke': 0.7, 'di': 0.9, 'pada': 0.7,
                'adalah': 0.8, 'akan': 0.7, 'sudah': 0.7, 'tidak': 0.9, 'bukan': 0.7,
                'saya': 0.8, 'anda': 0.7, 'kamu': 0.6, 'bisa': 0.7, 'dapat': 0.6,
                'apa': 0.8, 'bagaimana': 0.7, 'kapan': 0.6, 'dimana': 0.6,
                'tolong': 0.8, 'mohon': 0.6, 'terima kasih': 0.8, 'maaf': 0.7
            },
            Language.ENGLISH: {
                'the': 0.9, 'and': 0.9, 'to': 0.8, 'of': 0.8, 'a': 0.8,
                'in': 0.8, 'is': 0.8, 'it': 0.7, 'you': 0.8, 'that': 0.7,
                'he': 0.7, 'was': 0.7, 'for': 0.7, 'on': 0.7, 'are': 0.7,
                'with': 0.7, 'as': 0.6, 'i': 0.8, 'his': 0.6, 'they': 0.6,
                'what': 0.7, 'how': 0.7, 'when': 0.6, 'where': 0.6,
                'please': 0.8, 'thank': 0.7, 'sorry': 0.7, 'can': 0.7
            }
        }
    
    def _load_greeting_patterns(self) -> Dict[Language, List[str]]:
        """Load greeting patterns for each language"""
        return {
            Language.INDONESIAN: [
                'halo', 'hai', 'selamat pagi', 'selamat siang', 'selamat sore', 'selamat malam',
                'apa kabar', 'bagaimana kabar', 'gimana kabar', 'selamat datang',
                'permisi', 'mohon maaf', 'terima kasih', 'sama-sama', 'sampai jumpa',
                'selamat tinggal', 'dadah', 'bye'
            ],
            Language.ENGLISH: [
                'hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'good night',
                'how are you', 'how do you do', 'nice to meet you', 'welcome',
                'excuse me', 'sorry', 'thank you', 'thanks', 'you\'re welcome',
                'goodbye', 'bye', 'see you', 'take care'
            ]
        }
    
    def _load_localized_responses(self) -> Dict[str, Dict[Language, str]]:
        """Load localized response templates"""
        return {
            # Acknowledgments
            'understood': {
                Language.INDONESIAN: 'Baik, saya mengerti.',
                Language.ENGLISH: 'Alright, I understand.'
            },
            'processing': {
                Language.INDONESIAN: 'Sedang memproses permintaan Anda...',
                Language.ENGLISH: 'Processing your request...'
            },
            'completed': {
                Language.INDONESIAN: 'Tugas telah selesai.',
                Language.ENGLISH: 'Task completed.'
            },
            
            # Greetings
            'greeting_morning': {
                Language.INDONESIAN: 'Selamat pagi! Saya Jarvis, asisten AI Anda.',
                Language.ENGLISH: 'Good morning! I\'m Jarvis, your AI assistant.'
            },
            'greeting_afternoon': {
                Language.INDONESIAN: 'Selamat siang! Ada yang bisa saya bantu?',
                Language.ENGLISH: 'Good afternoon! How can I help you?'
            },
            'greeting_evening': {
                Language.INDONESIAN: 'Selamat sore! Siap membantu Anda.',
                Language.ENGLISH: 'Good evening! Ready to assist you.'
            },
            
            # Questions
            'clarification_needed': {
                Language.INDONESIAN: 'Maaf, bisa diperjelas lagi?',
                Language.ENGLISH: 'Sorry, could you clarify that?'
            },
            'what_can_i_help': {
                Language.INDONESIAN: 'Ada yang bisa saya bantu?',
                Language.ENGLISH: 'What can I help you with?'
            },
            
            # Errors
            'error_occurred': {
                Language.INDONESIAN: 'Maaf, terjadi kesalahan.',
                Language.ENGLISH: 'Sorry, an error occurred.'
            },
            'not_understood': {
                Language.INDONESIAN: 'Maaf, saya tidak mengerti permintaan Anda.',
                Language.ENGLISH: 'Sorry, I don\'t understand your request.'
            },
            
            # Confirmations
            'confirm_action': {
                Language.INDONESIAN: 'Apakah Anda yakin ingin melakukan ini?',
                Language.ENGLISH: 'Are you sure you want to do this?'
            },
            'action_cancelled': {
                Language.INDONESIAN: 'Tindakan dibatalkan.',
                Language.ENGLISH: 'Action cancelled.'
            },
            
            # Status updates
            'searching': {
                Language.INDONESIAN: 'Sedang mencari...',
                Language.ENGLISH: 'Searching...'
            },
            'opening_file': {
                Language.INDONESIAN: 'Membuka file...',
                Language.ENGLISH: 'Opening file...'
            },
            'saving_file': {
                Language.INDONESIAN: 'Menyimpan file...',
                Language.ENGLISH: 'Saving file...'
            }
        }
    
    def _load_system_messages(self) -> Dict[str, Dict[Language, str]]:
        """Load system messages"""
        return {
            'startup': {
                Language.INDONESIAN: 'Sistem Jarvis telah aktif. Siap melayani Anda.',
                Language.ENGLISH: 'Jarvis system is now active. Ready to serve you.'
            },
            'shutdown': {
                Language.INDONESIAN: 'Sistem Jarvis akan dimatikan. Sampai jumpa!',
                Language.ENGLISH: 'Jarvis system shutting down. Goodbye!'
            },
            'language_switched': {
                Language.INDONESIAN: 'Bahasa telah diubah ke Bahasa Indonesia.',
                Language.ENGLISH: 'Language has been switched to English.'
            }
        }
    
    def _load_translation_mappings(self) -> Dict[str, Dict[Language, str]]:
        """Load simple translation mappings for common phrases"""
        return {
            # Commands
            'open': {
                Language.INDONESIAN: 'buka',
                Language.ENGLISH: 'open'
            },
            'close': {
                Language.INDONESIAN: 'tutup',
                Language.ENGLISH: 'close'
            },
            'search': {
                Language.INDONESIAN: 'cari',
                Language.ENGLISH: 'search'
            },
            'create': {
                Language.INDONESIAN: 'buat',
                Language.ENGLISH: 'create'
            },
            'delete': {
                Language.INDONESIAN: 'hapus',
                Language.ENGLISH: 'delete'
            },
            'save': {
                Language.INDONESIAN: 'simpan',
                Language.ENGLISH: 'save'
            },
            
            # Objects
            'file': {
                Language.INDONESIAN: 'file',
                Language.ENGLISH: 'file'
            },
            'folder': {
                Language.INDONESIAN: 'folder',
                Language.ENGLISH: 'folder'
            },
            'document': {
                Language.INDONESIAN: 'dokumen',
                Language.ENGLISH: 'document'
            },
            'email': {
                Language.INDONESIAN: 'email',
                Language.ENGLISH: 'email'
            },
            
            # Time expressions
            'today': {
                Language.INDONESIAN: 'hari ini',
                Language.ENGLISH: 'today'
            },
            'tomorrow': {
                Language.INDONESIAN: 'besok',
                Language.ENGLISH: 'tomorrow'
            },
            'yesterday': {
                Language.INDONESIAN: 'kemarin',
                Language.ENGLISH: 'yesterday'
            }
        }
    
    def detect_language(self, text: str) -> LanguageDetectionResult:
        """Detect language of input text"""
        if not text or not text.strip():
            return LanguageDetectionResult(
                language=self.config.default_language,
                confidence=0.0,
                confidence_level=LanguageConfidence.LOW
            )
        
        text_lower = text.lower().strip()
        
        # Calculate scores for each language
        language_scores = {}
        detected_words = {}
        
        for language in Language:
            score = 0.0
            words_found = []
            
            # Check common words with weights
            common_words = self.common_words.get(language, {})
            for word, weight in common_words.items():
                if word in text_lower:
                    score += weight
                    words_found.append(word)
            
            # Check language patterns
            patterns = self.language_patterns.get(language, [])
            for pattern in patterns:
                if pattern in text_lower:
                    score += 0.5
                    words_found.append(pattern)
            
            # Check greeting patterns (higher weight)
            greetings = self.greeting_patterns.get(language, [])
            for greeting in greetings:
                if greeting in text_lower:
                    score += 1.0
                    words_found.append(greeting)
            
            language_scores[language] = score
            detected_words[language] = words_found
        
        # Normalize scores
        total_words = len(text_lower.split())
        if total_words > 0:
            for language in language_scores:
                language_scores[language] = language_scores[language] / total_words
        
        # Determine primary language
        primary_language = max(language_scores, key=language_scores.get)
        primary_score = language_scores[primary_language]
        
        # Check for mixed language
        other_scores = [score for lang, score in language_scores.items() if lang != primary_language]
        max_other_score = max(other_scores) if other_scores else 0.0
        
        mixed_language = (
            max_other_score > self.config.mixed_language_threshold and
            primary_score - max_other_score < 0.3
        )
        
        # Determine confidence level
        if primary_score > 0.8:
            confidence_level = LanguageConfidence.HIGH
        elif primary_score > 0.5:
            confidence_level = LanguageConfidence.MEDIUM
        else:
            confidence_level = LanguageConfidence.LOW
        
        # Fallback to default if confidence is too low
        if primary_score < self.config.detection_threshold:
            primary_language = self.config.default_language
            primary_score = 0.5
            confidence_level = LanguageConfidence.LOW
        
        return LanguageDetectionResult(
            language=primary_language,
            confidence=primary_score,
            confidence_level=confidence_level,
            detected_words=detected_words.get(primary_language, []),
            mixed_language=mixed_language
        )
    
    def get_localized_response(self, response_key: str, language: Language = None, 
                             **kwargs) -> str:
        """Get localized response for a given key"""
        language = language or self.config.default_language
        
        response_templates = self.localized_responses.get(response_key, {})
        template = response_templates.get(language)
        
        if not template:
            # Fallback to default language
            template = response_templates.get(self.config.default_language)
            
        if not template:
            # Fallback to English
            template = response_templates.get(Language.ENGLISH, response_key)
        
        # Format template with kwargs if provided
        if kwargs:
            try:
                return template.format(**kwargs)
            except (KeyError, ValueError):
                return template
        
        return template
    
    def get_system_message(self, message_key: str, language: Language = None) -> str:
        """Get system message in specified language"""
        language = language or self.config.default_language
        
        messages = self.system_messages.get(message_key, {})
        message = messages.get(language)
        
        if not message:
            message = messages.get(self.config.default_language, message_key)
        
        return message
    
    def translate_simple(self, text: str, target_language: Language, 
                        source_language: Language = None) -> TranslationResult:
        """Simple rule-based translation for common phrases"""
        if not source_language:
            detection = self.detect_language(text)
            source_language = detection.language
        
        if source_language == target_language:
            return TranslationResult(
                original_text=text,
                translated_text=text,
                source_language=source_language,
                target_language=target_language,
                confidence=1.0
            )
        
        translated_text = text
        confidence = 0.5  # Default confidence for rule-based translation
        
        # Apply translation mappings
        for key, translations in self.translation_mappings.items():
            source_phrase = translations.get(source_language, '')
            target_phrase = translations.get(target_language, '')
            
            if source_phrase and target_phrase and source_phrase in text.lower():
                translated_text = re.sub(
                    re.escape(source_phrase), 
                    target_phrase, 
                    translated_text, 
                    flags=re.IGNORECASE
                )
                confidence = min(confidence + 0.1, 1.0)
        
        return TranslationResult(
            original_text=text,
            translated_text=translated_text,
            source_language=source_language,
            target_language=target_language,
            confidence=confidence
        )
    
    def format_response_for_language(self, response: str, language: Language, 
                                   formal: bool = None) -> str:
        """Format response according to language conventions"""
        formal = formal if formal is not None else self.config.formal_tone
        
        if language == Language.INDONESIAN:
            # Indonesian formatting
            if formal:
                # Use formal pronouns
                response = re.sub(r'\bkamu\b', 'Anda', response, flags=re.IGNORECASE)
                response = re.sub(r'\bmu\b', 'Anda', response, flags=re.IGNORECASE)
            else:
                # Use informal pronouns
                response = re.sub(r'\bAnda\b', 'kamu', response, flags=re.IGNORECASE)
            
            # Add Indonesian politeness markers
            if not any(marker in response.lower() for marker in ['mohon', 'tolong', 'silakan']):
                if response.strip().endswith('?'):
                    response = response.rstrip('?') + ', ya?'
        
        elif language == Language.ENGLISH:
            # English formatting
            if formal:
                # Use formal language
                response = re.sub(r'\bcan\'t\b', 'cannot', response, flags=re.IGNORECASE)
                response = re.sub(r'\bwon\'t\b', 'will not', response, flags=re.IGNORECASE)
                response = re.sub(r'\bdoesn\'t\b', 'does not', response, flags=re.IGNORECASE)
            
            # Ensure proper capitalization
            sentences = response.split('. ')
            sentences = [s.strip().capitalize() for s in sentences if s.strip()]
            response = '. '.join(sentences)
        
        return response
    
    def get_time_based_greeting(self, language: Language = None) -> str:
        """Get time-appropriate greeting"""
        from datetime import datetime
        
        language = language or self.config.default_language
        current_hour = datetime.now().hour
        
        if 5 <= current_hour < 12:
            greeting_key = 'greeting_morning'
        elif 12 <= current_hour < 17:
            greeting_key = 'greeting_afternoon'
        else:
            greeting_key = 'greeting_evening'
        
        return self.get_localized_response(greeting_key, language)
    
    def is_language_switch_request(self, text: str) -> Optional[Language]:
        """Check if text contains language switch request"""
        text_lower = text.lower()
        
        # Indonesian language switch patterns
        id_patterns = [
            'ganti ke bahasa indonesia', 'ubah ke bahasa indonesia', 'pakai bahasa indonesia',
            'bicara bahasa indonesia', 'gunakan bahasa indonesia', 'bahasa indonesia'
        ]
        
        # English language switch patterns
        en_patterns = [
            'switch to english', 'change to english', 'use english',
            'speak english', 'english please', 'in english'
        ]
        
        for pattern in id_patterns:
            if pattern in text_lower:
                return Language.INDONESIAN
        
        for pattern in en_patterns:
            if pattern in text_lower:
                return Language.ENGLISH
        
        return None
    
    def get_language_capabilities(self) -> Dict[str, Any]:
        """Get information about language capabilities"""
        return {
            'supported_languages': [lang.value for lang in Language],
            'default_language': self.config.default_language.value,
            'auto_detection': self.config.auto_detection_enabled,
            'translation_enabled': self.config.translation_enabled,
            'detection_threshold': self.config.detection_threshold,
            'localized_responses_count': len(self.localized_responses),
            'translation_mappings_count': len(self.translation_mappings)
        }
    
    def update_language_preference(self, language: Language):
        """Update default language preference"""
        old_language = self.config.default_language
        self.config.default_language = language
        
        logger.info(f"Language preference updated: {old_language.value} -> {language.value}")
    
    def analyze_conversation_language_patterns(self, messages: List[str]) -> Dict[str, Any]:
        """Analyze language patterns in conversation history"""
        if not messages:
            return {'total_messages': 0}
        
        language_counts = {lang: 0 for lang in Language}
        mixed_language_count = 0
        confidence_levels = {level: 0 for level in LanguageConfidence}
        
        for message in messages:
            detection = self.detect_language(message)
            language_counts[detection.language] += 1
            confidence_levels[detection.confidence_level] += 1
            
            if detection.mixed_language:
                mixed_language_count += 1
        
        total_messages = len(messages)
        dominant_language = max(language_counts, key=language_counts.get)
        
        return {
            'total_messages': total_messages,
            'language_distribution': {
                lang.value: count for lang, count in language_counts.items()
            },
            'dominant_language': dominant_language.value,
            'mixed_language_percentage': (mixed_language_count / total_messages) * 100,
            'confidence_distribution': {
                level.value: count for level, count in confidence_levels.items()
            },
            'language_consistency': language_counts[dominant_language] / total_messages
        }