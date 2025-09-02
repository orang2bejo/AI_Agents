"""Dashboard Module

Provides an intuitive graphical user interface for the Jarvis AI system,
including real-time monitoring, configuration, and interaction capabilities.
"""

import asyncio
import json
import logging
import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Tuple
from datetime import datetime, timedelta

# Setup logger
logger = logging.getLogger(__name__)

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from pydantic import BaseModel

# Import evolution module if available
try:
    from ..evolution import EvolutionEngine, EvolutionCycle
    EVOLUTION_AVAILABLE = True
except ImportError:
    EVOLUTION_AVAILABLE = False

# Import LLM module if available
try:
    from ..llm import LLMRouter, ModelRegistry, MODEL_CATALOG
    from ..llm.model_registry import ModelInfo, ModelStatus, ModelCapability
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    logger.warning("LLM module not available")

# Import Agent module if available
try:
    from ..agent import Agent
    from ..agent.views import AgentState, AgentStep, AgentResult, Action, AgentData
    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False
    logger.warning("Agent module not available")

# Import Web module if available
try:
    from ..web import (
        WebFormAutomation, AutomationMode, FormFieldType, ActionType,
        AutomationStatus, FormField, AutomationAction, FormTemplate,
        AutomationSession, RPAConfig
    )
    WEB_AVAILABLE = True
except ImportError:
    WEB_AVAILABLE = False
    logger.warning("Web module not available")

logger = logging.getLogger(__name__)

class DashboardTheme(Enum):
    """Dashboard themes"""
    DARK = "dark"
    LIGHT = "light"
    JARVIS = "jarvis"  # Blue/cyan theme like Iron Man's Jarvis

class WidgetType(Enum):
    """Dashboard widget types"""
    STATUS = "status"
    METRICS = "metrics"
    LOGS = "logs"
    VOICE_VISUALIZER = "voice_visualizer"
    TASK_MONITOR = "task_monitor"
    CONFIGURATION = "configuration"
    CHAT = "chat"

class SystemStatus(Enum):
    """System status indicators"""
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    INITIALIZING = "initializing"
    MAINTENANCE = "maintenance"

@dataclass
class DashboardMetrics:
    """Dashboard metrics data"""
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    voice_commands: int = 0
    tasks_completed: int = 0
    response_time: float = 0.0
    uptime: float = 0.0
    errors: int = 0
    timestamp: float = field(default_factory=time.time)

@dataclass
class LogEntry:
    """Log entry data"""
    timestamp: datetime
    level: str
    module: str
    message: str
    details: Optional[Dict[str, Any]] = None

class DashboardConfig(BaseModel):
    """Dashboard configuration"""
    # Appearance
    theme: DashboardTheme = DashboardTheme.JARVIS
    window_width: int = 1200
    window_height: int = 800
    always_on_top: bool = False
    
    # Layout
    show_sidebar: bool = True
    show_status_bar: bool = True
    widget_layout: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Updates
    refresh_interval: float = 1.0  # seconds
    metrics_history_size: int = 100
    log_buffer_size: int = 1000
    
    # Voice visualization
    voice_viz_enabled: bool = True
    voice_viz_sensitivity: float = 1.0
    
    # Notifications
    show_notifications: bool = True
    notification_timeout: float = 5.0

class VoiceVisualizer:
    """Real-time voice activity visualizer"""
    
    def __init__(self, parent, width=400, height=100):
        self.parent = parent
        self.width = width
        self.height = height
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(width/100, height/100), dpi=100)
        self.figure.patch.set_facecolor('#1a1a1a')
        
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#0a0a0a')
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(-1, 1)
        self.ax.axis('off')
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Audio data buffer
        self.audio_buffer = np.zeros(100)
        self.line, = self.ax.plot(self.audio_buffer, color='#00ffff', linewidth=2)
        
        # Animation
        self.is_active = False
        self.animation_thread = None
    
    def update_audio_data(self, audio_data: np.ndarray):
        """Update audio visualization with new data"""
        if len(audio_data) > 0:
            # Downsample to fit buffer
            if len(audio_data) > 100:
                step = len(audio_data) // 100
                downsampled = audio_data[::step][:100]
            else:
                downsampled = np.pad(audio_data, (0, 100 - len(audio_data)), 'constant')
            
            self.audio_buffer = downsampled
            
            # Update plot
            self.line.set_ydata(self.audio_buffer)
            
            # Add glow effect when speaking
            if np.max(np.abs(audio_data)) > 0.1:
                self.line.set_color('#00ffff')
                self.line.set_linewidth(3)
            else:
                self.line.set_color('#004444')
                self.line.set_linewidth(1)
            
            self.canvas.draw_idle()
    
    def start_animation(self):
        """Start voice visualization animation"""
        self.is_active = True
        self.animation_thread = threading.Thread(target=self._animation_loop, daemon=True)
        self.animation_thread.start()
    
    def stop_animation(self):
        """Stop voice visualization animation"""
        self.is_active = False
        if self.animation_thread:
            self.animation_thread.join(timeout=1.0)
    
    def _animation_loop(self):
        """Animation loop for idle state"""
        while self.is_active:
            if np.max(np.abs(self.audio_buffer)) < 0.01:
                # Create idle animation (subtle wave)
                t = time.time()
                idle_wave = 0.1 * np.sin(np.linspace(0, 4*np.pi, 100) + t)
                self.audio_buffer = idle_wave
                self.line.set_ydata(self.audio_buffer)
                self.line.set_color('#002222')
                self.line.set_linewidth(1)
                self.canvas.draw_idle()
            
            time.sleep(0.1)

class MetricsChart:
    """Real-time metrics chart widget"""
    
    def __init__(self, parent, width=400, height=200):
        self.parent = parent
        self.width = width
        self.height = height
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(width/100, height/100), dpi=100)
        self.figure.patch.set_facecolor('#1a1a1a')
        
        # Create subplots
        self.ax1 = self.figure.add_subplot(221)  # CPU
        self.ax2 = self.figure.add_subplot(222)  # Memory
        self.ax3 = self.figure.add_subplot(223)  # Response Time
        self.ax4 = self.figure.add_subplot(224)  # Commands
        
        # Configure axes
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            ax.set_facecolor('#0a0a0a')
            ax.tick_params(colors='white', labelsize=8)
            ax.grid(True, alpha=0.3, color='#333333')
        
        self.ax1.set_title('CPU Usage (%)', color='white', fontsize=10)
        self.ax2.set_title('Memory Usage (%)', color='white', fontsize=10)
        self.ax3.set_title('Response Time (ms)', color='white', fontsize=10)
        self.ax4.set_title('Commands/min', color='white', fontsize=10)
        
        # Data storage
        self.max_points = 50
        self.cpu_data = []
        self.memory_data = []
        self.response_data = []
        self.commands_data = []
        self.timestamps = []
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initial plot
        self._update_plots()
    
    def add_metrics(self, metrics: DashboardMetrics):
        """Add new metrics data point"""
        current_time = datetime.now()
        
        # Add data points
        self.cpu_data.append(metrics.cpu_usage)
        self.memory_data.append(metrics.memory_usage)
        self.response_data.append(metrics.response_time * 1000)  # Convert to ms
        self.commands_data.append(metrics.voice_commands)
        self.timestamps.append(current_time)
        
        # Limit data points
        if len(self.cpu_data) > self.max_points:
            self.cpu_data.pop(0)
            self.memory_data.pop(0)
            self.response_data.pop(0)
            self.commands_data.pop(0)
            self.timestamps.pop(0)
        
        self._update_plots()
    
    def _update_plots(self):
        """Update all metric plots"""
        if not self.timestamps:
            return
        
        # Clear axes
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        self.ax4.clear()
        
        # Plot data
        x_range = range(len(self.timestamps))
        
        self.ax1.plot(x_range, self.cpu_data, color='#ff6b6b', linewidth=2)
        self.ax1.fill_between(x_range, self.cpu_data, alpha=0.3, color='#ff6b6b')
        self.ax1.set_ylim(0, 100)
        
        self.ax2.plot(x_range, self.memory_data, color='#4ecdc4', linewidth=2)
        self.ax2.fill_between(x_range, self.memory_data, alpha=0.3, color='#4ecdc4')
        self.ax2.set_ylim(0, 100)
        
        self.ax3.plot(x_range, self.response_data, color='#ffe66d', linewidth=2)
        self.ax3.fill_between(x_range, self.response_data, alpha=0.3, color='#ffe66d')
        
        self.ax4.plot(x_range, self.commands_data, color='#a8e6cf', linewidth=2)
        self.ax4.fill_between(x_range, self.commands_data, alpha=0.3, color='#a8e6cf')
        
        # Configure axes
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            ax.set_facecolor('#0a0a0a')
            ax.tick_params(colors='white', labelsize=8)
            ax.grid(True, alpha=0.3, color='#333333')
            ax.set_xlim(0, max(1, len(self.timestamps) - 1))
        
        self.ax1.set_title('CPU Usage (%)', color='white', fontsize=10)
        self.ax2.set_title('Memory Usage (%)', color='white', fontsize=10)
        self.ax3.set_title('Response Time (ms)', color='white', fontsize=10)
        self.ax4.set_title('Commands/min', color='white', fontsize=10)
        
        self.figure.tight_layout()
        self.canvas.draw_idle()

