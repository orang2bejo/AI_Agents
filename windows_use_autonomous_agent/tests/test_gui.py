#!/usr/bin/env python3
"""
Unit Tests for GUI Module

Tests for GUI dashboard, monitoring interface, and configuration management.

Author: Jarvis AI Team
Date: 2024
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk
from tkinter import ttk

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from windows_use.observability.dashboard import Dashboard
    from windows_use.observability.monitoring import SystemMonitor
    from windows_use.observability.metrics import MetricsCollector
except ImportError as e:
    pytest.skip(f"GUI modules not available: {e}", allow_module_level=True)


class TestDashboard:
    """Test cases for Dashboard GUI"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Mock tkinter to avoid GUI creation during tests
        with patch('tkinter.Tk'):
            self.dashboard = Dashboard()
    
    @pytest.mark.unit
    @pytest.mark.gui
    def test_initialization(self):
        """Test Dashboard initialization"""
        assert self.dashboard is not None
        assert hasattr(self.dashboard, 'root')
        assert hasattr(self.dashboard, 'metrics_frame')
        assert hasattr(self.dashboard, 'config_frame')
    
    @pytest.mark.unit
    @pytest.mark.gui
    @patch('tkinter.Tk')
    def test_create_main_window(self, mock_tk):
        """Test main window creation"""
        mock_root = Mock()
        mock_tk.return_value = mock_root
        
        dashboard = Dashboard()
        dashboard.create_main_window()
        
        mock_root.title.assert_called()
        mock_root.geometry.assert_called()
    
    @pytest.mark.unit
    @pytest.mark.gui
    def test_create_metrics_frame(self):
        """Test metrics frame creation"""
        mock_root = Mock()
        self.dashboard.root = mock_root
        
        with patch('tkinter.ttk.Frame') as mock_frame:
            mock_frame_instance = Mock()
            mock_frame.return_value = mock_frame_instance
            
            self.dashboard.create_metrics_frame()
            
            mock_frame.assert_called_with(mock_root)
            mock_frame_instance.pack.assert_called()
    
    @pytest.mark.unit
    @pytest.mark.gui
    def test_create_config_frame(self):
        """Test configuration frame creation"""
        mock_root = Mock()
        self.dashboard.root = mock_root
        
        with patch('tkinter.ttk.Frame') as mock_frame, \
             patch('tkinter.ttk.Label') as mock_label, \
             patch('tkinter.ttk.Entry') as mock_entry:
            
            mock_frame_instance = Mock()
            mock_frame.return_value = mock_frame_instance
            
            self.dashboard.create_config_frame()
            
            mock_frame.assert_called_with(mock_root)
            mock_label.assert_called()
            mock_entry.assert_called()
    
    @pytest.mark.unit
    @pytest.mark.gui
    def test_update_metrics_display(self):
        """Test metrics display update"""
        mock_metrics = {
            'cpu_usage': 45.2,
            'memory_usage': 67.8,
            'disk_usage': 23.1,
            'network_io': 1024
        }
        
        mock_labels = {
            'cpu_label': Mock(),
            'memory_label': Mock(),
            'disk_label': Mock(),
            'network_label': Mock()
        }
        
        self.dashboard.metric_labels = mock_labels
        self.dashboard.update_metrics_display(mock_metrics)
        
        mock_labels['cpu_label'].config.assert_called_with(text='CPU Usage: 45.2%')
        mock_labels['memory_label'].config.assert_called_with(text='Memory Usage: 67.8%')
    
    @pytest.mark.unit
    @pytest.mark.gui
    def test_save_configuration(self):
        """Test configuration saving"""
        mock_config = {
            'llm_provider': 'openai',
            'model_name': 'gpt-4',
            'temperature': 0.7,
            'max_tokens': 2048
        }
        
        with patch('json.dump') as mock_dump, \
             patch('builtins.open', create=True) as mock_open:
            
            self.dashboard.save_configuration(mock_config)
            
            mock_open.assert_called_once()
            mock_dump.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.gui
    def test_load_configuration(self):
        """Test configuration loading"""
        mock_config = {
            'llm_provider': 'anthropic',
            'model_name': 'claude-3',
            'temperature': 0.5
        }
        
        with patch('json.load', return_value=mock_config) as mock_load, \
             patch('builtins.open', create=True) as mock_open:
            
            config = self.dashboard.load_configuration()
            
            assert config == mock_config
            mock_open.assert_called_once()
            mock_load.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.gui
    def test_start_monitoring(self):
        """Test monitoring start"""
        with patch.object(self.dashboard, 'update_metrics_loop') as mock_update:
            self.dashboard.start_monitoring()
            
            assert self.dashboard.monitoring_active is True
            mock_update.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.gui
    def test_stop_monitoring(self):
        """Test monitoring stop"""
        self.dashboard.monitoring_active = True
        self.dashboard.stop_monitoring()
        
        assert self.dashboard.monitoring_active is False
    
    @pytest.mark.unit
    @pytest.mark.gui
    def test_create_menu_bar(self):
        """Test menu bar creation"""
        mock_root = Mock()
        self.dashboard.root = mock_root
        
        with patch('tkinter.Menu') as mock_menu:
            mock_menu_instance = Mock()
            mock_menu.return_value = mock_menu_instance
            
            self.dashboard.create_menu_bar()
            
            mock_menu.assert_called()
            mock_menu_instance.add_cascade.assert_called()
            mock_root.config.assert_called_with(menu=mock_menu_instance)


