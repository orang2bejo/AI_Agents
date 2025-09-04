"""Web Search and Browser Automation Demo

Demonstrates the capabilities of the web search and browser automation modules.
"""

import asyncio
import logging
import os
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from web.search_engine import SearchEngine, SearchConfig, SearchType
from web.html_parser import HTMLParser, ContentExtractor, ParsingConfig
from web.voice_web_control import VoiceWebController, VoiceWebConfig, Language
from web.web_scraper import WebScraper, ScrapingConfig
from web.browser_automation import BrowserAutomation, BrowserConfig, BrowserType, AutomationFramework

def demo_search_engine():
    """Demo search engine functionality"""
    print("\n=== Search Engine Demo ===")
    
    # Configure search
    config = SearchConfig(
        google_api_key=os.getenv('GOOGLE_API_KEY'),
        google_cse_id=os.getenv('GOOGLE_CSE_ID'),
        bing_api_key=os.getenv('BING_API_KEY'),
        serper_api_key=os.getenv('SERPER_API_KEY'),
        serpapi_key=os.getenv('SERPAPI_KEY'),
        default_engine='duckduckgo',  # Free option
        language='id',
        region='ID',
        safe_search=True,
        max_results=5
    )
    
    search_engine = SearchEngine(config)
    
    # Test web search
    print("\n1. Web Search:")
    try:
        results = search_engine.search(
            query="artificial intelligence Indonesia",
            search_type=SearchType.WEB
        )
        
        for i, result in enumerate(results.results[:3], 1):
            print(f"  {i}. {result.title}")
            print(f"     URL: {result.url}")
            print(f"     Snippet: {result.snippet[:100]}...")
            print()
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test news search
    print("\n2. News Search:")
    try:
        results = search_engine.search(
            query="teknologi AI terbaru",
            search_type=SearchType.NEWS
        )
        
        for i, result in enumerate(results.results[:3], 1):
            print(f"  {i}. {result.title}")
            print(f"     URL: {result.url}")
            print(f"     Date: {result.date}")
            print()
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test search suggestions
    print("\n3. Search Suggestions:")
    try:
        suggestions = search_engine.get_suggestions("machine learning")
        for i, suggestion in enumerate(suggestions[:5], 1):
            print(f"  {i}. {suggestion}")
    except Exception as e:
        print(f"  Error: {e}")

def demo_html_parser():
    """Demo HTML parser functionality"""
    print("\n=== HTML Parser Demo ===")
    
    config = ParsingConfig(
        extract_links=True,
        extract_images=True,
        extract_tables=True,
        clean_html=True,
        min_text_length=50,
        max_text_length=5000
    )
    
    parser = HTMLParser(config)
    extractor = ContentExtractor(config)
    
    # Test URL parsing
    print("\n1. Parsing URL:")
    test_url = "https://www.wikipedia.org"
    
    try:
        content = parser.parse_url(test_url)
        print(f"  Title: {content.title}")
        print(f"  Text length: {len(content.text)} characters")
        print(f"  Links found: {len(content.links)}")
        print(f"  Images found: {len(content.images)}")
        print(f"  First paragraph: {content.text[:200]}...")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test content extraction
    print("\n2. Content Extraction:")
    try:
        extracted = extractor.extract_content(test_url)
        print(f"  Main content length: {len(extracted.main_content)} characters")
        print(f"  Summary: {extracted.summary[:150]}...")
        print(f"  Key points: {len(extracted.key_points)}")
        
        if extracted.key_points:
            for i, point in enumerate(extracted.key_points[:3], 1):
                print(f"    {i}. {point}")
    except Exception as e:
        print(f"  Error: {e}")

def demo_voice_web_control():
    """Demo voice web control functionality"""
    print("\n=== Voice Web Control Demo ===")
    
    config = VoiceWebConfig(
        language=Language.INDONESIAN,
        enable_tts=False,  # Disable TTS for demo
        confidence_threshold=0.7
    )
    
    controller = VoiceWebController(config)
    
    # Test voice command parsing
    print("\n1. Voice Command Parsing:")
    test_commands = [
        "cari informasi tentang artificial intelligence",
        "buka website google.com",
        "baca halaman ini",
        "ringkas artikel ini",
        "kembali ke halaman sebelumnya"
    ]
    
    for command in test_commands:
        try:
            intent = controller.parse_voice_command(command)
            print(f"  Command: '{command}'")
            print(f"  Intent: {intent.command.value}")
            print(f"  Query: {intent.query}")
            print(f"  Confidence: {intent.confidence:.2f}")
            print()
        except Exception as e:
            print(f"  Error parsing '{command}': {e}")