class JarvisDashboard:
    """Main Jarvis AI Dashboard"""
    
    def __init__(self, config: DashboardConfig = None):
        self.config = config or DashboardConfig()
        
        # Initialize main window
        self.root = tk.Tk()
        self.root.title("Jarvis AI - Dashboard")
        self.root.geometry(f"{self.config.window_width}x{self.config.window_height}")
        
        # Apply theme
        self._apply_theme()
        
        # Data storage
        self.metrics_history: List[DashboardMetrics] = []
        self.log_entries: List[LogEntry] = []
        self.system_status = SystemStatus.OFFLINE
        
        # Evolution state
        self.evolution_running = False
        self.evolution_engine = None
        
        # LLM state
        self.llm_router = None
        self.model_registry = None
        self.current_provider = None
        self.llm_metrics = {}
        
        # Agent state
        self.agent_instance = None
        self.agent_state = None
        self.agent_tasks = []
        self.agent_metrics = {}
        self.agent_running = False
        
        # Web automation state
        self.web_automation = None
        self.automation_sessions = {}
        self.web_templates = {}
        self.web_metrics = {
            'total_sessions': 0,
            'completed_sessions': 0,
            'failed_sessions': 0,
            'success_rate': 0.0,
            'avg_session_time': 0.0,
            'last_session': None
        }
        self.web_running = False
        
        # Callbacks
        self.on_command_send: Optional[Callable[[str], None]] = None
        self.on_config_change: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_shutdown: Optional[Callable[[], None]] = None
        
        # UI Components
        self.status_indicators = {}
        self.metrics_chart = None
        self.voice_visualizer = None
        self.log_text = None
        self.chat_text = None
        self.chat_entry = None
        
        # Threading
        self.update_thread = None
        self.is_running = False
        
        # Build UI
        self._build_ui()
        
        # Start update loop
        self.start_updates()
        
        logger.info("Jarvis Dashboard initialized")
    
    def _apply_theme(self):
        """Apply dashboard theme"""
        if self.config.theme == DashboardTheme.JARVIS:
            # Jarvis theme - dark with cyan accents
            self.colors = {
                'bg': '#0a0a0a',
                'fg': '#ffffff',
                'accent': '#00ffff',
                'secondary': '#004444',
                'success': '#00ff00',
                'warning': '#ffff00',
                'error': '#ff0000',
                'panel': '#1a1a1a'
            }
        elif self.config.theme == DashboardTheme.DARK:
            # Standard dark theme
            self.colors = {
                'bg': '#2b2b2b',
                'fg': '#ffffff',
                'accent': '#0078d4',
                'secondary': '#404040',
                'success': '#107c10',
                'warning': '#ffb900',
                'error': '#d13438',
                'panel': '#3c3c3c'
            }
        else:
            # Light theme
            self.colors = {
                'bg': '#ffffff',
                'fg': '#000000',
                'accent': '#0078d4',
                'secondary': '#f3f2f1',
                'success': '#107c10',
                'warning': '#ffb900',
                'error': '#d13438',
                'panel': '#faf9f8'
            }
        
        # Configure root window
        self.root.configure(bg=self.colors['bg'])
        
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles for theme
        style.configure('Dashboard.TFrame', background=self.colors['bg'])
        style.configure('Panel.TFrame', background=self.colors['panel'])
        style.configure('Dashboard.TLabel', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('Accent.TLabel', background=self.colors['bg'], foreground=self.colors['accent'])
        style.configure('Dashboard.TButton', background=self.colors['accent'], foreground=self.colors['bg'])
    
    def _build_ui(self):
        """Build the main dashboard UI"""
        # Main container
        main_frame = ttk.Frame(self.root, style='Dashboard.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create layout
        if self.config.show_sidebar:
            self._create_sidebar_layout(main_frame)
        else:
            self._create_full_layout(main_frame)
        
        # Status bar
        if self.config.show_status_bar:
            self._create_status_bar()
        
        # Bind events
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Configure window properties
        if self.config.always_on_top:
            self.root.attributes('-topmost', True)
    
    def _create_sidebar_layout(self, parent):
        """Create layout with sidebar"""
        # Create paned window
        paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar
        sidebar = ttk.Frame(paned, style='Panel.TFrame', width=250)
        paned.add(sidebar, weight=0)
        
        # Main content area
        content = ttk.Frame(paned, style='Dashboard.TFrame')
        paned.add(content, weight=1)
        
        # Build sidebar
        self._build_sidebar(sidebar)
        
        # Build main content
        self._build_main_content(content)
    
    def _create_full_layout(self, parent):
        """Create full-width layout"""
        self._build_main_content(parent)
    
    def _build_sidebar(self, parent):
        """Build sidebar with controls and status"""
        # Title
        title_label = ttk.Label(parent, text="JARVIS AI", style='Accent.TLabel', font=('Arial', 16, 'bold'))
        title_label.pack(pady=(10, 20))
        
        # System status
        status_frame = ttk.LabelFrame(parent, text="System Status", style='Panel.TFrame')
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self._create_status_indicators(status_frame)
        
        # Quick controls
        controls_frame = ttk.LabelFrame(parent, text="Controls", style='Panel.TFrame')
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self._create_quick_controls(controls_frame)
        
        # Configuration
        config_frame = ttk.LabelFrame(parent, text="Configuration", style='Panel.TFrame')
        config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self._create_config_controls(config_frame)
    
    def _create_status_indicators(self, parent):
        """Create system status indicators"""
        indicators = [
            ('Voice Interface', 'voice'),
            ('LLM Provider', 'llm'),
            ('Task Coordinator', 'tasks'),
            ('Web Search', 'web'),
            ('Office Automation', 'office')
        ]
        
        for i, (name, key) in enumerate(indicators):
            frame = ttk.Frame(parent)
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            label = ttk.Label(frame, text=name, style='Dashboard.TLabel')
            label.pack(side=tk.LEFT)
            
            status_label = ttk.Label(frame, text="●", foreground=self.colors['error'], font=('Arial', 12))
            status_label.pack(side=tk.RIGHT)
            
            self.status_indicators[key] = status_label
    
    def _create_quick_controls(self, parent):
        """Create quick control buttons"""
        buttons = [
            ('Start Voice', self._start_voice),
            ('Stop Voice', self._stop_voice),
            ('Clear Logs', self._clear_logs),
            ('Export Data', self._export_data),
            ('Settings', self._open_settings)
        ]
        
        for text, command in buttons:
            btn = ttk.Button(parent, text=text, command=command, style='Dashboard.TButton')
            btn.pack(fill=tk.X, padx=5, pady=2)
    
    def _create_config_controls(self, parent):
        """Create configuration controls"""
        # Theme selection
        theme_frame = ttk.Frame(parent)
        theme_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(theme_frame, text="Theme:", style='Dashboard.TLabel').pack(side=tk.LEFT)
        
        theme_var = tk.StringVar(value=self.config.theme.value)
        theme_combo = ttk.Combobox(theme_frame, textvariable=theme_var, 
                                  values=[t.value for t in DashboardTheme],
                                  state='readonly', width=10)
        theme_combo.pack(side=tk.RIGHT)
        theme_combo.bind('<<ComboboxSelected>>', lambda e: self._change_theme(theme_var.get()))
        
        # Refresh interval
        refresh_frame = ttk.Frame(parent)
        refresh_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(refresh_frame, text="Refresh (s):", style='Dashboard.TLabel').pack(side=tk.LEFT)
        
        refresh_var = tk.DoubleVar(value=self.config.refresh_interval)
        refresh_spin = ttk.Spinbox(refresh_frame, from_=0.1, to=10.0, increment=0.1,
                                  textvariable=refresh_var, width=8)
        refresh_spin.pack(side=tk.RIGHT)
        refresh_spin.bind('<Return>', lambda e: self._change_refresh_interval(refresh_var.get()))
    
    def _build_main_content(self, parent):
        """Build main content area"""
        # Create notebook for tabs
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Overview tab
        overview_frame = ttk.Frame(notebook, style='Dashboard.TFrame')
        notebook.add(overview_frame, text="Overview")
        self._build_overview_tab(overview_frame)
        
        # Voice tab
        voice_frame = ttk.Frame(notebook, style='Dashboard.TFrame')
        notebook.add(voice_frame, text="Voice Interface")
        self._build_voice_tab(voice_frame)
        
        # Chat tab
        chat_frame = ttk.Frame(notebook, style='Dashboard.TFrame')
        notebook.add(chat_frame, text="Chat")
        self._build_chat_tab(chat_frame)
        
        # Logs tab
        logs_frame = ttk.Frame(notebook, style='Dashboard.TFrame')
        notebook.add(logs_frame, text="Logs")
        self._build_logs_tab(logs_frame)
        
        # Tasks tab
        tasks_frame = ttk.Frame(notebook, style='Dashboard.TFrame')
        notebook.add(tasks_frame, text="Tasks")
        self._build_tasks_tab(tasks_frame)
        
        # Evolution tab (if available)
        if EVOLUTION_AVAILABLE:
            evolution_frame = ttk.Frame(notebook, style='Dashboard.TFrame')
            notebook.add(evolution_frame, text="Evolution")
            self._build_evolution_tab(evolution_frame)
        
        # LLM Management tab (if available)
        if LLM_AVAILABLE:
            llm_frame = ttk.Frame(notebook, style='Dashboard.TFrame')
            notebook.add(llm_frame, text="LLM Management")
            self._build_llm_tab(llm_frame)
        
        # Agent Control tab (if available)
        if AGENT_AVAILABLE:
            agent_frame = ttk.Frame(notebook, style='Dashboard.TFrame')
            notebook.add(agent_frame, text="Agent Control")
            self._build_agent_tab(agent_frame)
        
        # Web Automation tab (if available)
        if WEB_AVAILABLE:
            web_frame = ttk.Frame(notebook, style='Dashboard.TFrame')
            notebook.add(web_frame, text="Web Automation")
            self._build_web_tab(web_frame)
    
    def _build_overview_tab(self, parent):
        """Build overview tab with metrics"""
        # Metrics chart
        chart_frame = ttk.LabelFrame(parent, text="System Metrics")
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.metrics_chart = MetricsChart(chart_frame)
        
        # Summary stats
        stats_frame = ttk.LabelFrame(parent, text="Summary")
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self._create_summary_stats(stats_frame)
    
    def _build_voice_tab(self, parent):
        """Build voice interface tab"""
        # Voice visualizer
        viz_frame = ttk.LabelFrame(parent, text="Voice Activity")
        viz_frame.pack(fill=tk.X, padx=10, pady=5, ipady=10)
        
        self.voice_visualizer = VoiceVisualizer(viz_frame)
        
        # Voice controls
        controls_frame = ttk.LabelFrame(parent, text="Voice Controls")
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self._create_voice_controls(controls_frame)
        
        # Voice settings
        settings_frame = ttk.LabelFrame(parent, text="Voice Settings")
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self._create_voice_settings(settings_frame)
    
    def _build_chat_tab(self, parent):
        """Build chat interface tab"""
        # Chat display
        chat_frame = ttk.Frame(parent)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Chat text area
        self.chat_text = tk.Text(chat_frame, bg=self.colors['panel'], fg=self.colors['fg'],
                                insertbackground=self.colors['accent'], wrap=tk.WORD)
        chat_scrollbar = ttk.Scrollbar(chat_frame, orient=tk.VERTICAL, command=self.chat_text.yview)
        self.chat_text.configure(yscrollcommand=chat_scrollbar.set)
        
        self.chat_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Chat input
        input_frame = ttk.Frame(parent)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.chat_entry = tk.Entry(input_frame, bg=self.colors['panel'], fg=self.colors['fg'],
                                  insertbackground=self.colors['accent'])
        self.chat_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.chat_entry.bind('<Return>', self._send_chat_message)
        
        send_btn = ttk.Button(input_frame, text="Send", command=self._send_chat_message)
        send_btn.pack(side=tk.RIGHT)
    
    def _build_logs_tab(self, parent):
        """Build logs tab"""
        # Log controls
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(controls_frame, text="Clear", command=self._clear_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Export", command=self._export_logs).pack(side=tk.LEFT, padx=5)
        
        # Log level filter
        ttk.Label(controls_frame, text="Level:").pack(side=tk.LEFT, padx=(20, 5))
        log_level_var = tk.StringVar(value="ALL")
        log_level_combo = ttk.Combobox(controls_frame, textvariable=log_level_var,
                                      values=["ALL", "DEBUG", "INFO", "WARNING", "ERROR"],
                                      state='readonly', width=10)
        log_level_combo.pack(side=tk.LEFT, padx=5)
        
        # Log display
        log_frame = ttk.Frame(parent)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = tk.Text(log_frame, bg=self.colors['panel'], fg=self.colors['fg'],
                               insertbackground=self.colors['accent'], wrap=tk.WORD, state=tk.DISABLED)
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _build_tasks_tab(self, parent):
        """Build tasks monitoring tab"""
        # Task list
        tasks_frame = ttk.LabelFrame(parent, text="Active Tasks")
        tasks_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create treeview for tasks
        columns = ('ID', 'Type', 'Status', 'Progress', 'Started')
        self.tasks_tree = ttk.Treeview(tasks_frame, columns=columns, show='headings')
        
        for col in columns:
            self.tasks_tree.heading(col, text=col)
            self.tasks_tree.column(col, width=100)
        
        tasks_scrollbar = ttk.Scrollbar(tasks_frame, orient=tk.VERTICAL, command=self.tasks_tree.yview)
        self.tasks_tree.configure(yscrollcommand=tasks_scrollbar.set)
        
        self.tasks_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tasks_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_summary_stats(self, parent):
        """Create summary statistics display"""
        stats = [
            ('Uptime', '00:00:00'),
            ('Commands Processed', '0'),
            ('Tasks Completed', '0'),
            ('Avg Response Time', '0ms'),
            ('Memory Usage', '0%'),
            ('CPU Usage', '0%')
        ]
        
        # Create grid layout
        for i, (label, value) in enumerate(stats):
            row = i // 3
            col = i % 3
            
            stat_frame = ttk.Frame(parent)
            stat_frame.grid(row=row, column=col, padx=10, pady=5, sticky='ew')
            
            ttk.Label(stat_frame, text=label, style='Dashboard.TLabel').pack()
            value_label = ttk.Label(stat_frame, text=value, style='Accent.TLabel', font=('Arial', 12, 'bold'))
            value_label.pack()
            
            # Store reference for updates
            setattr(self, f'stat_{label.lower().replace(" ", "_")}', value_label)
        
        # Configure grid weights
        for i in range(3):
            parent.columnconfigure(i, weight=1)
    
    def _create_voice_controls(self, parent):
        """Create voice control buttons"""
        controls = [
            ('Start Listening', self._start_voice),
            ('Stop Listening', self._stop_voice),
            ('Test Microphone', self._test_microphone),
            ('Test Speaker', self._test_speaker)
        ]
        
        for i, (text, command) in enumerate(controls):
            row = i // 2
            col = i % 2
            
            btn = ttk.Button(parent, text=text, command=command)
            btn.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
        
        # Configure grid weights
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)
    
    def _create_voice_settings(self, parent):
        """Create voice settings controls"""
        # Settings will be populated based on voice interface config
        settings_text = tk.Text(parent, bg=self.colors['panel'], fg=self.colors['fg'],
                               height=10, wrap=tk.WORD)
        settings_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Placeholder content
        settings_text.insert(tk.END, "Voice settings will be displayed here...\n")
        settings_text.insert(tk.END, "- STT Engine: Whisper\n")
        settings_text.insert(tk.END, "- TTS Engine: Piper\n")
        settings_text.insert(tk.END, "- Language: Indonesian\n")
        settings_text.insert(tk.END, "- Input Mode: Voice Activation\n")
    
    def _create_status_bar(self):
        """Create status bar at bottom"""
        self.status_bar = ttk.Frame(self.root, style='Panel.TFrame')
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Status text
        self.status_text = ttk.Label(self.status_bar, text="Ready", style='Dashboard.TLabel')
        self.status_text.pack(side=tk.LEFT, padx=10)
        
        # Connection status
        self.connection_status = ttk.Label(self.status_bar, text="●", foreground=self.colors['error'])
        self.connection_status.pack(side=tk.RIGHT, padx=10)
        
        ttk.Label(self.status_bar, text="Status:", style='Dashboard.TLabel').pack(side=tk.RIGHT)
    
    # Event handlers
    def _start_voice(self):
        """Start voice interface"""
        self.update_status_text("Starting voice interface...")
        # Implementation would call voice interface start method
        logger.info("Voice interface start requested")
    
    def _stop_voice(self):
        """Stop voice interface"""
        self.update_status_text("Stopping voice interface...")
        # Implementation would call voice interface stop method
        logger.info("Voice interface stop requested")
    
    def _test_microphone(self):
        """Test microphone"""
        self.update_status_text("Testing microphone...")
        # Implementation would test microphone
        logger.info("Microphone test requested")
    
    def _test_speaker(self):
        """Test speaker"""
        self.update_status_text("Testing speaker...")
        # Implementation would test speaker
        logger.info("Speaker test requested")
    
    def _clear_logs(self):
        """Clear log display"""
        if self.log_text:
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete(1.0, tk.END)
            self.log_text.config(state=tk.DISABLED)
        
        self.log_entries.clear()
        logger.info("Logs cleared")
    
    def _export_data(self):
        """Export dashboard data"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                data = {
                    'metrics': [m.__dict__ for m in self.metrics_history],
                    'logs': [{
                        'timestamp': entry.timestamp.isoformat(),
                        'level': entry.level,
                        'module': entry.module,
                        'message': entry.message,
                        'details': entry.details
                    } for entry in self.log_entries],
                    'config': self.config.dict()
                }
                
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                
                self.update_status_text(f"Data exported to {filename}")
                logger.info(f"Dashboard data exported to {filename}")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export data: {e}")
                logger.error(f"Export failed: {e}")
    
    def _export_logs(self):
        """Export logs only"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    for entry in self.log_entries:
                        f.write(f"[{entry.timestamp}] {entry.level} - {entry.module}: {entry.message}\n")
                
                self.update_status_text(f"Logs exported to {filename}")
                logger.info(f"Logs exported to {filename}")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export logs: {e}")
                logger.error(f"Log export failed: {e}")
    
    def _build_evolution_tab(self, parent):
        """Build evolution monitoring and control tab"""
        # Evolution status section
        status_frame = ttk.LabelFrame(parent, text="Evolution Status")
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Status indicators
        status_grid = ttk.Frame(status_frame)
        status_grid.pack(fill=tk.X, padx=10, pady=5)
        
        # Evolution engine status
        ttk.Label(status_grid, text="Engine Status:", style='Dashboard.TLabel').grid(row=0, column=0, sticky='w', padx=5)
        self.evolution_status_label = ttk.Label(status_grid, text="Initializing...", style='Accent.TLabel')
        self.evolution_status_label.grid(row=0, column=1, sticky='w', padx=5)
        
        # Last evolution time
        ttk.Label(status_grid, text="Last Evolution:", style='Dashboard.TLabel').grid(row=0, column=2, sticky='w', padx=5)
        self.last_evolution_label = ttk.Label(status_grid, text="Never", style='Dashboard.TLabel')
        self.last_evolution_label.grid(row=0, column=3, sticky='w', padx=5)
        
        # Next evolution countdown
        ttk.Label(status_grid, text="Next Evolution:", style='Dashboard.TLabel').grid(row=1, column=0, sticky='w', padx=5)
        self.next_evolution_label = ttk.Label(status_grid, text="--:--", style='Dashboard.TLabel')
        self.next_evolution_label.grid(row=1, column=1, sticky='w', padx=5)
        
        # Total cycles
        ttk.Label(status_grid, text="Total Cycles:", style='Dashboard.TLabel').grid(row=1, column=2, sticky='w', padx=5)
        self.total_cycles_label = ttk.Label(status_grid, text="0", style='Dashboard.TLabel')
        self.total_cycles_label.grid(row=1, column=3, sticky='w', padx=5)
        
        # Evolution controls
        controls_frame = ttk.LabelFrame(parent, text="Evolution Controls")
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        controls_grid = ttk.Frame(controls_frame)
        controls_grid.pack(fill=tk.X, padx=10, pady=5)
        
        # Control buttons
        self.start_evolution_btn = ttk.Button(controls_grid, text="Start Evolution", command=self._start_evolution)
        self.start_evolution_btn.grid(row=0, column=0, padx=5, pady=2)
        
        self.stop_evolution_btn = ttk.Button(controls_grid, text="Stop Evolution", command=self._stop_evolution, state='disabled')
        self.stop_evolution_btn.grid(row=0, column=1, padx=5, pady=2)
        
        self.force_evolution_btn = ttk.Button(controls_grid, text="Force Evolution", command=self._force_evolution)
        self.force_evolution_btn.grid(row=0, column=2, padx=5, pady=2)
        
        self.reset_evolution_btn = ttk.Button(controls_grid, text="Reset Memory", command=self._reset_evolution_memory)
        self.reset_evolution_btn.grid(row=0, column=3, padx=5, pady=2)
        
        # Evolution metrics
        metrics_frame = ttk.LabelFrame(parent, text="Evolution Metrics")
        metrics_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create metrics chart
        self.evolution_chart = self._create_evolution_chart(metrics_frame)
        
        # Recent cycles list
        cycles_frame = ttk.LabelFrame(parent, text="Recent Evolution Cycles")
        cycles_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create treeview for cycles
        columns = ('Cycle ID', 'Start Time', 'Duration', 'Mutations', 'Performance', 'Status')
        self.cycles_tree = ttk.Treeview(cycles_frame, columns=columns, show='headings', height=6)
        
        for col in columns:
            self.cycles_tree.heading(col, text=col)
            self.cycles_tree.column(col, width=100)
        
        cycles_scrollbar = ttk.Scrollbar(cycles_frame, orient=tk.VERTICAL, command=self.cycles_tree.yview)
        self.cycles_tree.configure(yscrollcommand=cycles_scrollbar.set)
        
        self.cycles_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cycles_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Initialize evolution engine if available
        self.evolution_engine = None
        if EVOLUTION_AVAILABLE:
            try:
                self.evolution_engine = EvolutionEngine()
                self._update_evolution_status()
            except Exception as e:
                logger.error(f"Failed to initialize evolution engine: {e}")
    
    def _create_evolution_chart(self, parent):
        """Create evolution performance chart"""
        fig = Figure(figsize=(8, 4), dpi=100)
        fig.patch.set_facecolor(self.colors['bg'])
        
        ax = fig.add_subplot(111)
        ax.set_facecolor(self.colors['panel'])
        ax.tick_params(colors=self.colors['fg'])
        ax.set_xlabel('Evolution Cycle', color=self.colors['fg'])
        ax.set_ylabel('Performance Improvement', color=self.colors['fg'])
        ax.set_title('Evolution Performance Over Time', color=self.colors['fg'])
        
        # Initialize with empty data
        self.evolution_line, = ax.plot([], [], color=self.colors['accent'], linewidth=2)
        ax.grid(True, alpha=0.3, color=self.colors['fg'])
        
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        return {'fig': fig, 'ax': ax, 'canvas': canvas, 'line': self.evolution_line}
    
    def _start_evolution(self):
        """Start evolution engine"""
        if self.evolution_engine:
            try:
                # Start evolution in background thread
                threading.Thread(target=self._evolution_loop, daemon=True).start()
                self.start_evolution_btn.config(state='disabled')
                self.stop_evolution_btn.config(state='normal')
                self.evolution_status_label.config(text="Running")
                logger.info("Evolution engine started")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start evolution: {e}")
    
    def _stop_evolution(self):
        """Stop evolution engine"""
        if self.evolution_engine:
            self.evolution_running = False
            self.start_evolution_btn.config(state='normal')
            self.stop_evolution_btn.config(state='disabled')
            self.evolution_status_label.config(text="Stopped")
            logger.info("Evolution engine stopped")
    
    def _force_evolution(self):
        """Force immediate evolution cycle"""
        if self.evolution_engine:
            try:
                # Run evolution in background thread
                threading.Thread(target=self._run_evolution_cycle, daemon=True).start()
                logger.info("Forced evolution cycle started")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to force evolution: {e}")
    
    def _reset_evolution_memory(self):
        """Reset evolution memory"""
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset evolution memory? This cannot be undone."):
            if self.evolution_engine:
                try:
                    self.evolution_engine.memory_store.clear_all_experiences()
                    self.evolution_engine.evolution_cycles.clear()
                    self._update_evolution_display()
                    logger.info("Evolution memory reset")
                    messagebox.showinfo("Success", "Evolution memory has been reset")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to reset memory: {e}")
    
    def _evolution_loop(self):
        """Main evolution loop running in background"""
        self.evolution_running = True
        while self.evolution_running:
            try:
                if self.evolution_engine and self.evolution_engine.should_evolve():
                    asyncio.run(self.evolution_engine.evolve())
                    self.root.after(0, self._update_evolution_display)
                time.sleep(10)  # Check every 10 seconds
            except Exception as e:
                logger.error(f"Evolution loop error: {e}")
                time.sleep(30)  # Wait longer on error
    
    def _run_evolution_cycle(self):
        """Run a single evolution cycle"""
        try:
            if self.evolution_engine:
                # Temporarily override should_evolve to force evolution
                original_time = self.evolution_engine.last_evolution_time
                self.evolution_engine.last_evolution_time = 0
                
                cycle = asyncio.run(self.evolution_engine.evolve())
                
                # Restore original time if evolution failed
                if not cycle or not cycle.success:
                    self.evolution_engine.last_evolution_time = original_time
                
                self.root.after(0, self._update_evolution_display)
        except Exception as e:
            logger.error(f"Evolution cycle error: {e}")
    
    def _update_evolution_status(self):
        """Update evolution status display"""
        if self.evolution_engine:
            # Update status labels
            if hasattr(self, 'evolution_status_label'):
                status = "Running" if getattr(self, 'evolution_running', False) else "Ready"
                self.evolution_status_label.config(text=status)
            
            if hasattr(self, 'total_cycles_label'):
                self.total_cycles_label.config(text=str(len(self.evolution_engine.evolution_cycles)))
            
            if hasattr(self, 'last_evolution_label') and self.evolution_engine.evolution_cycles:
                last_cycle = self.evolution_engine.evolution_cycles[-1]
                last_time = datetime.fromtimestamp(last_cycle.start_time).strftime('%H:%M:%S')
                self.last_evolution_label.config(text=last_time)
    
    def _update_evolution_display(self):
        """Update evolution display with latest data"""
        if not self.evolution_engine:
            return
        
        # Update status
        self._update_evolution_status()
        
        # Update cycles tree
        if hasattr(self, 'cycles_tree'):
            # Clear existing items
            for item in self.cycles_tree.get_children():
                self.cycles_tree.delete(item)
            
            # Add recent cycles (last 10)
            recent_cycles = self.evolution_engine.evolution_cycles[-10:]
            for cycle in reversed(recent_cycles):
                start_time = datetime.fromtimestamp(cycle.start_time).strftime('%H:%M:%S')
                duration = f"{cycle.end_time - cycle.start_time:.1f}s" if cycle.end_time else "Running"
                status = "Success" if cycle.success else "Failed"
                performance = f"{cycle.performance_improvement:+.2%}" if cycle.performance_improvement else "N/A"
                
                self.cycles_tree.insert('', 0, values=(
                    cycle.cycle_id[-8:],  # Short ID
                    start_time,
                    duration,
                    cycle.mutations_applied,
                    performance,
                    status
                ))
        
        # Update chart
        if hasattr(self, 'evolution_chart'):
            cycles = self.evolution_engine.evolution_cycles
            if cycles:
                x_data = list(range(len(cycles)))
                y_data = [c.performance_improvement for c in cycles]
                
                self.evolution_chart['line'].set_data(x_data, y_data)
                self.evolution_chart['ax'].relim()
                self.evolution_chart['ax'].autoscale_view()
                self.evolution_chart['canvas'].draw()
    
    def _open_settings(self):
        """Open settings dialog"""
        # Create settings window
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.configure(bg=self.colors['bg'])
        
        # Settings content would go here
        ttk.Label(settings_window, text="Settings", style='Accent.TLabel', font=('Arial', 16)).pack(pady=20)
        ttk.Label(settings_window, text="Settings dialog will be implemented here", style='Dashboard.TLabel').pack()
    
    def _send_chat_message(self, event=None):
        """Send chat message"""
        if self.chat_entry:
            message = self.chat_entry.get().strip()
            if message:
                # Add to chat display
                self.add_chat_message("User", message)
                
                # Clear entry
                self.chat_entry.delete(0, tk.END)
                
                # Send to callback
                if self.on_command_send:
                    self.on_command_send(message)
                
                logger.info(f"Chat message sent: {message}")
    
    def _change_theme(self, theme_name: str):
        """Change dashboard theme"""
        try:
            self.config.theme = DashboardTheme(theme_name)
            self._apply_theme()
            logger.info(f"Theme changed to {theme_name}")
        except ValueError:
            logger.error(f"Invalid theme: {theme_name}")
    
    def _change_refresh_interval(self, interval: float):
        """Change refresh interval"""
        self.config.refresh_interval = max(0.1, interval)
        logger.info(f"Refresh interval changed to {interval}s")
    
    def _on_closing(self):
        """Handle window closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit Jarvis Dashboard?"):
            self.shutdown()
    
    # Public methods
    def start_updates(self):
        """Start dashboard update loop"""
        self.is_running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        
        if self.voice_visualizer:
            self.voice_visualizer.start_animation()
        
        logger.info("Dashboard updates started")
    
    def stop_updates(self):
        """Stop dashboard update loop"""
        self.is_running = False
        
        if self.update_thread:
            self.update_thread.join(timeout=2.0)
        
        if self.voice_visualizer:
            self.voice_visualizer.stop_animation()
        
        logger.info("Dashboard updates stopped")
    
    def _update_loop(self):
        """Main update loop"""
        while self.is_running:
            try:
                # Update metrics display
                self._update_metrics_display()
                
                # Update status indicators
                self._update_status_indicators()
                
                # Update summary stats
                self._update_summary_stats()
                
                # Update evolution display if available
                if EVOLUTION_AVAILABLE and self.evolution_engine:
                    self.root.after(0, self._update_evolution_status)
                
                # Update LLM metrics display if available
                if LLM_AVAILABLE:
                    self.root.after(0, self._update_llm_metrics_display)
                
                # Update Agent metrics display if available
                if AGENT_AVAILABLE:
                    self.root.after(0, self._update_agent_metrics_display)
                
                # Update Web automation metrics display if available
                if WEB_AVAILABLE:
                    self.root.after(0, self._update_web_metrics_display)
                
                time.sleep(self.config.refresh_interval)
                
            except Exception as e:
                logger.error(f"Dashboard update error: {e}")
                time.sleep(1.0)
    
    def _update_metrics_display(self):
        """Update metrics chart (thread-safe)"""
        if self.metrics_chart and self.metrics_history:
            def update_ui():
                try:
                    latest_metrics = self.metrics_history[-1]
                    self.metrics_chart.add_metrics(latest_metrics)
                except Exception as e:
                    logger.error(f"Metrics display update error: {e}")
            
            # Schedule UI update in main thread
            if self.root:
                self.root.after(0, update_ui)
    
    def _update_status_indicators(self):
        """Update status indicator colors (thread-safe)"""
        def update_ui():
            try:
                # This would be updated based on actual system status
                for key, indicator in self.status_indicators.items():
                    # Placeholder logic
                    if self.system_status == SystemStatus.ONLINE:
                        color = self.colors['success']
                    elif self.system_status == SystemStatus.ERROR:
                        color = self.colors['error']
                    else:
                        color = self.colors['warning']
                    
                    indicator.configure(foreground=color)
            except Exception as e:
                logger.error(f"Status indicators update error: {e}")
        
        # Schedule UI update in main thread
        if self.root:
            self.root.after(0, update_ui)
    
    def _update_summary_stats(self):
        """Update summary statistics (thread-safe)"""
        if self.metrics_history:
            def update_ui():
                try:
                    latest = self.metrics_history[-1]
                    
                    # Update stat labels if they exist
                    if hasattr(self, 'stat_memory_usage'):
                        self.stat_memory_usage.configure(text=f"{latest.memory_usage:.1f}%")
                    
                    if hasattr(self, 'stat_cpu_usage'):
                        self.stat_cpu_usage.configure(text=f"{latest.cpu_usage:.1f}%")
                    
                    if hasattr(self, 'stat_commands_processed'):
                        self.stat_commands_processed.configure(text=str(latest.voice_commands))
                    
                    if hasattr(self, 'stat_avg_response_time'):
                        self.stat_avg_response_time.configure(text=f"{latest.response_time*1000:.0f}ms")
                except Exception as e:
                    logger.error(f"Summary stats update error: {e}")
            
            # Schedule UI update in main thread
            if self.root:
                self.root.after(0, update_ui)
    
    def add_metrics(self, metrics: DashboardMetrics):
        """Add new metrics data"""
        self.metrics_history.append(metrics)
        
        # Limit history size
        if len(self.metrics_history) > self.config.metrics_history_size:
            self.metrics_history.pop(0)
    
    def add_log_entry(self, level: str, module: str, message: str, details: Dict[str, Any] = None):
        """Add new log entry"""
        entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            module=module,
            message=message,
            details=details
        )
        
        self.log_entries.append(entry)
        
        # Limit log buffer size
        if len(self.log_entries) > self.config.log_buffer_size:
            self.log_entries.pop(0)
        
        # Update log display
        if self.log_text:
            self.root.after(0, self._update_log_display, entry)
    
    def _update_log_display(self, entry: LogEntry):
        """Update log display with new entry"""
        if self.log_text:
            self.log_text.config(state=tk.NORMAL)
            
            # Color code by level
            color = {
                'DEBUG': '#888888',
                'INFO': self.colors['fg'],
                'WARNING': self.colors['warning'],
                'ERROR': self.colors['error']
            }.get(entry.level, self.colors['fg'])
            
            # Insert log entry
            timestamp_str = entry.timestamp.strftime('%H:%M:%S')
            log_line = f"[{timestamp_str}] {entry.level} - {entry.module}: {entry.message}\n"
            
            self.log_text.insert(tk.END, log_line)
            self.log_text.see(tk.END)
            
            self.log_text.config(state=tk.DISABLED)
    
    def add_chat_message(self, sender: str, message: str):
        """Add message to chat display"""
        if self.chat_text:
            timestamp = datetime.now().strftime('%H:%M:%S')
            chat_line = f"[{timestamp}] {sender}: {message}\n"
            
            self.chat_text.insert(tk.END, chat_line)
            self.chat_text.see(tk.END)
    
    def update_status_text(self, text: str):
        """Update status bar text"""
        if hasattr(self, 'status_text'):
            self.status_text.configure(text=text)
    
    def update_system_status(self, status: SystemStatus):
        """Update system status"""
        self.system_status = status
        
        # Update connection indicator
        if hasattr(self, 'connection_status'):
            color = {
                SystemStatus.ONLINE: self.colors['success'],
                SystemStatus.OFFLINE: self.colors['error'],
                SystemStatus.ERROR: self.colors['error'],
                SystemStatus.INITIALIZING: self.colors['warning'],
                SystemStatus.MAINTENANCE: self.colors['warning']
            }.get(status, self.colors['error'])
            
            self.connection_status.configure(foreground=color)
    
    def update_voice_visualization(self, audio_data: np.ndarray):
        """Update voice visualization"""
        if self.voice_visualizer:
            self.voice_visualizer.update_audio_data(audio_data)
    
    def run(self):
        """Run the dashboard"""
        logger.info("Starting Jarvis Dashboard")
        self.root.mainloop()
    
    def _build_llm_tab(self, parent):
        """Build LLM Management tab"""
        # Provider status section
        status_frame = ttk.LabelFrame(parent, text="Provider Status")
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self._create_provider_status(status_frame)
        
        # Model selection section
        model_frame = ttk.LabelFrame(parent, text="Model Selection")
        model_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self._create_model_selection(model_frame)
        
        # Usage metrics section
        metrics_frame = ttk.LabelFrame(parent, text="Usage Metrics")
        metrics_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self._create_llm_metrics(metrics_frame)
        
        # Control buttons
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self._create_llm_controls(controls_frame)
    
    def _create_provider_status(self, parent):
        """Create provider status display"""
        # Create grid for provider status
        providers = ['OpenAI', 'Anthropic', 'Groq', 'DeepSeek', 'Ollama', 'Gemini']
        
        for i, provider in enumerate(providers):
            row = i // 3
            col = i % 3
            
            provider_frame = ttk.Frame(parent)
            provider_frame.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
            
            # Provider name
            name_label = ttk.Label(provider_frame, text=provider, font=('Arial', 10, 'bold'))
            name_label.pack()
            
            # Status indicator
            status_label = ttk.Label(provider_frame, text="●", foreground='green')
            status_label.pack()
            
            # Store reference for updates
            self.status_indicators[f'llm_{provider.lower()}'] = status_label
        
        # Configure grid weights
        for i in range(3):
            parent.columnconfigure(i, weight=1)
    
    def _create_model_selection(self, parent):
        """Create model selection controls"""
        # Current provider
        provider_frame = ttk.Frame(parent)
        provider_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(provider_frame, text="Current Provider:").pack(side=tk.LEFT)
        self.current_provider_var = tk.StringVar(value="OpenAI")
        provider_combo = ttk.Combobox(provider_frame, textvariable=self.current_provider_var,
                                    values=['OpenAI', 'Anthropic', 'Groq', 'DeepSeek', 'Ollama', 'Gemini'],
                                    state='readonly', width=15)
        provider_combo.pack(side=tk.RIGHT)
        provider_combo.bind('<<ComboboxSelected>>', self._on_provider_change)
        
        # Current model
        model_frame = ttk.Frame(parent)
        model_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(model_frame, text="Current Model:").pack(side=tk.LEFT)
        self.current_model_var = tk.StringVar(value="gpt-4")
        self.model_combo = ttk.Combobox(model_frame, textvariable=self.current_model_var,
                                      state='readonly', width=20)
        self.model_combo.pack(side=tk.RIGHT)
        self.model_combo.bind('<<ComboboxSelected>>', self._on_model_change)
        
        # Update model list based on provider
        self._update_model_list()
    
    def _create_llm_metrics(self, parent):
        """Create LLM usage metrics display"""
        # Metrics tree
        columns = ('Metric', 'Value', 'Trend')
        self.llm_metrics_tree = ttk.Treeview(parent, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.llm_metrics_tree.heading(col, text=col)
            self.llm_metrics_tree.column(col, width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.llm_metrics_tree.yview)
        self.llm_metrics_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        self.llm_metrics_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Initialize with sample data
        self._update_llm_metrics_display()
    
    def _create_llm_controls(self, parent):
        """Create LLM control buttons"""
        buttons = [
            ('Test Connection', self._test_llm_connection),
            ('Refresh Models', self._refresh_model_list),
            ('Reset Metrics', self._reset_llm_metrics),
            ('Export Config', self._export_llm_config)
        ]
        
        for text, command in buttons:
            btn = ttk.Button(parent, text=text, command=command)
            btn.pack(side=tk.LEFT, padx=5)
    
    def _on_provider_change(self, event=None):
        """Handle provider change"""
        self.current_provider = self.current_provider_var.get()
        self._update_model_list()
        logger.info(f"Provider changed to: {self.current_provider}")
    
    def _on_model_change(self, event=None):
        """Handle model change"""
        model = self.current_model_var.get()
        logger.info(f"Model changed to: {model}")
    
    def _update_model_list(self):
        """Update available models based on selected provider"""
        provider = self.current_provider_var.get()
        
        # Mock model lists for each provider
        model_lists = {
            'OpenAI': ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo'],
            'Anthropic': ['claude-3.5-sonnet', 'claude-3.5-haiku', 'claude-3-opus'],
            'Groq': ['llama-3.1-70b', 'llama-3.1-8b', 'mixtral-8x7b'],
            'DeepSeek': ['deepseek-r1', 'deepseek-coder', 'deepseek-chat'],
            'Ollama': ['llama3.2:3b', 'llama3.2:7b', 'llama3.2-vision:11b'],
            'Gemini': ['gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-1.0-pro']
        }
        
        models = model_lists.get(provider, [])
        self.model_combo['values'] = models
        if models:
            self.current_model_var.set(models[0])
    
    def _update_llm_metrics_display(self):
        """Update LLM metrics display"""
        if not hasattr(self, 'llm_metrics_tree') or not self.llm_metrics_tree:
            return
            
        try:
            # Clear existing items
            for item in self.llm_metrics_tree.get_children():
                self.llm_metrics_tree.delete(item)
            
            # Sample metrics data
            metrics = [
                ('Total Requests', '1,247', '↑ 12%'),
                ('Avg Response Time', '1.2s', '↓ 5%'),
                ('Success Rate', '98.5%', '↑ 2%'),
                ('Token Usage', '45,678', '↑ 8%'),
                ('Cost Today', '$12.34', '↑ 15%'),
                ('Active Models', '3', '→ 0%'),
                ('Failed Requests', '18', '↓ 25%'),
                ('Cache Hit Rate', '67%', '↑ 3%')
            ]
            
            for metric in metrics:
                self.llm_metrics_tree.insert('', 'end', values=metric)
                
        except Exception as e:
            logger.error(f"Error updating LLM metrics display: {e}")
    
    def _test_llm_connection(self):
        """Test connection to current LLM provider"""
        provider = self.current_provider_var.get()
        model = self.current_model_var.get()
        
        # Mock connection test
        import random
        success = random.choice([True, True, True, False])  # 75% success rate
        
        if success:
            messagebox.showinfo("Connection Test", f"Successfully connected to {provider} - {model}")
            # Update status indicator
            if f'llm_{provider.lower()}' in self.status_indicators:
                self.status_indicators[f'llm_{provider.lower()}'].configure(foreground='green')
        else:
            messagebox.showerror("Connection Test", f"Failed to connect to {provider} - {model}")
            # Update status indicator
            if f'llm_{provider.lower()}' in self.status_indicators:
                self.status_indicators[f'llm_{provider.lower()}'].configure(foreground='red')
    
    def _refresh_model_list(self):
        """Refresh available models"""
        self._update_model_list()
        messagebox.showinfo("Refresh", "Model list refreshed successfully")
    
    def _reset_llm_metrics(self):
        """Reset LLM metrics"""
        self.llm_metrics = {}
        self._update_llm_metrics_display()
        messagebox.showinfo("Reset", "LLM metrics reset successfully")
    
    def _export_llm_config(self):
        """Export LLM configuration"""
        config = {
            'current_provider': self.current_provider_var.get(),
            'current_model': self.current_model_var.get(),
            'metrics': self.llm_metrics
        }
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                import json
                with open(filename, 'w') as f:
                    json.dump(config, f, indent=2)
                messagebox.showinfo("Export", f"Configuration exported to {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export configuration: {e}")
    
    def _build_agent_tab(self, parent):
        """Build Agent Control tab"""
        if not AGENT_AVAILABLE:
            no_agent_label = ttk.Label(parent, text="Agent module not available")
            no_agent_label.pack(expand=True)
            return
        
        # Agent status section
        status_frame = ttk.LabelFrame(parent, text="Agent Status")
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        self._create_agent_status(status_frame)
        
        # Task management section
        task_frame = ttk.LabelFrame(parent, text="Task Management")
        task_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self._create_task_management(task_frame)
        
        # Agent metrics section
        metrics_frame = ttk.LabelFrame(parent, text="Agent Metrics")
        metrics_frame.pack(fill=tk.X, padx=10, pady=5)
        self._create_agent_metrics(metrics_frame)
        
        # Agent controls section
        controls_frame = ttk.LabelFrame(parent, text="Agent Controls")
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        self._create_agent_controls(controls_frame)
    
    def _create_agent_status(self, parent):
        """Create agent status display"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Agent state indicator
        ttk.Label(status_frame, text="Status:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.agent_status_label = ttk.Label(status_frame, text="Offline", foreground="red")
        self.agent_status_label.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Current task
        ttk.Label(status_frame, text="Current Task:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.current_task_label = ttk.Label(status_frame, text="None")
        self.current_task_label.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # Step counter
        ttk.Label(status_frame, text="Steps:").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.agent_steps_label = ttk.Label(status_frame, text="0/0")
        self.agent_steps_label.grid(row=2, column=1, sticky=tk.W, padx=5)
    
    def _create_task_management(self, parent):
        """Create task management interface"""
        # Task input
        input_frame = ttk.Frame(parent)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(input_frame, text="New Task:").pack(side=tk.LEFT)
        self.task_entry = ttk.Entry(input_frame)
        self.task_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Button(input_frame, text="Add Task", command=self._add_agent_task).pack(side=tk.RIGHT)
        
        # Task list
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Task listbox with scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.task_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.task_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.task_listbox.yview)
        
        # Task control buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Execute Selected", command=self._execute_selected_task).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Remove Selected", command=self._remove_selected_task).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Clear All", command=self._clear_all_tasks).pack(side=tk.LEFT, padx=2)
    
    def _create_agent_metrics(self, parent):
        """Create agent metrics display"""
        metrics_frame = ttk.Frame(parent)
        metrics_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Metrics labels
        self.agent_metrics_labels = {}
        metrics = ['Tasks Completed', 'Success Rate', 'Avg Steps', 'Total Runtime', 'Failures']
        
        for i, metric in enumerate(metrics):
            row = i // 3
            col = (i % 3) * 2
            
            ttk.Label(metrics_frame, text=f"{metric}:").grid(row=row, column=col, sticky=tk.W, padx=5, pady=2)
            label = ttk.Label(metrics_frame, text="0")
            label.grid(row=row, column=col+1, sticky=tk.W, padx=5, pady=2)
            self.agent_metrics_labels[metric] = label
    
    def _create_agent_controls(self, parent):
        """Create agent control buttons"""
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(controls_frame, text="Initialize Agent", command=self._initialize_agent).pack(side=tk.LEFT, padx=2)
        ttk.Button(controls_frame, text="Stop Agent", command=self._stop_agent).pack(side=tk.LEFT, padx=2)
        ttk.Button(controls_frame, text="Reset Metrics", command=self._reset_agent_metrics).pack(side=tk.LEFT, padx=2)
        ttk.Button(controls_frame, text="Export Tasks", command=self._export_agent_tasks).pack(side=tk.LEFT, padx=2)
    
    def _add_agent_task(self):
        """Add a new task to the agent queue"""
        task = self.task_entry.get().strip()
        if task:
            self.agent_tasks.append({
                'id': len(self.agent_tasks),
                'description': task,
                'status': 'pending',
                'created_at': time.time()
            })
            self.task_listbox.insert(tk.END, f"[PENDING] {task}")
            self.task_entry.delete(0, tk.END)
    
    def _execute_selected_task(self):
        """Execute the selected task"""
        selection = self.task_listbox.curselection()
        if not selection or not AGENT_AVAILABLE:
            return
        
        task_index = selection[0]
        if task_index < len(self.agent_tasks):
            task = self.agent_tasks[task_index]
            if task['status'] == 'pending':
                # Update task status
                task['status'] = 'running'
                self.task_listbox.delete(task_index)
                self.task_listbox.insert(task_index, f"[RUNNING] {task['description']}")
                
                # Execute task in background thread
                import threading
                thread = threading.Thread(target=self._run_agent_task, args=(task,))
                thread.daemon = True
                thread.start()
    
    def _run_agent_task(self, task):
        """Run agent task in background"""
        try:
            if not self.agent_instance:
                self._initialize_agent()
            
            if self.agent_instance:
                self.agent_running = True
                result = self.agent_instance.invoke(task['description'])
                
                # Update task status
                task['status'] = 'completed' if result.is_done else 'failed'
                task['result'] = result.content if result.is_done else result.error
                task['completed_at'] = time.time()
                
                # Update UI on main thread
                self.root.after(0, self._update_task_display, task)
                
        except Exception as e:
            task['status'] = 'failed'
            task['error'] = str(e)
            self.root.after(0, self._update_task_display, task)
        finally:
            self.agent_running = False
    
    def _update_task_display(self, task):
        """Update task display in UI"""
        # Find and update task in listbox
        for i in range(self.task_listbox.size()):
            item = self.task_listbox.get(i)
            if task['description'] in item:
                self.task_listbox.delete(i)
                status = task['status'].upper()
                self.task_listbox.insert(i, f"[{status}] {task['description']}")
                break
        
        # Update metrics
        self._update_agent_metrics_display()
    
    def _remove_selected_task(self):
        """Remove selected task from queue"""
        selection = self.task_listbox.curselection()
        if selection:
            task_index = selection[0]
            if task_index < len(self.agent_tasks):
                del self.agent_tasks[task_index]
                self.task_listbox.delete(task_index)
    
    def _clear_all_tasks(self):
        """Clear all tasks from queue"""
        self.agent_tasks.clear()
        self.task_listbox.delete(0, tk.END)
    
    def _initialize_agent(self):
        """Initialize the agent instance"""
        try:
            if AGENT_AVAILABLE:
                self.agent_instance = Agent(
                    instructions=["You are a helpful Windows automation agent."],
                    max_steps=50,
                    use_vision=True
                )
                self.agent_status_label.config(text="Ready", foreground="green")
                messagebox.showinfo("Success", "Agent initialized successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize agent: {str(e)}")
    
    def _stop_agent(self):
        """Stop the agent"""
        self.agent_running = False
        self.agent_instance = None
        self.agent_status_label.config(text="Offline", foreground="red")
        self.current_task_label.config(text="None")
    
    def _reset_agent_metrics(self):
        """Reset agent metrics"""
        self.agent_metrics.clear()
        self._update_agent_metrics_display()
    
    def _export_agent_tasks(self):
        """Export agent tasks to file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        
        if filename:
            try:
                import json
                with open(filename, 'w') as f:
                    json.dump(self.agent_tasks, f, indent=2)
                messagebox.showinfo("Success", "Agent tasks exported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export tasks: {str(e)}")
    
    def _update_agent_metrics_display(self):
        """Update agent metrics display"""
        if not AGENT_AVAILABLE or not hasattr(self, 'agent_metrics_labels'):
            return
        
        # Calculate metrics from task history
        completed_tasks = [t for t in self.agent_tasks if t['status'] == 'completed']
        failed_tasks = [t for t in self.agent_tasks if t['status'] == 'failed']
        total_tasks = len(completed_tasks) + len(failed_tasks)
        
        metrics = {
            'Tasks Completed': len(completed_tasks),
            'Success Rate': f"{(len(completed_tasks)/max(total_tasks,1)*100):.1f}%",
            'Avg Steps': "N/A",  # Would need step tracking
            'Total Runtime': f"{sum(t.get('completed_at', 0) - t.get('created_at', 0) for t in completed_tasks):.1f}s",
            'Failures': len(failed_tasks)
        }
        
        for metric, value in metrics.items():
            if metric in self.agent_metrics_labels:
                self.agent_metrics_labels[metric].config(text=str(value))
    
    def _build_web_tab(self, parent):
        """Build Web Automation tab"""
        if not WEB_AVAILABLE:
            ttk.Label(parent, text="Web module not available", 
                     style='Error.TLabel').pack(pady=20)
            return
        
        # Create main container with scrollable frame
        canvas = tk.Canvas(parent, bg=self.colors['bg'])
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Dashboard.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Web automation status
        self._create_web_status(scrollable_frame)
        
        # Session management
        self._create_session_management(scrollable_frame)
        
        # Web metrics
        self._create_web_metrics(scrollable_frame)
        
        # Web controls
        self._create_web_controls(scrollable_frame)
    
    def _create_web_status(self, parent):
        """Create web automation status section"""
        status_frame = ttk.LabelFrame(parent, text="Web Automation Status", 
                                     style='Dashboard.TLabelframe')
        status_frame.pack(fill='x', padx=10, pady=5)
        
        # Status indicators
        indicators_frame = ttk.Frame(status_frame, style='Dashboard.TFrame')
        indicators_frame.pack(fill='x', padx=10, pady=5)
        
        # Web automation status
        ttk.Label(indicators_frame, text="Automation:", 
                 style='Dashboard.TLabel').grid(row=0, column=0, sticky='w', padx=(0, 5))
        self.web_status_label = ttk.Label(indicators_frame, text="Idle", 
                                         style='Success.TLabel')
        self.web_status_label.grid(row=0, column=1, sticky='w')
        
        # Active sessions
        ttk.Label(indicators_frame, text="Active Sessions:", 
                 style='Dashboard.TLabel').grid(row=0, column=2, sticky='w', padx=(20, 5))
        self.active_sessions_label = ttk.Label(indicators_frame, text="0", 
                                              style='Dashboard.TLabel')
        self.active_sessions_label.grid(row=0, column=3, sticky='w')
        
        # Templates loaded
        ttk.Label(indicators_frame, text="Templates:", 
                 style='Dashboard.TLabel').grid(row=1, column=0, sticky='w', padx=(0, 5))
        self.templates_label = ttk.Label(indicators_frame, text="0", 
                                        style='Dashboard.TLabel')
        self.templates_label.grid(row=1, column=1, sticky='w')
        
        # Browser status
        ttk.Label(indicators_frame, text="Browser:", 
                 style='Dashboard.TLabel').grid(row=1, column=2, sticky='w', padx=(20, 5))
        self.browser_status_label = ttk.Label(indicators_frame, text="Disconnected", 
                                             style='Error.TLabel')
        self.browser_status_label.grid(row=1, column=3, sticky='w')
    
    def _create_session_management(self, parent):
        """Create session management section"""
        session_frame = ttk.LabelFrame(parent, text="Session Management", 
                                      style='Dashboard.TLabelframe')
        session_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Session controls
        controls_frame = ttk.Frame(session_frame, style='Dashboard.TFrame')
        controls_frame.pack(fill='x', padx=10, pady=5)
        
        # Template selection
        ttk.Label(controls_frame, text="Template:", 
                 style='Dashboard.TLabel').grid(row=0, column=0, sticky='w', padx=(0, 5))
        self.template_var = tk.StringVar()
        self.template_combo = ttk.Combobox(controls_frame, textvariable=self.template_var, 
                                          state='readonly', width=20)
        self.template_combo.grid(row=0, column=1, sticky='w', padx=(0, 10))
        
        # Mode selection
        ttk.Label(controls_frame, text="Mode:", 
                 style='Dashboard.TLabel').grid(row=0, column=2, sticky='w', padx=(0, 5))
        self.mode_var = tk.StringVar(value="assistive")
        self.mode_combo = ttk.Combobox(controls_frame, textvariable=self.mode_var, 
                                      values=["assistive", "semi_auto", "full_auto"], 
                                      state='readonly', width=15)
        self.mode_combo.grid(row=0, column=3, sticky='w', padx=(0, 10))
        
        # Session buttons
        ttk.Button(controls_frame, text="Start Session", 
                  command=self._start_automation_session).grid(row=0, column=4, padx=5)
        ttk.Button(controls_frame, text="Stop Session", 
                  command=self._stop_automation_session).grid(row=0, column=5, padx=5)
        
        # Sessions list
        list_frame = ttk.Frame(session_frame, style='Dashboard.TFrame')
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Sessions treeview
        columns = ('Session ID', 'Template', 'Status', 'Progress', 'Start Time')
        self.sessions_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.sessions_tree.heading(col, text=col)
            self.sessions_tree.column(col, width=120)
        
        # Scrollbar for sessions
        sessions_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', 
                                          command=self.sessions_tree.yview)
        self.sessions_tree.configure(yscrollcommand=sessions_scrollbar.set)
        
        self.sessions_tree.pack(side='left', fill='both', expand=True)
        sessions_scrollbar.pack(side='right', fill='y')
        
        # Session management buttons
        session_buttons_frame = ttk.Frame(session_frame, style='Dashboard.TFrame')
        session_buttons_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(session_buttons_frame, text="View Details", 
                  command=self._view_session_details).pack(side='left', padx=5)
        ttk.Button(session_buttons_frame, text="Pause Session", 
                  command=self._pause_session).pack(side='left', padx=5)
        ttk.Button(session_buttons_frame, text="Resume Session", 
                  command=self._resume_session).pack(side='left', padx=5)
        ttk.Button(session_buttons_frame, text="Cancel Session", 
                  command=self._cancel_session).pack(side='left', padx=5)
    
    def _create_web_metrics(self, parent):
        """Create web automation metrics section"""
        metrics_frame = ttk.LabelFrame(parent, text="Automation Metrics", 
                                      style='Dashboard.TLabelframe')
        metrics_frame.pack(fill='x', padx=10, pady=5)
        
        # Metrics display
        self.web_metrics_text = tk.Text(metrics_frame, height=8, width=60, 
                                       bg=self.colors['bg'], fg=self.colors['text'], 
                                       font=('Consolas', 9), state='disabled')
        self.web_metrics_text.pack(padx=10, pady=5)
    
    def _create_web_controls(self, parent):
        """Create web automation controls section"""
        controls_frame = ttk.LabelFrame(parent, text="Automation Controls", 
                                       style='Dashboard.TLabelframe')
        controls_frame.pack(fill='x', padx=10, pady=5)
        
        # Control buttons
        buttons_frame = ttk.Frame(controls_frame, style='Dashboard.TFrame')
        buttons_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(buttons_frame, text="Initialize Browser", 
                  command=self._initialize_browser).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Load Templates", 
                  command=self._load_web_templates).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Refresh Sessions", 
                  command=self._refresh_sessions).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Clear History", 
                  command=self._clear_session_history).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Export Sessions", 
                  command=self._export_sessions).pack(side='left', padx=5)
    
    def _start_automation_session(self):
        """Start a new automation session"""
        try:
            template_name = self.template_var.get()
            mode = self.mode_var.get()
            
            if not template_name:
                messagebox.showwarning("Warning", "Please select a template")
                return
            
            if not self.web_automation:
                self._initialize_browser()
            
            # Create new session
            session_id = str(uuid.uuid4())[:8]
            session = AutomationSession(
                session_id=session_id,
                template_name=template_name,
                mode=AutomationMode(mode),
                status=AutomationStatus.PENDING,
                start_time=datetime.now()
            )
            
            self.automation_sessions[session_id] = session
            self._update_sessions_display()
            
            # Start session in background
            threading.Thread(target=self._run_automation_session, 
                           args=(session_id,), daemon=True).start()
            
        except Exception as e:
            logger.error(f"Error starting automation session: {e}")
            messagebox.showerror("Error", f"Failed to start session: {e}")
    
    def _stop_automation_session(self):
        """Stop the current automation session"""
        try:
            selected = self.sessions_tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Please select a session to stop")
                return
            
            session_id = self.sessions_tree.item(selected[0])['values'][0]
            if session_id in self.automation_sessions:
                session = self.automation_sessions[session_id]
                session.status = AutomationStatus.CANCELLED
                session.end_time = datetime.now()
                self._update_sessions_display()
            
        except Exception as e:
            logger.error(f"Error stopping automation session: {e}")
    
    def _run_automation_session(self, session_id):
        """Run automation session in background"""
        try:
            session = self.automation_sessions[session_id]
            session.status = AutomationStatus.RUNNING
            
            # Simulate automation execution
            for i in range(10):
                if session.status == AutomationStatus.CANCELLED:
                    break
                
                session.progress = (i + 1) * 10
                session.current_step = f"Step {i + 1}/10"
                time.sleep(1)
                
                # Update display
                self.root.after(0, self._update_sessions_display)
            
            if session.status != AutomationStatus.CANCELLED:
                session.status = AutomationStatus.COMPLETED
                session.end_time = datetime.now()
                
                # Update metrics
                self.web_metrics['total_sessions'] += 1
                self.web_metrics['completed_sessions'] += 1
                self.web_metrics['success_rate'] = (
                    self.web_metrics['completed_sessions'] / 
                    self.web_metrics['total_sessions'] * 100
                )
                self.web_metrics['last_session'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            self.root.after(0, self._update_sessions_display)
            
        except Exception as e:
            logger.error(f"Error running automation session: {e}")
            session.status = AutomationStatus.FAILED
            session.errors.append(str(e))
    
    def _update_sessions_display(self):
        """Update sessions display"""
        try:
            # Clear existing items
            for item in self.sessions_tree.get_children():
                self.sessions_tree.delete(item)
            
            # Add sessions
            for session in self.automation_sessions.values():
                self.sessions_tree.insert('', 'end', values=(
                    session.session_id,
                    session.template_name,
                    session.status.value,
                    f"{session.progress:.1f}%",
                    session.start_time.strftime('%H:%M:%S')
                ))
            
            # Update status labels
            active_count = sum(1 for s in self.automation_sessions.values() 
                             if s.status == AutomationStatus.RUNNING)
            self.active_sessions_label.config(text=str(active_count))
            
            if active_count > 0:
                self.web_status_label.config(text="Running", style='Success.TLabel')
            else:
                self.web_status_label.config(text="Idle", style='Dashboard.TLabel')
            
        except Exception as e:
            logger.error(f"Error updating sessions display: {e}")
    
    def _view_session_details(self):
        """View details of selected session"""
        try:
            selected = self.sessions_tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Please select a session")
                return
            
            session_id = self.sessions_tree.item(selected[0])['values'][0]
            session = self.automation_sessions.get(session_id)
            
            if session:
                details = f"""Session Details:

ID: {session.session_id}
Template: {session.template_name}
Mode: {session.mode.value}
Status: {session.status.value}
Progress: {session.progress:.1f}%
Current Step: {session.current_step}
Start Time: {session.start_time}
End Time: {session.end_time or 'N/A'}

Errors: {len(session.errors)}
Screenshots: {len(session.screenshots)}
Logs: {len(session.logs)}"""
                
                messagebox.showinfo("Session Details", details)
            
        except Exception as e:
            logger.error(f"Error viewing session details: {e}")
    
    def _pause_session(self):
        """Pause selected session"""
        try:
            selected = self.sessions_tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Please select a session")
                return
            
            session_id = self.sessions_tree.item(selected[0])['values'][0]
            if session_id in self.automation_sessions:
                session = self.automation_sessions[session_id]
                if session.status == AutomationStatus.RUNNING:
                    session.status = AutomationStatus.PAUSED
                    self._update_sessions_display()
            
        except Exception as e:
            logger.error(f"Error pausing session: {e}")
    
    def _resume_session(self):
        """Resume selected session"""
        try:
            selected = self.sessions_tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Please select a session")
                return
            
            session_id = self.sessions_tree.item(selected[0])['values'][0]
            if session_id in self.automation_sessions:
                session = self.automation_sessions[session_id]
                if session.status == AutomationStatus.PAUSED:
                    session.status = AutomationStatus.RUNNING
                    self._update_sessions_display()
            
        except Exception as e:
            logger.error(f"Error resuming session: {e}")
    
    def _cancel_session(self):
        """Cancel selected session"""
        try:
            selected = self.sessions_tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Please select a session")
                return
            
            session_id = self.sessions_tree.item(selected[0])['values'][0]
            if session_id in self.automation_sessions:
                session = self.automation_sessions[session_id]
                session.status = AutomationStatus.CANCELLED
                session.end_time = datetime.now()
                self._update_sessions_display()
            
        except Exception as e:
            logger.error(f"Error cancelling session: {e}")
    
    def _initialize_browser(self):
        """Initialize web automation browser"""
        try:
            if WEB_AVAILABLE:
                config = RPAConfig(headless=False)
                self.web_automation = WebFormAutomation(config)
                self.browser_status_label.config(text="Connected", style='Success.TLabel')
                self._load_web_templates()
            
        except Exception as e:
            logger.error(f"Error initializing browser: {e}")
            self.browser_status_label.config(text="Error", style='Error.TLabel')
            messagebox.showerror("Error", f"Failed to initialize browser: {e}")
    
    def _load_web_templates(self):
        """Load web automation templates"""
        try:
            if self.web_automation:
                self.web_templates = self.web_automation.templates
                template_names = list(self.web_templates.keys())
                self.template_combo['values'] = template_names
                self.templates_label.config(text=str(len(template_names)))
            
        except Exception as e:
            logger.error(f"Error loading templates: {e}")
    
    def _refresh_sessions(self):
        """Refresh sessions display"""
        self._update_sessions_display()
    
    def _clear_session_history(self):
        """Clear session history"""
        try:
            # Keep only running sessions
            active_sessions = {
                sid: session for sid, session in self.automation_sessions.items()
                if session.status in [AutomationStatus.RUNNING, AutomationStatus.PAUSED]
            }
            self.automation_sessions = active_sessions
            self._update_sessions_display()
            
        except Exception as e:
            logger.error(f"Error clearing session history: {e}")
    
    def _export_sessions(self):
        """Export session data"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Export Sessions"
            )
            
            if filename:
                sessions_data = {
                    sid: {
                        'session_id': session.session_id,
                        'template_name': session.template_name,
                        'mode': session.mode.value,
                        'status': session.status.value,
                        'start_time': session.start_time.isoformat(),
                        'end_time': session.end_time.isoformat() if session.end_time else None,
                        'progress': session.progress,
                        'current_step': session.current_step,
                        'errors': session.errors,
                        'logs': session.logs
                    }
                    for sid, session in self.automation_sessions.items()
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(sessions_data, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Success", f"Sessions exported to {filename}")
            
        except Exception as e:
            logger.error(f"Error exporting sessions: {e}")
            messagebox.showerror("Error", f"Failed to export sessions: {e}")
    
    def _update_web_metrics_display(self):
        """Update web automation metrics display"""
        if not WEB_AVAILABLE or not hasattr(self, 'web_metrics_text'):
            return
            
        try:
            metrics_text = f"""Web Automation Metrics:

Total Sessions: {self.web_metrics.get('total_sessions', 0)}
Completed: {self.web_metrics.get('completed_sessions', 0)}
Failed: {self.web_metrics.get('failed_sessions', 0)}
Success Rate: {self.web_metrics.get('success_rate', 0.0):.1f}%
Avg Session Time: {self.web_metrics.get('avg_session_time', 0.0):.2f}s
Last Session: {self.web_metrics.get('last_session', 'Never')}

Active Sessions: {len([s for s in self.automation_sessions.values() if s.status == AutomationStatus.RUNNING])}
Templates Loaded: {len(self.web_templates)}
Browser Status: {'Connected' if self.web_automation else 'Disconnected'}"""
            
            self.web_metrics_text.config(state='normal')
            self.web_metrics_text.delete(1.0, tk.END)
            self.web_metrics_text.insert(1.0, metrics_text)
            self.web_metrics_text.config(state='disabled')
            
        except Exception as e:
            logger.error(f"Error updating web metrics display: {e}")
    
    def shutdown(self):
        """Shutdown dashboard"""
        logger.info("Shutting down Jarvis Dashboard")
        
        self.stop_updates()
        
        if self.on_shutdown:
            self.on_shutdown()
        
        self.root.quit()
        self.root.destroy()

# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create and run dashboard
    dashboard = JarvisDashboard()
    
    # Add some sample data
    import random
    
    def add_sample_data():
        metrics = DashboardMetrics(
            cpu_usage=random.uniform(10, 80),
            memory_usage=random.uniform(20, 70),
            voice_commands=random.randint(0, 10),
            tasks_completed=random.randint(0, 5),
            response_time=random.uniform(0.1, 2.0)
        )
        dashboard.add_metrics(metrics)
        
        # Schedule next update
        dashboard.root.after(2000, add_sample_data)
    
    # Start sample data
    dashboard.root.after(1000, add_sample_data)
    
    # Add sample log entries
    dashboard.add_log_entry("INFO", "dashboard", "Dashboard started")
    dashboard.add_log_entry("INFO", "voice", "Voice interface initialized")
    
    # Run dashboard
    dashboard.run()