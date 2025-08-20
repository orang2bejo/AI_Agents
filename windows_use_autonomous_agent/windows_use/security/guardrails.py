"""Guardrails & Security Module

Module ini menyediakan sistem keamanan dan validasi untuk Windows Use Autonomous Agent.
Termasuk validasi perintah, whitelist/blacklist, dan mekanisme keamanan lainnya.

Fitur:
- Command validation dan sanitization
- File path security checks
- Dangerous operation detection
- Rate limiting
- Permission checks
- Audit logging
"""

import logging
import os
import re
import time
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import hashlib
from pathlib import Path

class SecurityLevel(Enum):
    """Security levels untuk operasi"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ActionType(Enum):
    """Tipe aksi yang dapat dilakukan"""
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    FILE_DELETE = "file_delete"
    SYSTEM_COMMAND = "system_command"
    OFFICE_AUTOMATION = "office_automation"
    NETWORK_ACCESS = "network_access"
    REGISTRY_ACCESS = "registry_access"
    PROCESS_CONTROL = "process_control"

@dataclass
class SecurityResult:
    """Hasil validasi keamanan"""
    allowed: bool
    reason: str
    security_level: SecurityLevel
    recommendations: List[str] = None
    requires_confirmation: bool = False

@dataclass
class RateLimitEntry:
    """Entry untuk rate limiting"""
    count: int
    first_request: float
    last_request: float

class GuardrailsEngine:
    """Engine untuk validasi keamanan dan guardrails"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Args:
            config_path: Path ke file konfigurasi keamanan
        """
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Rate limiting storage
        self.rate_limits: Dict[str, RateLimitEntry] = {}
        
        # Audit log
        self.audit_log: List[Dict[str, Any]] = []
        
        # Initialize security rules
        self._init_security_rules()
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load security configuration
        
        Args:
            config_path: Path ke file konfigurasi
            
        Returns:
            Dictionary konfigurasi
        """
        default_config = {
            "max_file_size_mb": 100,
            "allowed_file_extensions": [
                ".txt", ".docx", ".xlsx", ".pptx", ".pdf", ".csv", ".json", ".xml"
            ],
            "blocked_file_extensions": [
                ".exe", ".bat", ".cmd", ".ps1", ".vbs", ".scr", ".com", ".pif"
            ],
            "protected_directories": [
                "C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)",
                "C:\\System32", "C:\\Users\\All Users"
            ],
            "allowed_commands": [
                "dir", "ls", "pwd", "cd", "type", "cat", "echo", "find", "grep"
            ],
            "blocked_commands": [
                "format", "del", "rm", "rmdir", "rd", "shutdown", "restart",
                "net", "sc", "reg", "regedit", "taskkill", "wmic"
            ],
            "rate_limit_requests_per_minute": 60,
            "rate_limit_window_seconds": 60,
            "require_confirmation_for": [
                ActionType.FILE_DELETE.value,
                ActionType.SYSTEM_COMMAND.value,
                ActionType.REGISTRY_ACCESS.value
            ]
        }
        
        if config_path and os.path.exists(config_path):
            try:
                import json
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"Failed to load config from {config_path}: {e}")
        
        return default_config
    
    def _init_security_rules(self):
        """Initialize security rules dan patterns"""
        # Dangerous command patterns
        self.dangerous_patterns = [
            r'\b(format|del|rm|rmdir)\s+[a-zA-Z]:\\',  # Format/delete drive
            r'\b(shutdown|restart)\b',  # System shutdown
            r'\breg\s+(delete|add)\b',  # Registry modification
            r'\bnet\s+(user|localgroup)\b',  # User management
            r'\bsc\s+(delete|create|config)\b',  # Service control
            r'\btaskkill\s+/f\b',  # Force kill processes
            r'\bwmic\b.*\b(delete|create)\b',  # WMI operations
        ]
        
        # Suspicious file patterns
        self.suspicious_file_patterns = [
            r'.*\.(exe|bat|cmd|ps1|vbs|scr|com|pif)$',  # Executable files
            r'.*\\(system32|windows|program files)\\.*',  # System directories
            r'.*\\(autoexec|config|boot)\..*',  # System files
        ]
        
        # Safe directories for file operations
        self.safe_directories = [
            os.path.expanduser("~"),  # User home
            os.path.join(os.path.expanduser("~"), "Documents"),
            os.path.join(os.path.expanduser("~"), "Desktop"),
            os.path.join(os.path.expanduser("~"), "Downloads"),
            "D:\\Project Jarvis",  # Project directory
        ]
    
    def validate_action(self, action_type: ActionType, parameters: Dict[str, Any], 
                       context: Dict[str, Any] = None) -> SecurityResult:
        """Validate action berdasarkan security rules
        
        Args:
            action_type: Tipe aksi yang akan dilakukan
            parameters: Parameter aksi
            context: Konteks eksekusi
            
        Returns:
            SecurityResult
        """
        try:
            # Check rate limiting
            if not self._check_rate_limit(action_type):
                return SecurityResult(
                    allowed=False,
                    reason="Rate limit exceeded",
                    security_level=SecurityLevel.MEDIUM,
                    recommendations=["Wait before retrying", "Reduce request frequency"]
                )
            
            # Validate based on action type
            if action_type == ActionType.FILE_READ:
                return self._validate_file_read(parameters)
            elif action_type == ActionType.FILE_WRITE:
                return self._validate_file_write(parameters)
            elif action_type == ActionType.FILE_DELETE:
                return self._validate_file_delete(parameters)
            elif action_type == ActionType.SYSTEM_COMMAND:
                return self._validate_system_command(parameters)
            elif action_type == ActionType.OFFICE_AUTOMATION:
                return self._validate_office_automation(parameters)
            elif action_type == ActionType.NETWORK_ACCESS:
                return self._validate_network_access(parameters)
            elif action_type == ActionType.REGISTRY_ACCESS:
                return self._validate_registry_access(parameters)
            elif action_type == ActionType.PROCESS_CONTROL:
                return self._validate_process_control(parameters)
            else:
                return SecurityResult(
                    allowed=False,
                    reason=f"Unknown action type: {action_type}",
                    security_level=SecurityLevel.HIGH
                )
                
        except Exception as e:
            self.logger.error(f"Security validation error: {e}")
            return SecurityResult(
                allowed=False,
                reason=f"Security validation failed: {str(e)}",
                security_level=SecurityLevel.CRITICAL
            )
    
    def _check_rate_limit(self, action_type: ActionType) -> bool:
        """Check rate limiting untuk action type
        
        Args:
            action_type: Tipe aksi
            
        Returns:
            True jika dalam batas rate limit
        """
        current_time = time.time()
        key = action_type.value
        
        if key not in self.rate_limits:
            self.rate_limits[key] = RateLimitEntry(
                count=1,
                first_request=current_time,
                last_request=current_time
            )
            return True
        
        entry = self.rate_limits[key]
        window_seconds = self.config["rate_limit_window_seconds"]
        max_requests = self.config["rate_limit_requests_per_minute"]
        
        # Reset window if expired
        if current_time - entry.first_request > window_seconds:
            entry.count = 1
            entry.first_request = current_time
            entry.last_request = current_time
            return True
        
        # Check if within limit
        if entry.count >= max_requests:
            return False
        
        # Update counter
        entry.count += 1
        entry.last_request = current_time
        return True
    
    def _validate_file_read(self, parameters: Dict[str, Any]) -> SecurityResult:
        """Validate file read operation
        
        Args:
            parameters: Parameter operasi file
            
        Returns:
            SecurityResult
        """
        file_path = parameters.get("file_path", "")
        
        if not file_path:
            return SecurityResult(
                allowed=False,
                reason="File path not specified",
                security_level=SecurityLevel.LOW
            )
        
        # Check if file exists
        if not os.path.exists(file_path):
            return SecurityResult(
                allowed=False,
                reason=f"File does not exist: {file_path}",
                security_level=SecurityLevel.LOW
            )
        
        # Check file size
        try:
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if file_size_mb > self.config["max_file_size_mb"]:
                return SecurityResult(
                    allowed=False,
                    reason=f"File too large: {file_size_mb:.1f}MB > {self.config['max_file_size_mb']}MB",
                    security_level=SecurityLevel.MEDIUM,
                    recommendations=["Use smaller files", "Increase size limit in config"]
                )
        except Exception as e:
            self.logger.warning(f"Could not check file size: {e}")
        
        # Check if in protected directory
        if self._is_protected_path(file_path):
            return SecurityResult(
                allowed=False,
                reason=f"Access to protected directory denied: {file_path}",
                security_level=SecurityLevel.HIGH,
                recommendations=["Use files in user directories", "Request admin permission"]
            )
        
        return SecurityResult(
            allowed=True,
            reason="File read operation allowed",
            security_level=SecurityLevel.LOW
        )
    
    def _validate_file_write(self, parameters: Dict[str, Any]) -> SecurityResult:
        """Validate file write operation
        
        Args:
            parameters: Parameter operasi file
            
        Returns:
            SecurityResult
        """
        file_path = parameters.get("file_path", "")
        
        if not file_path:
            return SecurityResult(
                allowed=False,
                reason="File path not specified",
                security_level=SecurityLevel.LOW
            )
        
        # Check file extension
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext in self.config["blocked_file_extensions"]:
            return SecurityResult(
                allowed=False,
                reason=f"Blocked file extension: {file_ext}",
                security_level=SecurityLevel.HIGH,
                recommendations=["Use allowed file types", "Check security policy"]
            )
        
        # Check if in protected directory
        if self._is_protected_path(file_path):
            return SecurityResult(
                allowed=False,
                reason=f"Write to protected directory denied: {file_path}",
                security_level=SecurityLevel.HIGH,
                recommendations=["Write to user directories", "Request admin permission"]
            )
        
        # Check if overwriting important file
        if os.path.exists(file_path):
            if self._is_important_file(file_path):
                return SecurityResult(
                    allowed=False,
                    reason=f"Overwriting important file denied: {file_path}",
                    security_level=SecurityLevel.HIGH,
                    requires_confirmation=True,
                    recommendations=["Backup file first", "Use different filename"]
                )
        
        return SecurityResult(
            allowed=True,
            reason="File write operation allowed",
            security_level=SecurityLevel.LOW
        )
    
    def _validate_file_delete(self, parameters: Dict[str, Any]) -> SecurityResult:
        """Validate file delete operation
        
        Args:
            parameters: Parameter operasi file
            
        Returns:
            SecurityResult
        """
        file_path = parameters.get("file_path", "")
        
        if not file_path:
            return SecurityResult(
                allowed=False,
                reason="File path not specified",
                security_level=SecurityLevel.LOW
            )
        
        # Check if in protected directory
        if self._is_protected_path(file_path):
            return SecurityResult(
                allowed=False,
                reason=f"Delete from protected directory denied: {file_path}",
                security_level=SecurityLevel.CRITICAL,
                recommendations=["Delete from user directories only", "Request admin permission"]
            )
        
        # Check if important file
        if self._is_important_file(file_path):
            return SecurityResult(
                allowed=False,
                reason=f"Deleting important file denied: {file_path}",
                security_level=SecurityLevel.CRITICAL,
                requires_confirmation=True,
                recommendations=["Backup file first", "Confirm deletion is necessary"]
            )
        
        # Always require confirmation for delete
        return SecurityResult(
            allowed=True,
            reason="File delete operation allowed with confirmation",
            security_level=SecurityLevel.HIGH,
            requires_confirmation=True,
            recommendations=["Confirm deletion", "Ensure file is backed up"]
        )
    
    def _validate_system_command(self, parameters: Dict[str, Any]) -> SecurityResult:
        """Validate system command execution
        
        Args:
            parameters: Parameter command
            
        Returns:
            SecurityResult
        """
        command = parameters.get("command", "")
        
        if not command:
            return SecurityResult(
                allowed=False,
                reason="Command not specified",
                security_level=SecurityLevel.LOW
            )
        
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return SecurityResult(
                    allowed=False,
                    reason=f"Dangerous command pattern detected: {pattern}",
                    security_level=SecurityLevel.CRITICAL,
                    recommendations=["Use safer alternatives", "Request admin permission"]
                )
        
        # Check blocked commands
        command_parts = command.split()
        if command_parts:
            base_command = command_parts[0].lower()
            if base_command in self.config["blocked_commands"]:
                return SecurityResult(
                    allowed=False,
                    reason=f"Blocked command: {base_command}",
                    security_level=SecurityLevel.HIGH,
                    recommendations=["Use allowed commands", "Check security policy"]
                )
        
        # Check if command is in allowed list
        if command_parts:
            base_command = command_parts[0].lower()
            if base_command in self.config["allowed_commands"]:
                return SecurityResult(
                    allowed=True,
                    reason="Command in allowed list",
                    security_level=SecurityLevel.LOW
                )
        
        # Unknown command - require confirmation
        return SecurityResult(
            allowed=True,
            reason="Unknown command - requires confirmation",
            security_level=SecurityLevel.MEDIUM,
            requires_confirmation=True,
            recommendations=["Verify command safety", "Check command documentation"]
        )
    
    def _validate_office_automation(self, parameters: Dict[str, Any]) -> SecurityResult:
        """Validate Office automation operation
        
        Args:
            parameters: Parameter operasi Office
            
        Returns:
            SecurityResult
        """
        action = parameters.get("action", "")
        file_path = parameters.get("file_path", "")
        
        # Office automation is generally safe
        if file_path and self._is_protected_path(file_path):
            return SecurityResult(
                allowed=False,
                reason=f"Office operation on protected file denied: {file_path}",
                security_level=SecurityLevel.MEDIUM,
                recommendations=["Use files in user directories", "Request permission"]
            )
        
        return SecurityResult(
            allowed=True,
            reason="Office automation operation allowed",
            security_level=SecurityLevel.LOW
        )
    
    def _validate_network_access(self, parameters: Dict[str, Any]) -> SecurityResult:
        """Validate network access operation
        
        Args:
            parameters: Parameter network access
            
        Returns:
            SecurityResult
        """
        url = parameters.get("url", "")
        
        if not url:
            return SecurityResult(
                allowed=False,
                reason="URL not specified",
                security_level=SecurityLevel.LOW
            )
        
        # Basic URL validation
        if not (url.startswith("http://") or url.startswith("https://")):
            return SecurityResult(
                allowed=False,
                reason="Invalid URL protocol",
                security_level=SecurityLevel.MEDIUM,
                recommendations=["Use HTTP/HTTPS URLs only"]
            )
        
        # Network access requires confirmation
        return SecurityResult(
            allowed=True,
            reason="Network access allowed with confirmation",
            security_level=SecurityLevel.MEDIUM,
            requires_confirmation=True,
            recommendations=["Verify URL safety", "Check network policy"]
        )
    
    def _validate_registry_access(self, parameters: Dict[str, Any]) -> SecurityResult:
        """Validate registry access operation
        
        Args:
            parameters: Parameter registry access
            
        Returns:
            SecurityResult
        """
        # Registry access is always high risk
        return SecurityResult(
            allowed=False,
            reason="Registry access denied by security policy",
            security_level=SecurityLevel.CRITICAL,
            recommendations=["Use alternative methods", "Request admin permission"]
        )
    
    def _validate_process_control(self, parameters: Dict[str, Any]) -> SecurityResult:
        """Validate process control operation
        
        Args:
            parameters: Parameter process control
            
        Returns:
            SecurityResult
        """
        action = parameters.get("action", "")
        process_name = parameters.get("process_name", "")
        
        # Process control requires confirmation
        return SecurityResult(
            allowed=True,
            reason="Process control allowed with confirmation",
            security_level=SecurityLevel.HIGH,
            requires_confirmation=True,
            recommendations=["Verify process safety", "Backup important data"]
        )
    
    def _is_protected_path(self, file_path: str) -> bool:
        """Check if path is in protected directory
        
        Args:
            file_path: Path to check
            
        Returns:
            True if path is protected
        """
        try:
            abs_path = os.path.abspath(file_path)
            for protected_dir in self.config["protected_directories"]:
                if abs_path.lower().startswith(protected_dir.lower()):
                    return True
            return False
        except Exception:
            return True  # Err on the side of caution
    
    def _is_important_file(self, file_path: str) -> bool:
        """Check if file is important system file
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file is important
        """
        important_patterns = [
            r'.*\.(sys|dll|exe|ini)$',
            r'.*\\(boot|config|autoexec)\.',
            r'.*\\(ntldr|bootmgr|pagefile)\.',
        ]
        
        for pattern in important_patterns:
            if re.match(pattern, file_path, re.IGNORECASE):
                return True
        
        return False
    
    def log_action(self, action_type: ActionType, parameters: Dict[str, Any], 
                  result: SecurityResult, user_id: str = "system"):
        """Log action untuk audit trail
        
        Args:
            action_type: Tipe aksi
            parameters: Parameter aksi
            result: Hasil validasi
            user_id: ID user yang melakukan aksi
        """
        log_entry = {
            "timestamp": time.time(),
            "user_id": user_id,
            "action_type": action_type.value,
            "parameters": parameters,
            "allowed": result.allowed,
            "reason": result.reason,
            "security_level": result.security_level.value,
            "requires_confirmation": result.requires_confirmation
        }
        
        self.audit_log.append(log_entry)
        
        # Log to file
        self.logger.info(f"Security audit: {log_entry}")
    
    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit log entries
        
        Args:
            limit: Maximum number of entries
            
        Returns:
            List of audit log entries
        """
        return self.audit_log[-limit:]
    
    def clear_rate_limits(self):
        """Clear rate limit counters"""
        self.rate_limits.clear()
        self.logger.info("Rate limits cleared")
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get current security status
        
        Returns:
            Dictionary dengan status keamanan
        """
        return {
            "rate_limits": {
                action: {
                    "count": entry.count,
                    "window_remaining": max(0, self.config["rate_limit_window_seconds"] - 
                                           (time.time() - entry.first_request))
                }
                for action, entry in self.rate_limits.items()
            },
            "audit_log_size": len(self.audit_log),
            "config": self.config
        }


