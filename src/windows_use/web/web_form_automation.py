#!/usr/bin/env python3
"""
Web Form Automation Module for Windows Use Autonomous Agent

Integrated RPA (Robotic Process Automation) capabilities for web form automation
using Playwright with enhanced features for government forms and e-Kinerja.

Author: Jarvis AI Team
Date: 2024
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Union
from pathlib import Path

try:
    from playwright.async_api import async_playwright, Page, Browser, BrowserContext
    from playwright.async_api import TimeoutError as PlaywrightTimeoutError
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Warning: Playwright not installed. Install with: pip install playwright")

logger = logging.getLogger(__name__)

class AutomationMode(Enum):
    """Mode otomasi form"""
    ASSISTIVE = "assistive"  # Mode bantuan dengan konfirmasi user
    SEMI_AUTO = "semi_auto"  # Mode semi-otomatis dengan checkpoint
    FULL_AUTO = "full_auto"  # Mode otomatis penuh

class FormFieldType(Enum):
    """Tipe field form"""
    TEXT = "text"
    EMAIL = "email"
    PASSWORD = "password"
    NUMBER = "number"
    DATE = "date"
    SELECT = "select"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    TEXTAREA = "textarea"
    FILE = "file"
    BUTTON = "button"
    SUBMIT = "submit"

class ActionType(Enum):
    """Tipe aksi otomasi"""
    FILL = "fill"
    CLICK = "click"
    SELECT = "select"
    UPLOAD = "upload"
    WAIT = "wait"
    NAVIGATE = "navigate"
    SCREENSHOT = "screenshot"
    EXTRACT = "extract"
    VERIFY = "verify"

class AutomationStatus(Enum):
    """Status otomasi"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

@dataclass
class FormField:
    """Definisi field form"""
    name: str
    field_type: FormFieldType
    selector: str
    value: Optional[str] = None
    required: bool = False
    validation: Optional[str] = None
    description: Optional[str] = None
    wait_for: Optional[str] = None
    retry_count: int = 3
    timeout: int = 5000

@dataclass
class AutomationAction:
    """Aksi otomasi"""
    action_type: ActionType
    selector: Optional[str] = None
    value: Optional[str] = None
    description: Optional[str] = None
    wait_for: Optional[str] = None
    timeout: int = 5000
    retry_count: int = 3
    screenshot: bool = False
    verify_success: Optional[str] = None

@dataclass
class FormTemplate:
    """Template form untuk otomasi"""
    name: str
    url: str
    description: str
    fields: List[FormField] = field(default_factory=list)
    actions: List[AutomationAction] = field(default_factory=list)
    pre_actions: List[AutomationAction] = field(default_factory=list)
    post_actions: List[AutomationAction] = field(default_factory=list)
    login_required: bool = False
    login_url: Optional[str] = None
    login_fields: List[FormField] = field(default_factory=list)
    success_indicators: List[str] = field(default_factory=list)
    error_indicators: List[str] = field(default_factory=list)
    max_retry: int = 3
    timeout: int = 30000

@dataclass
class AutomationSession:
    """Sesi otomasi"""
    session_id: str
    template_name: str
    mode: AutomationMode
    status: AutomationStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    data: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    screenshots: List[str] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)
    progress: float = 0.0
    current_step: str = ""

@dataclass
class RPAConfig:
    """Konfigurasi RPA"""
    browser_type: str = "chromium"  # chromium, firefox, webkit
    headless: bool = False
    slow_mo: int = 100  # Delay antar aksi (ms)
    timeout: int = 30000
    screenshot_on_failure: bool = True
    screenshot_dir: str = "screenshots"
    data_dir: str = "automation_data"
    templates_dir: str = "templates"
    max_concurrent_sessions: int = 3
    retry_on_failure: bool = True
    auto_save_progress: bool = True
    voice_confirmation: bool = True
    safety_checks: bool = True
    # Security settings
    domain_allowlist: List[str] = field(default_factory=lambda: [
        "ekinerja.bkn.go.id",
        "simpeg.bkn.go.id",
        "localhost",
        "127.0.0.1"
    ])
    require_confirmation: bool = True
    confirmation_timeout: int = 30  # seconds