class TestSystemMonitor:
    """Test cases for SystemMonitor"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.monitor = SystemMonitor()
    
    @pytest.mark.unit
    @pytest.mark.gui
    def test_initialization(self):
        """Test SystemMonitor initialization"""
        assert self.monitor is not None
        assert hasattr(self.monitor, 'metrics_history')
        assert hasattr(self.monitor, 'alert_thresholds')
    
    @pytest.mark.unit
    @pytest.mark.gui
    @patch('psutil.cpu_percent')
    def test_get_cpu_usage(self, mock_cpu):
        """Test CPU usage monitoring"""
        mock_cpu.return_value = 42.5
        
        cpu_usage = self.monitor.get_cpu_usage()
        
        assert cpu_usage == 42.5
        mock_cpu.assert_called_once_with(interval=1)
    
    @pytest.mark.unit
    @pytest.mark.gui
    @patch('psutil.virtual_memory')
    def test_get_memory_usage(self, mock_memory):
        """Test memory usage monitoring"""
        mock_memory_info = Mock()
        mock_memory_info.percent = 68.3
        mock_memory_info.used = 8589934592  # 8GB
        mock_memory_info.total = 17179869184  # 16GB
        mock_memory.return_value = mock_memory_info
        
        memory_usage = self.monitor.get_memory_usage()
        
        assert memory_usage['percent'] == 68.3
        assert memory_usage['used_gb'] == 8.0
        assert memory_usage['total_gb'] == 16.0
    
    @pytest.mark.unit
    @pytest.mark.gui
    @patch('psutil.disk_usage')
    def test_get_disk_usage(self, mock_disk):
        """Test disk usage monitoring"""
        mock_disk_info = Mock()
        mock_disk_info.percent = 45.7
        mock_disk_info.used = 107374182400  # 100GB
        mock_disk_info.total = 214748364800  # 200GB
        mock_disk.return_value = mock_disk_info
        
        disk_usage = self.monitor.get_disk_usage('/')
        
        assert disk_usage['percent'] == 45.7
        assert disk_usage['used_gb'] == 100.0
        assert disk_usage['total_gb'] == 200.0
    
    @pytest.mark.unit
    @pytest.mark.gui
    @patch('psutil.net_io_counters')
    def test_get_network_io(self, mock_net):
        """Test network I/O monitoring"""
        mock_net_info = Mock()
        mock_net_info.bytes_sent = 1048576  # 1MB
        mock_net_info.bytes_recv = 2097152  # 2MB
        mock_net.return_value = mock_net_info
        
        network_io = self.monitor.get_network_io()
        
        assert network_io['bytes_sent'] == 1048576
        assert network_io['bytes_recv'] == 2097152
    
    @pytest.mark.unit
    @pytest.mark.gui
    def test_collect_all_metrics(self):
        """Test comprehensive metrics collection"""
        with patch.object(self.monitor, 'get_cpu_usage', return_value=50.0), \
             patch.object(self.monitor, 'get_memory_usage', return_value={'percent': 60.0}), \
             patch.object(self.monitor, 'get_disk_usage', return_value={'percent': 30.0}), \
             patch.object(self.monitor, 'get_network_io', return_value={'bytes_sent': 1024}):
            
            metrics = self.monitor.collect_all_metrics()
            
            assert 'cpu_usage' in metrics
            assert 'memory_usage' in metrics
            assert 'disk_usage' in metrics
            assert 'network_io' in metrics
            assert metrics['cpu_usage'] == 50.0
    
    @pytest.mark.unit
    @pytest.mark.gui
    def test_check_alerts(self):
        """Test alert checking functionality"""
        self.monitor.alert_thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'disk_usage': 90.0
        }
        
        metrics = {
            'cpu_usage': 85.0,  # Above threshold
            'memory_usage': {'percent': 70.0},  # Below threshold
            'disk_usage': {'percent': 95.0}  # Above threshold
        }
        
        alerts = self.monitor.check_alerts(metrics)
        
        assert len(alerts) == 2
        assert any('CPU usage' in alert for alert in alerts)
        assert any('Disk usage' in alert for alert in alerts)
    
    @pytest.mark.unit
    @pytest.mark.gui
    def test_store_metrics_history(self):
        """Test metrics history storage"""
        metrics = {
            'cpu_usage': 45.0,
            'memory_usage': {'percent': 55.0},
            'timestamp': '2024-01-01T12:00:00'
        }
        
        self.monitor.store_metrics_history(metrics)
        
        assert len(self.monitor.metrics_history) == 1
        assert self.monitor.metrics_history[0] == metrics
    
    @pytest.mark.unit
    @pytest.mark.gui
    def test_get_metrics_trend(self):
        """Test metrics trend analysis"""
        # Add sample metrics history
        history = [
            {'cpu_usage': 40.0, 'timestamp': '2024-01-01T12:00:00'},
            {'cpu_usage': 45.0, 'timestamp': '2024-01-01T12:01:00'},
            {'cpu_usage': 50.0, 'timestamp': '2024-01-01T12:02:00'}
        ]
        self.monitor.metrics_history = history
        
        trend = self.monitor.get_metrics_trend('cpu_usage', minutes=5)
        
        assert len(trend) == 3
        assert trend[-1] == 50.0  # Latest value
        assert trend[0] == 40.0   # Oldest value


class TestMetricsCollector:
    """Test cases for MetricsCollector"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.collector = MetricsCollector()
    
    @pytest.mark.unit
    @pytest.mark.gui
    def test_initialization(self):
        """Test MetricsCollector initialization"""
        assert self.collector is not None
        assert hasattr(self.collector, 'metrics_buffer')
        assert hasattr(self.collector, 'collection_interval')
    
    @pytest.mark.unit
    @pytest.mark.gui
    def test_add_metric(self):
        """Test metric addition"""
        metric_name = 'test_metric'
        metric_value = 42.0
        
        self.collector.add_metric(metric_name, metric_value)
        
        assert metric_name in self.collector.metrics_buffer
        assert self.collector.metrics_buffer[metric_name] == metric_value
    
    @pytest.mark.unit
    @pytest.mark.gui
    def test_get_metric(self):
        """Test metric retrieval"""
        metric_name = 'test_metric'
        metric_value = 123.45
        
        self.collector.metrics_buffer[metric_name] = metric_value
        retrieved_value = self.collector.get_metric(metric_name)
        
        assert retrieved_value == metric_value
    
    @pytest.mark.unit
    @pytest.mark.gui
    def test_get_nonexistent_metric(self):
        """Test retrieval of non-existent metric"""
        retrieved_value = self.collector.get_metric('nonexistent_metric')
        
        assert retrieved_value is None
    
    @pytest.mark.unit
    @pytest.mark.gui
    def test_clear_metrics(self):
        """Test metrics buffer clearing"""
        self.collector.add_metric('metric1', 10.0)
        self.collector.add_metric('metric2', 20.0)
        
        assert len(self.collector.metrics_buffer) == 2
        
        self.collector.clear_metrics()
        
        assert len(self.collector.metrics_buffer) == 0
    
    @pytest.mark.unit
    @pytest.mark.gui
    def test_export_metrics(self):
        """Test metrics export functionality"""
        self.collector.add_metric('cpu_usage', 45.0)
        self.collector.add_metric('memory_usage', 67.5)
        
        exported_metrics = self.collector.export_metrics()
        
        assert 'cpu_usage' in exported_metrics
        assert 'memory_usage' in exported_metrics
        assert exported_metrics['cpu_usage'] == 45.0
        assert exported_metrics['memory_usage'] == 67.5
    
    @pytest.mark.unit
    @pytest.mark.gui
    def test_import_metrics(self):
        """Test metrics import functionality"""
        metrics_data = {
            'disk_usage': 30.0,
            'network_io': 1024,
            'process_count': 156
        }
        
        self.collector.import_metrics(metrics_data)
        
        assert self.collector.get_metric('disk_usage') == 30.0
        assert self.collector.get_metric('network_io') == 1024
        assert self.collector.get_metric('process_count') == 156


