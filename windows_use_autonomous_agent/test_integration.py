#!/usr/bin/env python3
"""
Integration Test for Migrated Components

Test script to verify that all migrated components from jarvis_core
are properly integrated into the windows_use_autonomous_agent structure.

Author: Jarvis AI Team
Date: 2024
"""

import sys
import traceback
from pathlib import Path

# Add the windows_use directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "windows_use"))

def test_web_components():
    """Test web module components"""
    print("Testing web module components...")
    
    try:
        # Test web form automation
        from windows_use.web.web_form_automation import (
            WebFormAutomation,
            AutomationMode,
            FormFieldType,
            ActionType,
            AutomationStatus
        )
        print("✓ Web Form Automation components imported successfully")
        
        # Test browser automation
        from windows_use.web.browser_automation import (
            BrowserAutomation,
            BrowserType,
            AutomationFramework
        )
        print("✓ Browser Automation components imported successfully")
        
        # Test web search
        from windows_use.web import SearchEngine
        print("✓ Web Search components imported successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Web components test failed: {e}")
        traceback.print_exc()
        return False

def test_security_components():
    """Test security module components"""
    print("\nTesting security module components...")
    
    try:
        # Test voice authentication
        from windows_use.security.voice_authentication import (
            VoiceAuthenticator,
            AuthenticationLevel,
            VoiceAuthStatus,
            PermissionType
        )
        print("✓ Voice Authentication components imported successfully")
        
        # Test existing security components
        from windows_use.security import (
            GuardrailsEngine,
            HITLManager,
            SecurityResult
        )
        print("✓ Existing Security components imported successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Security components test failed: {e}")
        traceback.print_exc()
        return False

def test_llm_components():
    """Test LLM module components"""
    print("\nTesting LLM module components...")
    
    try:
        # Test LLM providers
        from windows_use.llm.llm_provider import (
            LLMRouter,
            BaseLLMProvider,
            OpenAIProvider,
            LLMProvider,
            LLMMessage,
            LLMResponse
        )
        print("✓ LLM Provider components imported successfully")
        
        # Test model registry
        from windows_use.llm.model_registry import (
            ModelRegistry,
            ModelInfo,
            ModelCapability,
            MODEL_CATALOG
        )
        print("✓ Model Registry components imported successfully")
        
        # Test existing LLM components
        from windows_use.llm import (
            LLMProvider as ExistingLLMProvider,
            ModelRegistry as ExistingModelRegistry
        )
        print("✓ Existing LLM components imported successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ LLM components test failed: {e}")
        traceback.print_exc()
        return False

def test_jarvis_ai_components():
    """Test Jarvis AI module components"""
    print("\nTesting Jarvis AI module components...")
    
    try:
        # Test agent manager
        from windows_use.jarvis_ai.agent_manager import (
            AgentManager,
            BaseAgent,
            AgentType,
            AgentStatus,
            AgentTask
        )
        print("✓ Agent Manager components imported successfully")
        
        # Test existing Jarvis AI components
        from windows_use.jarvis_ai import (
            JarvisPersonality,
            ConversationManager,
            VoiceInterface
        )
        print("✓ Existing Jarvis AI components imported successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Jarvis AI components test failed: {e}")
        traceback.print_exc()
        return False

def test_component_functionality():
    """Test basic functionality of migrated components"""
    print("\nTesting component functionality...")
    
    try:
        # Test Model Registry functionality
        from windows_use.llm.model_registry import MODEL_CATALOG, ModelCapability
        
        # Get available models
        models = MODEL_CATALOG.list_models()
        print(f"✓ Model Registry contains {len(models)} models")
        
        # Test capability search
        code_models = MODEL_CATALOG.find_models_by_capability([ModelCapability.CODE_GENERATION])
        print(f"✓ Found {len(code_models)} models with code generation capability")
        
        # Test best model selection
        best_model = MODEL_CATALOG.get_best_model_for_task([ModelCapability.TEXT_GENERATION])
        if best_model:
            print(f"✓ Best model for text generation: {best_model.name}")
        
        # Test Web Form Automation initialization
        from windows_use.web.web_form_automation import WebFormAutomation, RPAConfig
        
        config = RPAConfig(
            headless=True,
            timeout=30000,
            retry_on_failure=True
        )
        
        # Note: We don't actually initialize the browser to avoid dependencies
        print("✓ Web Form Automation configuration created successfully")
        
        # Test Voice Authentication configuration
        from windows_use.security.voice_authentication import VoiceAuthConfig
        
        auth_config = VoiceAuthConfig(
            audio_sample_rate=16000,
            enrollment_duration=3.0,
            verification_threshold=0.8
        )
        print("✓ Voice Authentication configuration created successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Component functionality test failed: {e}")
        traceback.print_exc()
        return False

def test_import_paths():
    """Test that import paths are correctly updated"""
    print("\nTesting import paths...")
    
    try:
        # Test that we can import from the new structure
        import windows_use.web
        import windows_use.security
        import windows_use.llm
        import windows_use.jarvis_ai
        
        print("✓ All module imports successful")
        
        # Test that __all__ exports are working
        from windows_use.web import __all__ as web_all
        from windows_use.security import __all__ as security_all
        from windows_use.llm import __all__ as llm_all
        from windows_use.jarvis_ai import __all__ as jarvis_all
        
        print(f"✓ Web module exports: {len(web_all)} items")
        print(f"✓ Security module exports: {len(security_all)} items")
        print(f"✓ LLM module exports: {len(llm_all)} items")
        print(f"✓ Jarvis AI module exports: {len(jarvis_all)} items")
        
        return True
        
    except Exception as e:
        print(f"✗ Import paths test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all integration tests"""
    print("=" * 60)
    print("JARVIS CORE MIGRATION INTEGRATION TESTS")
    print("=" * 60)
    
    tests = [
        test_web_components,
        test_security_components,
        test_llm_components,
        test_jarvis_ai_components,
        test_component_functionality,
        test_import_paths
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {passed + failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Migration integration successful.")
        return True
    else:
        print(f"\n❌ {failed} test(s) failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)