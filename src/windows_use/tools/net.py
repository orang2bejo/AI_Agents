"""Windows network operations with safety controls.

This module provides secure network operations with proper validation and logging.
"""

import socket
import subprocess
import psutil
import requests
import logging
import ipaddress
import time
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from pathlib import Path
import json
import re


@dataclass
class NetworkAdapter:
    """Information about a network adapter."""
    name: str
    description: str
    status: str
    speed: Optional[int]
    mac_address: str
    ip_addresses: List[str]
    gateway: Optional[str]
    dns_servers: List[str]
    

@dataclass
class ConnectionTest:
    """Result of a network connection test."""
    target: str
    port: Optional[int]
    success: bool
    response_time: Optional[float]
    error_message: Optional[str]
    

@dataclass
class NetworkStats:
    """Network interface statistics."""
    interface: str
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    errors_in: int
    errors_out: int
    drops_in: int
    drops_out: int
    

class NetworkManager:
    """Safe Windows network operations with validation and logging."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        
    def get_network_adapters(self) -> List[NetworkAdapter]:
        """Get information about network adapters.
        
        Returns:
            List of NetworkAdapter objects
        """
        adapters = []
        
        try:
            # Get adapter information using psutil
            addrs = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            for interface_name, addresses in addrs.items():
                # Get interface statistics
                interface_stats = stats.get(interface_name)
                if not interface_stats:
                    continue
                
                # Extract IP addresses and MAC address
                ip_addresses = []
                mac_address = ""
                
                for addr in addresses:
                    if addr.family == socket.AF_INET:  # IPv4
                        ip_addresses.append(addr.address)
                    elif addr.family == psutil.AF_LINK:  # MAC address
                        mac_address = addr.address
                
                # Get gateway and DNS info using PowerShell
                gateway, dns_servers = self._get_adapter_network_config(interface_name)
                
                adapter = NetworkAdapter(
                    name=interface_name,
                    description=interface_name,  # Could be enhanced with WMI
                    status="up" if interface_stats.isup else "down",
                    speed=interface_stats.speed if interface_stats.speed != 0 else None,
                    mac_address=mac_address,
                    ip_addresses=ip_addresses,
                    gateway=gateway,
                    dns_servers=dns_servers
                )
                
                adapters.append(adapter)
                
        except Exception as e:
            self.logger.error(f"Error getting network adapters: {e}")
            
        self.logger.info(f"Found {len(adapters)} network adapters")
        return adapters
    
    def _get_adapter_network_config(self, interface_name: str) -> Tuple[Optional[str], List[str]]:
        """Get gateway and DNS configuration for an adapter using PowerShell.
        
        Args:
            interface_name: Network interface name
            
        Returns:
            Tuple of (gateway, dns_servers)
        """
        try:
            # Get gateway
            gateway_cmd = f"Get-NetRoute -InterfaceAlias '{interface_name}' -DestinationPrefix '0.0.0.0/0' | Select-Object -ExpandProperty NextHop"
            gateway_result = subprocess.run(
                ["powershell", "-Command", gateway_cmd],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            gateway = None
            if gateway_result.returncode == 0 and gateway_result.stdout.strip():
                gateway = gateway_result.stdout.strip().split('\n')[0]
            
            # Get DNS servers
            dns_cmd = f"Get-DnsClientServerAddress -InterfaceAlias '{interface_name}' | Select-Object -ExpandProperty ServerAddresses"
            dns_result = subprocess.run(
                ["powershell", "-Command", dns_cmd],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            dns_servers = []
            if dns_result.returncode == 0 and dns_result.stdout.strip():
                dns_servers = [addr.strip() for addr in dns_result.stdout.strip().split('\n') if addr.strip()]
            
            return gateway, dns_servers
            
        except Exception as e:
            self.logger.error(f"Error getting network config for {interface_name}: {e}")
            return None, []
    
    def test_connection(self, target: str, port: Optional[int] = None, 
                      timeout: int = 5) -> ConnectionTest:
        """Test network connection to a target.
        
        Args:
            target: Target hostname or IP address
            port: Optional port number (default: ping test)
            timeout: Connection timeout in seconds
            
        Returns:
            ConnectionTest result
        """
        start_time = time.time()
        
        try:
            # Validate target
            if not self._is_valid_target(target):
                return ConnectionTest(
                    target=target,
                    port=port,
                    success=False,
                    response_time=None,
                    error_message="Invalid target address"
                )
            
            if port is not None:
                # TCP connection test
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                
                try:
                    result = sock.connect_ex((target, port))
                    response_time = (time.time() - start_time) * 1000  # Convert to ms
                    
                    if result == 0:
                        return ConnectionTest(
                            target=target,
                            port=port,
                            success=True,
                            response_time=response_time,
                            error_message=None
                        )
                    else:
                        return ConnectionTest(
                            target=target,
                            port=port,
                            success=False,
                            response_time=response_time,
                            error_message=f"Connection failed (error {result})"
                        )
                finally:
                    sock.close()
            else:
                # Ping test using subprocess
                result = subprocess.run(
                    ["ping", "-n", "1", "-w", str(timeout * 1000), target],
                    capture_output=True,
                    text=True,
                    timeout=timeout + 2
                )
                
                response_time = (time.time() - start_time) * 1000
                
                if result.returncode == 0:
                    # Extract actual ping time from output
                    ping_match = re.search(r'time[<=](\d+)ms', result.stdout)
                    if ping_match:
                        response_time = float(ping_match.group(1))
                    
                    return ConnectionTest(
                        target=target,
                        port=port,
                        success=True,
                        response_time=response_time,
                        error_message=None
                    )
                else:
                    return ConnectionTest(
                        target=target,
                        port=port,
                        success=False,
                        response_time=response_time,
                        error_message="Ping failed"
                    )
                    
        except socket.timeout:
            response_time = (time.time() - start_time) * 1000
            return ConnectionTest(
                target=target,
                port=port,
                success=False,
                response_time=response_time,
                error_message="Connection timeout"
            )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return ConnectionTest(
                target=target,
                port=port,
                success=False,
                response_time=response_time,
                error_message=str(e)
            )
    
    def _is_valid_target(self, target: str) -> bool:
        """Validate if target is a valid hostname or IP address.
        
        Args:
            target: Target to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Try to parse as IP address
            ipaddress.ip_address(target)
            return True
        except ValueError:
            # Not an IP, check if it's a valid hostname
            if re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$', target):
                return True
            return False
    
    def get_network_statistics(self) -> List[NetworkStats]:
        """Get network interface statistics.
        
        Returns:
            List of NetworkStats objects
        """
        stats_list = []
        
        try:
            io_counters = psutil.net_io_counters(pernic=True)
            
            for interface, counters in io_counters.items():
                stats = NetworkStats(
                    interface=interface,
                    bytes_sent=counters.bytes_sent,
                    bytes_recv=counters.bytes_recv,
                    packets_sent=counters.packets_sent,
                    packets_recv=counters.packets_recv,
                    errors_in=counters.errin,
                    errors_out=counters.errout,
                    drops_in=counters.dropin,
                    drops_out=counters.dropout
                )
                stats_list.append(stats)
                
        except Exception as e:
            self.logger.error(f"Error getting network statistics: {e}")
            
        return stats_list
    
    def resolve_hostname(self, hostname: str) -> List[str]:
        """Resolve hostname to IP addresses.
        
        Args:
            hostname: Hostname to resolve
            
        Returns:
            List of IP addresses
        """
        try:
            if not self._is_valid_target(hostname):
                self.logger.error(f"Invalid hostname: {hostname}")
                return []
            
            # Get address info
            addr_info = socket.getaddrinfo(hostname, None)
            ip_addresses = list(set([addr[4][0] for addr in addr_info]))
            
            self.logger.info(f"Resolved {hostname} to {len(ip_addresses)} addresses")
            return ip_addresses
            
        except socket.gaierror as e:
            self.logger.error(f"DNS resolution failed for {hostname}: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error resolving {hostname}: {e}")
            return []
    
    def get_public_ip(self, timeout: int = 10) -> Optional[str]:
        """Get public IP address using external service.
        
        Args:
            timeout: Request timeout in seconds
            
        Returns:
            Public IP address or None if failed
        """
        services = [
            "https://api.ipify.org",
            "https://icanhazip.com",
            "https://ipecho.net/plain"
        ]
        
        for service in services:
            try:
                response = requests.get(service, timeout=timeout)
                if response.status_code == 200:
                    ip = response.text.strip()
                    # Validate IP address
                    ipaddress.ip_address(ip)
                    self.logger.info(f"Public IP: {ip}")
                    return ip
            except Exception as e:
                self.logger.debug(f"Failed to get IP from {service}: {e}")
                continue
        
        self.logger.error("Failed to get public IP from all services")
        return None
    
    def scan_port_range(self, target: str, start_port: int, end_port: int,
                       timeout: int = 1, max_threads: int = 50) -> List[int]:
        """Scan a range of ports on a target.
        
        Args:
            target: Target hostname or IP
            start_port: Starting port number
            end_port: Ending port number
            timeout: Connection timeout per port
            max_threads: Maximum concurrent threads
            
        Returns:
            List of open port numbers
        """
        import threading
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        if not self._is_valid_target(target):
            self.logger.error(f"Invalid target: {target}")
            return []
        
        # Limit port range for safety
        if end_port - start_port > 1000:
            self.logger.warning("Port range too large, limiting to 1000 ports")
            end_port = start_port + 1000
        
        open_ports = []
        lock = threading.Lock()
        
        def scan_port(port: int) -> Optional[int]:
            """Scan a single port."""
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result = sock.connect_ex((target, port))
                sock.close()
                
                if result == 0:
                    with lock:
                        open_ports.append(port)
                    return port
            except Exception:
                pass
            return None
        
        try:
            with ThreadPoolExecutor(max_workers=min(max_threads, end_port - start_port + 1)) as executor:
                futures = [executor.submit(scan_port, port) for port in range(start_port, end_port + 1)]
                
                for future in as_completed(futures):
                    future.result()  # Wait for completion
            
            open_ports.sort()
            self.logger.info(f"Found {len(open_ports)} open ports on {target}")
            return open_ports
            
        except Exception as e:
            self.logger.error(f"Error scanning ports on {target}: {e}")
            return []
    
    def get_routing_table(self) -> List[Dict[str, Any]]:
        """Get system routing table.
        
        Returns:
            List of routing table entries
        """
        routes = []
        
        try:
            # Use PowerShell to get routing table
            cmd = "Get-NetRoute | Select-Object DestinationPrefix, NextHop, InterfaceAlias, RouteMetric | ConvertTo-Json"
            result = subprocess.run(
                ["powershell", "-Command", cmd],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout.strip():
                data = json.loads(result.stdout)
                if isinstance(data, list):
                    routes = data
                else:
                    routes = [data]
                    
        except Exception as e:
            self.logger.error(f"Error getting routing table: {e}")
            
        return routes
    
    def flush_dns_cache(self) -> bool:
        """Flush DNS resolver cache.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            result = subprocess.run(
                ["ipconfig", "/flushdns"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.logger.info("DNS cache flushed successfully")
                return True
            else:
                self.logger.error(f"Failed to flush DNS cache: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error flushing DNS cache: {e}")
            return False
    
    def get_network_connections(self, process_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get active network connections.
        
        Args:
            process_name: Optional filter by process name
            
        Returns:
            List of connection information
        """
        connections = []
        
        try:
            for conn in psutil.net_connections(kind='inet'):
                try:
                    # Get process info if PID is available
                    process_info = None
                    if conn.pid:
                        try:
                            proc = psutil.Process(conn.pid)
                            process_info = {
                                'pid': conn.pid,
                                'name': proc.name(),
                                'exe': proc.exe()
                            }
                            
                            # Filter by process name if specified
                            if process_name and process_name.lower() not in proc.name().lower():
                                continue
                                
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            process_info = {'pid': conn.pid, 'name': 'Unknown', 'exe': None}
                    
                    connection_info = {
                        'family': 'IPv4' if conn.family == socket.AF_INET else 'IPv6',
                        'type': 'TCP' if conn.type == socket.SOCK_STREAM else 'UDP',
                        'local_address': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                        'remote_address': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                        'status': conn.status,
                        'process': process_info
                    }
                    
                    connections.append(connection_info)
                    
                except Exception:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error getting network connections: {e}")
            
        return connections


# Common network utilities
def format_bytes(bytes_value: int) -> str:
    """Format bytes to human readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def is_private_ip(ip: str) -> bool:
    """Check if IP address is private."""
    try:
        return ipaddress.ip_address(ip).is_private
    except ValueError:
        return False


def get_network_class(ip: str) -> Optional[str]:
    """Get network class for IPv4 address."""
    try:
        addr = ipaddress.IPv4Address(ip)
        if addr.is_loopback:
            return "Loopback"
        elif addr.is_private:
            return "Private"
        elif addr.is_multicast:
            return "Multicast"
        elif addr.is_reserved:
            return "Reserved"
        else:
            return "Public"
    except ValueError:
        return None