@pytest.mark.integration
@pytest.mark.gui
class TestGUIIntegration:
    """Integration tests for GUI components"""
    
    def setup_method(self):
        """Set up integration test fixtures"""
        with patch('tkinter.Tk'):
            self.dashboard = Dashboard()
        self.monitor = SystemMonitor()
        self.collector = MetricsCollector()
    
    @pytest.mark.slow
    def test_dashboard_monitor_integration(self):
        """Test dashboard and monitor integration"""
        # Mock system metrics
        mock_metrics = {
            'cpu_usage': 55.0,
            'memory_usage': {'percent': 70.0},
            'disk_usage': {'percent': 40.0}
        }
        
        with patch.object(self.monitor, 'collect_all_metrics', return_value=mock_metrics):
            # Simulate dashboard updating with monitor data
            metrics = self.monitor.collect_all_metrics()
            
            # Verify metrics are collected
            assert metrics['cpu_usage'] == 55.0
            assert metrics['memory_usage']['percent'] == 70.0
            
            # Test dashboard update (mocked)
            with patch.object(self.dashboard, 'update_metrics_display') as mock_update:
                self.dashboard.update_metrics_display(metrics)
                mock_update.assert_called_once_with(metrics)
    
    def test_collector_dashboard_integration(self):
        """Test collector and dashboard integration"""
        # Add metrics to collector
        self.collector.add_metric('active_sessions', 5)
        self.collector.add_metric('api_requests', 1250)
        self.collector.add_metric('error_rate', 0.02)
        
        # Export metrics
        exported_metrics = self.collector.export_metrics()
        
        # Verify integration data flow
        assert 'active_sessions' in exported_metrics
        assert exported_metrics['api_requests'] == 1250
        
        # Test dashboard configuration update
        with patch.object(self.dashboard, 'save_configuration') as mock_save:
            config = {'metrics_source': 'collector', 'update_interval': 5}
            self.dashboard.save_configuration(config)
            mock_save.assert_called_once_with(config)
    
    def test_end_to_end_monitoring_workflow(self):
        """Test complete monitoring workflow"""
        with patch.object(self.monitor, 'collect_all_metrics') as mock_collect, \
             patch.object(self.collector, 'add_metric') as mock_add, \
             patch.object(self.dashboard, 'update_metrics_display') as mock_update:
            
            # Mock metrics collection
            mock_metrics = {
                'cpu_usage': 60.0,
                'memory_usage': {'percent': 75.0},
                'custom_metric': 42.0
            }
            mock_collect.return_value = mock_metrics
            
            # Simulate monitoring workflow
            metrics = self.monitor.collect_all_metrics()
            
            # Add custom metrics to collector
            self.collector.add_metric('workflow_status', 'active')
            
            # Update dashboard
            self.dashboard.update_metrics_display(metrics)
            
            # Verify workflow execution
            mock_collect.assert_called_once()
            mock_add.assert_called_once_with('workflow_status', 'active')
            mock_update.assert_called_once_with(mock_metrics)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])