"""Search Engine Integration Module

Provides unified interface for multiple search APIs including Google, Bing, and DuckDuckGo.
Supports voice-controlled search with Indonesian and English language support.
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from urllib.parse import quote_plus, urljoin

import aiohttp
import requests
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class SearchProvider(Enum):
    """Supported search providers"""
    GOOGLE = "google"
    BING = "bing"
    DUCKDUCKGO = "duckduckgo"
    SERPER = "serper"  # Google Search API alternative
    SERPAPI = "serpapi"  # Another Google Search API

class SearchType(Enum):
    """Types of search queries"""
    WEB = "web"
    IMAGES = "images"
    NEWS = "news"
    VIDEOS = "videos"
    SHOPPING = "shopping"
    ACADEMIC = "academic"

@dataclass
class SearchResult:
    """Individual search result"""
    title: str
    url: str
    snippet: str
    provider: SearchProvider
    rank: int
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'title': self.title,
            'url': self.url,
            'snippet': self.snippet,
            'provider': self.provider.value,
            'rank': self.rank,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }

class SearchConfig(BaseModel):
    """Search configuration"""
    providers: List[SearchProvider] = [SearchProvider.DUCKDUCKGO, SearchProvider.GOOGLE]
    default_provider: SearchProvider = SearchProvider.DUCKDUCKGO
    max_results: int = 10
    timeout: int = 30
    rate_limit_delay: float = 1.0
    language: str = "id"  # Indonesian by default
    region: str = "ID"   # Indonesia
    safe_search: bool = True
    
    # API Keys (optional)
    google_api_key: Optional[str] = None
    google_cse_id: Optional[str] = None
    bing_api_key: Optional[str] = None
    serper_api_key: Optional[str] = None
    serpapi_key: Optional[str] = None

class SearchEngine:
    """Unified search engine interface"""
    
    def __init__(self, config: SearchConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self._last_request_time = {}
        
    def search(self, query: str, 
              search_type: SearchType = SearchType.WEB,
              provider: Optional[SearchProvider] = None,
              max_results: Optional[int] = None) -> List[SearchResult]:
        """Perform search with specified provider"""
        provider = provider or self.config.default_provider
        max_results = max_results or self.config.max_results
        
        logger.info(f"Searching '{query}' using {provider.value}")
        
        # Rate limiting
        self._apply_rate_limit(provider)
        
        try:
            if provider == SearchProvider.GOOGLE:
                return self._search_google(query, search_type, max_results)
            elif provider == SearchProvider.BING:
                return self._search_bing(query, search_type, max_results)
            elif provider == SearchProvider.DUCKDUCKGO:
                return self._search_duckduckgo(query, search_type, max_results)
            elif provider == SearchProvider.SERPER:
                return self._search_serper(query, search_type, max_results)
            elif provider == SearchProvider.SERPAPI:
                return self._search_serpapi(query, search_type, max_results)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
                
        except Exception as e:
            logger.error(f"Search failed for provider {provider.value}: {e}")
            # Try fallback provider
            if provider != SearchProvider.DUCKDUCKGO:
                logger.info("Falling back to DuckDuckGo")
                return self._search_duckduckgo(query, search_type, max_results)
            return []
    
    def multi_search(self, query: str, 
                    providers: Optional[List[SearchProvider]] = None,
                    search_type: SearchType = SearchType.WEB,
                    max_results: Optional[int] = None) -> Dict[SearchProvider, List[SearchResult]]:
        """Search across multiple providers"""
        providers = providers or self.config.providers
        results = {}
        
        for provider in providers:
            try:
                results[provider] = self.search(query, search_type, provider, max_results)
            except Exception as e:
                logger.error(f"Multi-search failed for {provider.value}: {e}")
                results[provider] = []
                
        return results
    
    def _apply_rate_limit(self, provider: SearchProvider):
        """Apply rate limiting between requests"""
        now = time.time()
        last_time = self._last_request_time.get(provider, 0)
        
        if now - last_time < self.config.rate_limit_delay:
            sleep_time = self.config.rate_limit_delay - (now - last_time)
            time.sleep(sleep_time)
            
        self._last_request_time[provider] = time.time()
    
    def _search_google(self, query: str, search_type: SearchType, max_results: int) -> List[SearchResult]:
        """Search using Google Custom Search API"""
        if not self.config.google_api_key or not self.config.google_cse_id:
            raise ValueError("Google API key and CSE ID required")
            
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': self.config.google_api_key,
            'cx': self.config.google_cse_id,
            'q': query,
            'num': min(max_results, 10),  # Google API limit
            'lr': f'lang_{self.config.language}',
            'gl': self.config.region.lower(),
            'safe': 'active' if self.config.safe_search else 'off'
        }
        
        if search_type == SearchType.IMAGES:
            params['searchType'] = 'image'
        
        response = self.session.get(url, params=params, timeout=self.config.timeout)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for i, item in enumerate(data.get('items', [])):
            result = SearchResult(
                title=item.get('title', ''),
                url=item.get('link', ''),
                snippet=item.get('snippet', ''),
                provider=SearchProvider.GOOGLE,
                rank=i + 1,
                metadata={
                    'displayLink': item.get('displayLink'),
                    'formattedUrl': item.get('formattedUrl')
                }
            )
            results.append(result)
            
        return results
    
    def _search_bing(self, query: str, search_type: SearchType, max_results: int) -> List[SearchResult]:
        """Search using Bing Search API"""
        if not self.config.bing_api_key:
            raise ValueError("Bing API key required")
            
        url = "https://api.bing.microsoft.com/v7.0/search"
        headers = {'Ocp-Apim-Subscription-Key': self.config.bing_api_key}
        params = {
            'q': query,
            'count': min(max_results, 50),  # Bing API limit
            'mkt': f'{self.config.language}-{self.config.region}',
            'safeSearch': 'Strict' if self.config.safe_search else 'Off'
        }
        
        response = self.session.get(url, headers=headers, params=params, timeout=self.config.timeout)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for i, item in enumerate(data.get('webPages', {}).get('value', [])):
            result = SearchResult(
                title=item.get('name', ''),
                url=item.get('url', ''),
                snippet=item.get('snippet', ''),
                provider=SearchProvider.BING,
                rank=i + 1,
                metadata={
                    'displayUrl': item.get('displayUrl'),
                    'dateLastCrawled': item.get('dateLastCrawled')
                }
            )
            results.append(result)
            
        return results
    
    def _search_duckduckgo(self, query: str, search_type: SearchType, max_results: int) -> List[SearchResult]:
        """Search using DuckDuckGo (no API key required)"""
        # DuckDuckGo Instant Answer API
        url = "https://api.duckduckgo.com/"
        params = {
            'q': query,
            'format': 'json',
            'no_html': '1',
            'skip_disambig': '1'
        }
        
        response = self.session.get(url, params=params, timeout=self.config.timeout)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        # Process instant answer
        if data.get('AbstractText'):
            result = SearchResult(
                title=data.get('Heading', query),
                url=data.get('AbstractURL', ''),
                snippet=data.get('AbstractText', ''),
                provider=SearchProvider.DUCKDUCKGO,
                rank=1,
                metadata={'type': 'instant_answer'}
            )
            results.append(result)
        
        # Process related topics
        for i, topic in enumerate(data.get('RelatedTopics', [])[:max_results-1]):
            if isinstance(topic, dict) and 'Text' in topic:
                result = SearchResult(
                    title=topic.get('Text', '').split(' - ')[0],
                    url=topic.get('FirstURL', ''),
                    snippet=topic.get('Text', ''),
                    provider=SearchProvider.DUCKDUCKGO,
                    rank=len(results) + 1,
                    metadata={'type': 'related_topic'}
                )
                results.append(result)
                
        return results[:max_results]
    
    def _search_serper(self, query: str, search_type: SearchType, max_results: int) -> List[SearchResult]:
        """Search using Serper API (Google Search alternative)"""
        if not self.config.serper_api_key:
            raise ValueError("Serper API key required")
            
        url = "https://google.serper.dev/search"
        headers = {
            'X-API-KEY': self.config.serper_api_key,
            'Content-Type': 'application/json'
        }
        payload = {
            'q': query,
            'num': min(max_results, 100),
            'gl': self.config.region.lower(),
            'hl': self.config.language
        }
        
        response = self.session.post(url, headers=headers, json=payload, timeout=self.config.timeout)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for i, item in enumerate(data.get('organic', [])):
            result = SearchResult(
                title=item.get('title', ''),
                url=item.get('link', ''),
                snippet=item.get('snippet', ''),
                provider=SearchProvider.SERPER,
                rank=i + 1,
                metadata={
                    'position': item.get('position'),
                    'date': item.get('date')
                }
            )
            results.append(result)
            
        return results
    
    def _search_serpapi(self, query: str, search_type: SearchType, max_results: int) -> List[SearchResult]:
        """Search using SerpAPI"""
        if not self.config.serpapi_key:
            raise ValueError("SerpAPI key required")
            
        url = "https://serpapi.com/search"
        params = {
            'api_key': self.config.serpapi_key,
            'engine': 'google',
            'q': query,
            'num': min(max_results, 100),
            'gl': self.config.region.lower(),
            'hl': self.config.language
        }
        
        response = self.session.get(url, params=params, timeout=self.config.timeout)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for i, item in enumerate(data.get('organic_results', [])):
            result = SearchResult(
                title=item.get('title', ''),
                url=item.get('link', ''),
                snippet=item.get('snippet', ''),
                provider=SearchProvider.SERPAPI,
                rank=i + 1,
                metadata={
                    'position': item.get('position'),
                    'displayed_link': item.get('displayed_link')
                }
            )
            results.append(result)
            
        return results
    
    def get_search_suggestions(self, query: str, provider: Optional[SearchProvider] = None) -> List[str]:
        """Get search suggestions for autocomplete"""
        provider = provider or SearchProvider.GOOGLE
        
        try:
            if provider == SearchProvider.GOOGLE:
                url = "http://suggestqueries.google.com/complete/search"
                params = {
                    'client': 'firefox',
                    'q': query,
                    'hl': self.config.language
                }
                response = self.session.get(url, params=params, timeout=10)
                data = response.json()
                return data[1] if len(data) > 1 else []
                
        except Exception as e:
            logger.error(f"Failed to get suggestions: {e}")
            return []
    
    def close(self):
        """Close the session"""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()