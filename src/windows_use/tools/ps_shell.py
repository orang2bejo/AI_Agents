"""PowerShell integration for safe Windows system operations.

This module provides secure PowerShell cmdlet execution with proper validation and logging.
"""

import subprocess
import json
import logging
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
import tempfile
import os


@dataclass
class PSResult:
    """Result from PowerShell command execution."""
    success: bool
    output: str
    error: str
    exit_code: int
    execution_time: float


class PowerShellManager:
    """Safe PowerShell operations with validation and logging."""
    
    # Whitelist of safe PowerShell cmdlets
    SAFE_CMDLETS = {
        # File and folder operations
        'Get-ChildItem', 'Get-Item', 'Get-Content', 'Set-Content',
        'Copy-Item', 'Move-Item', 'Remove-Item', 'New-Item',
        'Test-Path', 'Resolve-Path', 'Split-Path', 'Join-Path',
        
        # Process management
        'Get-Process', 'Stop-Process', 'Start-Process',
        
        # Service management (read-only by default)
        'Get-Service', 'Get-WmiObject',
        
        # System information
        'Get-ComputerInfo', 'Get-SystemInfo', 'Get-Date',
        'Get-TimeZone', 'Get-Culture', 'Get-Host',
        
        # Network (read-only)
        'Get-NetAdapter', 'Get-NetIPAddress', 'Get-NetRoute',
        'Test-NetConnection', 'Resolve-DnsName',
        
        # Registry (read-only by default)
        'Get-ItemProperty', 'Get-ChildItem',
        
        # Archive operations
        'Compress-Archive', 'Expand-Archive',
        
        # Text processing
        'Select-String', 'ConvertTo-Json', 'ConvertFrom-Json',
        'ConvertTo-Csv', 'ConvertFrom-Csv',
        
        # Basic utilities
        'Write-Output', 'Write-Host', 'Measure-Object',
        'Sort-Object', 'Group-Object', 'Where-Object', 'ForEach-Object'
    }
    
    # Dangerous cmdlets that require explicit approval
    DANGEROUS_CMDLETS = {
        'Remove-Item', 'Remove-ItemProperty', 'Clear-Content',
        'Stop-Process', 'Stop-Service', 'Restart-Service',
        'Set-ItemProperty', 'New-ItemProperty', 'Remove-ItemProperty',
        'Invoke-Expression', 'Invoke-Command', 'Start-Process'
    }
    
    def __init__(self, logger: Optional[logging.Logger] = None, 
                 require_approval_for_dangerous: bool = True):
        self.logger = logger or logging.getLogger(__name__)
        self.require_approval = require_approval_for_dangerous
        self._validate_powershell_available()
        
    def _validate_powershell_available(self) -> bool:
        """Check if PowerShell is available on the system."""
        try:
            result = subprocess.run(
                ["powershell", "-Command", "$PSVersionTable.PSVersion"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                self.logger.info(f"PowerShell available: {result.stdout.strip()}")
                return True
            else:
                raise RuntimeError("PowerShell not available")
        except (subprocess.TimeoutExpired, FileNotFoundError, RuntimeError) as e:
            self.logger.error(f"PowerShell validation failed: {e}")
            raise RuntimeError("PowerShell is not available on this system")
    
    def _validate_command_safety(self, command: str) -> Tuple[bool, str]:
        """Validate if a PowerShell command is safe to execute.
        
        Args:
            command: PowerShell command to validate
            
        Returns:
            Tuple of (is_safe, reason)
        """
        # Remove comments and normalize whitespace
        clean_command = re.sub(r'#.*$', '', command, flags=re.MULTILINE)
        clean_command = ' '.join(clean_command.split())
        
        # Check for dangerous patterns
        dangerous_patterns = [
            r'Invoke-Expression',
            r'IEX\s',
            r'&\s*\(',
            r'cmd\.exe',
            r'powershell\.exe.*-EncodedCommand',
            r'DownloadString',
            r'DownloadFile',
            r'WebClient',
            r'Net\.WebClient',
            r'Start-BitsTransfer',
            r'Invoke-WebRequest.*-OutFile',
            r'curl.*-o',
            r'wget',
            r'Format-.*-Force',
            r'Remove-.*-Recurse.*-Force'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, clean_command, re.IGNORECASE):
                return False, f"Dangerous pattern detected: {pattern}"
        
        # Extract cmdlets from command
        cmdlet_pattern = r'([A-Za-z]+-[A-Za-z]+)'
        cmdlets = re.findall(cmdlet_pattern, clean_command)
        
        # Check if all cmdlets are in safe list
        for cmdlet in cmdlets:
            if cmdlet not in self.SAFE_CMDLETS:
                if cmdlet in self.DANGEROUS_CMDLETS:
                    if self.require_approval:
                        return False, f"Dangerous cmdlet requires approval: {cmdlet}"
                else:
                    return False, f"Unknown/unsafe cmdlet: {cmdlet}"
        
        return True, "Command appears safe"
    
    def execute_command(self, command: str, timeout: int = 30, 
                       working_directory: Optional[str] = None,
                       force_approve: bool = False) -> PSResult:
        """Execute a PowerShell command safely.
        
        Args:
            command: PowerShell command to execute
            timeout: Execution timeout in seconds
            working_directory: Working directory for command execution
            force_approve: Skip safety validation (use with caution)
            
        Returns:
            PSResult object with execution details
        """
        import time
        start_time = time.time()
        
        # Validate command safety
        if not force_approve:
            is_safe, reason = self._validate_command_safety(command)
            if not is_safe:
                self.logger.error(f"Command rejected: {reason}")
                return PSResult(
                    success=False,
                    output="",
                    error=f"Command rejected for safety: {reason}",
                    exit_code=-1,
                    execution_time=time.time() - start_time
                )
        
        try:
            # Prepare PowerShell command
            ps_cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command"]
            
            # Set working directory if specified
            if working_directory:
                command = f"Set-Location '{working_directory}'; {command}"
            
            ps_cmd.append(command)
            
            self.logger.info(f"Executing PowerShell command: {command[:100]}...")
            
            # Execute command
            result = subprocess.run(
                ps_cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=working_directory
            )
            
            execution_time = time.time() - start_time
            
            ps_result = PSResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr,
                exit_code=result.returncode,
                execution_time=execution_time
            )
            
            if ps_result.success:
                self.logger.info(f"Command executed successfully in {execution_time:.2f}s")
            else:
                self.logger.error(f"Command failed with exit code {result.returncode}: {result.stderr}")
            
            return ps_result
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            error_msg = f"Command timeout after {timeout} seconds"
            self.logger.error(error_msg)
            return PSResult(
                success=False,
                output="",
                error=error_msg,
                exit_code=-2,
                execution_time=execution_time
            )
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Command execution error: {e}"
            self.logger.error(error_msg)
            return PSResult(
                success=False,
                output="",
                error=error_msg,
                exit_code=-3,
                execution_time=execution_time
            )
    
    def execute_script_file(self, script_path: str, parameters: Optional[Dict[str, Any]] = None,
                           timeout: int = 60) -> PSResult:
        """Execute a PowerShell script file.
        
        Args:
            script_path: Path to PowerShell script file
            parameters: Script parameters
            timeout: Execution timeout in seconds
            
        Returns:
            PSResult object with execution details
        """
        if not Path(script_path).exists():
            return PSResult(
                success=False,
                output="",
                error=f"Script file not found: {script_path}",
                exit_code=-1,
                execution_time=0.0
            )
        
        # Build command with parameters
        command = f"& '{script_path}'"
        if parameters:
            param_strings = []
            for key, value in parameters.items():
                if isinstance(value, str):
                    param_strings.append(f"-{key} '{value}'")
                else:
                    param_strings.append(f"-{key} {value}")
            command += " " + " ".join(param_strings)
        
        return self.execute_command(command, timeout=timeout, force_approve=True)
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get basic system information using PowerShell.
        
        Returns:
            Dictionary with system information
        """
        command = """
        $info = @{}
        $info['ComputerName'] = $env:COMPUTERNAME
        $info['UserName'] = $env:USERNAME
        $info['OS'] = (Get-WmiObject -Class Win32_OperatingSystem).Caption
        $info['Version'] = (Get-WmiObject -Class Win32_OperatingSystem).Version
        $info['Architecture'] = (Get-WmiObject -Class Win32_OperatingSystem).OSArchitecture
        $info['TotalMemory'] = [math]::Round((Get-WmiObject -Class Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 2)
        $info['Processor'] = (Get-WmiObject -Class Win32_Processor).Name
        $info['PowerShellVersion'] = $PSVersionTable.PSVersion.ToString()
        $info | ConvertTo-Json
        """
        
        result = self.execute_command(command)
        if result.success:
            try:
                return json.loads(result.output)
            except json.JSONDecodeError:
                self.logger.error("Failed to parse system info JSON")
                return {}
        else:
            self.logger.error(f"Failed to get system info: {result.error}")
            return {}
    
    def get_running_processes(self, name_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of running processes.
        
        Args:
            name_filter: Optional process name filter
            
        Returns:
            List of process information dictionaries
        """
        command = "Get-Process"
        if name_filter:
            command += f" -Name '*{name_filter}*'"
        command += " | Select-Object Name, Id, CPU, WorkingSet, StartTime | ConvertTo-Json"
        
        result = self.execute_command(command)
        if result.success:
            try:
                data = json.loads(result.output)
                return data if isinstance(data, list) else [data]
            except json.JSONDecodeError:
                self.logger.error("Failed to parse process list JSON")
                return []
        else:
            self.logger.error(f"Failed to get process list: {result.error}")
            return []
    
    def compress_folder(self, source_path: str, destination_path: str) -> PSResult:
        """Compress a folder to ZIP archive.
        
        Args:
            source_path: Source folder path
            destination_path: Destination ZIP file path
            
        Returns:
            PSResult object
        """
        command = f"Compress-Archive -Path '{source_path}' -DestinationPath '{destination_path}' -Force"
        return self.execute_command(command)
    
    def extract_archive(self, archive_path: str, destination_path: str) -> PSResult:
        """Extract ZIP archive to destination folder.
        
        Args:
            archive_path: ZIP file path
            destination_path: Destination folder path
            
        Returns:
            PSResult object
        """
        command = f"Expand-Archive -Path '{archive_path}' -DestinationPath '{destination_path}' -Force"
        return self.execute_command(command)
    
    def test_network_connection(self, target: str, port: Optional[int] = None) -> Dict[str, Any]:
        """Test network connection to target.
        
        Args:
            target: Target hostname or IP
            port: Optional port number
            
        Returns:
            Connection test results
        """
        command = f"Test-NetConnection -ComputerName '{target}'"
        if port:
            command += f" -Port {port}"
        command += " | ConvertTo-Json"
        
        result = self.execute_command(command)
        if result.success:
            try:
                return json.loads(result.output)
            except json.JSONDecodeError:
                self.logger.error("Failed to parse network test JSON")
                return {}
        else:
            self.logger.error(f"Failed to test network connection: {result.error}")
            return {}


# Common PowerShell snippets for safe operations
COMMON_SNIPPETS = {
    "list_files": "Get-ChildItem -Path '{path}' | Select-Object Name, Length, LastWriteTime",
    "disk_usage": "Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, Size, FreeSpace",
    "system_uptime": "(Get-Date) - (Get-CimInstance Win32_OperatingSystem).LastBootUpTime",
    "installed_programs": "Get-WmiObject -Class Win32_Product | Select-Object Name, Version, Vendor",
    "network_adapters": "Get-NetAdapter | Select-Object Name, InterfaceDescription, LinkSpeed, Status",
    "services_status": "Get-Service | Where-Object {$_.Status -eq 'Running'} | Select-Object Name, Status, StartType"
}


def get_snippet(name: str, **kwargs) -> Optional[str]:
    """Get a common PowerShell snippet with parameter substitution.
    
    Args:
        name: Snippet name
        **kwargs: Parameters for snippet formatting
        
    Returns:
        Formatted PowerShell command or None if snippet not found
    """
    if name in COMMON_SNIPPETS:
        try:
            return COMMON_SNIPPETS[name].format(**kwargs)
        except KeyError as e:
            logging.getLogger(__name__).error(f"Missing parameter for snippet {name}: {e}")
            return None
    return None