class WebFormAutomation:
    """Sistem otomasi form web dengan Playwright"""
    
    def __init__(self, config: Optional[RPAConfig] = None):
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright not available. Install with: pip install playwright")
            
        self.config = config or RPAConfig()
        self.logger = logging.getLogger(__name__)
        self.templates: Dict[str, FormTemplate] = {}
        self.active_sessions: Dict[str, AutomationSession] = {}
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None
        
        # Setup directories
        self._setup_directories()
        
        # Load templates
        self._load_templates()
        
        # Initialize built-in templates
        self._init_builtin_templates()
    
    def _is_domain_allowed(self, url: str) -> bool:
        """Check if domain is in allowlist"""
        from urllib.parse import urlparse
        
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            
            # Remove port if present
            if ':' in domain:
                domain = domain.split(':')[0]
            
            return any(allowed_domain in domain or domain == allowed_domain 
                      for allowed_domain in self.config.domain_allowlist)
        except Exception as e:
            self.logger.error(f"Error parsing URL {url}: {e}")
            return False
    
    def _get_user_confirmation(self, message: str) -> bool:
        """Get user confirmation for automation action"""
        if not self.config.require_confirmation:
            return True
        
        try:
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("Confirmation timeout")
            
            # Set timeout for confirmation
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(self.config.confirmation_timeout)
            
            try:
                response = input(f"\n{message}\nProceed? (y/N): ").strip().lower()
                signal.alarm(0)  # Cancel timeout
                return response in ['y', 'yes', 'ya']
            except TimeoutError:
                print("\nConfirmation timeout. Automation cancelled.")
                return False
            
        except Exception as e:
            self.logger.error(f"Error getting user confirmation: {e}")
            return False
    
    def _is_domain_allowed(self, url: str) -> bool:
        """Check if domain is in allowlist"""
        from urllib.parse import urlparse
        
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            
            # Remove port if present
            if ':' in domain:
                domain = domain.split(':')[0]
            
            return any(allowed_domain in domain or domain == allowed_domain 
                      for allowed_domain in self.config.domain_allowlist)
        except Exception as e:
            self.logger.error(f"Error parsing URL {url}: {e}")
            return False
    
    def _get_user_confirmation(self, message: str) -> bool:
        """Get user confirmation for automation action"""
        if not self.config.require_confirmation:
            return True
        
        try:
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("Confirmation timeout")
            
            # Set timeout for confirmation
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(self.config.confirmation_timeout)
            
            try:
                response = input(f"\n{message}\nProceed? (y/N): ").strip().lower()
                signal.alarm(0)  # Cancel timeout
                return response in ['y', 'yes', 'ya']
            except TimeoutError:
                print("\nConfirmation timeout. Automation cancelled.")
                return False
            
        except Exception as e:
            self.logger.error(f"Error getting user confirmation: {e}")
            return False
    
    def _setup_directories(self):
        """Setup direktori yang diperlukan"""
        directories = [
            self.config.screenshot_dir,
            self.config.data_dir,
            self.config.templates_dir
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def _load_templates(self):
        """Load template dari file"""
        templates_path = Path(self.config.templates_dir)
        
        for template_file in templates_path.glob("*.json"):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                    template = self._dict_to_template(template_data)
                    self.templates[template.name] = template
                    self.logger.info(f"Loaded template: {template.name}")
            except Exception as e:
                self.logger.error(f"Error loading template {template_file}: {e}")
    
    def _dict_to_template(self, data: Dict) -> FormTemplate:
        """Convert dictionary to FormTemplate"""
        fields = [FormField(**field) for field in data.get('fields', [])]
        actions = [AutomationAction(**action) for action in data.get('actions', [])]
        pre_actions = [AutomationAction(**action) for action in data.get('pre_actions', [])]
        post_actions = [AutomationAction(**action) for action in data.get('post_actions', [])]
        login_fields = [FormField(**field) for field in data.get('login_fields', [])]
        
        return FormTemplate(
            name=data['name'],
            url=data['url'],
            description=data['description'],
            fields=fields,
            actions=actions,
            pre_actions=pre_actions,
            post_actions=post_actions,
            login_required=data.get('login_required', False),
            login_url=data.get('login_url'),
            login_fields=login_fields,
            success_indicators=data.get('success_indicators', []),
            error_indicators=data.get('error_indicators', []),
            max_retry=data.get('max_retry', 3),
            timeout=data.get('timeout', 30000)
        )
    
    def _init_builtin_templates(self):
        """Initialize built-in templates"""
        # Template untuk e-Kinerja
        ekinerja_template = FormTemplate(
            name="ekinerja_login",
            url="https://ekinerja.bkn.go.id",
            description="Template login e-Kinerja BKN",
            login_required=True,
            login_fields=[
                FormField(
                    name="username",
                    field_type=FormFieldType.TEXT,
                    selector="input[name='username']",
                    required=True,
                    description="Username e-Kinerja"
                ),
                FormField(
                    name="password",
                    field_type=FormFieldType.PASSWORD,
                    selector="input[name='password']",
                    required=True,
                    description="Password e-Kinerja"
                )
            ],
            actions=[
                AutomationAction(
                    action_type=ActionType.CLICK,
                    selector="button[type='submit']",
                    description="Click login button"
                )
            ],
            success_indicators=["dashboard", "beranda"],
            error_indicators=["error", "gagal", "salah"]
        )
        
        self.templates["ekinerja_login"] = ekinerja_template
    
    async def start_browser(self) -> bool:
        """Start browser instance"""
        try:
            self.playwright = await async_playwright().start()
            
            if self.config.browser_type == "chromium":
                self.browser = await self.playwright.chromium.launch(
                    headless=self.config.headless,
                    slow_mo=self.config.slow_mo
                )
            elif self.config.browser_type == "firefox":
                self.browser = await self.playwright.firefox.launch(
                    headless=self.config.headless,
                    slow_mo=self.config.slow_mo
                )
            elif self.config.browser_type == "webkit":
                self.browser = await self.playwright.webkit.launch(
                    headless=self.config.headless,
                    slow_mo=self.config.slow_mo
                )
            
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()
            
            self.logger.info(f"Browser {self.config.browser_type} started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start browser: {e}")
            return False
    
    async def stop_browser(self):
        """Stop browser instance"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
                
            self.logger.info("Browser stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping browser: {e}")
    
    async def create_session(self, template_name: str, mode: AutomationMode, data: Dict[str, Any]) -> str:
        """Create new automation session"""
        session_id = str(uuid.uuid4())
        
        session = AutomationSession(
            session_id=session_id,
            template_name=template_name,
            mode=mode,
            status=AutomationStatus.PENDING,
            start_time=datetime.now(),
            data=data
        )
        
        self.active_sessions[session_id] = session
        self.logger.info(f"Created session {session_id} for template {template_name}")
        
        return session_id
    
    async def run_automation(self, session_id: str) -> bool:
        """Run automation for given session"""
        if session_id not in self.active_sessions:
            self.logger.error(f"Session {session_id} not found")
            return False
        
        session = self.active_sessions[session_id]
        template = self.templates.get(session.template_name)
        
        if not template:
            self.logger.error(f"Template {session.template_name} not found")
            return False
        
        # Security checks
        if not self._is_domain_allowed(template.url):
            self.logger.error(f"Domain not allowed: {template.url}")
            session.status = AutomationStatus.FAILED
            session.errors.append(f"Domain not in allowlist: {template.url}")
            return False
        
        # Get user confirmation
        confirmation_msg = f"About to run automation '{template.name}' on {template.url}"
        if not self._get_user_confirmation(confirmation_msg):
            self.logger.info(f"User cancelled automation for session {session_id}")
            session.status = AutomationStatus.CANCELLED
            return False
        
        try:
            session.status = AutomationStatus.RUNNING
            session.current_step = "Starting automation"
            
            # Start browser if not already started
            if not self.browser:
                await self.start_browser()
            
            # Navigate to URL
            await self.page.goto(template.url)
            session.current_step = f"Navigated to {template.url}"
            
            # Execute pre-actions
            for action in template.pre_actions:
                await self._execute_action(action, session)
            
            # Handle login if required
            if template.login_required:
                await self._handle_login(template, session)
            
            # Fill form fields
            for field in template.fields:
                await self._fill_field(field, session)
            
            # Execute actions
            for action in template.actions:
                await self._execute_action(action, session)
            
            # Execute post-actions
            for action in template.post_actions:
                await self._execute_action(action, session)
            
            # Verify success
            success = await self._verify_success(template, session)
            
            if success:
                session.status = AutomationStatus.COMPLETED
                session.progress = 100.0
            else:
                session.status = AutomationStatus.FAILED
            
            session.end_time = datetime.now()
            
            return success
            
        except Exception as e:
            self.logger.error(f"Automation failed for session {session_id}: {e}")
            session.status = AutomationStatus.FAILED
            session.errors.append(str(e))
            session.end_time = datetime.now()
            
            if self.config.screenshot_on_failure:
                await self._take_screenshot(session, "failure")
            
            return False
    
    async def _execute_action(self, action: AutomationAction, session: AutomationSession):
        """Execute automation action"""
        try:
            session.current_step = f"Executing {action.action_type.value}: {action.description}"
            
            if action.action_type == ActionType.CLICK:
                await self.page.click(action.selector, timeout=action.timeout)
            elif action.action_type == ActionType.FILL:
                await self.page.fill(action.selector, action.value, timeout=action.timeout)
            elif action.action_type == ActionType.SELECT:
                await self.page.select_option(action.selector, action.value, timeout=action.timeout)
            elif action.action_type == ActionType.WAIT:
                await asyncio.sleep(int(action.value) / 1000)
            elif action.action_type == ActionType.SCREENSHOT:
                await self._take_screenshot(session, action.description or "action")
            
            if action.screenshot:
                await self._take_screenshot(session, f"after_{action.action_type.value}")
                
        except Exception as e:
            self.logger.error(f"Action failed: {e}")
            session.errors.append(f"Action {action.action_type.value} failed: {e}")
            raise
    
    async def _fill_field(self, field: FormField, session: AutomationSession):
        """Fill form field"""
        try:
            value = session.data.get(field.name, field.value)
            if not value and field.required:
                raise ValueError(f"Required field {field.name} has no value")
            
            if value:
                session.current_step = f"Filling field: {field.name}"
                
                if field.field_type == FormFieldType.TEXT:
                    await self.page.fill(field.selector, str(value), timeout=field.timeout)
                elif field.field_type == FormFieldType.SELECT:
                    await self.page.select_option(field.selector, str(value), timeout=field.timeout)
                elif field.field_type == FormFieldType.CHECKBOX:
                    if value:
                        await self.page.check(field.selector, timeout=field.timeout)
                    else:
                        await self.page.uncheck(field.selector, timeout=field.timeout)
                
        except Exception as e:
            self.logger.error(f"Failed to fill field {field.name}: {e}")
            session.errors.append(f"Field {field.name} failed: {e}")
            raise
    
    async def _handle_login(self, template: FormTemplate, session: AutomationSession):
        """Handle login process"""
        if template.login_url:
            await self.page.goto(template.login_url)
        
        for field in template.login_fields:
            await self._fill_field(field, session)
    
    async def _verify_success(self, template: FormTemplate, session: AutomationSession) -> bool:
        """Verify automation success"""
        try:
            # Check for success indicators
            for indicator in template.success_indicators:
                try:
                    await self.page.wait_for_selector(f"text={indicator}", timeout=5000)
                    return True
                except (PlaywrightTimeoutError, Exception) as e:
                    self.logger.debug(f"Success indicator '{indicator}' not found: {e}")
                    continue
            
            # Check for error indicators
            for indicator in template.error_indicators:
                try:
                    await self.page.wait_for_selector(f"text={indicator}", timeout=1000)
                    return False
                except (PlaywrightTimeoutError, Exception) as e:
                    self.logger.debug(f"Error indicator '{indicator}' not found: {e}")
                    continue
            
            return True
            
        except Exception as e:
            self.logger.error(f"Verification failed: {e}")
            return False
    
    async def _take_screenshot(self, session: AutomationSession, name: str):
        """Take screenshot"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{session.session_id}_{name}_{timestamp}.png"
            filepath = Path(self.config.screenshot_dir) / filename
            
            await self.page.screenshot(path=str(filepath))
            session.screenshots.append(str(filepath))
            
        except Exception as e:
            self.logger.error(f"Screenshot failed: {e}")
    
    def get_session_status(self, session_id: str) -> Optional[AutomationSession]:
        """Get session status"""
        return self.active_sessions.get(session_id)
    
    def list_templates(self) -> List[str]:
        """List available templates"""
        return list(self.templates.keys())
    
    def get_template(self, name: str) -> Optional[FormTemplate]:
        """Get template by name"""
        return self.templates.get(name)
    
    def add_allowed_domain(self, domain: str) -> bool:
        """Add domain to allowlist"""
        try:
            if domain not in self.config.domain_allowlist:
                self.config.domain_allowlist.append(domain)
                self.logger.info(f"Added domain to allowlist: {domain}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error adding domain to allowlist: {e}")
            return False
    
    def remove_allowed_domain(self, domain: str) -> bool:
        """Remove domain from allowlist"""
        try:
            if domain in self.config.domain_allowlist:
                self.config.domain_allowlist.remove(domain)
                self.logger.info(f"Removed domain from allowlist: {domain}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error removing domain from allowlist: {e}")
            return False
    
    def get_allowed_domains(self) -> List[str]:
        """Get list of allowed domains"""
        return self.config.domain_allowlist.copy()
    
    async def cancel_session(self, session_id: str) -> bool:
        """Cancel running session"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.status = AutomationStatus.CANCELLED
            session.end_time = datetime.now()
            return True
        return False

# Export main classes
__all__ = [
    'WebFormAutomation',
    'AutomationMode',
    'FormFieldType', 
    'ActionType',
    'AutomationStatus',
    'FormField',
    'AutomationAction',
    'FormTemplate',
    'AutomationSession',
    'RPAConfig'
]