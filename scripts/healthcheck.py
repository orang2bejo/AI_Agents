#!/usr/bin/env python3
"""Health Check Script for Jarvis AI System

This script provides comprehensive health monitoring for the Jarvis AI system,
including CPU, GPU, memory, disk, and service status checks.

Usage:
    python healthcheck.py [options]
    
Options:
    --interval SECONDS    Monitoring interval (default: 30)
    --duration MINUTES    How long to monitor (default: continuous)
    --output FILE         Output file for metrics (optional)
    --format FORMAT       Output format: json, csv, or console (default: console)
    --thresholds FILE     JSON file with custom thresholds (optional)
    --quiet              Suppress console output
    --check-services     Check Jarvis services status
    --export-only        Export current metrics and exit
"""

import argparse
import json
import logging
import signal
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    from windows_use.utils.device_telemetry import DeviceTelemetry, SystemMetrics, GPUMetrics
except ImportError as e:
    print(f"Error importing telemetry module: {e}")
    print("Make sure you're running from the correct directory and dependencies are installed.")
    sys.exit(1)

try:
    import psutil
except ImportError:
    psutil = None
    print("Warning: psutil not available. Some health checks will be limited.")


class HealthChecker:
    """Main health checking class."""
    
    def __init__(self, 
                 interval: float = 30.0,
                 duration_minutes: Optional[int] = None,
                 output_file: Optional[Path] = None,
                 output_format: str = 'console',
                 thresholds_file: Optional[Path] = None,
                 quiet: bool = False,
                 check_services: bool = False):
        """Initialize health checker.
        
        Args:
            interval: Seconds between health checks
            duration_minutes: How long to monitor (None for continuous)
            output_file: Optional file to write metrics to
            output_format: Output format (console, json, csv)
            thresholds_file: JSON file with custom alert thresholds
            quiet: Suppress console output
            check_services: Whether to check Jarvis services
        """
        self.interval = interval
        self.duration_minutes = duration_minutes
        self.output_file = output_file
        self.output_format = output_format.lower()
        self.quiet = quiet
        self.check_services = check_services
        
        self.telemetry = DeviceTelemetry(
            collection_interval=interval,
            enable_gpu_monitoring=True,
            log_file=output_file if output_format == 'json' else None
        )
        
        # Default thresholds
        self.thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_percent': 90.0,
            'gpu_percent': 90.0,
            'gpu_memory_percent': 90.0,
            'gpu_temperature': 80.0,
            'response_time_ms': 5000.0
        }
        
        # Load custom thresholds if provided
        if thresholds_file and thresholds_file.exists():
            self._load_thresholds(thresholds_file)
        
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        
        self._running = False
        self._start_time = None
        
        # Health status tracking
        self.health_status = {
            'overall': 'unknown',
            'cpu': 'unknown',
            'memory': 'unknown',
            'disk': 'unknown',
            'gpu': 'unknown',
            'services': 'unknown'
        }
        
        self.alerts = []
        
    def _setup_logging(self):
        """Setup logging configuration."""
        level = logging.WARNING if self.quiet else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def _load_thresholds(self, thresholds_file: Path):
        """Load custom thresholds from JSON file."""
        try:
            with open(thresholds_file, 'r') as f:
                custom_thresholds = json.load(f)
                self.thresholds.update(custom_thresholds)
                self.logger.info(f"Loaded custom thresholds from {thresholds_file}")
        except Exception as e:
            self.logger.error(f"Error loading thresholds: {e}")
    
    def check_system_health(self) -> Dict[str, Any]:
        """Perform comprehensive system health check."""
        health_report = {
            'timestamp': datetime.now().isoformat(),
            'status': 'healthy',
            'alerts': [],
            'metrics': {},
            'services': {}
        }
        
        try:
            # Collect current metrics
            system_metrics = self.telemetry.collect_system_metrics()
            gpu_metrics = self.telemetry.collect_gpu_metrics()
            
            # Check system metrics
            self._check_system_metrics(system_metrics, health_report)
            
            # Check GPU metrics
            if gpu_metrics:
                self._check_gpu_metrics(gpu_metrics, health_report)
            
            # Check services if requested
            if self.check_services:
                self._check_jarvis_services(health_report)
            
            # Determine overall status
            if health_report['alerts']:
                critical_alerts = [a for a in health_report['alerts'] if a['severity'] == 'critical']
                warning_alerts = [a for a in health_report['alerts'] if a['severity'] == 'warning']
                
                if critical_alerts:
                    health_report['status'] = 'critical'
                elif warning_alerts:
                    health_report['status'] = 'warning'
                else:
                    health_report['status'] = 'healthy'
            
            # Store metrics
            health_report['metrics']['system'] = system_metrics.to_dict()
            health_report['metrics']['gpu'] = [gpu.to_dict() for gpu in gpu_metrics]
            
        except Exception as e:
            self.logger.error(f"Error during health check: {e}")
            health_report['status'] = 'error'
            health_report['alerts'].append({
                'type': 'system_error',
                'severity': 'critical',
                'message': f"Health check failed: {e}",
                'timestamp': datetime.now().isoformat()
            })
        
        return health_report
    
    def _check_system_metrics(self, metrics: SystemMetrics, health_report: Dict[str, Any]):
        """Check system metrics against thresholds."""
        # CPU check
        if metrics.cpu_percent > self.thresholds['cpu_percent']:
            health_report['alerts'].append({
                'type': 'high_cpu',
                'severity': 'warning' if metrics.cpu_percent < 95 else 'critical',
                'message': f"High CPU usage: {metrics.cpu_percent:.1f}%",
                'value': metrics.cpu_percent,
                'threshold': self.thresholds['cpu_percent'],
                'timestamp': metrics.timestamp.isoformat()
            })
        
        # Memory check
        if metrics.memory_percent > self.thresholds['memory_percent']:
            health_report['alerts'].append({
                'type': 'high_memory',
                'severity': 'warning' if metrics.memory_percent < 95 else 'critical',
                'message': f"High memory usage: {metrics.memory_percent:.1f}%",
                'value': metrics.memory_percent,
                'threshold': self.thresholds['memory_percent'],
                'timestamp': metrics.timestamp.isoformat()
            })
        
        # Disk check
        if metrics.disk_percent > self.thresholds['disk_percent']:
            health_report['alerts'].append({
                'type': 'high_disk',
                'severity': 'warning' if metrics.disk_percent < 98 else 'critical',
                'message': f"High disk usage: {metrics.disk_percent:.1f}%",
                'value': metrics.disk_percent,
                'threshold': self.thresholds['disk_percent'],
                'timestamp': metrics.timestamp.isoformat()
            })
        
        # Low memory check
        if metrics.memory_available < 1024 * 1024 * 1024:  # Less than 1GB
            health_report['alerts'].append({
                'type': 'low_memory',
                'severity': 'critical',
                'message': f"Very low available memory: {metrics.memory_available / (1024**3):.1f}GB",
                'value': metrics.memory_available,
                'timestamp': metrics.timestamp.isoformat()
            })
    
    def _check_gpu_metrics(self, gpu_metrics: list, health_report: Dict[str, Any]):
        """Check GPU metrics against thresholds."""
        for gpu in gpu_metrics:
            gpu_id = gpu.gpu_id
            
            # GPU utilization check
            if gpu.gpu_percent > self.thresholds['gpu_percent']:
                health_report['alerts'].append({
                    'type': 'high_gpu_usage',
                    'severity': 'warning',
                    'message': f"High GPU {gpu_id} usage: {gpu.gpu_percent:.1f}%",
                    'gpu_id': gpu_id,
                    'value': gpu.gpu_percent,
                    'threshold': self.thresholds['gpu_percent'],
                    'timestamp': gpu.timestamp.isoformat()
                })
            
            # GPU memory check
            if gpu.memory_percent > self.thresholds['gpu_memory_percent']:
                health_report['alerts'].append({
                    'type': 'high_gpu_memory',
                    'severity': 'warning',
                    'message': f"High GPU {gpu_id} memory: {gpu.memory_percent:.1f}%",
                    'gpu_id': gpu_id,
                    'value': gpu.memory_percent,
                    'threshold': self.thresholds['gpu_memory_percent'],
                    'timestamp': gpu.timestamp.isoformat()
                })
            
            # GPU temperature check
            if gpu.temperature and gpu.temperature > self.thresholds['gpu_temperature']:
                severity = 'critical' if gpu.temperature > 90 else 'warning'
                health_report['alerts'].append({
                    'type': 'high_gpu_temperature',
                    'severity': severity,
                    'message': f"High GPU {gpu_id} temperature: {gpu.temperature:.1f}°C",
                    'gpu_id': gpu_id,
                    'value': gpu.temperature,
                    'threshold': self.thresholds['gpu_temperature'],
                    'timestamp': gpu.timestamp.isoformat()
                })
    
    def _check_jarvis_services(self, health_report: Dict[str, Any]):
        """Check Jarvis-related services and processes."""
        if not psutil:
            health_report['services']['status'] = 'unknown'
            health_report['services']['message'] = 'psutil not available'
            return
        
        jarvis_processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if 'jarvis' in cmdline.lower() or 'jarvis' in proc.info['name'].lower():
                        jarvis_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cmdline': cmdline,
                            'cpu_percent': proc.info['cpu_percent'],
                            'memory_percent': proc.info['memory_percent']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            health_report['services']['jarvis_processes'] = jarvis_processes
            health_report['services']['process_count'] = len(jarvis_processes)
            
            if jarvis_processes:
                health_report['services']['status'] = 'running'
            else:
                health_report['services']['status'] = 'not_running'
                health_report['alerts'].append({
                    'type': 'no_jarvis_processes',
                    'severity': 'warning',
                    'message': 'No Jarvis processes detected',
                    'timestamp': datetime.now().isoformat()
                })
                
        except Exception as e:
            health_report['services']['status'] = 'error'
            health_report['services']['error'] = str(e)
    
    def _output_health_report(self, health_report: Dict[str, Any]):
        """Output health report in the specified format."""
        if self.output_format == 'console' and not self.quiet:
            self._print_console_report(health_report)
        elif self.output_format == 'json':
            self._output_json_report(health_report)
        elif self.output_format == 'csv':
            self._output_csv_report(health_report)
    
    def _print_console_report(self, health_report: Dict[str, Any]):
        """Print health report to console."""
        status = health_report['status']
        timestamp = health_report['timestamp']
        
        # Status indicator
        status_symbols = {
            'healthy': '✅',
            'warning': '⚠️',
            'critical': '❌',
            'error': '💥',
            'unknown': '❓'
        }
        
        symbol = status_symbols.get(status, '❓')
        print(f"\n{symbol} System Health: {status.upper()} - {timestamp}")
        print("=" * 60)
        
        # System metrics
        if 'system' in health_report['metrics']:
            sys_metrics = health_report['metrics']['system']
            print(f"CPU: {sys_metrics['cpu_percent']:.1f}% | "
                  f"Memory: {sys_metrics['memory_percent']:.1f}% | "
                  f"Disk: {sys_metrics['disk_percent']:.1f}%")
        
        # GPU metrics
        if health_report['metrics'].get('gpu'):
            for gpu in health_report['metrics']['gpu']:
                print(f"GPU {gpu['gpu_id']} ({gpu['name']}): "
                      f"{gpu['gpu_percent']:.1f}% | "
                      f"Memory: {gpu['memory_percent']:.1f}%"
                      f"{f' | Temp: {gpu["temperature"]:.1f}°C' if gpu['temperature'] else ''}")
        
        # Services
        if 'services' in health_report:
            services = health_report['services']
            if 'process_count' in services:
                print(f"Jarvis Processes: {services['process_count']}")
        
        # Alerts
        if health_report['alerts']:
            print("\nAlerts:")
            for alert in health_report['alerts']:
                severity_symbols = {
                    'warning': '⚠️',
                    'critical': '❌',
                    'info': 'ℹ️'
                }
                alert_symbol = severity_symbols.get(alert['severity'], '⚠️')
                print(f"  {alert_symbol} {alert['message']}")
        else:
            print("\n✅ No alerts")
        
        print()
    
    def _output_json_report(self, health_report: Dict[str, Any]):
        """Output health report as JSON."""
        if self.output_file:
            with open(self.output_file, 'a') as f:
                f.write(json.dumps(health_report) + '\n')
        else:
            print(json.dumps(health_report, indent=2))
    
    def _output_csv_report(self, health_report: Dict[str, Any]):
        """Output health report as CSV."""
        # This is a simplified CSV output focusing on key metrics
        if not self.output_file:
            return
        
        import csv
        
        file_exists = self.output_file.exists()
        
        with open(self.output_file, 'a', newline='') as f:
            fieldnames = ['timestamp', 'status', 'cpu_percent', 'memory_percent', 
                         'disk_percent', 'alert_count', 'gpu_count']
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            row = {
                'timestamp': health_report['timestamp'],
                'status': health_report['status'],
                'alert_count': len(health_report['alerts']),
                'gpu_count': len(health_report['metrics'].get('gpu', []))
            }
            
            if 'system' in health_report['metrics']:
                sys_metrics = health_report['metrics']['system']
                row.update({
                    'cpu_percent': sys_metrics['cpu_percent'],
                    'memory_percent': sys_metrics['memory_percent'],
                    'disk_percent': sys_metrics['disk_percent']
                })
            
            writer.writerow(row)
    
    def run_continuous_monitoring(self):
        """Run continuous health monitoring."""
        self._running = True
        self._start_time = datetime.now()
        
        if not self.quiet:
            print(f"Starting health monitoring (interval: {self.interval}s)")
            if self.duration_minutes:
                print(f"Duration: {self.duration_minutes} minutes")
            else:
                print("Duration: continuous (Ctrl+C to stop)")
            print()
        
        try:
            while self._running:
                # Check if duration limit reached
                if self.duration_minutes:
                    elapsed = datetime.now() - self._start_time
                    if elapsed.total_seconds() > self.duration_minutes * 60:
                        break
                
                # Perform health check
                health_report = self.check_system_health()
                self._output_health_report(health_report)
                
                # Wait for next check
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            if not self.quiet:
                print("\nHealth monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"Error in monitoring loop: {e}")
        finally:
            self._running = False
    
    def run_single_check(self) -> Dict[str, Any]:
        """Run a single health check and return the report."""
        health_report = self.check_system_health()
        self._output_health_report(health_report)
        return health_report
    
    def export_current_metrics(self) -> Dict[str, Any]:
        """Export current metrics without continuous monitoring."""
        return self.telemetry.get_current_metrics()


def setup_signal_handlers(health_checker: HealthChecker):
    """Setup signal handlers for graceful shutdown."""
    def signal_handler(signum, frame):
        health_checker._running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Jarvis AI System Health Checker',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('--interval', type=float, default=30.0,
                       help='Monitoring interval in seconds (default: 30)')
    parser.add_argument('--duration', type=int, default=None,
                       help='Monitoring duration in minutes (default: continuous)')
    parser.add_argument('--output', type=Path, default=None,
                       help='Output file for metrics')
    parser.add_argument('--format', choices=['console', 'json', 'csv'], default='console',
                       help='Output format (default: console)')
    parser.add_argument('--thresholds', type=Path, default=None,
                       help='JSON file with custom alert thresholds')
    parser.add_argument('--quiet', action='store_true',
                       help='Suppress console output')
    parser.add_argument('--check-services', action='store_true',
                       help='Check Jarvis services status')
    parser.add_argument('--export-only', action='store_true',
                       help='Export current metrics and exit')
    parser.add_argument('--single-check', action='store_true',
                       help='Run single health check and exit')
    
    args = parser.parse_args()
    
    # Create health checker
    health_checker = HealthChecker(
        interval=args.interval,
        duration_minutes=args.duration,
        output_file=args.output,
        output_format=args.format,
        thresholds_file=args.thresholds,
        quiet=args.quiet,
        check_services=args.check_services
    )
    
    # Setup signal handlers
    setup_signal_handlers(health_checker)
    
    try:
        if args.export_only:
            # Export current metrics and exit
            metrics = health_checker.export_current_metrics()
            if args.format == 'json':
                print(json.dumps(metrics, indent=2))
            else:
                print("Current metrics exported")
                
        elif args.single_check:
            # Run single check and exit
            health_checker.run_single_check()
            
        else:
            # Run continuous monitoring
            health_checker.run_continuous_monitoring()
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()