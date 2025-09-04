"""Web Search and Internet Browsing Module

This module provides comprehensive web search and internet browsing capabilities
for the Windows Use Autonomous Agent, including:

- Multi-provider search engine integration (Google, Bing, DuckDuckGo, etc.)
- Intelligent HTML parsing and content extraction
- Voice-controlled web navigation
- Advanced web scraping with rate limiting and robots.txt compliance
- Browser automation for complex interactions

Sub-modules:
- search_engine: Multi-provider search API integration
- html_parser: HTML parsing and content extraction
- voice_web_control: Voice-controlled web navigation
- web_scraper: Intelligent web scraping
- browser_automation: Browser automation with Selenium/Playwright
"""

# Import main classes for easy access
try:
    from .search_engine import SearchEngine, SearchConfig, SearchResult, SearchType
except ImportError:
    SearchEngine = SearchConfig = SearchResult = SearchType = None

try:
    from .html_parser import HTMLParser, ContentExtractor, ExtractedContent, ParsingConfig
except ImportError:
    HTMLParser = ContentExtractor = ExtractedContent = ParsingConfig = None

try:
    from .voice_web_control import VoiceWebController, VoiceWebConfig, VoiceCommand, Language
except ImportError:
    VoiceWebController = VoiceWebConfig = VoiceCommand = Language = None

try:
    from .web_scraper import WebScraper, ScrapingConfig, ScrapingResult
except ImportError:
    WebScraper = ScrapingConfig = ScrapingResult = None

try:
    from .browser_automation import BrowserAutomation, BrowserConfig, BrowserType, AutomationFramework
except ImportError:
    BrowserAutomation = BrowserConfig = BrowserType = AutomationFramework = None

try:
    from .web_form_automation import (
        WebFormAutomation, AutomationMode, FormFieldType, ActionType, 
        AutomationStatus, FormField, AutomationAction, FormTemplate, 
        AutomationSession, RPAConfig
    )
except ImportError:
    WebFormAutomation = AutomationMode = FormFieldType = ActionType = None
    AutomationStatus = FormField = AutomationAction = FormTemplate = None
    AutomationSession = RPAConfig = None

__all__ = [
    'SearchEngine', 'SearchConfig', 'SearchResult', 'SearchType',
    'HTMLParser', 'ContentExtractor', 'ExtractedContent', 'ParsingConfig',
    'VoiceWebController', 'VoiceWebConfig', 'VoiceCommand', 'Language',
    'WebScraper', 'ScrapingConfig', 'ScrapingResult',
    'BrowserAutomation', 'BrowserConfig', 'BrowserType', 'AutomationFramework',
    'WebFormAutomation', 'AutomationMode', 'FormFieldType', 'ActionType',
    'AutomationStatus', 'FormField', 'AutomationAction', 'FormTemplate',
    'AutomationSession', 'RPAConfig'
]

# Version info
__version__ = '1.0.0'
__author__ = 'Windows Use Autonomous Agent'
__description__ = 'Web Search and Internet Browsing Module'