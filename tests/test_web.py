#!/usr/bin/env python3
"""
Unit Tests for Web Module

Tests for web automation, browser control, and RPA functionality.

Author: Jarvis AI Team
Date: 2024
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from windows_use.web.browser_automation import BrowserAutomation
    from windows_use.web.web_form_automation import WebFormAutomation
    from windows_use.web.search_engine import SearchEngine
    from windows_use.web.web_scraper import WebScraper
except ImportError as e:
    pytest.skip(f"Web modules not available: {e}", allow_module_level=True)


class TestBrowserAutomation:
    """Test cases for BrowserAutomation"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.browser = BrowserAutomation()
    
    @pytest.mark.unit
    @pytest.mark.web
    def test_initialization(self):
        """Test BrowserAutomation initialization"""
        assert self.browser is not None
        assert hasattr(self.browser, 'driver')
        assert hasattr(self.browser, 'browser_type')
    
    @pytest.mark.unit
    @pytest.mark.web
    @patch('selenium.webdriver.Chrome')
    def test_chrome_driver_initialization(self, mock_chrome):
        """Test Chrome driver initialization"""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        
        browser = BrowserAutomation(browser_type='chrome')
        browser.start_browser()
        
        mock_chrome.assert_called_once()
        assert browser.driver == mock_driver
    
    @pytest.mark.unit
    @pytest.mark.web
    @patch('selenium.webdriver.Firefox')
    def test_firefox_driver_initialization(self, mock_firefox):
        """Test Firefox driver initialization"""
        mock_driver = Mock()
        mock_firefox.return_value = mock_driver
        
        browser = BrowserAutomation(browser_type='firefox')
        browser.start_browser()
        
        mock_firefox.assert_called_once()
        assert browser.driver == mock_driver
    
    @pytest.mark.unit
    @pytest.mark.web
    def test_navigate_to_url(self):
        """Test URL navigation"""
        mock_driver = Mock()
        self.browser.driver = mock_driver
        
        test_url = "https://www.example.com"
        self.browser.navigate_to(test_url)
        
        mock_driver.get.assert_called_once_with(test_url)
    
    @pytest.mark.unit
    @pytest.mark.web
    def test_find_element(self):
        """Test element finding functionality"""
        mock_driver = Mock()
        mock_element = Mock()
        mock_driver.find_element.return_value = mock_element
        self.browser.driver = mock_driver
        
        element = self.browser.find_element('id', 'test-id')
        
        assert element == mock_element
        mock_driver.find_element.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.web
    def test_click_element(self):
        """Test element clicking"""
        mock_driver = Mock()
        mock_element = Mock()
        mock_driver.find_element.return_value = mock_element
        self.browser.driver = mock_driver
        
        self.browser.click_element('id', 'test-button')
        
        mock_element.click.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.web
    def test_input_text(self):
        """Test text input functionality"""
        mock_driver = Mock()
        mock_element = Mock()
        mock_driver.find_element.return_value = mock_element
        self.browser.driver = mock_driver
        
        test_text = "Hello, World!"
        self.browser.input_text('name', 'username', test_text)
        
        mock_element.clear.assert_called_once()
        mock_element.send_keys.assert_called_once_with(test_text)
    
    @pytest.mark.unit
    @pytest.mark.web
    def test_screenshot(self):
        """Test screenshot functionality"""
        mock_driver = Mock()
        mock_driver.save_screenshot.return_value = True
        self.browser.driver = mock_driver
        
        result = self.browser.take_screenshot('test_screenshot.png')
        
        assert result is True
        mock_driver.save_screenshot.assert_called_once_with('test_screenshot.png')
    
    @pytest.mark.unit
    @pytest.mark.web
    def test_browser_cleanup(self):
        """Test browser cleanup"""
        mock_driver = Mock()
        self.browser.driver = mock_driver
        
        self.browser.close_browser()
        
        mock_driver.quit.assert_called_once()
        assert self.browser.driver is None


