"""Web Scraper Module

Provides intelligent web scraping capabilities with rate limiting,
robot.txt compliance, and content extraction for the Jarvis AI system.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Union, Any, Callable
from urllib.parse import urljoin, urlparse, robots
from urllib.robotparser import RobotFileParser

import aiohttp
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel

logger = logging.getLogger(__name__)

@dataclass
class ScrapingResult:
    """Result of web scraping operation"""
    url: str
    status_code: int
    content: str = ""
    headers: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = True
    error: Optional[str] = None
    
class ScrapingConfig(BaseModel):
    """Web scraping configuration"""
    # Rate limiting
    requests_per_second: float = 1.0
    requests_per_minute: int = 30
    requests_per_hour: int = 1000
    
    # Timeouts
    connect_timeout: int = 10
    read_timeout: int = 30
    total_timeout: int = 60
    
    # Retry settings
    max_retries: int = 3
    retry_delay: float = 1.0
    backoff_factor: float = 2.0
    
    # Headers
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    custom_headers: Dict[str, str] = {}
    
    # Compliance
    respect_robots_txt: bool = True
    check_robots_cache_hours: int = 24
    
    # Content filtering
    max_content_size: int = 10 * 1024 * 1024  # 10MB
    allowed_content_types: List[str] = ["text/html", "text/plain", "application/json", "application/xml"]
    
    # Security
    follow_redirects: bool = True
    max_redirects: int = 5
    verify_ssl: bool = True
    
class RateLimiter:
    """Rate limiter for web requests"""
    
    def __init__(self, config: ScrapingConfig):
        self.config = config
        self.request_times = []
        self.domain_last_request = {}
        
    def can_make_request(self, domain: str) -> bool:
        """Check if request can be made based on rate limits"""
        now = time.time()
        
        # Clean old request times
        self.request_times = [t for t in self.request_times if now - t < 3600]  # Keep last hour
        
        # Check per-second limit
        recent_requests = [t for t in self.request_times if now - t < 1.0]
        if len(recent_requests) >= self.config.requests_per_second:
            return False
        
        # Check per-minute limit
        minute_requests = [t for t in self.request_times if now - t < 60]
        if len(minute_requests) >= self.config.requests_per_minute:
            return False
        
        # Check per-hour limit
        if len(self.request_times) >= self.config.requests_per_hour:
            return False
        
        # Check domain-specific delay
        last_request = self.domain_last_request.get(domain, 0)
        min_delay = 1.0 / self.config.requests_per_second
        if now - last_request < min_delay:
            return False
        
        return True
    
    def wait_time(self, domain: str) -> float:
        """Calculate wait time before next request"""
        now = time.time()
        
        # Domain-specific wait time
        last_request = self.domain_last_request.get(domain, 0)
        min_delay = 1.0 / self.config.requests_per_second
        domain_wait = max(0, min_delay - (now - last_request))
        
        # Global rate limit wait time
        recent_requests = [t for t in self.request_times if now - t < 1.0]
        if len(recent_requests) >= self.config.requests_per_second:
            global_wait = 1.0 - (now - min(recent_requests))
        else:
            global_wait = 0
        
        return max(domain_wait, global_wait)
    
    def record_request(self, domain: str):
        """Record a request for rate limiting"""
        now = time.time()
        self.request_times.append(now)
        self.domain_last_request[domain] = now

class RobotsChecker:
    """Robots.txt compliance checker"""
    
    def __init__(self, config: ScrapingConfig):
        self.config = config
        self.robots_cache = {}
        self.cache_timestamps = {}
        
    def can_fetch(self, url: str, user_agent: str = "*") -> bool:
        """Check if URL can be fetched according to robots.txt"""
        if not self.config.respect_robots_txt:
            return True
        
        try:
            parsed_url = urlparse(url)
            domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
            robots_url = urljoin(domain, "/robots.txt")
            
            # Check cache
            now = datetime.now()
            if (robots_url in self.robots_cache and 
                robots_url in self.cache_timestamps and
                now - self.cache_timestamps[robots_url] < timedelta(hours=self.config.check_robots_cache_hours)):
                
                rp = self.robots_cache[robots_url]
            else:
                # Fetch and parse robots.txt
                rp = RobotFileParser()
                rp.set_url(robots_url)
                try:
                    rp.read()
                    self.robots_cache[robots_url] = rp
                    self.cache_timestamps[robots_url] = now
                except Exception as e:
                    logger.warning(f"Failed to fetch robots.txt from {robots_url}: {e}")
                    return True  # Allow if robots.txt is not accessible
            
            return rp.can_fetch(user_agent, url)
            
        except Exception as e:
            logger.warning(f"Error checking robots.txt for {url}: {e}")
            return True  # Allow if check fails

class WebScraper:
    """Intelligent web scraper with rate limiting and compliance"""
    
    def __init__(self, config: ScrapingConfig = None):
        self.config = config or ScrapingConfig()
        self.rate_limiter = RateLimiter(self.config)
        self.robots_checker = RobotsChecker(self.config)
        self.session = None
        self._setup_session()
        
    def _setup_session(self):
        """Setup requests session with configuration"""
        self.session = requests.Session()
        
        # Set headers
        headers = {
            'User-Agent': self.config.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        headers.update(self.config.custom_headers)
        self.session.headers.update(headers)
        
        # Set timeouts and retries
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def scrape_url(self, url: str, **kwargs) -> ScrapingResult:
        """Scrape single URL"""
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            
            # Check robots.txt
            if not self.robots_checker.can_fetch(url, self.config.user_agent):
                return ScrapingResult(
                    url=url,
                    status_code=403,
                    success=False,
                    error="Blocked by robots.txt"
                )
            
            # Rate limiting
            wait_time = self.rate_limiter.wait_time(domain)
            if wait_time > 0:
                logger.info(f"Rate limiting: waiting {wait_time:.2f}s for {domain}")
                time.sleep(wait_time)
            
            # Make request
            response = self.session.get(
                url,
                timeout=(self.config.connect_timeout, self.config.read_timeout),
                allow_redirects=self.config.follow_redirects,
                verify=self.config.verify_ssl,
                **kwargs
            )
            
            # Record request for rate limiting
            self.rate_limiter.record_request(domain)
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if not any(allowed in content_type for allowed in self.config.allowed_content_types):
                return ScrapingResult(
                    url=url,
                    status_code=response.status_code,
                    success=False,
                    error=f"Unsupported content type: {content_type}"
                )
            
            # Check content size
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > self.config.max_content_size:
                return ScrapingResult(
                    url=url,
                    status_code=response.status_code,
                    success=False,
                    error=f"Content too large: {content_length} bytes"
                )
            
            response.raise_for_status()
            
            # Get content with size check
            content = ""
            total_size = 0
            for chunk in response.iter_content(chunk_size=8192, decode_unicode=True):
                total_size += len(chunk.encode('utf-8'))
                if total_size > self.config.max_content_size:
                    return ScrapingResult(
                        url=url,
                        status_code=response.status_code,
                        success=False,
                        error=f"Content too large: {total_size} bytes"
                    )
                content += chunk
            
            return ScrapingResult(
                url=url,
                status_code=response.status_code,
                content=content,
                headers=dict(response.headers),
                metadata={
                    'final_url': response.url,
                    'encoding': response.encoding,
                    'content_type': content_type,
                    'content_length': len(content)
                }
            )
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {url}: {e}")
            return ScrapingResult(
                url=url,
                status_code=0,
                success=False,
                error=str(e)
            )
        except Exception as e:
            logger.error(f"Unexpected error scraping {url}: {e}")
            return ScrapingResult(
                url=url,
                status_code=0,
                success=False,
                error=str(e)
            )
    
    def scrape_urls(self, urls: List[str], **kwargs) -> List[ScrapingResult]:
        """Scrape multiple URLs with rate limiting"""
        results = []
        
        for url in urls:
            result = self.scrape_url(url, **kwargs)
            results.append(result)
            
            # Log progress
            if result.success:
                logger.info(f"Successfully scraped {url} ({result.status_code})")
            else:
                logger.warning(f"Failed to scrape {url}: {result.error}")
        
        return results
    
    async def scrape_url_async(self, url: str, session: aiohttp.ClientSession, **kwargs) -> ScrapingResult:
        """Async version of scrape_url"""
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            
            # Check robots.txt
            if not self.robots_checker.can_fetch(url, self.config.user_agent):
                return ScrapingResult(
                    url=url,
                    status_code=403,
                    success=False,
                    error="Blocked by robots.txt"
                )
            
            # Rate limiting
            wait_time = self.rate_limiter.wait_time(domain)
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            
            # Make request
            timeout = aiohttp.ClientTimeout(
                connect=self.config.connect_timeout,
                total=self.config.total_timeout
            )
            
            async with session.get(url, timeout=timeout, **kwargs) as response:
                # Record request for rate limiting
                self.rate_limiter.record_request(domain)
                
                # Check content type
                content_type = response.headers.get('content-type', '').lower()
                if not any(allowed in content_type for allowed in self.config.allowed_content_types):
                    return ScrapingResult(
                        url=url,
                        status_code=response.status,
                        success=False,
                        error=f"Unsupported content type: {content_type}"
                    )
                
                # Check content size
                content_length = response.headers.get('content-length')
                if content_length and int(content_length) > self.config.max_content_size:
                    return ScrapingResult(
                        url=url,
                        status_code=response.status,
                        success=False,
                        error=f"Content too large: {content_length} bytes"
                    )
                
                # Read content with size check
                content = ""
                total_size = 0
                async for chunk in response.content.iter_chunked(8192):
                    chunk_text = chunk.decode('utf-8', errors='ignore')
                    total_size += len(chunk)
                    if total_size > self.config.max_content_size:
                        return ScrapingResult(
                            url=url,
                            status_code=response.status,
                            success=False,
                            error=f"Content too large: {total_size} bytes"
                        )
                    content += chunk_text
                
                return ScrapingResult(
                    url=url,
                    status_code=response.status,
                    content=content,
                    headers=dict(response.headers),
                    metadata={
                        'final_url': str(response.url),
                        'content_type': content_type,
                        'content_length': len(content)
                    }
                )
                
        except asyncio.TimeoutError:
            return ScrapingResult(
                url=url,
                status_code=0,
                success=False,
                error="Request timeout"
            )
        except aiohttp.ClientError as e:
            return ScrapingResult(
                url=url,
                status_code=0,
                success=False,
                error=str(e)
            )
        except Exception as e:
            logger.error(f"Unexpected error scraping {url}: {e}")
            return ScrapingResult(
                url=url,
                status_code=0,
                success=False,
                error=str(e)
            )
    
    async def scrape_urls_async(self, urls: List[str], max_concurrent: int = 5, **kwargs) -> List[ScrapingResult]:
        """Async version of scrape_urls with concurrency control"""
        connector = aiohttp.TCPConnector(
            limit=max_concurrent,
            verify_ssl=self.config.verify_ssl
        )
        
        timeout = aiohttp.ClientTimeout(
            connect=self.config.connect_timeout,
            total=self.config.total_timeout
        )
        
        headers = {
            'User-Agent': self.config.user_agent
        }
        headers.update(self.config.custom_headers)
        
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=headers
        ) as session:
            
            # Create semaphore for concurrency control
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def scrape_with_semaphore(url):
                async with semaphore:
                    return await self.scrape_url_async(url, session, **kwargs)
            
            # Execute all requests
            tasks = [scrape_with_semaphore(url) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            final_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    final_results.append(ScrapingResult(
                        url=urls[i],
                        status_code=0,
                        success=False,
                        error=str(result)
                    ))
                else:
                    final_results.append(result)
            
            return final_results
    
    def extract_links(self, html_content: str, base_url: str = "") -> List[str]:
        """Extract all links from HTML content"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            links = []
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                if base_url:
                    href = urljoin(base_url, href)
                links.append(href)
            
            return list(set(links))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error extracting links: {e}")
            return []
    
    def extract_images(self, html_content: str, base_url: str = "") -> List[str]:
        """Extract all image URLs from HTML content"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            images = []
            
            for img in soup.find_all('img', src=True):
                src = img['src']
                if base_url:
                    src = urljoin(base_url, src)
                images.append(src)
            
            return list(set(images))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error extracting images: {e}")
            return []
    
    def get_domain_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get scraping statistics by domain"""
        stats = {}
        
        for domain, last_request in self.rate_limiter.domain_last_request.items():
            stats[domain] = {
                'last_request': datetime.fromtimestamp(last_request),
                'can_request': self.rate_limiter.can_make_request(domain),
                'wait_time': self.rate_limiter.wait_time(domain)
            }
        
        return stats
    
    def close(self):
        """Close the session"""
        if self.session:
            self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()