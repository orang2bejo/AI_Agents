"""Web Search and Internet Surfing Module

This module provides comprehensive web search and internet browsing capabilities
for the Windows Use Autonomous Agent, including:

- Search API integration (Google, Bing, DuckDuckGo)
- HTML parsing and content extraction
- Voice-controlled web navigation
- Web scraping with rate limiting
- Search result ranking and filtering
- Browser automation for complex tasks
"""

from .search_engine import SearchEngine, SearchResult
from .html_parser import HTMLParser, ContentExtractor
from .voice_web_control import VoiceWebController
from .web_scraper import WebScraper
from .browser_automation import BrowserAutomation

__all__ = [
    'SearchEngine',
    'SearchResult', 
    'HTMLParser',
    'ContentExtractor',
    'VoiceWebController',
    'WebScraper',
    'BrowserAutomation'
]

__version__ = '1.0.0'