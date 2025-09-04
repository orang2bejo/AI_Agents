"""Browser Automation Module

Provides browser automation capabilities using Selenium and Playwright
for complex web interactions and JavaScript-heavy sites.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Callable
from urllib.parse import urlparse

from pydantic import BaseModel

from ..utils.rate_limit import rate_limit
from ..utils.retry import retry

codex/conduct-comprehensive-audit-for-jarvis-ai-project-5clmg5
=======
try:
    from ..security import SecurityManager, SecurityLevel, ActionType
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False
    SecurityManager = None

try:
    from ..security import SecurityManager, SecurityLevel, ActionType
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False
    SecurityManager = None

main
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.edge.options import Options as EdgeOptions
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    # Create dummy classes for when Selenium is not available
    class By:
        CSS_SELECTOR = "css"
        XPATH = "xpath"
        ID = "id"
        CLASS_NAME = "class"
        TAG_NAME = "tag"

try:
    from playwright.async_api import async_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

logger = logging.getLogger(__name__)

class BrowserType(Enum):
    """Supported browser types"""
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"
    SAFARI = "safari"

class AutomationFramework(Enum):
    """Automation frameworks"""
    SELENIUM = "selenium"
    PLAYWRIGHT = "playwright"

@dataclass
class BrowserAction:
    """Browser action result"""
    action: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    duration: float = 0.0

class BrowserConfig(BaseModel):
    """Browser automation configuration"""
    # Browser settings
    browser_type: BrowserType = BrowserType.CHROME
    framework: AutomationFramework = AutomationFramework.SELENIUM
    headless: bool = False
    window_size: tuple = (1920, 1080)
    
    # Timeouts
    page_load_timeout: int = 30
    implicit_wait: int = 10
    explicit_wait: int = 20
    
    # Downloads
    download_directory: Optional[str] = None
    
    # Security
    disable_images: bool = False
    disable_javascript: bool = False
    disable_plugins: bool = True
    disable_extensions: bool = True
    
    # Performance
    disable_gpu: bool = True
    disable_dev_shm_usage: bool = True
    no_sandbox: bool = True
    
    # User agent
    user_agent: Optional[str] = None
    
    # Proxy
    proxy_server: Optional[str] = None
    
class SeleniumBrowser:
    """Selenium-based browser automation"""
    
    def __init__(self, config: BrowserConfig):
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium is not installed. Install with: pip install selenium")
        
        self.config = config
        self.driver = None
        self.wait = None
        
    @retry((Exception,), tries=3, backoff=0.2)
    def start(self):
        """Start browser session"""
        try:
            options = self._get_browser_options()
            
            if self.config.browser_type == BrowserType.CHROME:
                self.driver = webdriver.Chrome(options=options)
            elif self.config.browser_type == BrowserType.FIREFOX:
                self.driver = webdriver.Firefox(options=options)
            elif self.config.browser_type == BrowserType.EDGE:
                self.driver = webdriver.Edge(options=options)
            else:
                raise ValueError(f"Unsupported browser: {self.config.browser_type}")
            
            # Set timeouts
            self.driver.set_page_load_timeout(self.config.page_load_timeout)
            self.driver.implicitly_wait(self.config.implicit_wait)
            
            # Set window size
            self.driver.set_window_size(*self.config.window_size)
            
            # Setup explicit wait
            self.wait = WebDriverWait(self.driver, self.config.explicit_wait)
            
            logger.info(f"Started {self.config.browser_type.value} browser")
            
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            raise
    
    def _get_browser_options(self):
        """Get browser-specific options"""
        if self.config.browser_type == BrowserType.CHROME:
            options = ChromeOptions()
            
            if self.config.headless:
                options.add_argument("--headless")
            
            if self.config.disable_gpu:
                options.add_argument("--disable-gpu")
            
            if self.config.disable_dev_shm_usage:
                options.add_argument("--disable-dev-shm-usage")
            
            if self.config.no_sandbox:
                options.add_argument("--no-sandbox")
            
            if self.config.disable_images:
                prefs = {"profile.managed_default_content_settings.images": 2}
                options.add_experimental_option("prefs", prefs)
            
            if self.config.disable_javascript:
                prefs = {"profile.managed_default_content_settings.javascript": 2}
                options.add_experimental_option("prefs", prefs)
            
            if self.config.user_agent:
                options.add_argument(f"--user-agent={self.config.user_agent}")
            
            if self.config.proxy_server:
                options.add_argument(f"--proxy-server={self.config.proxy_server}")
            
            if self.config.download_directory:
                prefs = {
                    "download.default_directory": self.config.download_directory,
                    "download.prompt_for_download": False
                }
                options.add_experimental_option("prefs", prefs)
            
            return options
            
        elif self.config.browser_type == BrowserType.FIREFOX:
            options = FirefoxOptions()
            
            if self.config.headless:
                options.add_argument("--headless")
            
            if self.config.user_agent:
                options.set_preference("general.useragent.override", self.config.user_agent)
            
            if self.config.disable_images:
                options.set_preference("permissions.default.image", 2)
            
            if self.config.disable_javascript:
                options.set_preference("javascript.enabled", False)
            
            if self.config.download_directory:
                options.set_preference("browser.download.dir", self.config.download_directory)
                options.set_preference("browser.download.folderList", 2)
            
            return options
            
        elif self.config.browser_type == BrowserType.EDGE:
            options = EdgeOptions()
            
            if self.config.headless:
                options.add_argument("--headless")
            
            if self.config.user_agent:
                options.add_argument(f"--user-agent={self.config.user_agent}")
            
            return options
    
    @rate_limit(5, 1)
    def navigate_to(self, url: str) -> BrowserAction:
        """Navigate to URL"""
        start_time = time.time()
        try:
            self.driver.get(url)
            duration = time.time() - start_time
            
            return BrowserAction(
                action="navigate_to",
                success=True,
                result=self.driver.current_url,
                duration=duration
            )
        except Exception as e:
            duration = time.time() - start_time
            return BrowserAction(
                action="navigate_to",
                success=False,
                error=str(e),
                duration=duration
            )
    
    def find_element(self, selector: str, by: By = By.CSS_SELECTOR) -> BrowserAction:
        """Find element by selector"""
        start_time = time.time()
        try:
            element = self.wait.until(EC.presence_of_element_located((by, selector)))
            duration = time.time() - start_time
            
            return BrowserAction(
                action="find_element",
                success=True,
                result=element,
                duration=duration
            )
        except Exception as e:
            duration = time.time() - start_time
            return BrowserAction(
                action="find_element",
                success=False,
                error=str(e),
                duration=duration
            )
    
    def click_element(self, selector: str, by: By = By.CSS_SELECTOR) -> BrowserAction:
        """Click element"""
        start_time = time.time()
        try:
            element = self.wait.until(EC.element_to_be_clickable((by, selector)))
            element.click()
            duration = time.time() - start_time
            
            return BrowserAction(
                action="click_element",
                success=True,
                result=True,
                duration=duration
            )
        except Exception as e:
            duration = time.time() - start_time
            return BrowserAction(
                action="click_element",
                success=False,
                error=str(e),
                duration=duration
            )
    
    def type_text(self, selector: str, text: str, by: By = By.CSS_SELECTOR, clear_first: bool = True) -> BrowserAction:
        """Type text into element"""
        start_time = time.time()
        try:
            element = self.wait.until(EC.presence_of_element_located((by, selector)))
            
            if clear_first:
                element.clear()
            
            element.send_keys(text)
            duration = time.time() - start_time
            
            return BrowserAction(
                action="type_text",
                success=True,
                result=True,
                duration=duration
            )
        except Exception as e:
            duration = time.time() - start_time
            return BrowserAction(
                action="type_text",
                success=False,
                error=str(e),
                duration=duration
            )
    
    def get_text(self, selector: str, by: By = By.CSS_SELECTOR) -> BrowserAction:
        """Get text from element"""
        start_time = time.time()
        try:
            element = self.wait.until(EC.presence_of_element_located((by, selector)))
            text = element.text
            duration = time.time() - start_time
            
            return BrowserAction(
                action="get_text",
                success=True,
                result=text,
                duration=duration
            )
        except Exception as e:
            duration = time.time() - start_time
            return BrowserAction(
                action="get_text",
                success=False,
                error=str(e),
                duration=duration
            )
    
    def scroll_to_element(self, selector: str, by: By = By.CSS_SELECTOR) -> BrowserAction:
        """Scroll to element"""
        start_time = time.time()
        try:
            element = self.wait.until(EC.presence_of_element_located((by, selector)))
            self.driver.execute_script("arguments[0].scrollIntoView();", element)
            duration = time.time() - start_time
            
            return BrowserAction(
                action="scroll_to_element",
                success=True,
                result=True,
                duration=duration
            )
        except Exception as e:
            duration = time.time() - start_time
            return BrowserAction(
                action="scroll_to_element",
                success=False,
                error=str(e),
                duration=duration
            )
    
    def take_screenshot(self, filename: Optional[str] = None) -> BrowserAction:
        """Take screenshot"""
        start_time = time.time()
        try:
            if not filename:
                filename = f"screenshot_{int(time.time())}.png"
            
            self.driver.save_screenshot(filename)
            duration = time.time() - start_time
            
            return BrowserAction(
                action="take_screenshot",
                success=True,
                result=filename,
                duration=duration
            )
        except Exception as e:
            duration = time.time() - start_time
            return BrowserAction(
                action="take_screenshot",
                success=False,
                error=str(e),
                duration=duration
            )
    
    def execute_script(self, script: str, *args) -> BrowserAction:
        """Execute JavaScript"""
        start_time = time.time()
        try:
            result = self.driver.execute_script(script, *args)
            duration = time.time() - start_time
            
            return BrowserAction(
                action="execute_script",
                success=True,
                result=result,
                duration=duration
            )
        except Exception as e:
            duration = time.time() - start_time
            return BrowserAction(
                action="execute_script",
                success=False,
                error=str(e),
                duration=duration
            )
    
    def go_back(self) -> BrowserAction:
        """Go back in browser history"""
        start_time = time.time()
        try:
            self.driver.back()
            duration = time.time() - start_time
            
            return BrowserAction(
                action="go_back",
                success=True,
                result=self.driver.current_url,
                duration=duration
            )
        except Exception as e:
            duration = time.time() - start_time
            return BrowserAction(
                action="go_back",
                success=False,
                error=str(e),
                duration=duration
            )
    
    def go_forward(self) -> BrowserAction:
        """Go forward in browser history"""
        start_time = time.time()
        try:
            self.driver.forward()
            duration = time.time() - start_time
            
            return BrowserAction(
                action="go_forward",
                success=True,
                result=self.driver.current_url,
                duration=duration
            )
        except Exception as e:
            duration = time.time() - start_time
            return BrowserAction(
                action="go_forward",
                success=False,
                error=str(e),
                duration=duration
            )
    
    def refresh(self) -> BrowserAction:
        """Refresh current page"""
        start_time = time.time()
        try:
            self.driver.refresh()
            duration = time.time() - start_time
            
            return BrowserAction(
                action="refresh",
                success=True,
                result=self.driver.current_url,
                duration=duration
            )
        except Exception as e:
            duration = time.time() - start_time
            return BrowserAction(
                action="refresh",
                success=False,
                error=str(e),
                duration=duration
            )
    
    def get_page_source(self) -> BrowserAction:
        """Get page source HTML"""
        start_time = time.time()
        try:
            source = self.driver.page_source
            duration = time.time() - start_time
            
            return BrowserAction(
                action="get_page_source",
                success=True,
                result=source,
                duration=duration
            )
        except Exception as e:
            duration = time.time() - start_time
            return BrowserAction(
                action="get_page_source",
                success=False,
                error=str(e),
                duration=duration
            )
    
    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")

class PlaywrightBrowser:
    """Playwright-based browser automation (async)"""
    
    def __init__(self, config: BrowserConfig):
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright is not installed. Install with: pip install playwright")
        
        self.config = config
        self.playwright = None
        self.browser = None
        self.page = None
    
    async def start(self):
        """Start browser session"""
        try:
            self.playwright = await async_playwright().start()
            
            # Browser launch options
            launch_options = {
                'headless': self.config.headless,
                'args': []
            }
            
            if self.config.disable_gpu:
                launch_options['args'].append('--disable-gpu')
            
            if self.config.no_sandbox:
                launch_options['args'].append('--no-sandbox')
            
            if self.config.proxy_server:
                launch_options['proxy'] = {'server': self.config.proxy_server}
            
            # Launch browser
            if self.config.browser_type == BrowserType.CHROME:
                self.browser = await self.playwright.chromium.launch(**launch_options)
            elif self.config.browser_type == BrowserType.FIREFOX:
                self.browser = await self.playwright.firefox.launch(**launch_options)
            elif self.config.browser_type == BrowserType.EDGE:
                self.browser = await self.playwright.chromium.launch(channel='msedge', **launch_options)
            else:
                raise ValueError(f"Unsupported browser: {self.config.browser_type}")
            
            # Create context and page
            context_options = {
                'viewport': {'width': self.config.window_size[0], 'height': self.config.window_size[1]}
            }
            
            if self.config.user_agent:
                context_options['user_agent'] = self.config.user_agent
            
            context = await self.browser.new_context(**context_options)
            self.page = await context.new_page()
            
            # Set timeouts
            self.page.set_default_timeout(self.config.explicit_wait * 1000)
            
            logger.info(f"Started {self.config.browser_type.value} browser with Playwright")
            
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            raise
    
    async def navigate_to(self, url: str) -> BrowserAction:
        """Navigate to URL"""
        start_time = time.time()
        try:
            await self.page.goto(url, timeout=self.config.page_load_timeout * 1000)
            duration = time.time() - start_time
            
            return BrowserAction(
                action="navigate_to",
                success=True,
                result=self.page.url,
                duration=duration
            )
        except Exception as e:
            duration = time.time() - start_time
            return BrowserAction(
                action="navigate_to",
                success=False,
                error=str(e),
                duration=duration
            )
    
    async def click_element(self, selector: str) -> BrowserAction:
        """Click element"""
        start_time = time.time()
        try:
            await self.page.click(selector)
            duration = time.time() - start_time
            
            return BrowserAction(
                action="click_element",
                success=True,
                result=True,
                duration=duration
            )
        except Exception as e:
            duration = time.time() - start_time
            return BrowserAction(
                action="click_element",
                success=False,
                error=str(e),
                duration=duration
            )
    
    async def type_text(self, selector: str, text: str, clear_first: bool = True) -> BrowserAction:
        """Type text into element"""
        start_time = time.time()
        try:
            if clear_first:
                await self.page.fill(selector, text)
            else:
                await self.page.type(selector, text)
            
            duration = time.time() - start_time
            
            return BrowserAction(
                action="type_text",
                success=True,
                result=True,
                duration=duration
            )
        except Exception as e:
            duration = time.time() - start_time
            return BrowserAction(
                action="type_text",
                success=False,
                error=str(e),
                duration=duration
            )
    
    async def get_text(self, selector: str) -> BrowserAction:
        """Get text from element"""
        start_time = time.time()
        try:
            text = await self.page.text_content(selector)
            duration = time.time() - start_time
            
            return BrowserAction(
                action="get_text",
                success=True,
                result=text,
                duration=duration
            )
        except Exception as e:
            duration = time.time() - start_time
            return BrowserAction(
                action="get_text",
                success=False,
                error=str(e),
                duration=duration
            )
    
    async def take_screenshot(self, filename: Optional[str] = None) -> BrowserAction:
        """Take screenshot"""
        start_time = time.time()
        try:
            if not filename:
                filename = f"screenshot_{int(time.time())}.png"
            
            await self.page.screenshot(path=filename)
            duration = time.time() - start_time
            
            return BrowserAction(
                action="take_screenshot",
                success=True,
                result=filename,
                duration=duration
            )
        except Exception as e:
            duration = time.time() - start_time
            return BrowserAction(
                action="take_screenshot",
                success=False,
                error=str(e),
                duration=duration
            )
    
    async def go_back(self) -> BrowserAction:
        """Go back in browser history"""
        start_time = time.time()
        try:
            await self.page.go_back()
            duration = time.time() - start_time
            
            return BrowserAction(
                action="go_back",
                success=True,
                result=self.page.url,
                duration=duration
            )
        except Exception as e:
            duration = time.time() - start_time
            return BrowserAction(
                action="go_back",
                success=False,
                error=str(e),
                duration=duration
            )
    
    async def go_forward(self) -> BrowserAction:
        """Go forward in browser history"""
        start_time = time.time()
        try:
            await self.page.go_forward()
            duration = time.time() - start_time
            
            return BrowserAction(
                action="go_forward",
                success=True,
                result=self.page.url,
                duration=duration
            )
        except Exception as e:
            duration = time.time() - start_time
            return BrowserAction(
                action="go_forward",
                success=False,
                error=str(e),
                duration=duration
            )
    
    async def refresh(self) -> BrowserAction:
        """Refresh current page"""
        start_time = time.time()
        try:
            await self.page.reload()
            duration = time.time() - start_time
            
            return BrowserAction(
                action="refresh",
                success=True,
                result=self.page.url,
                duration=duration
            )
        except Exception as e:
            duration = time.time() - start_time
            return BrowserAction(
                action="refresh",
                success=False,
                error=str(e),
                duration=duration
            )
    
    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Browser closed")

class BrowserAutomation:
    """High-level browser automation interface"""
    
    def __init__(self, config: BrowserConfig = None):
        self.config = config or BrowserConfig()
        self.browser = None
        
    def start(self):
        """Start browser automation"""
        if self.config.framework == AutomationFramework.SELENIUM:
            self.browser = SeleniumBrowser(self.config)
            self.browser.start()
        elif self.config.framework == AutomationFramework.PLAYWRIGHT:
            self.browser = PlaywrightBrowser(self.config)
            # Note: Playwright requires async context
            raise ValueError("Playwright requires async usage. Use start_async() instead.")
        else:
            raise ValueError(f"Unsupported framework: {self.config.framework}")
    
    async def start_async(self):
        """Start browser automation (async)"""
        if self.config.framework == AutomationFramework.PLAYWRIGHT:
            self.browser = PlaywrightBrowser(self.config)
            await self.browser.start()
        else:
            raise ValueError(f"Async mode only supported for Playwright")
    
    def navigate_to(self, url: str) -> BrowserAction:
        """Navigate to URL"""
        if not self.browser:
            raise RuntimeError("Browser not started")
        return self.browser.navigate_to(url)
    
    async def navigate_to_async(self, url: str) -> BrowserAction:
        """Navigate to URL (async)"""
        if not self.browser:
            raise RuntimeError("Browser not started")
        return await self.browser.navigate_to(url)
    
    def search_google(self, query: str) -> BrowserAction:
        """Search on Google"""
        try:
            # Navigate to Google
            nav_result = self.navigate_to("https://www.google.com")
            if not nav_result.success:
                return nav_result
            
            # Find search box and type query
            type_result = self.browser.type_text("input[name='q']", query)
            if not type_result.success:
                return type_result
            
            # Submit search
            click_result = self.browser.click_element("input[name='btnK']")
            return click_result
            
        except Exception as e:
            return BrowserAction(
                action="search_google",
                success=False,
                error=str(e)
            )
    
    def close(self):
        """Close browser"""
        if self.browser:
            if hasattr(self.browser, 'close'):
                if asyncio.iscoroutinefunction(self.browser.close):
                    # Handle async close
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.create_task(self.browser.close())
                    else:
                        loop.run_until_complete(self.browser.close())
                else:
                    self.browser.close()
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()