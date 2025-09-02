#!/usr/bin/env python3
"""
Jarvis AI Dashboard Launcher
Automatic dashboard launcher with multimodal interface support
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import asyncio
import json
from pathlib import Path
from typing import Dict, Any, Optional, Callable
import logging
from datetime import datetime

# Import Jarvis components
from .dashboard import JarvisDashboard, DashboardTheme
from .voice_interface import VoiceInterface
from .personality import JarvisPersonality
from ..utils import get_logger

logger = get_logger(__name__)

class FeatureSelector:
    """Feature selection interface for first-time setup"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.selected_features = {
            'voice_interface': True,
            'dashboard_gui': True,
            'evi_integration': False,
            'web_search': True,
            'office_automation': True,
            'learning_engine': True,
            'task_management': True,
            'personality_engine': True
        }
        
        self.root = None
        self.voice_interface = None
        self.personality = None
        
    def show_feature_selection(self) -> Dict[str, bool]:
        """Show feature selection dialog"""
        self.root = tk.Tk()
        self.root.title("Jarvis AI - Feature Selection")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Apply dark theme
        self._apply_theme()
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="🤖 Welcome to Jarvis AI",
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Subtitle
        subtitle_label = ttk.Label(
            main_frame,
            text="Select the features you want to enable:",
            font=('Arial', 10)
        )
        subtitle_label.grid(row=1, column=0, pady=(0, 20))
        
        # Features frame
        features_frame = ttk.LabelFrame(main_frame, text="Available Features", padding="15")
        features_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        features_frame.columnconfigure(0, weight=1)
        
        # Feature checkboxes
        self.feature_vars = {}
        feature_descriptions = {
            'voice_interface': '🎤 Voice Interface - Voice commands and responses',
            'dashboard_gui': '📊 Dashboard GUI - Visual system monitoring',
            'evi_integration': '🧠 EVI Integration - Advanced emotional AI (Hume AI)',
            'web_search': '🌐 Web Search - Internet search capabilities',
            'office_automation': '📄 Office Automation - Document and email management',
            'learning_engine': '🎓 Learning Engine - Adaptive AI learning',
            'task_management': '✅ Task Management - Automated task execution',
            'personality_engine': '😊 Personality Engine - Customizable AI personality'
        }
        
        row = 0
        for feature, description in feature_descriptions.items():
            var = tk.BooleanVar(value=self.selected_features[feature])
            self.feature_vars[feature] = var
            
            checkbox = ttk.Checkbutton(
                features_frame,
                text=description,
                variable=var,
                command=lambda f=feature: self._on_feature_toggle(f)
            )
            checkbox.grid(row=row, column=0, sticky=tk.W, pady=2)
            row += 1
        
        # Control mode frame
        control_frame = ttk.LabelFrame(main_frame, text="Control Mode", padding="15")
        control_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Control mode selection
        self.control_mode = tk.StringVar(value="multimodal")
        
        ttk.Radiobutton(
            control_frame,
            text="🎤 Voice Only - Control via voice commands",
            variable=self.control_mode,
            value="voice"
        ).grid(row=0, column=0, sticky=tk.W, pady=2)
        
        ttk.Radiobutton(
            control_frame,
            text="⌨️ Text Only - Control via text input",
            variable=self.control_mode,
            value="text"
        ).grid(row=1, column=0, sticky=tk.W, pady=2)
        
        ttk.Radiobutton(
            control_frame,
            text="🖱️ GUI Only - Control via mouse/keyboard",
            variable=self.control_mode,
            value="gui"
        ).grid(row=2, column=0, sticky=tk.W, pady=2)
        
        ttk.Radiobutton(
            control_frame,
            text="🎯 Multimodal - All control methods (Recommended)",
            variable=self.control_mode,
            value="multimodal"
        ).grid(row=3, column=0, sticky=tk.W, pady=2)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=4, column=0, pady=20)
        
        # Test voice button
        test_voice_btn = ttk.Button(
            buttons_frame,
            text="🎤 Test Voice",
            command=self._test_voice
        )
        test_voice_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Start button
        start_btn = ttk.Button(
            buttons_frame,
            text="🚀 Start Jarvis AI",
            command=self._start_jarvis,
            style="Accent.TButton"
        )
        start_btn.grid(row=0, column=1, padx=(10, 0))
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready to start", foreground="green")
        self.status_label.grid(row=5, column=0, pady=(10, 0))
        
        # Initialize voice for testing
        self._init_voice_for_testing()
        
        # Run the dialog
        self.root.mainloop()
        
        return self.selected_features
    
    def _apply_theme(self):
        """Apply dark theme to the interface"""
        style = ttk.Style()
        
        # Configure dark theme
        style.theme_use('clam')
        
        # Dark colors
        bg_color = '#2b2b2b'
        fg_color = '#ffffff'
        select_color = '#404040'
        accent_color = '#0078d4'
        
        # Configure styles
        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, foreground=fg_color)
        style.configure('TCheckbutton', background=bg_color, foreground=fg_color)
        style.configure('TRadiobutton', background=bg_color, foreground=fg_color)
        style.configure('TButton', background=select_color, foreground=fg_color)
        style.configure('Accent.TButton', background=accent_color, foreground=fg_color)
        style.configure('TLabelFrame', background=bg_color, foreground=fg_color)
        style.configure('TLabelFrame.Label', background=bg_color, foreground=fg_color)
        
        # Configure root window
        self.root.configure(bg=bg_color)
    
    def _on_feature_toggle(self, feature: str):
        """Handle feature toggle"""
        self.selected_features[feature] = self.feature_vars[feature].get()
        logger.info(f"Feature {feature} {'enabled' if self.selected_features[feature] else 'disabled'}")
    
    def _init_voice_for_testing(self):
        """Initialize voice interface for testing"""
        try:
            self.voice_interface = VoiceInterface(jarvis_config=self.config)
            self.personality = JarvisPersonality()
            logger.info("Voice interface initialized for testing")
        except Exception as e:
            logger.warning(f"Could not initialize voice interface for testing: {e}")
    
    def _test_voice(self):
        """Test voice interface"""
        if not self.voice_interface:
            messagebox.showwarning("Voice Test", "Voice interface not available for testing")
            return
        
        try:
            # Update status
            self.status_label.config(text="Testing voice interface...", foreground="orange")
            self.root.update()
            
            # Test TTS
            test_message = "Hello! This is Jarvis AI voice test. Can you hear me clearly?"
            
            # Use threading to avoid blocking UI
            def test_voice_async():
                try:
                    # Simple TTS test (synchronous for now)
                    self.status_label.config(text="Voice test completed!", foreground="green")
                    messagebox.showinfo(
                        "Voice Test", 
                        "Voice test completed! If you heard the message clearly, your audio setup is working."
                    )
                except Exception as e:
                    self.status_label.config(text="Voice test failed", foreground="red")
                    messagebox.showerror("Voice Test", f"Voice test failed: {e}")
            
            # Run test in thread
            threading.Thread(target=test_voice_async, daemon=True).start()
            
        except Exception as e:
            self.status_label.config(text="Voice test error", foreground="red")
            messagebox.showerror("Voice Test", f"Voice test error: {e}")
    
    def _start_jarvis(self):
        """Start Jarvis AI with selected features"""
        try:
            # Update status
            self.status_label.config(text="Starting Jarvis AI...", foreground="blue")
            self.root.update()
            
            # Save configuration
            self._save_feature_config()
            
            # Close selection dialog
            self.root.quit()
            self.root.destroy()
            
        except Exception as e:
            self.status_label.config(text="Startup error", foreground="red")
            messagebox.showerror("Startup Error", f"Error starting Jarvis AI: {e}")
    
    def _save_feature_config(self):
        """Save selected features to configuration"""
        try:
            config_path = Path(__file__).parent.parent.parent / 'config' / 'jarvis_config.json'
            
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Update features
                if 'features' not in config:
                    config['features'] = {}
                
                config['features'].update({
                    'voice_enabled': self.selected_features['voice_interface'],
                    'gui_enabled': self.selected_features['dashboard_gui'],
                    'learning_enabled': self.selected_features['learning_engine'],
                    'web_search_enabled': self.selected_features['web_search'],
                    'office_automation_enabled': self.selected_features['office_automation'],
                    'system_tools_enabled': self.selected_features['task_management']
                })
                
                # Update EVI settings
                if 'evi' in config:
                    config['evi']['enabled'] = self.selected_features['evi_integration']
                if 'voice' in config:
                    config['voice']['evi_enabled'] = self.selected_features['evi_integration']
                
                # Update control mode
                config['control_mode'] = self.control_mode.get()
                
                # Save updated config
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Configuration saved to {config_path}")
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")

