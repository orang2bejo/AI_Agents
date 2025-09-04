"""Device Telemetry Module

Provides comprehensive system monitoring including CPU, GPU, memory, and disk metrics.
Supports both NVIDIA and AMD GPUs with fallback to basic system metrics.
"""

import logging
import time
import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

try:
    import psutil
except ImportError:
    psutil = None
    logging.warning("psutil not available. System metrics will be limited.")

try:
    import GPUtil
except ImportError:
    GPUtil = None
    logging.warning("GPUtil not available. GPU metrics will be limited.")

try:
    import pynvml
except ImportError:
    pynvml = None
    logging.warning("pynvml not available. NVIDIA GPU metrics will be limited.")


@dataclass
class SystemMetrics:
    """System-wide metrics data structure."""
    timestamp: datetime = field(default_factory=datetime.now)
    cpu_percent: float = 0.0
    cpu_count: int = 0
    cpu_freq: Optional[float] = None
    memory_total: int = 0
    memory_available: int = 0
    memory_percent: float = 0.0
    disk_total: int = 0
    disk_used: int = 0
    disk_percent: float = 0.0
    network_sent: int = 0
    network_recv: int = 0
    boot_time: Optional[datetime] = None
    load_average: Optional[List[float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary format."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'cpu_percent': self.cpu_percent,
            'cpu_count': self.cpu_count,
            'cpu_freq': self.cpu_freq,
            'memory_total': self.memory_total,
            'memory_available': self.memory_available,
            'memory_percent': self.memory_percent,
            'disk_total': self.disk_total,
            'disk_used': self.disk_used,
            'disk_percent': self.disk_percent,
            'network_sent': self.network_sent,
            'network_recv': self.network_recv,
            'boot_time': self.boot_time.isoformat() if self.boot_time else None,
            'load_average': self.load_average
        }


@dataclass
class GPUMetrics:
    """GPU metrics data structure."""
    timestamp: datetime = field(default_factory=datetime.now)
    gpu_id: int = 0
    name: str = ""
    driver_version: str = ""
    memory_total: int = 0
    memory_used: int = 0
    memory_percent: float = 0.0
    gpu_percent: float = 0.0
    temperature: Optional[float] = None
    power_draw: Optional[float] = None
    power_limit: Optional[float] = None
    fan_speed: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert GPU metrics to dictionary format."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'gpu_id': self.gpu_id,
            'name': self.name,
            'driver_version': self.driver_version,
            'memory_total': self.memory_total,
            'memory_used': self.memory_used,
            'memory_percent': self.memory_percent,
            'gpu_percent': self.gpu_percent,
            'temperature': self.temperature,
            'power_draw': self.power_draw,
            'power_limit': self.power_limit,
            'fan_speed': self.fan_speed
        }


