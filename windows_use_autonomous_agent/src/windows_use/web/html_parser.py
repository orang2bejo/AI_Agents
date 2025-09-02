"""HTML Parser and Content Extraction Module

Provides intelligent HTML parsing, content extraction, and text processing
for web scraping and content analysis with voice-friendly output.
"""

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple, Union, Any
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Comment
import requests
from readability import Document
import html2text
from pydantic import BaseModel

logger = logging.getLogger(__name__)

@dataclass
class ExtractedContent:
    """Extracted content from HTML"""
    title: str = ""
    text: str = ""
    summary: str = ""
    links: List[Dict[str, str]] = field(default_factory=list)
    images: List[Dict[str, str]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    headings: List[Dict[str, str]] = field(default_factory=list)
    tables: List[List[List[str]]] = field(default_factory=list)
    lists: List[List[str]] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_voice_summary(self, max_length: int = 500) -> str:
        """Generate voice-friendly summary"""
        voice_text = f"Judul: {self.title}. "
        
        if self.summary:
            voice_text += f"Ringkasan: {self.summary[:max_length]}. "
        elif self.text:
            # Extract first paragraph or first few sentences
            sentences = self.text.split('. ')[:3]
            voice_text += f"Konten: {'. '.join(sentences)}. "
            
        if self.headings:
            main_headings = [h['text'] for h in self.headings[:3] if h['level'] in ['h1', 'h2']]
            if main_headings:
                voice_text += f"Bagian utama: {', '.join(main_headings)}. "
                
        return voice_text

class ParsingConfig(BaseModel):
    """HTML parsing configuration"""
    remove_scripts: bool = True
    remove_styles: bool = True
    remove_comments: bool = True
    remove_ads: bool = True
    extract_links: bool = True
    extract_images: bool = True
    extract_tables: bool = True
    extract_lists: bool = True
    min_text_length: int = 50
    max_text_length: int = 10000
    language: str = "id"
    
class HTMLParser:
    """Advanced HTML parser with content extraction"""
    
    def __init__(self, config: ParsingConfig = None):
        self.config = config or ParsingConfig()
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = False
        self.h2t.ignore_images = False
        self.h2t.body_width = 0  # No line wrapping
        
        # Common ad/tracking selectors to remove
        self.ad_selectors = [
            '.ad', '.ads', '.advertisement', '.google-ad',
            '.banner', '.popup', '.modal', '.overlay',
            '.tracking', '.analytics', '.social-share',
            '[id*="ad"]', '[class*="ad"]', '[id*="banner"]',
            'script[src*="google"]', 'script[src*="facebook"]',
            'iframe[src*="doubleclick"]', 'iframe[src*="googlesyndication"]'
        ]
        
    def parse_url(self, url: str, timeout: int = 30) -> ExtractedContent:
        """Parse content from URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            
            return self.parse_html(response.text, base_url=url)
            
        except Exception as e:
            logger.error(f"Failed to parse URL {url}: {e}")
            return ExtractedContent(metadata={'error': str(e), 'url': url})
    
    def parse_html(self, html: str, base_url: str = "") -> ExtractedContent:
        """Parse HTML content and extract structured data"""
        try:
            # Use readability for main content extraction
            doc = Document(html)
            readable_html = doc.summary()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            readable_soup = BeautifulSoup(readable_html, 'html.parser')
            
            # Clean the soup
            self._clean_soup(soup)
            self._clean_soup(readable_soup)
            
            # Extract content
            content = ExtractedContent()
            
            # Title
            content.title = self._extract_title(soup)
            
            # Main text content
            content.text = self._extract_text(readable_soup)
            content.summary = self._generate_summary(content.text)
            
            # Links
            if self.config.extract_links:
                content.links = self._extract_links(soup, base_url)
            
            # Images
            if self.config.extract_images:
                content.images = self._extract_images(soup, base_url)
            
            # Headings
            content.headings = self._extract_headings(soup)
            
            # Tables
            if self.config.extract_tables:
                content.tables = self._extract_tables(soup)
            
            # Lists
            if self.config.extract_lists:
                content.lists = self._extract_lists(soup)
            
            # Metadata
            content.metadata = self._extract_metadata(soup, base_url)
            
            return content
            
        except Exception as e:
            logger.error(f"Failed to parse HTML: {e}")
            return ExtractedContent(metadata={'error': str(e)})
    
    def _clean_soup(self, soup: BeautifulSoup):
        """Clean soup by removing unwanted elements"""
        # Remove scripts
        if self.config.remove_scripts:
            for script in soup.find_all('script'):
                script.decompose()
        
        # Remove styles
        if self.config.remove_styles:
            for style in soup.find_all('style'):
                style.decompose()
        
        # Remove comments
        if self.config.remove_comments:
            for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
                comment.extract()
        
        # Remove ads and tracking
        if self.config.remove_ads:
            for selector in self.ad_selectors:
                for element in soup.select(selector):
                    element.decompose()
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        # Try different title sources
        title_sources = [
            soup.find('title'),
            soup.find('h1'),
            soup.find('meta', property='og:title'),
            soup.find('meta', name='twitter:title')
        ]
        
        for source in title_sources:
            if source:
                if source.name == 'meta':
                    title = source.get('content', '')
                else:
                    title = source.get_text(strip=True)
                
                if title:
                    return title[:200]  # Limit title length
        
        return "Untitled"
    
    def _extract_text(self, soup: BeautifulSoup) -> str:
        """Extract clean text content"""
        # Remove navigation, footer, sidebar elements
        for element in soup.find_all(['nav', 'footer', 'aside', 'header']):
            element.decompose()
        
        # Get text content
        text = soup.get_text(separator=' ', strip=True)
        
        # Clean whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Apply length limits
        if len(text) < self.config.min_text_length:
            return ""
        
        if len(text) > self.config.max_text_length:
            text = text[:self.config.max_text_length] + "..."
        
        return text
    
    def _generate_summary(self, text: str, max_sentences: int = 3) -> str:
        """Generate summary from text"""
        if not text:
            return ""
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Take first few sentences as summary
        summary_sentences = sentences[:max_sentences]
        summary = '. '.join(summary_sentences)
        
        if len(summary) > 500:
            summary = summary[:500] + "..."
        
        return summary
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract all links"""
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True)
            
            # Convert relative URLs to absolute
            if base_url:
                href = urljoin(base_url, href)
            
            if href and text:
                links.append({
                    'url': href,
                    'text': text[:100],  # Limit text length
                    'title': link.get('title', '')
                })
        
        return links[:50]  # Limit number of links
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract all images"""
        images = []
        
        for img in soup.find_all('img', src=True):
            src = img['src']
            alt = img.get('alt', '')
            title = img.get('title', '')
            
            # Convert relative URLs to absolute
            if base_url:
                src = urljoin(base_url, src)
            
            images.append({
                'url': src,
                'alt': alt,
                'title': title,
                'width': img.get('width', ''),
                'height': img.get('height', '')
            })
        
        return images[:20]  # Limit number of images
    
    def _extract_headings(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract headings hierarchy"""
        headings = []
        
        for level in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            for heading in soup.find_all(level):
                text = heading.get_text(strip=True)
                if text:
                    headings.append({
                        'level': level,
                        'text': text,
                        'id': heading.get('id', '')
                    })
        
        return headings
    
    def _extract_tables(self, soup: BeautifulSoup) -> List[List[List[str]]]:
        """Extract table data"""
        tables = []
        
        for table in soup.find_all('table'):
            table_data = []
            
            for row in table.find_all('tr'):
                row_data = []
                for cell in row.find_all(['td', 'th']):
                    cell_text = cell.get_text(strip=True)
                    row_data.append(cell_text)
                
                if row_data:
                    table_data.append(row_data)
            
            if table_data:
                tables.append(table_data)
        
        return tables[:5]  # Limit number of tables
    
    def _extract_lists(self, soup: BeautifulSoup) -> List[List[str]]:
        """Extract list items"""
        lists = []
        
        for list_elem in soup.find_all(['ul', 'ol']):
            list_items = []
            
            for item in list_elem.find_all('li'):
                item_text = item.get_text(strip=True)
                if item_text:
                    list_items.append(item_text)
            
            if list_items:
                lists.append(list_items)
        
        return lists[:10]  # Limit number of lists
    
    def _extract_metadata(self, soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
        """Extract page metadata"""
        metadata = {'url': base_url}
        
        # Meta tags
        meta_tags = {
            'description': soup.find('meta', attrs={'name': 'description'}),
            'keywords': soup.find('meta', attrs={'name': 'keywords'}),
            'author': soup.find('meta', attrs={'name': 'author'}),
            'og:description': soup.find('meta', property='og:description'),
            'og:image': soup.find('meta', property='og:image'),
            'og:type': soup.find('meta', property='og:type'),
            'twitter:description': soup.find('meta', name='twitter:description'),
            'twitter:image': soup.find('meta', name='twitter:image')
        }
        
        for key, tag in meta_tags.items():
            if tag:
                content = tag.get('content')
                if content:
                    metadata[key] = content
        
        # Language
        html_tag = soup.find('html')
        if html_tag:
            lang = html_tag.get('lang')
            if lang:
                metadata['language'] = lang
        
        # Canonical URL
        canonical = soup.find('link', rel='canonical')
        if canonical:
            metadata['canonical'] = canonical.get('href')
        
        return metadata

class ContentExtractor:
    """High-level content extraction interface"""
    
    def __init__(self, config: ParsingConfig = None):
        self.parser = HTMLParser(config)
    
    def extract_from_url(self, url: str) -> ExtractedContent:
        """Extract content from URL"""
        return self.parser.parse_url(url)
    
    def extract_from_html(self, html: str, base_url: str = "") -> ExtractedContent:
        """Extract content from HTML string"""
        return self.parser.parse_html(html, base_url)
    
    def extract_voice_summary(self, url: str, max_length: int = 500) -> str:
        """Extract voice-friendly summary from URL"""
        content = self.extract_from_url(url)
        return content.to_voice_summary(max_length)
    
    def extract_key_points(self, url: str, max_points: int = 5) -> List[str]:
        """Extract key points from content"""
        content = self.extract_from_url(url)
        
        key_points = []
        
        # Add main headings as key points
        for heading in content.headings[:max_points]:
            if heading['level'] in ['h1', 'h2', 'h3']:
                key_points.append(heading['text'])
        
        # Add list items if not enough headings
        if len(key_points) < max_points:
            for list_items in content.lists:
                for item in list_items:
                    if len(key_points) < max_points:
                        key_points.append(item)
                    else:
                        break
                if len(key_points) >= max_points:
                    break
        
        return key_points[:max_points]