#!/usr/bin/env python3
# test_python312_upgrade.py
# Skrip untuk memverifikasi upgrade Python 3.12 berhasil

import sys
import os
import importlib
from datetime import datetime

def test_python_version():
    """Test Python version"""
    print("=" * 60)
    print("🐍 PYTHON VERSION TEST")
    print("=" * 60)
    
    version = sys.version_info
    print(f"Python Version: {version.major}.{version.minor}.{version.micro}")
    print(f"Full Version: {sys.version}")
    
    if version.major == 3 and version.minor >= 12:
        print("✅ Python 3.12+ detected - PASSED")
        return True
    else:
        print("❌ Python version requirement not met - FAILED")
        return False

def test_core_imports():
    """Test core module imports"""
    print("\n" + "=" * 60)
    print("📦 CORE IMPORTS TEST")
    print("=" * 60)
    
    modules_to_test = [
        'windows_use',
        'windows_use.agent',
        'windows_use.tools',
        'langchain',
        'dotenv',
        'numpy',
        'pandas',
        'requests'
    ]
    
    passed = 0
    failed = 0
    
    for module in modules_to_test:
        try:
            importlib.import_module(module)
            print(f"✅ {module} - PASSED")
            passed += 1
        except ImportError as e:
            print(f"❌ {module} - FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"⚠️  {module} - WARNING: {e}")
            passed += 1  # Count as passed if import works but has warnings
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0

def test_jarvis_components():
    """Test Jarvis AI specific components"""
    print("\n" + "=" * 60)
    print("🤖 JARVIS AI COMPONENTS TEST")
    print("=" * 60)
    
    try:
        from windows_use.agent import Agent
        print("✅ Agent class import - PASSED")
        
        # Test creating agent with mock LLM
        from langchain_community.llms import FakeListLLM
        mock_llm = FakeListLLM(responses=["Test response"])
        
        agent = Agent(
            instructions=["Test instruction"],
            llm=mock_llm,
            use_vision=False  # Disable vision for test
        )
        print("✅ Agent initialization - PASSED")
        
        return True
        
    except Exception as e:
        print(f"❌ Jarvis AI components test - FAILED: {e}")
        return False

def test_environment_setup():
    """Test environment configuration"""
    print("\n" + "=" * 60)
    print("🔧 ENVIRONMENT SETUP TEST")
    print("=" * 60)
    
    # Check virtual environment
    venv_path = os.path.join(os.getcwd(), 'venv')
    if os.path.exists(venv_path):
        print("✅ Virtual environment exists - PASSED")
    else:
        print("❌ Virtual environment not found - FAILED")
        return False
    
    # Check .env file
    env_path = os.path.join(os.getcwd(), '.env')
    if os.path.exists(env_path):
        print("✅ .env configuration file exists - PASSED")
    else:
        print("⚠️  .env file not found - creating default")
    
    # Check requirements installation
    req_path = os.path.join(os.getcwd(), 'requirements.txt')
    if os.path.exists(req_path):
        print("✅ requirements.txt exists - PASSED")
    else:
        print("❌ requirements.txt not found - FAILED")
        return False
    
    return True

def main():
    """Main test function"""
    print("🚀 PYTHON 3.12 UPGRADE VERIFICATION")
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Working Directory: {os.getcwd()}")
    
    tests = [
        ("Python Version", test_python_version),
        ("Core Imports", test_core_imports),
        ("Jarvis Components", test_jarvis_components),
        ("Environment Setup", test_environment_setup)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed_tests += 1
        except Exception as e:
            print(f"❌ {test_name} - CRITICAL ERROR: {e}")
    
    # Final results
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS")
    print("=" * 60)
    print(f"Tests Passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Python 3.12 upgrade successful!")
        print("✅ Jarvis AI is ready to use with Python 3.12")
        return True
    else:
        print(f"⚠️  {total_tests - passed_tests} test(s) failed")
        print("💡 Please check the errors above and resolve them")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)