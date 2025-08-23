"""Conversation Management Module

Manages conversation context, dialog history, and intelligent conversation flow
for the Jarvis AI system with dual language support.
"""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple

from pydantic import BaseModel

logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Types of conversation messages"""
    USER_INPUT = "user_input"
    JARVIS_RESPONSE = "jarvis_response"
    SYSTEM_MESSAGE = "system_message"
    TASK_UPDATE = "task_update"
    ERROR_MESSAGE = "error_message"
    PROACTIVE_SUGGESTION = "proactive_suggestion"

class ConversationState(Enum):
    """Current conversation state"""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    RESPONDING = "responding"
    WAITING_CONFIRMATION = "waiting_confirmation"
    TASK_EXECUTION = "task_execution"
    ERROR_HANDLING = "error_handling"

class Language(Enum):
    """Supported languages"""
    ENGLISH = "en"
    INDONESIAN = "id"

@dataclass
class ConversationMessage:
    """Individual conversation message"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    message_type: MessageType = MessageType.USER_INPUT
    content: str = ""
    language: Language = Language.INDONESIAN
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Context information
    intent: Optional[str] = None
    entities: Dict[str, Any] = field(default_factory=dict)
    sentiment: Optional[str] = None
    
    # Response information (for Jarvis messages)
    response_time: Optional[float] = None
    tokens_used: Optional[int] = None

@dataclass
class ConversationTurn:
    """A complete conversation turn (user input + Jarvis response)"""
    user_message: ConversationMessage
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    jarvis_response: Optional[ConversationMessage] = None
    context_used: Dict[str, Any] = field(default_factory=dict)
    task_executed: Optional[str] = None
    success: bool = True
    duration: Optional[float] = None

@dataclass
class ConversationContext:
    """Current conversation context"""
    # Session information
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    start_time: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    
    # Current state
    state: ConversationState = ConversationState.IDLE
    current_language: Language = Language.INDONESIAN
    
    # Context tracking
    current_topic: Optional[str] = None
    active_tasks: List[str] = field(default_factory=list)
    pending_confirmations: List[str] = field(default_factory=list)
    
    # User information
    user_name: Optional[str] = None
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    
    # Conversation flow
    last_intent: Optional[str] = None
    conversation_depth: int = 0
    topic_switches: int = 0
    
    # Memory and context
    short_term_memory: Dict[str, Any] = field(default_factory=dict)
    mentioned_entities: Dict[str, List[str]] = field(default_factory=dict)
    
class ConversationConfig(BaseModel):
    """Conversation management configuration"""
    # Session settings
    session_timeout_minutes: int = 30
    max_conversation_history: int = 100
    context_window_size: int = 10
    
    # Language settings
    auto_language_detection: bool = True
    language_switch_threshold: float = 0.8
    
    # Context management
    topic_tracking_enabled: bool = True
    entity_extraction_enabled: bool = True
    sentiment_analysis_enabled: bool = True
    
    # Memory settings
    short_term_memory_size: int = 20
    long_term_memory_enabled: bool = True
    
    # Response settings
    proactive_suggestions_enabled: bool = True
    context_aware_responses: bool = True
    
