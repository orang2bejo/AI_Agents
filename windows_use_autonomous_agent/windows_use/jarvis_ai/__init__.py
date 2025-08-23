"""Jarvis Voice AI Module

This module implements a sophisticated Voice AI system with Jarvis-like characteristics,
featuring dual language support (Indonesian/English), intelligent conversation management,
and an intuitive dashboard interface.

Key Features:
- Jarvis-inspired personality and response patterns
- Dual language support (Indonesian/English) with seamless switching
- Advanced conversation context management
- Intelligent task routing and execution
- Voice-optimized responses with natural speech patterns
- Real-time dashboard with voice visualization
- Adaptive learning from user interactions
- Proactive assistance and suggestions

Sub-modules:
- personality: Jarvis personality engine and response generation
- conversation: Conversation management and context tracking
- language_manager: Dual language support and translation
- voice_interface: Voice input/output coordination
- dashboard: Real-time dashboard and visualization
- task_coordinator: Task routing and execution management
- learning_engine: Adaptive learning and personalization
"""

# Import main classes for easy access
try:
    from .personality import JarvisPersonality, PersonalityConfig
except ImportError:
    JarvisPersonality = PersonalityConfig = None

try:
    from .conversation import ConversationManager, ConversationContext
except ImportError:
    ConversationManager = ConversationContext = None

try:
    from .language_manager import LanguageManager, LanguageConfig
except ImportError:
    LanguageManager = LanguageConfig = None

try:
    from .voice_interface import VoiceInterface, VoiceConfig
except ImportError:
    VoiceInterface = VoiceConfig = None

try:
    from .dashboard import JarvisDashboard, DashboardConfig
except ImportError:
    JarvisDashboard = DashboardConfig = None

try:
    from .task_coordinator import TaskCoordinator, TaskConfig
except ImportError:
    TaskCoordinator = TaskConfig = None

try:
    from .learning_engine import LearningEngine, LearningConfig
except ImportError:
    LearningEngine = LearningConfig = None

try:
    from .jarvis_core import JarvisAI, JarvisConfig
except ImportError:
    JarvisAI = JarvisConfig = None

__all__ = [
    'JarvisPersonality', 'PersonalityConfig',
    'ConversationManager', 'ConversationContext',
    'LanguageManager', 'LanguageConfig',
    'VoiceInterface', 'VoiceConfig',
    'JarvisDashboard', 'DashboardConfig',
    'TaskCoordinator', 'TaskConfig',
    'LearningEngine', 'LearningConfig',
    'JarvisAI', 'JarvisConfig'
]

# Version info
__version__ = '1.0.0'
__author__ = 'Windows Use Autonomous Agent'
__description__ = 'Jarvis Voice AI System with Dual Language Support'