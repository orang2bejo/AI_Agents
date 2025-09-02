"""Security Package

Package ini menyediakan sistem keamanan dan validasi untuk Windows Use Autonomous Agent.
Termasuk guardrails, Human-in-the-Loop (HITL), dan mekanisme keamanan lainnya.

Modules:
- guardrails: Security validation dan command filtering
- hitl: Human-in-the-Loop approval system

Usage:
    from windows_use.security import GuardrailsEngine, HITLManager
    from windows_use.security import SecurityLevel, ActionType, ApprovalStatus
    
    # Initialize security components
    guardrails = GuardrailsEngine()
    hitl = HITLManager()
    
    # Validate action
    result = guardrails.validate_action(
        ActionType.FILE_DELETE,
        {"file_path": "important.txt"}
    )
    
    # Request approval if needed
    if result.requires_confirmation:
        approval = hitl.request_approval(
            "File Deletion",
            "Delete important.txt?",
            "file_delete",
            {"file_path": "important.txt"},
            result.security_level.value
        )
"""

from typing import Dict, Any, Optional
import logging

try:
    from .guardrails import (
        GuardrailsEngine,
        SecurityResult,
        SecurityLevel,
        ActionType,
        RateLimitEntry
    )
    from .hitl import (
        HITLManager,
        HITLResult,
        ApprovalRequest,
        ApprovalStatus,
    )
    from .api_security import (
        APIProvider,
        APIKeyInfo,
        APIKeyValidator,
        APIKeyEncryption,
        APIKeyManager,
        api_key_manager,
    )
    from .input_validation import (
        ValidationLevel,
        InputType,
        ValidationResult,
        InputSanitizer,
        InputValidator,
        input_validator,
        ConfirmationType
    )
    
    # Voice Authentication components
    try:
        from .voice_authentication import (
            VoiceAuthenticator,
            AuthenticationLevel,
            VoiceAuthStatus,
            PermissionType,
            VoiceProfile,
            UserPermissions,
            AuthSession,
            VoiceAuthConfig
        )
    except ImportError:
        # Voice authentication dependencies not available
        VoiceAuthenticator = None
        AuthenticationLevel = None
        VoiceAuthStatus = None
        PermissionType = None
        VoiceProfile = None
        UserPermissions = None
        AuthSession = None
        VoiceAuthConfig = None
    
    SECURITY_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Security modules not available: {e}")
    SECURITY_AVAILABLE = False
    
    # Create dummy classes for graceful degradation
    class GuardrailsEngine:
        def __init__(self, *args, **kwargs):
            raise ImportError("Security dependencies not available")
    
    class HITLManager:
        def __init__(self, *args, **kwargs):
            raise ImportError("Security dependencies not available")
    
    SecurityResult = None
    HITLResult = None
    ApprovalRequest = None
    SecurityLevel = None
    ActionType = None
    ApprovalStatus = None
    ConfirmationType = None
    RateLimitEntry = None

