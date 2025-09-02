#!/usr/bin/env python3
"""
Jarvis AI Installation Test Script
This script verifies that all core components are properly installed and functional.
"""

import sys
import traceback
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Test importing all core Jarvis AI modules"""
    print("Testing core module imports...")
    
    try:
        # Test logging utilities
        from windows_use.utils import setup_logging, get_logger, LoggingManager
        print("✓ Logging utilities imported successfully")
        
        # Test Jarvis AI modules
        from windows_use.jarvis_ai import (
            JarvisPersonality, PersonalityTrait, ResponseTone,
            ConversationManager, MessageType, Language,
            LanguageManager,
            VoiceInterface, VoiceState, InputMode,
            TaskCoordinator, TaskType, TaskPriority,
            LearningEngine,
            JarvisDashboard, DashboardTheme
        )
        print("✓ Jarvis AI modules imported successfully")
        
        # Test web modules
        from windows_use.web import SearchEngine, WebScraper
        print("✓ Web modules imported successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Import failed: {e}")
        traceback.print_exc()
        return False

def test_basic_functionality():
    """Test basic functionality of core components"""
    print("\nTesting basic functionality...")
    
    try:
        # Test personality creation
        from windows_use.jarvis_ai import JarvisPersonality, PersonalityTrait, ResponseTone
        personality = JarvisPersonality()
        greeting = personality.generate_greeting()
        print("✓ Personality system functional")
        
        # Test conversation manager
        from windows_use.jarvis_ai import ConversationManager, MessageType
        conversation = ConversationManager()
        conversation.add_user_message("Hello")
        print("✓ Conversation manager functional")
        
        # Test task coordinator
        from windows_use.jarvis_ai import TaskCoordinator, TaskType, TaskPriority
        coordinator = TaskCoordinator()
        print("✓ Task coordinator functional")
        
        return True
        
    except Exception as e:
        print(f"✗ Functionality test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("Jarvis AI Installation Test")
    print("=" * 40)
    
    # Test imports
    imports_ok = test_imports()
    
    # Test basic functionality
    functionality_ok = test_basic_functionality()
    
    # Summary
    print("\nTest Summary:")
    print("=" * 40)
    
    if imports_ok and functionality_ok:
        print("🎉 All tests passed! Jarvis AI is properly installed.")
        print("\nYou can now run the main system with:")
        print("python scripts\\jarvis_main.py")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())