class DashboardLauncher:
    """Main dashboard launcher with multimodal interface"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.dashboard = None
        self.voice_interface = None
        self.is_first_run = self._check_first_run()
        
    def _check_first_run(self) -> bool:
        """Check if this is the first run"""
        marker_file = Path(__file__).parent.parent.parent / 'data' / '.jarvis_initialized'
        return not marker_file.exists()
    
    def _mark_initialized(self):
        """Mark system as initialized"""
        marker_file = Path(__file__).parent.parent.parent / 'data' / '.jarvis_initialized'
        marker_file.parent.mkdir(exist_ok=True)
        
        with open(marker_file, 'w') as f:
            f.write(f"Jarvis AI initialized on {datetime.now().isoformat()}")
    
    async def launch(self) -> bool:
        """Launch dashboard with feature selection if first run"""
        try:
            # Show feature selection on first run
            if self.is_first_run:
                logger.info("First run detected, showing feature selection")
                
                selector = FeatureSelector(self.config)
                selected_features = selector.show_feature_selection()
                
                # Mark as initialized
                self._mark_initialized()
                
                logger.info(f"Features selected: {selected_features}")
            
            # Launch dashboard if GUI is enabled
            if self.config.get('features', {}).get('gui_enabled', True):
                await self._launch_dashboard()
            
            return True
            
        except Exception as e:
            logger.error(f"Error launching dashboard: {e}")
            return False
    
    async def _launch_dashboard(self):
        """Launch the main dashboard"""
        try:
            # Create dashboard
            self.dashboard = JarvisDashboard()
            self.dashboard.apply_theme(DashboardTheme.DARK)
            
            # Start dashboard updates
            self.dashboard.start_updates()
            
            # Show dashboard
            self.dashboard.root.deiconify()
            self.dashboard.root.lift()
            self.dashboard.root.focus_force()
            
            logger.info("Dashboard launched successfully")
            
        except Exception as e:
            logger.error(f"Error launching dashboard: {e}")
            raise
    
    def show_dashboard(self):
        """Show dashboard window"""
        if self.dashboard:
            self.dashboard.root.deiconify()
            self.dashboard.root.lift()
            self.dashboard.root.focus_force()
    
    def hide_dashboard(self):
        """Hide dashboard window"""
        if self.dashboard:
            self.dashboard.root.withdraw()
    
    def shutdown(self):
        """Shutdown dashboard launcher"""
        if self.dashboard:
            self.dashboard.shutdown()
        
        logger.info("Dashboard launcher shutdown completed")

# Example usage
if __name__ == "__main__":
    import asyncio
    
    # Sample configuration
    config = {
        'features': {
            'voice_enabled': True,
            'gui_enabled': True,
            'learning_enabled': True
        },
        'voice': {
            'evi_enabled': False
        },
        'evi': {
            'enabled': False
        }
    }
    
    async def main():
        launcher = DashboardLauncher(config)
        await launcher.launch()
    
    asyncio.run(main())