# Example usage
if __name__ == "__main__":
    # Test guardrails engine
    print("=== Guardrails Engine Test ===")
    
    engine = GuardrailsEngine()
    
    # Test file operations
    print("\n--- File Operations ---")
    
    # Safe file read
    result = engine.validate_action(
        ActionType.FILE_READ,
        {"file_path": "C:\\Users\\test\\document.txt"}
    )
    print(f"File read: {result.allowed} - {result.reason}")
    
    # Dangerous file write
    result = engine.validate_action(
        ActionType.FILE_WRITE,
        {"file_path": "C:\\Windows\\System32\\malware.exe"}
    )
    print(f"Dangerous write: {result.allowed} - {result.reason}")
    
    # Test system commands
    print("\n--- System Commands ---")
    
    # Safe command
    result = engine.validate_action(
        ActionType.SYSTEM_COMMAND,
        {"command": "dir C:\\Users"}
    )
    print(f"Safe command: {result.allowed} - {result.reason}")
    
    # Dangerous command
    result = engine.validate_action(
        ActionType.SYSTEM_COMMAND,
        {"command": "format C: /q"}
    )
    print(f"Dangerous command: {result.allowed} - {result.reason}")
    
    # Test rate limiting
    print("\n--- Rate Limiting ---")
    for i in range(5):
        result = engine.validate_action(
            ActionType.FILE_READ,
            {"file_path": "test.txt"}
        )
        print(f"Request {i+1}: {result.allowed}")
    
    # Security status
    print("\n--- Security Status ---")
    status = engine.get_security_status()
    print(f"Rate limits: {len(status['rate_limits'])}")
    print(f"Audit log: {status['audit_log_size']} entries")