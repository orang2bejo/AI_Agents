"""Demo Multi-Provider LLM Manager

Contoh penggunaan LLM Manager dengan berbagai provider.
"""

import os
import asyncio
import logging
from typing import List

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import LLM components
from windows_use.llm import LLMManager, LLMManagerConfig
from windows_use.llm.base import LLMMessage, LLMConfig, MessageRole
from windows_use.llm.router import TaskType, RoutingPolicy


def setup_environment():
    """Setup environment variables for demo"""
    # Set demo API keys (replace with actual keys)
    demo_keys = {
        "GEMINI_API_KEY": "your-gemini-api-key",
        "ANTHROPIC_API_KEY": "your-anthropic-api-key", 
        "GROQ_API_KEY": "your-groq-api-key",
        "DEEPSEEK_API_KEY": "your-deepseek-api-key",
        "QWEN_API_KEY": "your-qwen-api-key"
    }
    
    for key, value in demo_keys.items():
        if not os.getenv(key):
            print(f"Warning: {key} not set. Provider will be unavailable.")


def demo_basic_chat():
    """Demo basic chat functionality"""
    print("\n=== Demo Basic Chat ===")
    
    # Initialize LLM Manager
    config = LLMManagerConfig(
        default_provider="ollama",
        routing_policy=RoutingPolicy.OFFLINE_FIRST,
        enable_fallback=True
    )
    
    llm_manager = LLMManager(config)
    
    # Check available providers
    providers = llm_manager.get_available_providers()
    print(f"Available providers: {providers}")
    
    if not providers:
        print("No providers available. Please check your setup.")
        return
    
    # Create messages
    messages = [
        LLMMessage(role=MessageRole.SYSTEM, content="Anda adalah asisten AI yang membantu dalam bahasa Indonesia."),
        LLMMessage(role=MessageRole.USER, content="Jelaskan apa itu artificial intelligence dalam 2 paragraf.")
    ]
    
    try:
        # Send request
        response = llm_manager.chat(
            messages=messages,
            task_type=TaskType.GENERAL
        )
        
        print(f"Provider: {response.provider}")
        print(f"Model: {response.model}")
        print(f"Response: {response.content}")
        print(f"Latency: {response.latency_ms}ms")
        
    except Exception as e:
        print(f"Error: {e}")


def demo_tool_calling():
    """Demo tool calling functionality"""
    print("\n=== Demo Tool Calling ===")
    
    llm_manager = LLMManager()
    
    # Define tools
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get current weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and country, e.g. Jakarta, Indonesia"
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "Temperature unit"
                        }
                    },
                    "required": ["location"]
                }
            }
        }
    ]
    
    messages = [
        LLMMessage(role=MessageRole.USER, content="Bagaimana cuaca di Jakarta hari ini?")
    ]
    
    try:
        response = llm_manager.chat(
            messages=messages,
            tools=tools,
            task_type=TaskType.PLANNING
        )
        
        print(f"Provider: {response.provider}")
        print(f"Content: {response.content}")
        
        if response.tool_calls:
            print("Tool calls:")
            for tool_call in response.tool_calls:
                print(f"  - {tool_call['function']['name']}: {tool_call['function']['arguments']}")
        
    except Exception as e:
        print(f"Error: {e}")


def demo_streaming():
    """Demo streaming responses"""
    print("\n=== Demo Streaming ===")
    
    llm_manager = LLMManager()
    
    messages = [
        LLMMessage(role=MessageRole.USER, content="Ceritakan sebuah dongeng pendek tentang robot yang belajar memasak.")
    ]
    
    config = LLMConfig(stream=True)
    
    try:
        response_stream = llm_manager.chat(
            messages=messages,
            config=config,
            task_type=TaskType.CREATIVE
        )
        
        print("Streaming response:")
        full_content = ""
        
        for chunk in response_stream:
            if chunk.content:
                print(chunk.content, end="", flush=True)
                full_content += chunk.content
            
            if chunk.finish_reason:
                print(f"\n\nFinished: {chunk.finish_reason}")
                print(f"Provider: {chunk.provider}")
                print(f"Total latency: {chunk.latency_ms}ms")
                break
        
    except Exception as e:
        print(f"Error: {e}")