def demo_web_scraper():
    """Demo web scraper functionality"""
    print("\n=== Web Scraper Demo ===")
    
    config = ScrapingConfig(
        rate_limit_delay=1.0,
        max_retries=2,
        timeout=10,
        respect_robots_txt=True,
        max_content_length=100000,
        allowed_domains=['example.com', 'httpbin.org']
    )
    
    scraper = WebScraper(config)
    
    # Test single URL scraping
    print("\n1. Single URL Scraping:")
    test_url = "https://httpbin.org/html"
    
    try:
        result = scraper.scrape_url(test_url)
        if result.success:
            print(f"  URL: {result.url}")
            print(f"  Status: {result.status_code}")
            print(f"  Content length: {len(result.content)} characters")
            print(f"  Title: {result.title}")
            print(f"  Links found: {len(result.links)}")
        else:
            print(f"  Failed: {result.error}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test robots.txt checking
    print("\n2. Robots.txt Check:")
    try:
        can_fetch = scraper.robots_checker.can_fetch("https://www.google.com/search")
        print(f"  Can fetch Google search: {can_fetch}")
    except Exception as e:
        print(f"  Error: {e}")

def demo_browser_automation():
    """Demo browser automation functionality"""
    print("\n=== Browser Automation Demo ===")
    
    config = BrowserConfig(
        browser_type=BrowserType.CHROME,
        framework=AutomationFramework.SELENIUM,
        headless=True,  # Run in headless mode for demo
        window_size=(1280, 720),
        page_load_timeout=15,
        implicit_wait=5
    )
    
    print("\n1. Basic Browser Operations:")
    
    try:
        with BrowserAutomation(config) as browser:
            # Navigate to a test page
            result = browser.navigate_to("https://httpbin.org/html")
            if result.success:
                print(f"  ✓ Navigated to: {result.result}")
            else:
                print(f"  ✗ Navigation failed: {result.error}")
                return
            
            # Get page title
            if hasattr(browser.browser, 'driver'):
                title = browser.browser.driver.title
                print(f"  ✓ Page title: {title}")
            
            # Take screenshot
            screenshot_result = browser.browser.take_screenshot("demo_screenshot.png")
            if screenshot_result.success:
                print(f"  ✓ Screenshot saved: {screenshot_result.result}")
            else:
                print(f"  ✗ Screenshot failed: {screenshot_result.error}")
            
            # Get page source
            source_result = browser.browser.get_page_source()
            if source_result.success:
                print(f"  ✓ Page source length: {len(source_result.result)} characters")
            else:
                print(f"  ✗ Failed to get page source: {source_result.error}")
    
    except Exception as e:
        print(f"  Error: {e}")
        print("  Note: Browser automation requires Chrome/Firefox to be installed")

async def demo_async_browser():
    """Demo async browser automation with Playwright"""
    print("\n=== Async Browser Automation Demo ===")
    
    config = BrowserConfig(
        browser_type=BrowserType.CHROME,
        framework=AutomationFramework.PLAYWRIGHT,
        headless=True,
        window_size=(1280, 720)
    )
    
    try:
        automation = BrowserAutomation(config)
        await automation.start_async()
        
        # Navigate to test page
        result = await automation.navigate_to_async("https://httpbin.org/html")
        if result.success:
            print(f"  ✓ Navigated to: {result.result}")
        
        # Take screenshot
        screenshot_result = await automation.browser.take_screenshot("demo_async_screenshot.png")
        if screenshot_result.success:
            print(f"  ✓ Async screenshot saved: {screenshot_result.result}")
        
        await automation.browser.close()
        
    except ImportError:
        print("  Playwright not installed. Install with: pip install playwright")
    except Exception as e:
        print(f"  Error: {e}")

def main():
    """Run all demos"""
    print("Windows Use Autonomous Agent - Web Module Demo")
    print("=" * 50)
    
    # Check for API keys
    api_keys = {
        'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
        'BING_API_KEY': os.getenv('BING_API_KEY'),
        'SERPER_API_KEY': os.getenv('SERPER_API_KEY')
    }
    
    missing_keys = [key for key, value in api_keys.items() if not value]
    if missing_keys:
        print(f"\nWarning: Missing API keys: {', '.join(missing_keys)}")
        print("Some search features may not work. DuckDuckGo will be used as fallback.")
    
    # Run demos
    try:
        demo_search_engine()
        demo_html_parser()
        demo_voice_web_control()
        demo_web_scraper()
        demo_browser_automation()
        
        # Run async demo
        print("\nRunning async browser demo...")
        asyncio.run(demo_async_browser())
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        logger.error(f"Demo error: {e}")
    
    print("\nDemo completed!")
    print("\nNote: For full functionality, install optional dependencies:")
    print("  pip install selenium playwright beautifulsoup4 requests")
    print("  playwright install chromium")

if __name__ == "__main__":
    main()