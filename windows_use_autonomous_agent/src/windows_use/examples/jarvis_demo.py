"""Jarvis AI System Demo

Demonstrates the complete Jarvis AI system with all modules:
- Personality and response generation
- Conversation management
- Language detection and translation
- Voice interface (STT/TTS)
- Task coordination
- Learning engine
- Dashboard interface

This demo shows how to integrate all components for a complete
Jarvis-like AI assistant experience.
"""

import asyncio
import logging
import os
import sys
import time
import threading
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent))

from windows_use.jarvis_ai import (
    JarvisPersonality, PersonalityTrait, ResponseTone,
    ConversationManager, MessageType,
    LanguageManager, Language,
    VoiceInterface, VoiceState, InputMode,
    TaskCoordinator, TaskType, TaskPriority,
    LearningEngine,
    JarvisDashboard, DashboardTheme
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class JarvisAISystem:
    """Complete Jarvis AI System Integration"""
    
    def __init__(self):
        # Initialize all components
        self.personality = JarvisPersonality()
        self.conversation = ConversationManager()
        self.language_manager = LanguageManager()
        self.voice_interface = VoiceInterface()
        self.task_coordinator = TaskCoordinator()
        self.learning_engine = LearningEngine()
        self.dashboard = None  # Will be initialized if GUI is available
        
        # System state
        self.is_running = False
        self.current_user = "demo_user"
        self.session_id = None
        
        # Demo settings
        self.demo_mode = True
        self.auto_responses = True
        
        logger.info("Jarvis AI System initialized")
    
    def start(self, enable_gui: bool = True):
        """Start the Jarvis AI system"""
        logger.info("Starting Jarvis AI System...")
        
        try:
            # Start core components
            self.task_coordinator.start()
            self.learning_engine.start()
            
            # Initialize voice interface
            self.voice_interface.initialize()
            
            # Start conversation session
            self.session_id = self.conversation.start_session(
                user_id=self.current_user,
                language=Language.ENGLISH
            )
            
            # Initialize dashboard if GUI enabled
            if enable_gui:
                try:
                    self.dashboard = JarvisDashboard()
                    self.dashboard.apply_theme(DashboardTheme.DARK)
                    
                    # Start dashboard in separate thread
                    dashboard_thread = threading.Thread(
                        target=self._run_dashboard,
                        daemon=True
                    )
                    dashboard_thread.start()
                    
                    logger.info("Dashboard started")
                except Exception as e:
                    logger.warning(f"Could not start dashboard: {e}")
                    self.dashboard = None
            
            self.is_running = True
            
            # Welcome message
            welcome_msg = self.personality.generate_greeting(
                Language.ENGLISH,
                self.current_user
            )
            
            self.conversation.add_message(
                self.session_id,
                MessageType.ASSISTANT,
                welcome_msg,
                Language.ENGLISH
            )
            
            if self.voice_interface.is_available():
                self.voice_interface.speak(welcome_msg, Language.ENGLISH)
            
            print(f"\n🤖 Jarvis: {welcome_msg}\n")
            
            logger.info("Jarvis AI System started successfully")
            
        except Exception as e:
            logger.error(f"Error starting Jarvis AI System: {e}")
            raise
    
    def stop(self):
        """Stop the Jarvis AI system"""
        logger.info("Stopping Jarvis AI System...")
        
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
        
        logger.info("Jarvis AI System stopped")
    
    def _run_dashboard(self):
        """Run dashboard in separate thread"""
        try:
            if self.dashboard:
                self.dashboard.run()
        except Exception as e:
            logger.error(f"Dashboard error: {e}")
    
    def process_user_input(self, user_input: str, language: Language = None) -> str:
        """Process user input and generate response"""
        try:
            # Detect language if not specified
            if not language:
                detection_result = self.language_manager.detect_language(user_input)
                language = detection_result.language
            
            # Add user message to conversation
            self.conversation.add_message(
                self.session_id,
                MessageType.USER,
                user_input,
                language
            )
            
            # Update conversation context
            context = self.conversation.get_context(self.session_id)
            
            # Generate response based on input
            response = self._generate_response(user_input, language, context)
            
            # Add assistant response to conversation
            self.conversation.add_message(
                self.session_id,
                MessageType.ASSISTANT,
                response,
                language
            )
            
            # Learn from interaction
            self.learning_engine.learn_from_command(
                user_input,
                self.current_user,
                success=True,
                metadata={'language': language.value, 'response_length': len(response)}
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing user input: {e}")
            error_response = self.personality.generate_error_response(
                language or Language.ENGLISH,
                str(e)
            )
            return error_response
    
    def _generate_response(self, user_input: str, language: Language, context) -> str:
        """Generate appropriate response based on input"""
        user_input_lower = user_input.lower()
        
        # Handle greetings
        if any(greeting in user_input_lower for greeting in ['hello', 'hi', 'hey', 'halo', 'hai']):
            return self.personality.generate_greeting(language, self.current_user)
        
        # Handle thanks
        if any(thanks in user_input_lower for thanks in ['thank', 'thanks', 'terima kasih']):
            return self.personality.generate_acknowledgment(language, "gratitude")
        
        # Handle status requests
        if any(status in user_input_lower for status in ['status', 'how are you', 'apa kabar']):
            return self._get_system_status_response(language)
        
        # Handle task requests
        if any(task in user_input_lower for task in ['do', 'execute', 'run', 'lakukan', 'jalankan']):
            return self._handle_task_request(user_input, language)
        
        # Handle learning requests
        if any(learn in user_input_lower for learn in ['learn', 'remember', 'ingat', 'pelajari']):
            return self._handle_learning_request(user_input, language)
        
        # Handle help requests
        if any(help_word in user_input_lower for help_word in ['help', 'bantuan', 'what can you do']):
            return self._get_help_response(language)
        
        # Handle goodbye
        if any(bye in user_input_lower for bye in ['bye', 'goodbye', 'exit', 'quit', 'selamat tinggal']):
            return self.personality.generate_completion_response(language, "conversation")
        
        # Default response with suggestions
        suggestions = self.learning_engine.get_user_recommendations(self.current_user)
        return self.personality.generate_proactive_suggestion(
            language,
            f"I understand you said: '{user_input}'. Here are some things I can help with.",
            suggestions[:3] if suggestions else []
        )
    
    def _get_system_status_response(self, language: Language) -> str:
        """Get system status response"""
        stats = {
            'tasks': self.task_coordinator.get_statistics(),
            'learning': self.learning_engine.get_learning_statistics(),
            'conversation': len(self.conversation.get_context(self.session_id).messages)
        }
        
        if language == Language.INDONESIAN:
            status_msg = f"Sistem berjalan dengan baik. Saya telah memproses {stats['conversation']} pesan dalam sesi ini."
        else:
            status_msg = f"All systems operational. I've processed {stats['conversation']} messages in this session."
        
        return self.personality.generate_status_update(language, status_msg)
    
    def _handle_task_request(self, user_input: str, language: Language) -> str:
        """Handle task execution request"""
        # Create a demo task
        task = self.task_coordinator.create_task(
            name=f"User Request: {user_input[:50]}",
            executor=self._demo_task_executor,
            user_input,
            task_type=TaskType.USER_INTERACTION,
            priority=TaskPriority.HIGH
        )
        
        # Submit task
        success = self.task_coordinator.submit_task(task)
        
        if success:
            if language == Language.INDONESIAN:
                response = f"Baik, saya akan menjalankan tugas: {user_input}"
            else:
                response = f"Understood, I'll execute the task: {user_input}"
        else:
            if language == Language.INDONESIAN:
                response = "Maaf, saya tidak dapat menjalankan tugas tersebut saat ini."
            else:
                response = "I'm sorry, I cannot execute that task at the moment."
        
        return self.personality.generate_acknowledgment(language, response)
    
    def _demo_task_executor(self, user_input: str) -> str:
        """Demo task executor"""
        # Simulate task execution
        time.sleep(1.0)
        return f"Task completed: {user_input}"
    
    def _handle_learning_request(self, user_input: str, language: Language) -> str:
        """Handle learning request"""
        # Extract what to learn (simplified)
        learning_content = user_input.replace('learn', '').replace('remember', '').replace('ingat', '').replace('pelajari', '').strip()
        
        # Update user preferences
        self.learning_engine.profile_manager.update_preferences(
            self.current_user,
            {'custom_learning': learning_content}
        )
        
        if language == Language.INDONESIAN:
            response = f"Baik, saya akan mengingat: {learning_content}"
        else:
            response = f"Understood, I'll remember: {learning_content}"
        
        return self.personality.generate_acknowledgment(language, response)
    
    def _get_help_response(self, language: Language) -> str:
        """Get help response"""
        if language == Language.INDONESIAN:
            help_text = """Saya dapat membantu Anda dengan:
• Menjalankan tugas dan perintah
• Mengingat informasi penting
• Memberikan status sistem
• Berkomunikasi dalam bahasa Indonesia dan Inggris
• Belajar dari interaksi kita

Coba katakan sesuatu seperti 'jalankan tugas' atau 'ingat informasi ini'."""
        else:
            help_text = """I can help you with:
• Executing tasks and commands
• Remembering important information
• Providing system status
• Communicating in Indonesian and English
• Learning from our interactions

Try saying something like 'execute task' or 'remember this information'."""
        
        return help_text
    
    def run_interactive_demo(self):
        """Run interactive demo"""
        print("\n" + "="*60)
        print("🤖 JARVIS AI SYSTEM - INTERACTIVE DEMO")
        print("="*60)
        print("Type 'quit' or 'exit' to stop the demo")
        print("You can speak in English or Indonesian")
        print("="*60 + "\n")
        
        try:
            while self.is_running:
                try:
                    # Get user input
                    user_input = input("👤 You: ").strip()
                    
                    if not user_input:
                        continue
                    
                    # Check for exit commands
                    if user_input.lower() in ['quit', 'exit', 'keluar']:
                        break
                    
                    # Process input and get response
                    response = self.process_user_input(user_input)
                    
                    # Display response
                    print(f"🤖 Jarvis: {response}\n")
                    
                    # Speak response if voice is available
                    if self.voice_interface.is_available():
                        # Detect language for TTS
                        detection = self.language_manager.detect_language(response)
                        self.voice_interface.speak(response, detection.language)
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    logger.error(f"Error in interactive demo: {e}")
                    print(f"🤖 Jarvis: I encountered an error: {e}\n")
        
        finally:
            # Goodbye message
            goodbye_msg = self.personality.generate_completion_response(
                Language.ENGLISH,
                "demo session"
            )
            print(f"🤖 Jarvis: {goodbye_msg}")
            
            if self.voice_interface.is_available():
                self.voice_interface.speak(goodbye_msg, Language.ENGLISH)
    
    def run_automated_demo(self):
        """Run automated demo with predefined interactions"""
        print("\n" + "="*60)
        print("🤖 JARVIS AI SYSTEM - AUTOMATED DEMO")
        print("="*60)
        
        demo_interactions = [
            ("Hello Jarvis", Language.ENGLISH),
            ("What can you do?", Language.ENGLISH),
            ("Execute a simple task", Language.ENGLISH),
            ("Remember that I like coffee", Language.ENGLISH),
            ("Halo Jarvis, apa kabar?", Language.INDONESIAN),
            ("Jalankan tugas sederhana", Language.INDONESIAN),
            ("Ingat bahwa saya suka kopi", Language.INDONESIAN),
            ("What's my status?", Language.ENGLISH),
            ("Thank you", Language.ENGLISH),
            ("Goodbye", Language.ENGLISH)
        ]
        
        for i, (user_input, expected_lang) in enumerate(demo_interactions, 1):
            print(f"\n--- Interaction {i} ---")
            print(f"👤 User: {user_input}")
            
            # Process input
            response = self.process_user_input(user_input, expected_lang)
            print(f"🤖 Jarvis: {response}")
            
            # Speak if available
            if self.voice_interface.is_available():
                self.voice_interface.speak(response, expected_lang)
            
            # Wait between interactions
            time.sleep(2)
        
        # Show final statistics
        self._show_demo_statistics()
    
    def _show_demo_statistics(self):
        """Show demo statistics"""
        print("\n" + "="*60)
        print("📊 DEMO STATISTICS")
        print("="*60)
        
        # Task coordinator stats
        task_stats = self.task_coordinator.get_statistics()
        print(f"Tasks Created: {task_stats['tasks_created']}")
        print(f"Tasks Completed: {task_stats['tasks_completed']}")
        print(f"Average Execution Time: {task_stats['average_execution_time']:.2f}s")
        
        # Learning engine stats
        learning_stats = self.learning_engine.get_learning_statistics()
        print(f"Learning Data Points: {learning_stats['data']['total_points']}")
        print(f"User Profiles: {learning_stats['profiles']['total_profiles']}")
        
        # Conversation stats
        context = self.conversation.get_context(self.session_id)
        print(f"Messages Exchanged: {len(context.messages)}")
        print(f"Session Duration: {time.time() - context.start_time:.1f}s")
        
        print("="*60)

def main():
    """Main demo function"""
    # Check for required dependencies
    missing_deps = []
    
    try:
        import numpy
    except ImportError:
        missing_deps.append("numpy")
    
    try:
        import sklearn
    except ImportError:
        missing_deps.append("scikit-learn")
    
    if missing_deps:
        print(f"⚠️  Missing dependencies: {', '.join(missing_deps)}")
        print("Please install them with: pip install " + " ".join(missing_deps))
        return
    
    # Create and start Jarvis system
    jarvis = JarvisAISystem()
    
    try:
        # Start the system
        jarvis.start(enable_gui=False)  # Disable GUI for demo
        
        # Choose demo mode
        print("\nSelect demo mode:")
        print("1. Interactive Demo (you type commands)")
        print("2. Automated Demo (predefined interactions)")
        
        choice = input("Enter choice (1 or 2): ").strip()
        
        if choice == "1":
            jarvis.run_interactive_demo()
        else:
            jarvis.run_automated_demo()
    
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        logger.error(f"Demo error: {e}")
        print(f"\nDemo error: {e}")
    finally:
        # Stop the system
        jarvis.stop()
        print("\nDemo completed. Thank you for trying Jarvis AI!")

if __name__ == "__main__":
    main()