def demo_provider_comparison():
    """Demo comparing different providers"""
    print("\n=== Demo Provider Comparison ===")
    
    llm_manager = LLMManager()
    
    messages = [
        LLMMessage(role=MessageRole.USER, content="Apa perbedaan antara machine learning dan deep learning?")
    ]
    
    # Test different providers
    providers_to_test = llm_manager.get_available_providers()
    
    for provider in providers_to_test[:3]:  # Test first 3 providers
        try:
            print(f"\n--- Testing {provider} ---")
            
            response = llm_manager.chat(
                messages=messages,
                provider=provider,
                task_type=TaskType.EDUCATIONAL
            )
            
            print(f"Model: {response.model}")
            print(f"Response length: {len(response.content)} chars")
            print(f"Latency: {response.latency_ms}ms")
            print(f"Preview: {response.content[:150]}...")
            
        except Exception as e:
            print(f"Error with {provider}: {e}")


def demo_cost_estimation():
    """Demo cost estimation"""
    print("\n=== Demo Cost Estimation ===")
    
    llm_manager = LLMManager()
    
    messages = [
        LLMMessage(role=MessageRole.USER, content="Buatkan rencana bisnis untuk startup teknologi AI yang fokus pada otomasi kantor. Sertakan analisis pasar, strategi pemasaran, proyeksi keuangan, dan roadmap pengembangan produk untuk 3 tahun ke depan.")
    ]
    
    # Estimate costs across providers
    costs = llm_manager.estimate_cost(messages)
    
    print("Estimated costs per provider:")
    for provider, cost in costs.items():
        print(f"  {provider}: ${cost:.4f}")
    
    # Find cheapest option
    if costs:
        cheapest = min(costs.items(), key=lambda x: x[1])
        print(f"\nCheapest option: {cheapest[0]} (${cheapest[1]:.4f})")


def demo_provider_status():
    """Demo provider status check"""
    print("\n=== Demo Provider Status ===")
    
    llm_manager = LLMManager()
    
    status = llm_manager.get_provider_status()
    
    for provider, info in status.items():
        print(f"\n{provider.upper()}:")
        print(f"  Available: {info.get('available', False)}")
        
        if 'capabilities' in info:
            caps = info['capabilities']
            print(f"  Max Context: {caps['max_context']:,} tokens")
            print(f"  Tools: {caps['supports_tools']}")
            print(f"  Vision: {caps['supports_vision']}")
            print(f"  JSON Mode: {caps['supports_json_mode']}")
            print(f"  Streaming: {caps['supports_streaming']}")
            print(f"  Cost (input/output): ${caps['cost_per_1k_input']:.3f}/${caps['cost_per_1k_output']:.3f} per 1K tokens")
            print(f"  Typical Latency: {caps['typical_latency_ms']}ms")
        
        if 'error' in info:
            print(f"  Error: {info['error']}")


def demo_routing_policies():
    """Demo different routing policies"""
    print("\n=== Demo Routing Policies ===")
    
    messages = [
        LLMMessage(role=MessageRole.USER, content="Hitung 15 * 23 + 47 - 8 / 2")
    ]
    
    policies = [
        (RoutingPolicy.OFFLINE_FIRST, "Offline First"),
        (RoutingPolicy.COST_OPTIMIZED, "Cost Optimized"),
        (RoutingPolicy.SPEED_OPTIMIZED, "Speed Optimized"),
        (RoutingPolicy.QUALITY_OPTIMIZED, "Quality Optimized")
    ]
    
    for policy, name in policies:
        try:
            print(f"\n--- {name} ---")
            
            config = LLMManagerConfig(routing_policy=policy)
            llm_manager = LLMManager(config)
            
            response = llm_manager.chat(
                messages=messages,
                task_type=TaskType.ANALYTICAL
            )
            
            print(f"Selected: {response.provider} ({response.model})")
            print(f"Response: {response.content}")
            print(f"Latency: {response.latency_ms}ms")
            
        except Exception as e:
            print(f"Error with {name}: {e}")


def main():
    """Main demo function"""
    print("Multi-Provider LLM Manager Demo")
    print("=" * 40)
    
    # Setup environment
    setup_environment()
    
    # Run demos
    try:
        demo_provider_status()
        demo_basic_chat()
        demo_tool_calling()
        demo_streaming()
        demo_provider_comparison()
        demo_cost_estimation()
        demo_routing_policies()
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo error: {e}")
        logger.exception("Demo failed")
    
    print("\nDemo completed!")


if __name__ == "__main__":
    main()