class ConversationManager:
    """Manages conversation flow and context for Jarvis AI"""
    
    def __init__(self, config: ConversationConfig = None):
        self.config = config or ConversationConfig()
        self.context = ConversationContext()
        self.conversation_history: List[ConversationTurn] = []
        self.message_history: List[ConversationMessage] = []
        
        # Topic and intent tracking
        self.topic_keywords = self._load_topic_keywords()
        self.intent_patterns = self._load_intent_patterns()
        
        logger.info(f"Conversation manager initialized with session {self.context.session_id}")
    
    def _load_topic_keywords(self) -> Dict[str, List[str]]:
        """Load topic keywords for topic detection"""
        return {
            "office": ["excel", "word", "powerpoint", "dokumen", "spreadsheet", "presentasi"],
            "system": ["windows", "file", "folder", "process", "sistem", "komputer"],
            "web": ["search", "browse", "website", "internet", "cari", "buka"],
            "email": ["email", "mail", "send", "kirim", "surat"],
            "schedule": ["calendar", "meeting", "appointment", "jadwal", "rapat"],
            "weather": ["weather", "temperature", "cuaca", "suhu"],
            "news": ["news", "berita", "update", "latest"],
            "entertainment": ["music", "video", "movie", "musik", "film"],
            "productivity": ["task", "todo", "reminder", "tugas", "pengingat"]
        }
    
    def _load_intent_patterns(self) -> Dict[str, List[str]]:
        """Load intent patterns for intent detection"""
        return {
            "greeting": ["hello", "hi", "hey", "halo", "hai", "selamat"],
            "question": ["what", "how", "when", "where", "why", "apa", "bagaimana", "kapan", "dimana", "mengapa"],
            "request": ["please", "can you", "could you", "tolong", "bisakah", "minta"],
            "command": ["open", "close", "start", "stop", "buka", "tutup", "mulai", "hentikan"],
            "search": ["search", "find", "look for", "cari", "temukan"],
            "create": ["create", "make", "new", "buat", "bikin", "baru"],
            "help": ["help", "assist", "support", "bantuan", "bantu"],
            "goodbye": ["bye", "goodbye", "see you", "dadah", "sampai jumpa"]
        }
    
    def start_conversation(self, user_name: str = None) -> str:
        """Start a new conversation session"""
        self.context = ConversationContext()
        if user_name:
            self.context.user_name = user_name
        
        self.conversation_history.clear()
        self.message_history.clear()
        
        logger.info(f"New conversation started: {self.context.session_id}")
        return self.context.session_id
    
    def add_user_message(self, content: str, language: Language = None, 
                        metadata: Dict[str, Any] = None) -> ConversationMessage:
        """Add user message to conversation"""
        # Detect language if not specified
        if language is None and self.config.auto_language_detection:
            language = self._detect_language(content)
        
        language = language or self.context.current_language
        
        # Create message
        message = ConversationMessage(
            message_type=MessageType.USER_INPUT,
            content=content,
            language=language,
            metadata=metadata or {}
        )
        
        # Extract intent and entities
        if self.config.entity_extraction_enabled:
            message.intent = self._extract_intent(content)
            message.entities = self._extract_entities(content)
        
        # Analyze sentiment
        if self.config.sentiment_analysis_enabled:
            message.sentiment = self._analyze_sentiment(content)
        
        # Update context
        self._update_context_from_message(message)
        
        # Add to history
        self.message_history.append(message)
        self._trim_message_history()
        
        logger.debug(f"User message added: {message.id}")
        return message
    
    def add_jarvis_response(self, content: str, language: Language = None,
                          response_time: float = None, metadata: Dict[str, Any] = None) -> ConversationMessage:
        """Add Jarvis response to conversation"""
        language = language or self.context.current_language
        
        message = ConversationMessage(
            message_type=MessageType.JARVIS_RESPONSE,
            content=content,
            language=language,
            response_time=response_time,
            metadata=metadata or {}
        )
        
        # Add to history
        self.message_history.append(message)
        self._trim_message_history()
        
        # Update context
        self.context.last_activity = datetime.now()
        self.context.state = ConversationState.IDLE
        
        logger.debug(f"Jarvis response added: {message.id}")
        return message
    
    def create_conversation_turn(self, user_message: ConversationMessage,
                               jarvis_response: ConversationMessage = None) -> ConversationTurn:
        """Create a complete conversation turn"""
        turn = ConversationTurn(
            user_message=user_message,
            jarvis_response=jarvis_response,
            context_used=self.get_current_context_summary()
        )
        
        if jarvis_response:
            turn.duration = (jarvis_response.timestamp - user_message.timestamp).total_seconds()
        
        self.conversation_history.append(turn)
        self._trim_conversation_history()
        
        return turn
    
    def get_conversation_context(self, window_size: int = None) -> Dict[str, Any]:
        """Get conversation context for response generation"""
        window_size = window_size or self.config.context_window_size
        
        # Get recent messages
        recent_messages = self.message_history[-window_size:] if self.message_history else []
        
        # Get recent turns
        recent_turns = self.conversation_history[-window_size//2:] if self.conversation_history else []
        
        context = {
            'session_id': self.context.session_id,
            'current_state': self.context.state.value,
            'current_language': self.context.current_language.value,
            'current_topic': self.context.current_topic,
            'last_intent': self.context.last_intent,
            'conversation_depth': self.context.conversation_depth,
            'user_name': self.context.user_name,
            'active_tasks': self.context.active_tasks,
            'pending_confirmations': self.context.pending_confirmations,
            'short_term_memory': self.context.short_term_memory,
            'mentioned_entities': self.context.mentioned_entities,
            'recent_messages': [
                {
                    'type': msg.message_type.value,
                    'content': msg.content,
                    'language': msg.language.value,
                    'intent': msg.intent,
                    'timestamp': msg.timestamp.isoformat()
                }
                for msg in recent_messages
            ],
            'recent_turns': [
                {
                    'user_intent': turn.user_message.intent,
                    'success': turn.success,
                    'task_executed': turn.task_executed,
                    'duration': turn.duration
                }
                for turn in recent_turns
            ]
        }
        
        return context
    
    def get_current_context_summary(self) -> Dict[str, Any]:
        """Get summary of current context"""
        return {
            'topic': self.context.current_topic,
            'language': self.context.current_language.value,
            'state': self.context.state.value,
            'last_intent': self.context.last_intent,
            'active_tasks_count': len(self.context.active_tasks),
            'conversation_depth': self.context.conversation_depth
        }
    
    def update_conversation_state(self, new_state: ConversationState):
        """Update conversation state"""
        old_state = self.context.state
        self.context.state = new_state
        self.context.last_activity = datetime.now()
        
        logger.debug(f"Conversation state changed: {old_state.value} -> {new_state.value}")
    
    def add_active_task(self, task_id: str):
        """Add active task to context"""
        if task_id not in self.context.active_tasks:
            self.context.active_tasks.append(task_id)
            logger.debug(f"Active task added: {task_id}")
    
    def remove_active_task(self, task_id: str):
        """Remove active task from context"""
        if task_id in self.context.active_tasks:
            self.context.active_tasks.remove(task_id)
            logger.debug(f"Active task removed: {task_id}")
    
    def add_to_short_term_memory(self, key: str, value: Any):
        """Add information to short-term memory"""
        self.context.short_term_memory[key] = {
            'value': value,
            'timestamp': datetime.now().isoformat()
        }
        
        # Trim memory if too large
        if len(self.context.short_term_memory) > self.config.short_term_memory_size:
            # Remove oldest entries
            sorted_items = sorted(
                self.context.short_term_memory.items(),
                key=lambda x: x[1]['timestamp']
            )
            for key_to_remove, _ in sorted_items[:-self.config.short_term_memory_size]:
                del self.context.short_term_memory[key_to_remove]
    
    def get_from_short_term_memory(self, key: str) -> Any:
        """Get information from short-term memory"""
        memory_item = self.context.short_term_memory.get(key)
        return memory_item['value'] if memory_item else None
    
    def is_session_expired(self) -> bool:
        """Check if conversation session has expired"""
        if not self.context.last_activity:
            return False
        
        time_since_activity = datetime.now() - self.context.last_activity
        return time_since_activity > timedelta(minutes=self.config.session_timeout_minutes)
    
    def _detect_language(self, text: str) -> Language:
        """Simple language detection based on keywords"""
        indonesian_words = ['dan', 'atau', 'yang', 'ini', 'itu', 'dengan', 'untuk', 'dari', 'ke', 'di', 'pada']
        english_words = ['and', 'or', 'the', 'this', 'that', 'with', 'for', 'from', 'to', 'in', 'on']
        
        text_lower = text.lower()
        
        id_count = sum(1 for word in indonesian_words if word in text_lower)
        en_count = sum(1 for word in english_words if word in text_lower)
        
        if id_count > en_count:
            return Language.INDONESIAN
        elif en_count > id_count:
            return Language.ENGLISH
        else:
            return self.context.current_language  # Default to current
    
    def _extract_intent(self, text: str) -> Optional[str]:
        """Extract intent from text"""
        text_lower = text.lower()
        
        for intent, patterns in self.intent_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                return intent
        
        return None
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities from text"""
        entities = {}
        text_lower = text.lower()
        
        # Extract file extensions
        import re
        file_extensions = re.findall(r'\.(\w+)', text)
        if file_extensions:
            entities['file_types'] = file_extensions
        
        # Extract numbers
        numbers = re.findall(r'\d+', text)
        if numbers:
            entities['numbers'] = [int(n) for n in numbers]
        
        # Extract time expressions
        time_patterns = ['today', 'tomorrow', 'yesterday', 'hari ini', 'besok', 'kemarin']
        time_entities = [pattern for pattern in time_patterns if pattern in text_lower]
        if time_entities:
            entities['time_expressions'] = time_entities
        
        return entities
    
    def _analyze_sentiment(self, text: str) -> str:
        """Simple sentiment analysis"""
        positive_words = ['good', 'great', 'excellent', 'amazing', 'bagus', 'hebat', 'luar biasa']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'buruk', 'jelek', 'parah']
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _update_context_from_message(self, message: ConversationMessage):
        """Update conversation context based on message"""
        # Update language
        if message.language != self.context.current_language:
            self.context.current_language = message.language
            self.context.topic_switches += 1
        
        # Update topic
        if self.config.topic_tracking_enabled:
            detected_topic = self._detect_topic(message.content)
            if detected_topic and detected_topic != self.context.current_topic:
                self.context.current_topic = detected_topic
                self.context.topic_switches += 1
        
        # Update intent
        if message.intent:
            self.context.last_intent = message.intent
        
        # Update conversation depth
        self.context.conversation_depth += 1
        
        # Update mentioned entities
        if message.entities:
            for entity_type, entities in message.entities.items():
                if entity_type not in self.context.mentioned_entities:
                    self.context.mentioned_entities[entity_type] = []
                self.context.mentioned_entities[entity_type].extend(entities)
        
        # Update activity timestamp
        self.context.last_activity = message.timestamp
    
    def _detect_topic(self, text: str) -> Optional[str]:
        """Detect conversation topic from text"""
        text_lower = text.lower()
        
        topic_scores = {}
        for topic, keywords in self.topic_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                topic_scores[topic] = score
        
        if topic_scores:
            return max(topic_scores, key=topic_scores.get)
        
        return None
    
    def _trim_message_history(self):
        """Trim message history to maximum size"""
        if len(self.message_history) > self.config.max_conversation_history:
            self.message_history = self.message_history[-self.config.max_conversation_history:]
    
    def _trim_conversation_history(self):
        """Trim conversation history to maximum size"""
        max_turns = self.config.max_conversation_history // 2
        if len(self.conversation_history) > max_turns:
            self.conversation_history = self.conversation_history[-max_turns:]
    
    def export_conversation_history(self) -> Dict[str, Any]:
        """Export conversation history for analysis or storage"""
        return {
            'session_id': self.context.session_id,
            'start_time': self.context.start_time.isoformat(),
            'last_activity': self.context.last_activity.isoformat(),
            'total_messages': len(self.message_history),
            'total_turns': len(self.conversation_history),
            'conversation_depth': self.context.conversation_depth,
            'topic_switches': self.context.topic_switches,
            'languages_used': list(set(msg.language.value for msg in self.message_history)),
            'intents_used': list(set(msg.intent for msg in self.message_history if msg.intent)),
            'topics_discussed': list(set(turn.context_used.get('topic') for turn in self.conversation_history if turn.context_used.get('topic'))),
            'messages': [
                {
                    'id': msg.id,
                    'timestamp': msg.timestamp.isoformat(),
                    'type': msg.message_type.value,
                    'content': msg.content,
                    'language': msg.language.value,
                    'intent': msg.intent,
                    'sentiment': msg.sentiment
                }
                for msg in self.message_history
            ]
        }