#!/usr/bin/env python3
"""Jarvis AI System - Main Entry Point

This is the main entry point for the complete Jarvis AI system.
It integrates all modules and provides a comprehensive AI assistant
with voice interaction, task management, learning capabilities,
and an intuitive dashboard.

Usage:
    python jarvis_main.py [options]

Options:
    --no-gui        Run without dashboard GUI
    --no-voice      Run without voice interface
    --demo          Run in demo mode
    --config FILE   Use custom configuration file
    --log-level     Set logging level (DEBUG, INFO, WARNING, ERROR)
"""

import argparse
import asyncio
import json
import logging
import os
import signal
import sys
import time
import threading
from pathlib import Path
from typing import Dict, Any, Optional

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

# Import all Jarvis AI modules
from jarvis_ai import (
    JarvisPersonality, PersonalityTrait, ResponseTone,
    ConversationManager, MessageType, Language,
    LanguageManager,
    VoiceInterface, VoiceState, InputMode,
    TaskCoordinator, TaskType, TaskPriority,
    LearningEngine,
    JarvisDashboard, DashboardTheme
)

# Import other modules
# Note: These modules are integrated into jarvis_ai package
# from voice import VoiceInputManager, TTSManager
# from intent_parser import IntentParser, Intent
# from office_automation import OfficeAutomation
# from windows_system_tools import WindowsSystemTools
# from self_evolving_agent import SelfEvolvingAgent
# from multi_provider_llm import LLMRouter
# from guardrails import GuardrailsManager
from web import SearchEngine, WebScraper

