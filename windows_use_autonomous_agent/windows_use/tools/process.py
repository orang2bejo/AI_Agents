"""Windows process management with safety controls.

This module provides secure process operations with proper validation and logging.
"""

import psutil
import subprocess
import logging
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
import os
import signal


@dataclass
class ProcessInfo:
    """Information about a Windows process."""
    pid: int
    name: str
    exe: Optional[str]
    cmdline: List[str]
    status: str
    cpu_percent: float
    memory_percent: float
    memory_info: Dict[str, int]
    create_time: float
    username: Optional[str]
    

@dataclass
class ProcessAction:
    """Result of a process action."""
    success: bool
    message: str
    pid: Optional[int] = None
    process_name: Optional[str] = None


class ProcessManager:
    """Safe Windows process management with validation and logging."""
    
    # Processes that should never be terminated
    PROTECTED_PROCESSES = {
        'System', 'Registry', 'smss.exe', 'csrss.exe', 'wininit.exe',
        'winlogon.exe', 'services.exe', 'lsass.exe', 'svchost.exe',
        'dwm.exe', 'explorer.exe', 'audiodg.exe', 'conhost.exe',
        'fontdrvhost.exe', 'WmiPrvSE.exe', 'dllhost.exe'
    }
    
    # Processes that require confirmation before termination
    SENSITIVE_PROCESSES = {
        'chrome.exe', 'firefox.exe', 'msedge.exe', 'iexplore.exe',
        'outlook.exe', 'winword.exe', 'excel.exe', 'powerpnt.exe',
        'notepad.exe', 'notepad++.exe', 'code.exe', 'devenv.exe',
        'steam.exe', 'discord.exe', 'spotify.exe', 'vlc.exe'
    }
    
    def __init__(self, logger: Optional[logging.Logger] = None,
                 require_confirmation: bool = True):
        self.logger = logger or logging.getLogger(__name__)
        self.require_confirmation = require_confirmation
        
    def get_process_list(self, name_filter: Optional[str] = None,
                        include_system: bool = False) -> List[ProcessInfo]:
        """Get list of running processes.
        
        Args:
            name_filter: Optional process name filter
            include_system: Include system processes
            
        Returns:
            List of ProcessInfo objects
        """
        processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline', 
                                           'status', 'cpu_percent', 'memory_percent',
                                           'memory_info', 'create_time', 'username']):
                try:
                    pinfo = proc.info
                    
                    # Filter by name if specified
                    if name_filter and name_filter.lower() not in pinfo['name'].lower():
                        continue
                    
                    # Filter system processes if not requested
                    if not include_system and pinfo['name'] in self.PROTECTED_PROCESSES:
                        continue
                    
                    # Get CPU percent (this may take a moment)
                    try:
                        cpu_percent = proc.cpu_percent(interval=0.1)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        cpu_percent = 0.0
                    
                    process_info = ProcessInfo(
                        pid=pinfo['pid'],
                        name=pinfo['name'],
                        exe=pinfo['exe'],
                        cmdline=pinfo['cmdline'] or [],
                        status=pinfo['status'],
                        cpu_percent=cpu_percent,
                        memory_percent=pinfo['memory_percent'] or 0.0,
                        memory_info=pinfo['memory_info']._asdict() if pinfo['memory_info'] else {},
                        create_time=pinfo['create_time'] or 0.0,
                        username=pinfo['username']
                    )
                    
                    processes.append(process_info)
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    # Process disappeared or access denied
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error getting process list: {e}")
            
        self.logger.info(f"Retrieved {len(processes)} processes")
        return processes
    
    def get_process_by_pid(self, pid: int) -> Optional[ProcessInfo]:
        """Get process information by PID.
        
        Args:
            pid: Process ID
            
        Returns:
            ProcessInfo object or None if not found
        """
        try:
            proc = psutil.Process(pid)
            
            # Get CPU percent
            try:
                cpu_percent = proc.cpu_percent(interval=0.1)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                cpu_percent = 0.0
            
            return ProcessInfo(
                pid=proc.pid,
                name=proc.name(),
                exe=proc.exe(),
                cmdline=proc.cmdline(),
                status=proc.status(),
                cpu_percent=cpu_percent,
                memory_percent=proc.memory_percent(),
                memory_info=proc.memory_info()._asdict(),
                create_time=proc.create_time(),
                username=proc.username()
            )
            
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            self.logger.error(f"Cannot access process {pid}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error getting process {pid}: {e}")
            return None
    
    def get_processes_by_name(self, name: str) -> List[ProcessInfo]:
        """Get processes by name.
        
        Args:
            name: Process name (can be partial)
            
        Returns:
            List of matching ProcessInfo objects
        """
        return self.get_process_list(name_filter=name)
    
    def is_process_safe_to_terminate(self, process_name: str, pid: int) -> Tuple[bool, str]:
        """Check if a process is safe to terminate.
        
        Args:
            process_name: Name of the process
            pid: Process ID
            
        Returns:
            Tuple of (is_safe, reason)
        """
        # Check if it's a protected system process
        if process_name in self.PROTECTED_PROCESSES:
            return False, f"Protected system process: {process_name}"
        
        # Check if it's the current Python process
        if pid == os.getpid():
            return False, "Cannot terminate current process"
        
        # Check if it's a parent process
        try:
            current_proc = psutil.Process()
            parent_pids = [p.pid for p in current_proc.parents()]
            if pid in parent_pids:
                return False, "Cannot terminate parent process"
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        
        # Check if it requires confirmation
        if process_name in self.SENSITIVE_PROCESSES:
            if self.require_confirmation:
                return False, f"Sensitive process requires confirmation: {process_name}"
        
        return True, "Process appears safe to terminate"
    
    def terminate_process(self, pid: int, force: bool = False,
                         timeout: int = 10) -> ProcessAction:
        """Terminate a process by PID.
        
        Args:
            pid: Process ID
            force: Force termination (kill instead of terminate)
            timeout: Timeout for graceful termination
            
        Returns:
            ProcessAction result
        """
        try:
            proc = psutil.Process(pid)
            process_name = proc.name()
            
            # Safety check
            is_safe, reason = self.is_process_safe_to_terminate(process_name, pid)
            if not is_safe:
                self.logger.warning(f"Process termination blocked: {reason}")
                return ProcessAction(
                    success=False,
                    message=f"Termination blocked: {reason}",
                    pid=pid,
                    process_name=process_name
                )
            
            self.logger.info(f"Terminating process {process_name} (PID: {pid})")
            
            if force:
                # Force kill
                proc.kill()
                message = f"Force killed process {process_name} (PID: {pid})"
            else:
                # Graceful termination
                proc.terminate()
                
                # Wait for process to terminate
                try:
                    proc.wait(timeout=timeout)
                    message = f"Gracefully terminated process {process_name} (PID: {pid})"
                except psutil.TimeoutExpired:
                    # Force kill if graceful termination failed
                    proc.kill()
                    message = f"Force killed process {process_name} (PID: {pid}) after timeout"
            
            self.logger.info(message)
            return ProcessAction(
                success=True,
                message=message,
                pid=pid,
                process_name=process_name
            )
            
        except psutil.NoSuchProcess:
            message = f"Process {pid} not found (may have already terminated)"
            self.logger.info(message)
            return ProcessAction(
                success=True,
                message=message,
                pid=pid
            )
        except psutil.AccessDenied:
            message = f"Access denied when terminating process {pid}"
            self.logger.error(message)
            return ProcessAction(
                success=False,
                message=message,
                pid=pid
            )
        except Exception as e:
            message = f"Error terminating process {pid}: {e}"
            self.logger.error(message)
            return ProcessAction(
                success=False,
                message=message,
                pid=pid
            )
    
    def terminate_processes_by_name(self, name: str, force: bool = False) -> List[ProcessAction]:
        """Terminate all processes with given name.
        
        Args:
            name: Process name
            force: Force termination
            
        Returns:
            List of ProcessAction results
        """
        processes = self.get_processes_by_name(name)
        results = []
        
        for proc_info in processes:
            result = self.terminate_process(proc_info.pid, force=force)
            results.append(result)
            
        return results
    
    def start_process(self, executable: str, arguments: Optional[List[str]] = None,
                     working_directory: Optional[str] = None,
                     wait: bool = False, timeout: Optional[int] = None) -> ProcessAction:
        """Start a new process.
        
        Args:
            executable: Path to executable
            arguments: Command line arguments
            working_directory: Working directory
            wait: Wait for process to complete
            timeout: Timeout for waiting
            
        Returns:
            ProcessAction result
        """
        try:
            # Validate executable exists
            if not Path(executable).exists():
                return ProcessAction(
                    success=False,
                    message=f"Executable not found: {executable}"
                )
            
            # Build command
            cmd = [executable]
            if arguments:
                cmd.extend(arguments)
            
            self.logger.info(f"Starting process: {' '.join(cmd)}")
            
            # Start process
            if wait:
                result = subprocess.run(
                    cmd,
                    cwd=working_directory,
                    timeout=timeout,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    message = f"Process completed successfully: {executable}"
                    self.logger.info(message)
                    return ProcessAction(
                        success=True,
                        message=message
                    )
                else:
                    message = f"Process failed with exit code {result.returncode}: {result.stderr}"
                    self.logger.error(message)
                    return ProcessAction(
                        success=False,
                        message=message
                    )
            else:
                # Start without waiting
                proc = subprocess.Popen(
                    cmd,
                    cwd=working_directory
                )
                
                message = f"Started process {executable} with PID {proc.pid}"
                self.logger.info(message)
                return ProcessAction(
                    success=True,
                    message=message,
                    pid=proc.pid
                )
                
        except subprocess.TimeoutExpired:
            message = f"Process timeout: {executable}"
            self.logger.error(message)
            return ProcessAction(
                success=False,
                message=message
            )
        except Exception as e:
            message = f"Error starting process {executable}: {e}"
            self.logger.error(message)
            return ProcessAction(
                success=False,
                message=message
            )
    
    def get_system_performance(self) -> Dict[str, Any]:
        """Get system performance metrics.
        
        Returns:
            Dictionary with performance metrics
        """
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory usage
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk usage
            disk_usage = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.device] = {
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': (usage.used / usage.total) * 100
                    }
                except PermissionError:
                    continue
            
            # Network stats
            network = psutil.net_io_counters()
            
            # Process count
            process_count = len(psutil.pids())
            
            return {
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'frequency': cpu_freq._asdict() if cpu_freq else None
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used,
                    'percent': memory.percent
                },
                'swap': {
                    'total': swap.total,
                    'used': swap.used,
                    'free': swap.free,
                    'percent': swap.percent
                },
                'disk': disk_usage,
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                'processes': {
                    'count': process_count
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system performance: {e}")
            return {}
    
    def get_top_processes(self, limit: int = 10, sort_by: str = 'cpu') -> List[ProcessInfo]:
        """Get top processes by resource usage.
        
        Args:
            limit: Number of processes to return
            sort_by: Sort criteria ('cpu', 'memory')
            
        Returns:
            List of top ProcessInfo objects
        """
        processes = self.get_process_list(include_system=True)
        
        if sort_by == 'cpu':
            processes.sort(key=lambda p: p.cpu_percent, reverse=True)
        elif sort_by == 'memory':
            processes.sort(key=lambda p: p.memory_percent, reverse=True)
        
        return processes[:limit]


def format_bytes(bytes_value: int) -> str:
    """Format bytes to human readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def format_process_info(process: ProcessInfo) -> str:
    """Format process information for display."""
    memory_mb = process.memory_info.get('rss', 0) / (1024 * 1024)
    return (
        f"PID: {process.pid:>6} | "
        f"Name: {process.name:<20} | "
        f"CPU: {process.cpu_percent:>5.1f}% | "
        f"Memory: {memory_mb:>6.1f} MB | "
        f"Status: {process.status}"
    )