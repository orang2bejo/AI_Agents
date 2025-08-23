"""Jarvis AI Module

Jarvis-like Voice AI system with dual language support (Indonesian/English),
conversation management, and intuitive dashboard interface.

Sub-modules:
- personality: Jarvis personality and response generation
- conversation: Conversation context and dialog management
- language_manager: Dual language support and translation
- voice_interface: Voice input/output interface
- dashboard: Graphical user interface and monitoring
- task_coordinator: Task scheduling and coordination
- learning_engine: Machine learning and adaptation
"""

from .personality import (
    JarvisPersonality, PersonalityTrait, ResponseTone, Language as PersonalityLanguage,
    PersonalityState, PersonalityConfig
)
from .conversation import (
    ConversationManager, MessageType, ConversationState, Language as ConversationLanguage,
    ConversationMessage, ConversationTurn, ConversationContext, ConversationConfig
)
from .language_manager import (
    LanguageManager, Language, LanguageConfidence, LanguageDetectionResult,
    TranslationResult, LanguageConfig
)
from .voice_interface import (
    VoiceInterface, VoiceState, InputMode, TTSEngine, STTEngine,
    VoiceCommand, VoiceResponse, VoiceConfig
)
from .dashboard import (
    JarvisDashboard, DashboardTheme, SystemStatus, WidgetType,
    DashboardMetrics, LogEntry, DashboardConfig, VoiceVisualizer, MetricsChart
)
from .task_coordinator import (
    TaskCoordinator, TaskType, TaskStatus, TaskPriority, ExecutionMode,
    Task, TaskResult, TaskDependency, TaskConfig, TaskQueue
)
from .learning_engine import (
    LearningEngine, LearningType, ModelType, DataType,
    LearningData, ModelMetrics, UserProfile, LearningConfig,
    FeatureExtractor, ModelManager, DataManager, UserProfileManager
)

__all__ = [
    # Personality
    'JarvisPersonality', 'PersonalityTrait', 'ResponseTone', 'PersonalityLanguage',
    'PersonalityState', 'PersonalityConfig',
    
    # Conversation
    'ConversationManager', 'MessageType', 'ConversationState', 'ConversationLanguage',
    'ConversationMessage', 'ConversationTurn', 'ConversationContext', 'ConversationConfig',
    
    # Language
    'LanguageManager', 'Language', 'LanguageConfidence', 'LanguageDetectionResult',
    'TranslationResult', 'LanguageConfig',
    
    # Voice Interface
    'VoiceInterface', 'VoiceState', 'InputMode', 'TTSEngine', 'STTEngine',
    'VoiceCommand', 'VoiceResponse', 'VoiceConfig',
    
    # Dashboard
    'JarvisDashboard', 'DashboardTheme', 'SystemStatus', 'WidgetType',
    'DashboardMetrics', 'LogEntry', 'DashboardConfig', 'VoiceVisualizer', 'MetricsChart',
    
    # Task Coordination
    'TaskCoordinator', 'TaskType', 'TaskStatus', 'TaskPriority', 'ExecutionMode',
    'Task', 'TaskResult', 'TaskDependency', 'TaskConfig', 'TaskQueue',
    
    # Learning Engine
    'LearningEngine', 'LearningType', 'ModelType', 'DataType',
    'LearningData', 'ModelMetrics', 'UserProfile', 'LearningConfig',
    'FeatureExtractor', 'ModelManager', 'DataManager', 'UserProfileManager'
]

# Module metadata
__version__ = "1.0.0"
__author__ = "Jarvis AI Development Team"
__description__ = "Advanced Voice AI Assistant with Jarvis-like capabilities"