class TestWebFormAutomation:
    """Test cases for WebFormAutomation"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.form_automation = WebFormAutomation()
    
    @pytest.mark.unit
    @pytest.mark.web
    def test_initialization(self):
        """Test WebFormAutomation initialization"""
        assert self.form_automation is not None
        assert hasattr(self.form_automation, 'browser')
    
    @pytest.mark.unit
    @pytest.mark.web
    def test_fill_form_field(self):
        """Test form field filling"""
        mock_browser = Mock()
        self.form_automation.browser = mock_browser
        
        field_data = {
            'selector': 'input[name="email"]',
            'value': 'test@example.com',
            'type': 'email'
        }
        
        self.form_automation.fill_form_field(field_data)
        
        mock_browser.input_text.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.web
    def test_select_dropdown_option(self):
        """Test dropdown selection"""
        mock_browser = Mock()
        mock_select_element = Mock()
        mock_browser.find_element.return_value = mock_select_element
        self.form_automation.browser = mock_browser
        
        with patch('selenium.webdriver.support.ui.Select') as mock_select:
            mock_select_instance = Mock()
            mock_select.return_value = mock_select_instance
            
            self.form_automation.select_dropdown_option('id', 'country', 'USA')
            
            mock_select_instance.select_by_visible_text.assert_called_once_with('USA')
    
    @pytest.mark.unit
    @pytest.mark.web
    def test_submit_form(self):
        """Test form submission"""
        mock_browser = Mock()
        self.form_automation.browser = mock_browser
        
        self.form_automation.submit_form('id', 'contact-form')
        
        mock_browser.click_element.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.web
    def test_validate_form_submission(self):
        """Test form submission validation"""
        mock_browser = Mock()
        mock_element = Mock()
        mock_element.text = "Form submitted successfully"
        mock_browser.find_element.return_value = mock_element
        self.form_automation.browser = mock_browser
        
        result = self.form_automation.validate_submission('class', 'success-message')
        
        assert "success" in result.lower()


class TestSearchEngine:
    """Test cases for SearchEngine"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.search_engine = SearchEngine()
    
    @pytest.mark.unit
    @pytest.mark.web
    def test_initialization(self):
        """Test SearchEngine initialization"""
        assert self.search_engine is not None
        assert hasattr(self.search_engine, 'search_providers')
    
    @pytest.mark.unit
    @pytest.mark.web
    @patch('requests.get')
    def test_google_search(self, mock_get):
        """Test Google search functionality"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<div class="g"><h3>Test Result</h3><span>Test description</span></div>'
        mock_get.return_value = mock_response
        
        results = self.search_engine.search_google("test query")
        
        assert isinstance(results, list)
        mock_get.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.web
    @patch('requests.get')
    def test_bing_search(self, mock_get):
        """Test Bing search functionality"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<li class="b_algo"><h2>Test Result</h2><p>Test description</p></li>'
        mock_get.return_value = mock_response
        
        results = self.search_engine.search_bing("test query")
        
        assert isinstance(results, list)
        mock_get.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.web
    def test_search_result_parsing(self):
        """Test search result parsing"""
        html_content = '''
        <div class="g">
            <h3>Test Title</h3>
            <span>Test description with keywords</span>
            <a href="https://example.com">Link</a>
        </div>
        '''
        
        results = self.search_engine.parse_search_results(html_content, 'google')
        
        assert len(results) > 0
        assert 'title' in results[0]
        assert 'description' in results[0]
    
    @pytest.mark.unit
    @pytest.mark.web
    def test_search_with_filters(self):
        """Test search with filters"""
        filters = {
            'site': 'github.com',
            'filetype': 'pdf',
            'date_range': 'past_year'
        }
        
        query = self.search_engine.build_filtered_query("machine learning", filters)
        
        assert 'site:github.com' in query
        assert 'filetype:pdf' in query