class SecurityManager:
    """Unified security manager yang menggabungkan guardrails dan HITL"""
    
    def __init__(self, guardrails_config: Optional[str] = None, 
                 hitl_timeout: int = 300, enable_gui: bool = True):
        """
        Args:
            guardrails_config: Path ke file konfigurasi guardrails
            hitl_timeout: Default timeout untuk HITL dalam detik
            enable_gui: Enable GUI untuk HITL
        """
        if not SECURITY_AVAILABLE:
            raise ImportError("Security dependencies not available")
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.guardrails = GuardrailsEngine(guardrails_config)
        self.hitl = HITLManager(hitl_timeout, enable_gui)
        
        # Security statistics
        self.stats = {
            "actions_validated": 0,
            "actions_blocked": 0,
            "approvals_requested": 0,
            "approvals_granted": 0,
            "approvals_denied": 0
        }
    
    async def validate_and_approve_action(self, action_type: ActionType, 
                                        parameters: Dict[str, Any],
                                        context: Dict[str, Any] = None,
                                        user_id: str = "system") -> Dict[str, Any]:
        """Validate action dengan guardrails dan request approval jika diperlukan
        
        Args:
            action_type: Tipe aksi
            parameters: Parameter aksi
            context: Konteks eksekusi
            user_id: ID user yang melakukan aksi
            
        Returns:
            Dictionary dengan hasil validasi dan approval
        """
        self.stats["actions_validated"] += 1
        
        try:
            # Step 1: Validate dengan guardrails
            security_result = self.guardrails.validate_action(
                action_type, parameters, context
            )
            
            # Log action
            self.guardrails.log_action(action_type, parameters, security_result, user_id)
            
            # If blocked by guardrails
            if not security_result.allowed:
                self.stats["actions_blocked"] += 1
                return {
                    "allowed": False,
                    "reason": security_result.reason,
                    "security_level": security_result.security_level.value,
                    "recommendations": security_result.recommendations or [],
                    "blocked_by": "guardrails"
                }
            
            # Step 2: Check if approval required
            if security_result.requires_confirmation:
                self.stats["approvals_requested"] += 1
                
                # Prepare approval message
                title = f"{action_type.value.replace('_', ' ').title()} Confirmation"
                message = f"Action: {action_type.value}\n"
                message += f"Reason: {security_result.reason}\n\n"
                
                if parameters.get("file_path"):
                    message += f"File: {parameters['file_path']}\n"
                if parameters.get("command"):
                    message += f"Command: {parameters['command']}\n"
                
                message += "\nDo you want to proceed?"
                
                # Request approval
                hitl_result = self.hitl.request_approval(
                    title=title,
                    message=message,
                    action_type=action_type.value,
                    parameters=parameters,
                    security_level=security_result.security_level.value,
                    confirmation_type=ConfirmationType.YES_NO
                )
                
                if hitl_result.approved:
                    self.stats["approvals_granted"] += 1
                    return {
                        "allowed": True,
                        "reason": "Approved by user",
                        "security_level": security_result.security_level.value,
                        "approval_status": hitl_result.status.value,
                        "user_comment": hitl_result.user_comment,
                        "response_time": hitl_result.response_time_seconds
                    }
                else:
                    self.stats["approvals_denied"] += 1
                    return {
                        "allowed": False,
                        "reason": "Denied by user",
                        "security_level": security_result.security_level.value,
                        "approval_status": hitl_result.status.value,
                        "user_comment": hitl_result.user_comment,
                        "blocked_by": "user"
                    }
            
            # Action allowed without confirmation
            return {
                "allowed": True,
                "reason": security_result.reason,
                "security_level": security_result.security_level.value,
                "recommendations": security_result.recommendations or []
            }
            
        except Exception as e:
            self.logger.error(f"Security validation error: {e}")
            self.stats["actions_blocked"] += 1
            return {
                "allowed": False,
                "reason": f"Security system error: {str(e)}",
                "security_level": "critical",
                "blocked_by": "error"
            }
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get comprehensive security status
        
        Returns:
            Dictionary dengan status keamanan lengkap
        """
        return {
            "guardrails": self.guardrails.get_security_status(),
            "hitl": self.hitl.get_hitl_status(),
            "statistics": self.stats,
            "available": SECURITY_AVAILABLE
        }
    
    def configure_user_preferences(self, preferences: Dict[str, Any]):
        """Configure user preferences untuk HITL
        
        Args:
            preferences: Dictionary dengan user preferences
        """
        for key, value in preferences.items():
            self.hitl.set_user_preference(key, value)
    
    def clear_caches(self):
        """Clear all security caches"""
        self.guardrails.clear_rate_limits()
        self.hitl.clear_decision_cache()
        self.logger.info("Security caches cleared")
    
    def export_audit_log(self, limit: int = 1000) -> Dict[str, Any]:
        """Export audit log untuk compliance
        
        Args:
            limit: Maximum number of entries
            
        Returns:
            Dictionary dengan audit log
        """
        return {
            "guardrails_audit": self.guardrails.get_audit_log(limit),
            "hitl_history": self.hitl.get_approval_history(limit),
            "statistics": self.stats,
            "exported_at": time.time()
        }

def create_security_manager(config_path: Optional[str] = None, 
                          enable_gui: bool = True) -> SecurityManager:
    """Factory function untuk membuat SecurityManager
    
    Args:
        config_path: Path ke file konfigurasi
        enable_gui: Enable GUI untuk HITL
        
    Returns:
        SecurityManager instance
        
    Raises:
        ImportError: Jika security dependencies tidak tersedia
    """
    if not SECURITY_AVAILABLE:
        raise ImportError("Security dependencies not available")
    
    return SecurityManager(
        guardrails_config=config_path,
        enable_gui=enable_gui
    )

def get_security_capabilities() -> Dict[str, Any]:
    """Get informasi kemampuan security system
    
    Returns:
        Dictionary dengan informasi capabilities
    """
    return {
        "available": SECURITY_AVAILABLE,
        "guardrails_features": [
            "Command validation",
            "File path security",
            "Rate limiting",
            "Dangerous operation detection",
            "Audit logging"
        ] if SECURITY_AVAILABLE else [],
        "hitl_features": [
            "Interactive confirmations",
            "GUI and console dialogs",
            "Decision caching",
            "Auto-approval rules",
            "Approval history",
            "Timeout handling"
        ] if SECURITY_AVAILABLE else [],
        "supported_action_types": [
            "file_read", "file_write", "file_delete",
            "system_command", "office_automation",
            "network_access", "registry_access", "process_control"
        ] if SECURITY_AVAILABLE else []
    }

# Import time for export_audit_log
import time

# Export all public classes and functions
__all__ = [
    "GuardrailsEngine",
    "HITLManager",
    "SecurityManager",
    "SecurityResult",
    "HITLResult",
    "ApprovalRequest",
    "SecurityLevel",
    "ActionType",
    "ApprovalStatus",
    "ConfirmationType",
    "RateLimitEntry",
    "create_security_manager",
    "get_security_capabilities",
    "SECURITY_AVAILABLE",
    # Voice Authentication
    "VoiceAuthenticator",
    "AuthenticationLevel",
    "VoiceAuthStatus",
    "PermissionType",
    "VoiceProfile",
    "UserPermissions",
    "AuthSession",
    "VoiceAuthConfig",
    # API Security
    "APIProvider",
    "APIKeyInfo",
    "APIKeyValidator",
    "APIKeyEncryption",
    "APIKeyManager",
    "api_key_manager",
    # Input Validation
    "ValidationLevel",
    "InputType",
    "ValidationResult",
    "InputSanitizer",
    "InputValidator",
    "input_validator"
]

# Package metadata
__version__ = "1.0.0"
__author__ = "Windows Use Autonomous Agent"
__description__ = "Security and validation system with guardrails and HITL"