class JarvisAIMain:
    """Main Jarvis AI System Controller"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._load_default_config()
        self.logger = self._setup_logging()
        
        # Core AI components
        self.personality = None
        self.conversation = None
        self.language_manager = None
        self.voice_interface = None
        self.task_coordinator = None
        self.learning_engine = None
        self.dashboard = None
        
        # Extended functionality
        self.voice_input = None
        self.tts_manager = None
        self.intent_parser = None
        self.office_automation = None
        self.system_tools = None
        self.evolving_agent = None
        self.llm_router = None
        self.guardrails = None
        self.search_engine = None
        self.web_scraper = None
        
        # System state
        self.is_running = False
        self.current_user = self.config.get('default_user', 'user')
        self.session_id = None
        self.shutdown_event = threading.Event()
        
        self.logger.info("Jarvis AI Main Controller initialized")
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration"""
        return {
            'default_user': 'user',
            'language': 'english',
            'voice_enabled': True,
            'gui_enabled': True,
            'demo_mode': False,
            'log_level': 'INFO',
            'personality': {
                'traits': ['helpful', 'professional', 'adaptive'],
                'tone': 'friendly',
                'proactive': True
            },
            'voice': {
                'input_mode': 'voice_activation',
                'stt_engine': 'whisper',
                'tts_engine': 'piper',
                'language': 'english'
            },
            'learning': {
                'enabled': True,
                'auto_save': True,
                'model_update_interval': 3600
            },
            'security': {
                'guardrails_enabled': True,
                'human_in_loop': True,
                'safe_mode': True
            }
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        log_level = getattr(logging, self.config.get('log_level', 'INFO').upper())
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('jarvis_ai.log')
            ]
        )
        
        return logging.getLogger('JarvisAI')
    
    async def initialize(self):
        """Initialize all system components"""
        self.logger.info("Initializing Jarvis AI System...")
        
        try:
            # Initialize core AI components
            await self._initialize_core_components()
            
            # Initialize extended functionality
            await self._initialize_extended_components()
            
            # Setup signal handlers
            self._setup_signal_handlers()
            
            self.logger.info("Jarvis AI System initialization completed")
            
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            raise
    
    async def _initialize_core_components(self):
        """Initialize core AI components"""
        # Personality
        self.personality = JarvisPersonality()
        
        # Conversation management
        self.conversation = ConversationManager()
        
        # Language management
        self.language_manager = LanguageManager()
        
        # Voice interface
        if self.config.get('voice_enabled', True):
            self.voice_interface = VoiceInterface()
            await asyncio.to_thread(self.voice_interface.initialize)
        
        # Task coordination
        self.task_coordinator = TaskCoordinator()
        self.task_coordinator.start()
        
        # Learning engine
        if self.config.get('learning', {}).get('enabled', True):
            self.learning_engine = LearningEngine()
            self.learning_engine.start()
        
        # Dashboard
        if self.config.get('gui_enabled', True):
            try:
                self.dashboard = JarvisDashboard()
                self.dashboard.apply_theme(DashboardTheme.DARK)
            except Exception as e:
                self.logger.warning(f"Could not initialize dashboard: {e}")
                self.dashboard = None
    
    async def _initialize_extended_components(self):
        """Initialize extended functionality components"""
        try:
            # Note: These components are integrated into jarvis_ai package
            # Voice input/output
            # self.voice_input = VoiceInputManager()
            # self.tts_manager = TTSManager()
            
            # Intent parsing
            # self.intent_parser = IntentParser()
            
            # Office automation
            # self.office_automation = OfficeAutomation()
            
            # Windows system tools
            # self.system_tools = WindowsSystemTools()
            
            # Self-evolving agent
            # self.evolving_agent = SelfEvolvingAgent()
            
            # Multi-provider LLM
            # self.llm_router = LLMRouter()
            
            # Guardrails
            # if self.config.get('security', {}).get('guardrails_enabled', True):
            #     self.guardrails = GuardrailsManager()
            
            # Web search and scraping
            self.search_engine = SearchEngine()
            self.web_scraper = WebScraper()
            
        except Exception as e:
            self.logger.warning(f"Some extended components failed to initialize: {e}")
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating shutdown...")
            self.shutdown_event.set()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def start(self):
        """Start the Jarvis AI system"""
        self.logger.info("Starting Jarvis AI System...")
        
        try:
            # Start conversation session
            language = Language.ENGLISH if self.config.get('language', 'english').lower() == 'english' else Language.INDONESIAN
            self.session_id = self.conversation.start_session(
                user_id=self.current_user,
                language=language
            )
            
            # Start dashboard if available
            if self.dashboard:
                dashboard_thread = threading.Thread(
                    target=self._run_dashboard,
                    daemon=True
                )
                dashboard_thread.start()
            
            self.is_running = True
            
            # Welcome message
            welcome_msg = self.personality.generate_greeting(
                language,
                self.current_user
            )
            
            self.conversation.add_message(
                self.session_id,
                MessageType.ASSISTANT,
                welcome_msg,
                language
            )
            
            # Speak welcome if voice is available
            if self.voice_interface and self.voice_interface.is_available():
                self.voice_interface.speak(welcome_msg, language)
            
            print(f"\n🤖 Jarvis: {welcome_msg}\n")
            
            self.logger.info("Jarvis AI System started successfully")
            
        except Exception as e:
            self.logger.error(f"Error starting Jarvis AI System: {e}")
            raise
    
    def _run_dashboard(self):
        """Run dashboard in separate thread"""
        try:
            if self.dashboard:
                self.dashboard.run()
        except Exception as e:
            self.logger.error(f"Dashboard error: {e}")
    
    async def process_input(self, user_input: str, language: Language = None) -> str:
        """Process user input through the complete pipeline"""
        try:
            # Detect language if not specified
            if not language:
                detection_result = self.language_manager.detect_language(user_input)
                language = detection_result.language
            
            # Security check with guardrails
            if self.guardrails:
                is_safe, risk_level, message = self.guardrails.validate_input(user_input)
                if not is_safe:
                    return self.personality.generate_error_response(
                        language,
                        f"Security concern detected: {message}"
                    )
            
            # Parse intent
            if self.intent_parser:
                intent_result = self.intent_parser.parse(user_input, language)
                intent = intent_result.intent
            else:
                intent = "general"
            
            # Add to conversation
            self.conversation.add_message(
                self.session_id,
                MessageType.USER,
                user_input,
                language
            )
            
            # Process based on intent
            response = await self._process_by_intent(intent, user_input, language)
            
            # Add response to conversation
            self.conversation.add_message(
                self.session_id,
                MessageType.ASSISTANT,
                response,
                language
            )
            
            # Learn from interaction
            if self.learning_engine:
                self.learning_engine.learn_from_command(
                    user_input,
                    self.current_user,
                    success=True,
                    metadata={
                        'language': language.value,
                        'intent': str(intent),
                        'response_length': len(response)
                    }
                )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing input: {e}")
            return self.personality.generate_error_response(
                language or Language.ENGLISH,
                str(e)
            )
    
    async def _process_by_intent(self, intent: str, user_input: str, language: Language) -> str:
        """Process input based on detected intent"""
        try:
            if intent == "office_automation" and self.office_automation:
                return await self._handle_office_automation(user_input, language)
            
            elif intent == "system_control" and self.system_tools:
                return await self._handle_system_control(user_input, language)
            
            elif intent == "web_search" and self.search_engine:
                return await self._handle_web_search(user_input, language)
            
            elif intent == "task_management":
                return await self._handle_task_management(user_input, language)
            
            elif intent == Intent.LEARNING:
                return await self._handle_learning(user_input, language)
            
            else:
                # Use LLM for general conversation
                if self.llm_router:
                    llm_response = await self.llm_router.generate_response(
                        user_input,
                        context=self.conversation.get_context(self.session_id)
                    )
                    return llm_response
                else:
                    # Fallback to personality-based response
                    return self.personality.generate_acknowledgment(
                        language,
                        f"I understand you said: '{user_input}'. How can I help you further?"
                    )
        
        except Exception as e:
            self.logger.error(f"Error processing intent {intent}: {e}")
            return self.personality.generate_error_response(language, str(e))
    
    async def _handle_office_automation(self, user_input: str, language: Language) -> str:
        """Handle office automation requests"""
        # This would integrate with the office automation module
        # For now, return a placeholder response
        if language == Language.INDONESIAN:
            return "Saya akan membantu dengan otomasi office. Fitur ini sedang dalam pengembangan."
        else:
            return "I'll help with office automation. This feature is under development."
    
    async def _handle_system_control(self, user_input: str, language: Language) -> str:
        """Handle system control requests"""
        # This would integrate with Windows system tools
        if language == Language.INDONESIAN:
            return "Saya akan membantu dengan kontrol sistem. Fitur ini sedang dalam pengembangan."
        else:
            return "I'll help with system control. This feature is under development."
    
    async def _handle_web_search(self, user_input: str, language: Language) -> str:
        """Handle web search requests"""
        try:
            # Extract search query (simplified)
            query = user_input.replace('search', '').replace('cari', '').strip()
            
            if self.search_engine:
                results = self.search_engine.search(query, max_results=3)
                
                if results:
                    if language == Language.INDONESIAN:
                        response = f"Hasil pencarian untuk '{query}':\n"
                    else:
                        response = f"Search results for '{query}':\n"
                    
                    for i, result in enumerate(results[:3], 1):
                        response += f"{i}. {result.get('title', 'No title')}\n"
                        response += f"   {result.get('url', 'No URL')}\n"
                    
                    return response
                else:
                    if language == Language.INDONESIAN:
                        return f"Tidak ditemukan hasil untuk '{query}'."
                    else:
                        return f"No results found for '{query}'."
            else:
                if language == Language.INDONESIAN:
                    return "Fitur pencarian web tidak tersedia saat ini."
                else:
                    return "Web search feature is not available at the moment."
        
        except Exception as e:
            self.logger.error(f"Web search error: {e}")
            return self.personality.generate_error_response(language, str(e))
    
    async def _handle_task_management(self, user_input: str, language: Language) -> str:
        """Handle task management requests"""
        if self.task_coordinator:
            # Create a task based on user input
            task = self.task_coordinator.create_task(
                name=f"User Task: {user_input[:50]}",
                description=user_input,
                executor=self._generic_task_executor,
                task_type=TaskType.USER_INTERACTION,
                priority=TaskPriority.MEDIUM
            )
            
            success = self.task_coordinator.submit_task(task)
            
            if success:
                if language == Language.INDONESIAN:
                    return f"Tugas telah dibuat: {user_input}"
                else:
                    return f"Task created: {user_input}"
            else:
                if language == Language.INDONESIAN:
                    return "Gagal membuat tugas."
                else:
                    return "Failed to create task."
        else:
            if language == Language.INDONESIAN:
                return "Manajemen tugas tidak tersedia."
            else:
                return "Task management is not available."
    
    async def _handle_learning(self, user_input: str, language: Language) -> str:
        """Handle learning requests"""
        if self.learning_engine:
            # Extract learning content
            content = user_input.replace('learn', '').replace('remember', '').replace('ingat', '').replace('pelajari', '').strip()
            
            # Update user preferences
            self.learning_engine.profile_manager.update_preferences(
                self.current_user,
                {'custom_learning': content}
            )
            
            if language == Language.INDONESIAN:
                return f"Saya telah mempelajari: {content}"
            else:
                return f"I have learned: {content}"
        else:
            if language == Language.INDONESIAN:
                return "Fitur pembelajaran tidak tersedia."
            else:
                return "Learning feature is not available."
    
    def _generic_task_executor(self, user_input: str) -> str:
        """Generic task executor"""
        # Simulate task execution
        time.sleep(0.5)
        return f"Completed: {user_input}"
    
    async def run_interactive_mode(self):
        """Run in interactive mode"""
        print("\n" + "="*60)
        print("🤖 JARVIS AI SYSTEM - INTERACTIVE MODE")
        print("="*60)
        print("Type 'quit', 'exit', or 'keluar' to stop")
        print("You can speak in English or Indonesian")
        print("="*60 + "\n")
        
        try:
            while self.is_running and not self.shutdown_event.is_set():
                try:
                    # Get user input
                    user_input = input("👤 You: ").strip()
                    
                    if not user_input:
                        continue
                    
                    # Check for exit commands
                    if user_input.lower() in ['quit', 'exit', 'keluar']:
                        break
                    
                    # Process input
                    response = await self.process_input(user_input)
                    
                    # Display response
                    print(f"🤖 Jarvis: {response}\n")
                    
                    # Speak response if voice is available
                    if self.voice_interface and self.voice_interface.is_available():
                        detection = self.language_manager.detect_language(response)
                        self.voice_interface.speak(response, detection.language)
                
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    self.logger.error(f"Error in interactive mode: {e}")
                    print(f"🤖 Jarvis: I encountered an error: {e}\n")
        
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Shutdown the system gracefully"""
        self.logger.info("Shutting down Jarvis AI System...")
        
        self.is_running = False
        
        # Stop components
        if self.task_coordinator:
            self.task_coordinator.stop()
        
        if self.learning_engine:
            self.learning_engine.stop()
        
        if self.voice_interface:
            self.voice_interface.cleanup()
        
        if self.dashboard:
            self.dashboard.destroy()
        
        # Goodbye message
        if self.personality:
            goodbye_msg = self.personality.generate_completion_response(
                Language.ENGLISH,
                "session"
            )
            print(f"\n🤖 Jarvis: {goodbye_msg}")
        
        self.logger.info("Jarvis AI System shutdown completed")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Jarvis AI System - Advanced AI Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--no-gui',
        action='store_true',
        help='Run without dashboard GUI'
    )
    
    parser.add_argument(
        '--no-voice',
        action='store_true',
        help='Run without voice interface'
    )
    
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run in demo mode'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to custom configuration file'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Set logging level'
    )
    
    parser.add_argument(
        '--user',
        type=str,
        default='user',
        help='Set default user name'
    )
    
    return parser.parse_args()

def load_config_file(config_path: str) -> Dict[str, Any]:
    """Load configuration from file"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config file {config_path}: {e}")
        return {}

async def main():
    """Main entry point"""
    args = parse_arguments()
    
    # Load configuration
    config = {}
    if args.config:
        config = load_config_file(args.config)
    
    # Override config with command line arguments
    config.update({
        'gui_enabled': not args.no_gui,
        'voice_enabled': not args.no_voice,
        'demo_mode': args.demo,
        'log_level': args.log_level,
        'default_user': args.user
    })
    
    # Create and run Jarvis AI system
    jarvis = JarvisAIMain(config)
    
    try:
        # Initialize system
        await jarvis.initialize()
        
        # Start system
        await jarvis.start()
        
        # Run in interactive mode
        if args.demo:
            # Import and run demo
            from examples.jarvis_demo import JarvisAISystem
            demo_system = JarvisAISystem()
            demo_system.start(enable_gui=not args.no_gui)
            demo_system.run_automated_demo()
            demo_system.stop()
        else:
            await jarvis.run_interactive_mode()
    
    except KeyboardInterrupt:
        print("\n\nSystem interrupted by user")
    except Exception as e:
        print(f"\nSystem error: {e}")
        logging.error(f"System error: {e}")
    finally:
        await jarvis.shutdown()
        print("\nThank you for using Jarvis AI!")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())