class TestWebScraper:
    """Test cases for WebScraper"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.scraper = WebScraper()
    
    @pytest.mark.unit
    @pytest.mark.web
    def test_initialization(self):
        """Test WebScraper initialization"""
        assert self.scraper is not None
        assert hasattr(self.scraper, 'session')
    
    @pytest.mark.unit
    @pytest.mark.web
    @patch('requests.Session.get')
    def test_fetch_page(self, mock_get):
        """Test page fetching"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><h1>Test Page</h1></body></html>'
        mock_get.return_value = mock_response
        
        content = self.scraper.fetch_page('https://example.com')
        
        assert content is not None
        assert '<h1>Test Page</h1>' in content
    
    @pytest.mark.unit
    @pytest.mark.web
    def test_parse_html(self):
        """Test HTML parsing"""
        html_content = '''
        <html>
            <body>
                <h1>Main Title</h1>
                <p class="content">Paragraph 1</p>
                <p class="content">Paragraph 2</p>
                <a href="https://example.com">Link</a>
            </body>
        </html>
        '''
        
        soup = self.scraper.parse_html(html_content)
        
        assert soup is not None
        assert soup.find('h1').text == 'Main Title'
        assert len(soup.find_all('p', class_='content')) == 2
    
    @pytest.mark.unit
    @pytest.mark.web
    def test_extract_links(self):
        """Test link extraction"""
        html_content = '''
        <html>
            <body>
                <a href="https://example.com">External Link</a>
                <a href="/internal">Internal Link</a>
                <a href="mailto:test@example.com">Email Link</a>
            </body>
        </html>
        '''
        
        links = self.scraper.extract_links(html_content, 'https://test.com')
        
        assert len(links) >= 2  # Should find at least HTTP links
        assert any('https://example.com' in link for link in links)
    
    @pytest.mark.unit
    @pytest.mark.web
    def test_extract_text(self):
        """Test text extraction"""
        html_content = '''
        <html>
            <body>
                <h1>Title</h1>
                <p>This is a paragraph with <strong>bold</strong> text.</p>
                <script>console.log('script');</script>
                <style>body { color: red; }</style>
            </body>
        </html>
        '''
        
        text = self.scraper.extract_text(html_content)
        
        assert 'Title' in text
        assert 'This is a paragraph' in text
        assert 'bold' in text
        assert 'console.log' not in text  # Scripts should be excluded
        assert 'color: red' not in text  # Styles should be excluded
    
    @pytest.mark.unit
    @pytest.mark.web
    def test_extract_metadata(self):
        """Test metadata extraction"""
        html_content = '''
        <html>
            <head>
                <title>Test Page Title</title>
                <meta name="description" content="Test page description">
                <meta name="keywords" content="test, page, metadata">
                <meta property="og:title" content="Open Graph Title">
            </head>
            <body>
                <h1>Content</h1>
            </body>
        </html>
        '''
        
        metadata = self.scraper.extract_metadata(html_content)
        
        assert metadata['title'] == 'Test Page Title'
        assert metadata['description'] == 'Test page description'
        assert 'test' in metadata['keywords']
        assert metadata['og:title'] == 'Open Graph Title'


@pytest.mark.integration
@pytest.mark.web
class TestWebIntegration:
    """Integration tests for web components"""
    
    def setup_method(self):
        """Set up integration test fixtures"""
        self.browser = BrowserAutomation()
        self.form_automation = WebFormAutomation()
        self.search_engine = SearchEngine()
        self.scraper = WebScraper()
    
    @pytest.mark.slow
    def test_end_to_end_form_automation(self):
        """Test end-to-end form automation workflow"""
        # This would be a real browser test in a full implementation
        # For now, we'll mock the components
        
        with patch.object(self.browser, 'start_browser'), \
             patch.object(self.browser, 'navigate_to'), \
             patch.object(self.form_automation, 'fill_form_field'), \
             patch.object(self.form_automation, 'submit_form'):
            
            # Simulate form automation workflow
            self.browser.start_browser()
            self.browser.navigate_to('https://example.com/contact')
            
            form_data = {
                'name': 'Test User',
                'email': 'test@example.com',
                'message': 'Test message'
            }
            
            for field, value in form_data.items():
                self.form_automation.fill_form_field({
                    'selector': f'input[name="{field}"]',
                    'value': value
                })
            
            self.form_automation.submit_form('id', 'contact-form')
    
    def test_search_and_scrape_workflow(self):
        """Test search and scrape workflow"""
        with patch.object(self.search_engine, 'search_google') as mock_search, \
             patch.object(self.scraper, 'fetch_page') as mock_fetch:
            
            # Mock search results
            mock_search.return_value = [
                {'title': 'Test Result', 'url': 'https://example.com', 'description': 'Test'}
            ]
            
            # Mock page content
            mock_fetch.return_value = '<html><body><h1>Test Content</h1></body></html>'
            
            # Execute workflow
            search_results = self.search_engine.search_google('test query')
            assert len(search_results) > 0
            
            first_result = search_results[0]
            page_content = self.scraper.fetch_page(first_result['url'])
            assert page_content is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])