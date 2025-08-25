# main.py
import os
from dotenv import load_dotenv
from windows_use.agent import Agent

load_dotenv()

def create_llm():
    """Create LLM with fallback options"""
    try:
        # Try Google Gemini if API key is available
        google_api_key = os.getenv('GOOGLE_API_KEY')
        if google_api_key and google_api_key != 'your_google_api_key_here':
            from langchain_google_genai import ChatGoogleGenerativeAI
            print("🤖 Using Google Gemini...")
            return ChatGoogleGenerativeAI(model='gemini-2.0-flash')
    except Exception as e:
        print(f"⚠️  Google Gemini not available: {e}")
    
    try:
        # Try OpenAI if API key is available
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if openai_api_key and openai_api_key != 'your_openai_api_key_here':
            from langchain_openai import ChatOpenAI
            print("🤖 Using OpenAI GPT...")
            return ChatOpenAI(model='gpt-3.5-turbo')
    except Exception as e:
        print(f"⚠️  OpenAI not available: {e}")
    
    # Fallback to mock LLM for development
    print("🤖 Using Mock LLM for development...")
    from langchain.llms.fake import FakeListLLM
    return FakeListLLM(responses=[
        "Hello! I'm Jarvis AI running in development mode. All core systems are operational.",
        "System check complete. All modules loaded successfully with Python 3.12.",
        "Ready to assist you with Windows automation tasks."
    ])

def main():
    print("🚀 Starting Jarvis AI System...")
    print(f"🐍 Python Version: {os.sys.version}")
    
    # Create LLM with fallback
    llm = create_llm()
    
    # Initialize agent
    instructions = [
        'We have Claude Desktop, Perplexity and ChatGPT App installed on the desktop so if you need any help, just ask your AI friends.',
        'You are running on Python 3.12 with all dependencies successfully installed.',
        'All core Windows automation modules are available and functional.'
    ]
    
    try:
        agent = Agent(instructions=instructions, llm=llm, use_vision=True)
        print("✅ Jarvis AI Agent initialized successfully!")
        
        # Interactive loop
        while True:
            query = input("\n🎯 Enter your query (or 'quit' to exit): ")
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            try:
                agent_result = agent.invoke(query=query)
                print(f"\n🤖 Jarvis: {agent_result.content}")
            except Exception as e:
                print(f"❌ Error processing query: {e}")
                
    except Exception as e:
        print(f"❌ Error initializing agent: {e}")
        print("💡 Tip: Make sure to configure API keys in .env file for full functionality")

if __name__ == "__main__":
    main()