class DeviceTelemetry:
    """Main telemetry collection class."""
    
    def __init__(self, 
                 collection_interval: float = 5.0,
                 max_history_size: int = 1000,
                 enable_gpu_monitoring: bool = True,
                 log_file: Optional[Path] = None):
        """Initialize device telemetry.
        
        Args:
            collection_interval: Seconds between metric collections
            max_history_size: Maximum number of metric records to keep
            enable_gpu_monitoring: Whether to collect GPU metrics
            log_file: Optional file to log metrics to
        """
        self.collection_interval = collection_interval
        self.max_history_size = max_history_size
        self.enable_gpu_monitoring = enable_gpu_monitoring
        self.log_file = log_file
        
        self.system_metrics_history: List[SystemMetrics] = []
        self.gpu_metrics_history: List[GPUMetrics] = []
        
        self._running = False
        self._collection_thread: Optional[threading.Thread] = None
        self._callbacks: List[Callable[[SystemMetrics, List[GPUMetrics]], None]] = []
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize GPU monitoring
        self._gpu_available = False
        self._nvidia_available = False
        self._init_gpu_monitoring()
        
    def _init_gpu_monitoring(self):
        """Initialize GPU monitoring capabilities."""
        if not self.enable_gpu_monitoring:
            return
            
        # Try NVIDIA first
        if pynvml:
            try:
                pynvml.nvmlInit()
                self._nvidia_available = True
                self._gpu_available = True
                self.logger.info("NVIDIA GPU monitoring initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize NVIDIA monitoring: {e}")
        
        # Fallback to GPUtil
        if not self._gpu_available and GPUtil:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    self._gpu_available = True
                    self.logger.info("GPU monitoring initialized via GPUtil")
            except Exception as e:
                self.logger.warning(f"Failed to initialize GPU monitoring: {e}")
    
    def add_callback(self, callback: Callable[[SystemMetrics, List[GPUMetrics]], None]):
        """Add a callback function to be called when new metrics are collected."""
        self._callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[SystemMetrics, List[GPUMetrics]], None]):
        """Remove a callback function."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics."""
        metrics = SystemMetrics()
        
        if not psutil:
            self.logger.warning("psutil not available, returning empty metrics")
            return metrics
        
        try:
            # CPU metrics
            metrics.cpu_percent = psutil.cpu_percent(interval=1)
            metrics.cpu_count = psutil.cpu_count()
            
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                metrics.cpu_freq = cpu_freq.current
            
            # Memory metrics
            memory = psutil.virtual_memory()
            metrics.memory_total = memory.total
            metrics.memory_available = memory.available
            metrics.memory_percent = memory.percent
            
            # Disk metrics (root drive)
            disk = psutil.disk_usage('/')
            metrics.disk_total = disk.total
            metrics.disk_used = disk.used
            metrics.disk_percent = (disk.used / disk.total) * 100
            
            # Network metrics
            network = psutil.net_io_counters()
            if network:
                metrics.network_sent = network.bytes_sent
                metrics.network_recv = network.bytes_recv
            
            # Boot time
            metrics.boot_time = datetime.fromtimestamp(psutil.boot_time())
            
            # Load average (Unix-like systems)
            if hasattr(os, 'getloadavg'):
                try:
                    metrics.load_average = list(os.getloadavg())
                except (OSError, AttributeError):
                    pass
                    
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
        
        return metrics
    
    def collect_gpu_metrics(self) -> List[GPUMetrics]:
        """Collect current GPU metrics."""
        gpu_metrics = []
        
        if not self._gpu_available:
            return gpu_metrics
        
        try:
            if self._nvidia_available:
                gpu_metrics.extend(self._collect_nvidia_metrics())
            elif GPUtil:
                gpu_metrics.extend(self._collect_gputil_metrics())
        except Exception as e:
            self.logger.error(f"Error collecting GPU metrics: {e}")
        
        return gpu_metrics
    
    def _collect_nvidia_metrics(self) -> List[GPUMetrics]:
        """Collect NVIDIA GPU metrics using pynvml."""
        gpu_metrics = []
        
        try:
            device_count = pynvml.nvmlDeviceGetCount()
            
            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                
                metrics = GPUMetrics(gpu_id=i)
                
                # Basic info
                metrics.name = pynvml.nvmlDeviceGetName(handle).decode('utf-8')
                metrics.driver_version = pynvml.nvmlSystemGetDriverVersion().decode('utf-8')
                
                # Memory info
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                metrics.memory_total = mem_info.total
                metrics.memory_used = mem_info.used
                metrics.memory_percent = (mem_info.used / mem_info.total) * 100
                
                # GPU utilization
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                metrics.gpu_percent = util.gpu
                
                # Temperature
                try:
                    metrics.temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                except pynvml.NVMLError:
                    pass
                
                # Power
                try:
                    metrics.power_draw = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # Convert to watts
                    metrics.power_limit = pynvml.nvmlDeviceGetPowerManagementLimitConstraints(handle)[1] / 1000.0
                except pynvml.NVMLError:
                    pass
                
                # Fan speed
                try:
                    metrics.fan_speed = pynvml.nvmlDeviceGetFanSpeed(handle)
                except pynvml.NVMLError:
                    pass
                
                gpu_metrics.append(metrics)
                
        except Exception as e:
            self.logger.error(f"Error collecting NVIDIA metrics: {e}")
        
        return gpu_metrics
    
    def _collect_gputil_metrics(self) -> List[GPUMetrics]:
        """Collect GPU metrics using GPUtil."""
        gpu_metrics = []
        
        try:
            gpus = GPUtil.getGPUs()
            
            for i, gpu in enumerate(gpus):
                metrics = GPUMetrics(gpu_id=i)
                metrics.name = gpu.name
                metrics.driver_version = gpu.driver
                metrics.memory_total = int(gpu.memoryTotal * 1024 * 1024)  # Convert MB to bytes
                metrics.memory_used = int(gpu.memoryUsed * 1024 * 1024)
                metrics.memory_percent = gpu.memoryUtil * 100
                metrics.gpu_percent = gpu.load * 100
                metrics.temperature = gpu.temperature
                
                gpu_metrics.append(metrics)
                
        except Exception as e:
            self.logger.error(f"Error collecting GPUtil metrics: {e}")
        
        return gpu_metrics
    
    def start_monitoring(self):
        """Start continuous monitoring in a background thread."""
        if self._running:
            self.logger.warning("Monitoring already running")
            return
        
        self._running = True
        self._collection_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self._collection_thread.start()
        self.logger.info("Device monitoring started")
    
    def stop_monitoring(self):
        """Stop continuous monitoring."""
        if not self._running:
            return
        
        self._running = False
        if self._collection_thread:
            self._collection_thread.join(timeout=5.0)
        self.logger.info("Device monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self._running:
            try:
                # Collect metrics
                system_metrics = self.collect_system_metrics()
                gpu_metrics = self.collect_gpu_metrics()
                
                # Store in history
                self._add_to_history(system_metrics, gpu_metrics)
                
                # Log to file if configured
                if self.log_file:
                    self._log_metrics(system_metrics, gpu_metrics)
                
                # Call callbacks
                for callback in self._callbacks:
                    try:
                        callback(system_metrics, gpu_metrics)
                    except Exception as e:
                        self.logger.error(f"Error in telemetry callback: {e}")
                
                time.sleep(self.collection_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.collection_interval)
    
    def _add_to_history(self, system_metrics: SystemMetrics, gpu_metrics: List[GPUMetrics]):
        """Add metrics to history with size limit."""
        self.system_metrics_history.append(system_metrics)
        if len(self.system_metrics_history) > self.max_history_size:
            self.system_metrics_history.pop(0)
        
        for gpu_metric in gpu_metrics:
            self.gpu_metrics_history.append(gpu_metric)
        
        # Keep GPU history size manageable
        if len(self.gpu_metrics_history) > self.max_history_size * 4:  # Allow more GPU entries
            excess = len(self.gpu_metrics_history) - self.max_history_size * 4
            self.gpu_metrics_history = self.gpu_metrics_history[excess:]
    
    def _log_metrics(self, system_metrics: SystemMetrics, gpu_metrics: List[GPUMetrics]):
        """Log metrics to file."""
        try:
            log_data = {
                'system': system_metrics.to_dict(),
                'gpus': [gpu.to_dict() for gpu in gpu_metrics]
            }
            
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_data) + '\n')
                
        except Exception as e:
            self.logger.error(f"Error logging metrics: {e}")
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system and GPU metrics."""
        system_metrics = self.collect_system_metrics()
        gpu_metrics = self.collect_gpu_metrics()
        
        return {
            'system': system_metrics.to_dict(),
            'gpus': [gpu.to_dict() for gpu in gpu_metrics],
            'collection_time': datetime.now().isoformat()
        }
    
    def get_metrics_summary(self, duration_minutes: int = 10) -> Dict[str, Any]:
        """Get metrics summary for the specified duration."""
        cutoff_time = datetime.now() - timedelta(minutes=duration_minutes)
        
        # Filter recent system metrics
        recent_system = [m for m in self.system_metrics_history if m.timestamp >= cutoff_time]
        recent_gpu = [m for m in self.gpu_metrics_history if m.timestamp >= cutoff_time]
        
        summary = {
            'duration_minutes': duration_minutes,
            'system_samples': len(recent_system),
            'gpu_samples': len(recent_gpu)
        }
        
        if recent_system:
            cpu_values = [m.cpu_percent for m in recent_system]
            memory_values = [m.memory_percent for m in recent_system]
            
            summary['system'] = {
                'cpu_avg': sum(cpu_values) / len(cpu_values),
                'cpu_max': max(cpu_values),
                'cpu_min': min(cpu_values),
                'memory_avg': sum(memory_values) / len(memory_values),
                'memory_max': max(memory_values),
                'memory_min': min(memory_values)
            }
        
        if recent_gpu:
            gpu_util_values = [m.gpu_percent for m in recent_gpu]
            gpu_mem_values = [m.memory_percent for m in recent_gpu]
            
            summary['gpu'] = {
                'utilization_avg': sum(gpu_util_values) / len(gpu_util_values),
                'utilization_max': max(gpu_util_values),
                'utilization_min': min(gpu_util_values),
                'memory_avg': sum(gpu_mem_values) / len(gpu_mem_values),
                'memory_max': max(gpu_mem_values),
                'memory_min': min(gpu_mem_values)
            }
        
        return summary
    
    def clear_history(self):
        """Clear all stored metrics history."""
        self.system_metrics_history.clear()
        self.gpu_metrics_history.clear()
        self.logger.info("Metrics history cleared")
    
    def export_metrics(self, file_path: Path, format: str = 'json') -> bool:
        """Export metrics history to file.
        
        Args:
            file_path: Path to export file
            format: Export format ('json' or 'csv')
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            if format.lower() == 'json':
                data = {
                    'system_metrics': [m.to_dict() for m in self.system_metrics_history],
                    'gpu_metrics': [m.to_dict() for m in self.gpu_metrics_history],
                    'export_time': datetime.now().isoformat()
                }
                
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)
                    
            elif format.lower() == 'csv':
                import csv
                
                with open(file_path, 'w', newline='') as f:
                    if self.system_metrics_history:
                        writer = csv.DictWriter(f, fieldnames=self.system_metrics_history[0].to_dict().keys())
                        writer.writeheader()
                        for metrics in self.system_metrics_history:
                            writer.writerow(metrics.to_dict())
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            self.logger.info(f"Metrics exported to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting metrics: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry."""
        self.start_monitoring()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_monitoring()