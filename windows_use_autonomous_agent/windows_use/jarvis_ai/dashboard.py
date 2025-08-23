"""Dashboard Module

Provides an intuitive graphical user interface for the Jarvis AI system,
including real-time monitoring, configuration, and interaction capabilities.
"""

import asyncio
import json
import logging
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Tuple
from datetime import datetime, timedelta

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from pydantic import BaseModel

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
                
                time.sleep(self.config.refresh_interval)
                
            except Exception as e:
                logger.error(f"Dashboard update error: {e}")
                time.sleep(1.0)
    
    def _update_metrics_display(self):
        """Update metrics chart"""
        if self.metrics_chart and self.metrics_history:
            latest_metrics = self.metrics_history[-1]
            self.metrics_chart.add_metrics(latest_metrics)
    
    def _update_status_indicators(self):
        """Update status indicator colors"""
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
    
    def _update_summary_stats(self):
        """Update summary statistics"""
        if self.metrics_history:
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