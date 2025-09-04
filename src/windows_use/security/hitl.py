"""Human-in-the-Loop (HITL) Module

Module ini menyediakan sistem Human-in-the-Loop untuk meminta konfirmasi
dan persetujuan user sebelum melakukan operasi yang berisiko atau sensitif.

Fitur:
- Interactive confirmation dialogs
- Approval workflows
- User consent management
- Action review and approval
- Timeout handling
- Audit trail untuk user decisions
"""

import logging
import time
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime

try:
    import tkinter as tk
    from tkinter import messagebox, simpledialog
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    logging.warning("tkinter not available. GUI confirmations will not work.")

class ApprovalStatus(Enum):
    """Status persetujuan"""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"

class ConfirmationType(Enum):
    """Tipe konfirmasi"""
    YES_NO = "yes_no"
    OK_CANCEL = "ok_cancel"
    CUSTOM = "custom"
    TEXT_INPUT = "text_input"

@dataclass
class ApprovalRequest:
    """Request untuk persetujuan user"""
    id: str
    title: str
    message: str
    action_type: str
    parameters: Dict[str, Any]
    security_level: str
    confirmation_type: ConfirmationType
    timeout_seconds: int = 300  # 5 minutes default
    created_at: float = None
    status: ApprovalStatus = ApprovalStatus.PENDING
    user_response: Any = None
    user_comment: str = ""

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()

@dataclass
class HITLResult:
    """Hasil HITL operation"""
    approved: bool
    status: ApprovalStatus
    user_response: Any = None
    user_comment: str = ""
    response_time_seconds: float = 0
    timeout_occurred: bool = False

class HITLManager:
    """Manager untuk Human-in-the-Loop operations"""
    
    def __init__(self, default_timeout: int = 300, enable_gui: bool = True):
        """
        Args:
            default_timeout: Default timeout dalam detik
            enable_gui: Enable GUI dialogs
        """
        self.logger = logging.getLogger(__name__)
        self.default_timeout = default_timeout
        self.enable_gui = enable_gui and GUI_AVAILABLE
        
        # Pending requests
        self.pending_requests: Dict[str, ApprovalRequest] = {}
        
        # Approval history
        self.approval_history: List[ApprovalRequest] = []
        
        # User preferences
        self.user_preferences = {
            "auto_approve_low_risk": False,
            "auto_deny_high_risk": False,
            "remember_decisions": True,
            "default_timeout": default_timeout
        }
        
        # Decision cache untuk remember decisions
        self.decision_cache: Dict[str, Dict[str, Any]] = {}
        
        # Callback functions
        self.approval_callbacks: List[Callable] = []
        
        if not self.enable_gui:
            self.logger.warning("GUI not available. Using console-based confirmations.")
    
    def request_approval(self, title: str, message: str, action_type: str,
                        parameters: Dict[str, Any], security_level: str = "medium",
                        confirmation_type: ConfirmationType = ConfirmationType.YES_NO,
                        timeout_seconds: Optional[int] = None) -> HITLResult:
        """Request approval dari user
        
        Args:
            title: Judul dialog
            message: Pesan untuk user
            action_type: Tipe aksi yang akan dilakukan
            parameters: Parameter aksi
            security_level: Level keamanan (low, medium, high, critical)
            confirmation_type: Tipe konfirmasi
            timeout_seconds: Timeout dalam detik
            
        Returns:
            HITLResult
        """
        if timeout_seconds is None:
            timeout_seconds = self.default_timeout
        
        # Generate unique request ID
        request_id = f"{action_type}_{int(time.time())}_{hash(message) % 10000}"
        
        # Check decision cache
        if self.user_preferences["remember_decisions"]:
            cache_key = self._generate_cache_key(action_type, parameters)
            if cache_key in self.decision_cache:
                cached_decision = self.decision_cache[cache_key]
                self.logger.info(f"Using cached decision for {action_type}: {cached_decision['approved']}")
                return HITLResult(
                    approved=cached_decision["approved"],
                    status=ApprovalStatus.APPROVED if cached_decision["approved"] else ApprovalStatus.DENIED,
                    user_response=cached_decision.get("response"),
                    user_comment="Cached decision",
                    response_time_seconds=0
                )
        
        # Check auto-approval rules
        auto_result = self._check_auto_approval(security_level, action_type)
        if auto_result:
            return auto_result
        
        # Create approval request
        request = ApprovalRequest(
            id=request_id,
            title=title,
            message=message,
            action_type=action_type,
            parameters=parameters,
            security_level=security_level,
            confirmation_type=confirmation_type,
            timeout_seconds=timeout_seconds
        )
        
        self.pending_requests[request_id] = request
        
        try:
            # Show confirmation dialog
            result = self._show_confirmation_dialog(request)
            
            # Cache decision if approved
            if (result.approved and self.user_preferences["remember_decisions"] and 
                result.status == ApprovalStatus.APPROVED):
                cache_key = self._generate_cache_key(action_type, parameters)
                self.decision_cache[cache_key] = {
                    "approved": result.approved,
                    "response": result.user_response,
                    "timestamp": time.time()
                }
            
            # Update request status
            request.status = result.status
            request.user_response = result.user_response
            request.user_comment = result.user_comment
            
            # Move to history
            self.approval_history.append(request)
            
            # Notify callbacks
            self._notify_callbacks(request, result)
            
            return result
            
        finally:
            # Clean up pending request
            if request_id in self.pending_requests:
                del self.pending_requests[request_id]
    
    def _check_auto_approval(self, security_level: str, action_type: str) -> Optional[HITLResult]:
        """Check auto-approval rules
        
        Args:
            security_level: Level keamanan
            action_type: Tipe aksi
            
        Returns:
            HITLResult jika auto-approved/denied, None jika perlu manual approval
        """
        # Auto-approve low risk actions
        if (security_level.lower() == "low" and 
            self.user_preferences["auto_approve_low_risk"]):
            self.logger.info(f"Auto-approved low risk action: {action_type}")
            return HITLResult(
                approved=True,
                status=ApprovalStatus.APPROVED,
                user_comment="Auto-approved (low risk)",
                response_time_seconds=0
            )
        
        # Auto-deny high risk actions
        if (security_level.lower() in ["high", "critical"] and 
            self.user_preferences["auto_deny_high_risk"]):
            self.logger.info(f"Auto-denied high risk action: {action_type}")
            return HITLResult(
                approved=False,
                status=ApprovalStatus.DENIED,
                user_comment="Auto-denied (high risk)",
                response_time_seconds=0
            )
        
        return None
    
    def _show_confirmation_dialog(self, request: ApprovalRequest) -> HITLResult:
        """Show confirmation dialog to user
        
        Args:
            request: Approval request
            
        Returns:
            HITLResult
        """
        start_time = time.time()
        
        if self.enable_gui:
            return self._show_gui_dialog(request, start_time)
        else:
            return self._show_console_dialog(request, start_time)
    
    def _show_gui_dialog(self, request: ApprovalRequest, start_time: float) -> HITLResult:
        """Show GUI confirmation dialog
        
        Args:
            request: Approval request
            start_time: Start time
            
        Returns:
            HITLResult
        """
        try:
            # Create root window (hidden)
            root = tk.Tk()
            root.withdraw()
            
            # Prepare message
            full_message = f"{request.message}\n\n"
            full_message += f"Action: {request.action_type}\n"
            full_message += f"Security Level: {request.security_level.upper()}\n"
            full_message += f"Parameters: {json.dumps(request.parameters, indent=2)}"
            
            result = None
            user_response = None
            user_comment = ""
            
            if request.confirmation_type == ConfirmationType.YES_NO:
                response = messagebox.askyesno(
                    request.title,
                    full_message,
                    icon="question"
                )
                user_response = response
                result = HITLResult(
                    approved=response,
                    status=ApprovalStatus.APPROVED if response else ApprovalStatus.DENIED,
                    user_response=response,
                    response_time_seconds=time.time() - start_time
                )
            
            elif request.confirmation_type == ConfirmationType.OK_CANCEL:
                response = messagebox.askokcancel(
                    request.title,
                    full_message,
                    icon="warning"
                )
                user_response = response
                result = HITLResult(
                    approved=response,
                    status=ApprovalStatus.APPROVED if response else ApprovalStatus.CANCELLED,
                    user_response=response,
                    response_time_seconds=time.time() - start_time
                )
            
            elif request.confirmation_type == ConfirmationType.TEXT_INPUT:
                response = simpledialog.askstring(
                    request.title,
                    full_message,
                    show="*" if "password" in request.title.lower() else None
                )
                user_response = response
                result = HITLResult(
                    approved=response is not None and response.strip() != "",
                    status=ApprovalStatus.APPROVED if response else ApprovalStatus.CANCELLED,
                    user_response=response,
                    response_time_seconds=time.time() - start_time
                )
            
            # Ask for comment if denied
            if result and not result.approved and result.status == ApprovalStatus.DENIED:
                comment = simpledialog.askstring(
                    "Comment",
                    "Optional comment for denial:",
                    initialvalue=""
                )
                result.user_comment = comment or ""
            
            root.destroy()
            return result
            
        except Exception as e:
            self.logger.error(f"GUI dialog error: {e}")
            # Fallback to console
            return self._show_console_dialog(request, start_time)
    
    def _show_console_dialog(self, request: ApprovalRequest, start_time: float) -> HITLResult:
        """Show console confirmation dialog
        
        Args:
            request: Approval request
            start_time: Start time
            
        Returns:
            HITLResult
        """
        try:
            print(f"\n{'='*60}")
            print(f"APPROVAL REQUEST: {request.title}")
            print(f"{'='*60}")
            print(f"Message: {request.message}")
            print(f"Action: {request.action_type}")
            print(f"Security Level: {request.security_level.upper()}")
            print(f"Parameters: {json.dumps(request.parameters, indent=2)}")
            print(f"Timeout: {request.timeout_seconds} seconds")
            print(f"{'='*60}")
            
            if request.confirmation_type == ConfirmationType.YES_NO:
                while True:
                    response = input("Approve this action? (y/n): ").strip().lower()
                    if response in ['y', 'yes']:
                        return HITLResult(
                            approved=True,
                            status=ApprovalStatus.APPROVED,
                            user_response=True,
                            response_time_seconds=time.time() - start_time
                        )
                    elif response in ['n', 'no']:
                        comment = input("Optional comment for denial: ").strip()
                        return HITLResult(
                            approved=False,
                            status=ApprovalStatus.DENIED,
                            user_response=False,
                            user_comment=comment,
                            response_time_seconds=time.time() - start_time
                        )
                    else:
                        print("Please enter 'y' or 'n'")
            
            elif request.confirmation_type == ConfirmationType.TEXT_INPUT:
                response = input("Enter required input: ").strip()
                return HITLResult(
                    approved=response != "",
                    status=ApprovalStatus.APPROVED if response else ApprovalStatus.CANCELLED,
                    user_response=response,
                    response_time_seconds=time.time() - start_time
                )
            
            else:  # OK_CANCEL
                while True:
                    response = input("Continue with this action? (ok/cancel): ").strip().lower()
                    if response in ['ok', 'o']:
                        return HITLResult(
                            approved=True,
                            status=ApprovalStatus.APPROVED,
                            user_response=True,
                            response_time_seconds=time.time() - start_time
                        )
                    elif response in ['cancel', 'c']:
                        return HITLResult(
                            approved=False,
                            status=ApprovalStatus.CANCELLED,
                            user_response=False,
                            response_time_seconds=time.time() - start_time
                        )
                    else:
                        print("Please enter 'ok' or 'cancel'")
                        
        except KeyboardInterrupt:
            return HITLResult(
                approved=False,
                status=ApprovalStatus.CANCELLED,
                user_comment="Cancelled by user (Ctrl+C)",
                response_time_seconds=time.time() - start_time
            )
        except Exception as e:
            self.logger.error(f"Console dialog error: {e}")
            return HITLResult(
                approved=False,
                status=ApprovalStatus.DENIED,
                user_comment=f"Error: {str(e)}",
                response_time_seconds=time.time() - start_time
            )
    
    def _generate_cache_key(self, action_type: str, parameters: Dict[str, Any]) -> str:
        """Generate cache key untuk decision caching
        
        Args:
            action_type: Tipe aksi
            parameters: Parameter aksi
            
        Returns:
            Cache key string
        """
        # Create deterministic key from action and key parameters
        key_params = {
            "action_type": action_type,
            "file_path": parameters.get("file_path", ""),
            "command": parameters.get("command", ""),
            "url": parameters.get("url", "")
        }
        
        key_str = json.dumps(key_params, sort_keys=True)
        return f"{action_type}_{hash(key_str) % 100000}"
    
    def _notify_callbacks(self, request: ApprovalRequest, result: HITLResult):
        """Notify registered callbacks
        
        Args:
            request: Approval request
            result: HITL result
        """
        for callback in self.approval_callbacks:
            try:
                callback(request, result)
            except Exception as e:
                self.logger.error(f"Callback error: {e}")
    
    def add_approval_callback(self, callback: Callable[[ApprovalRequest, HITLResult], None]):
        """Add callback untuk approval events
        
        Args:
            callback: Callback function
        """
        self.approval_callbacks.append(callback)
    
    def set_user_preference(self, key: str, value: Any):
        """Set user preference
        
        Args:
            key: Preference key
            value: Preference value
        """
        if key in self.user_preferences:
            self.user_preferences[key] = value
            self.logger.info(f"User preference updated: {key} = {value}")
        else:
            self.logger.warning(f"Unknown preference key: {key}")
    
    def clear_decision_cache(self):
        """Clear decision cache"""
        self.decision_cache.clear()
        self.logger.info("Decision cache cleared")
    
    def get_approval_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get approval history
        
        Args:
            limit: Maximum number of entries
            
        Returns:
            List of approval history entries
        """
        history = []
        for request in self.approval_history[-limit:]:
            history.append({
                "id": request.id,
                "title": request.title,
                "action_type": request.action_type,
                "security_level": request.security_level,
                "status": request.status.value,
                "approved": request.status == ApprovalStatus.APPROVED,
                "created_at": datetime.fromtimestamp(request.created_at).isoformat(),
                "user_comment": request.user_comment
            })
        return history
    
    def get_pending_requests(self) -> List[Dict[str, Any]]:
        """Get pending approval requests
        
        Returns:
            List of pending requests
        """
        pending = []
        current_time = time.time()
        
        for request in self.pending_requests.values():
            # Check for timeout
            if current_time - request.created_at > request.timeout_seconds:
                request.status = ApprovalStatus.TIMEOUT
                continue
            
            pending.append({
                "id": request.id,
                "title": request.title,
                "message": request.message,
                "action_type": request.action_type,
                "security_level": request.security_level,
                "created_at": datetime.fromtimestamp(request.created_at).isoformat(),
                "timeout_in": request.timeout_seconds - (current_time - request.created_at)
            })
        
        return pending
    
    def get_hitl_status(self) -> Dict[str, Any]:
        """Get HITL system status
        
        Returns:
            Dictionary dengan status HITL
        """
        return {
            "gui_available": self.enable_gui,
            "pending_requests": len(self.pending_requests),
            "approval_history_size": len(self.approval_history),
            "decision_cache_size": len(self.decision_cache),
            "user_preferences": self.user_preferences,
            "callbacks_registered": len(self.approval_callbacks)
        }


# Example usage
if __name__ == "__main__":
    # Test HITL manager
    print("=== HITL Manager Test ===")
    
    hitl = HITLManager(enable_gui=False)  # Use console for testing
    
    # Test approval request
    result = hitl.request_approval(
        title="File Deletion Confirmation",
        message="Are you sure you want to delete this file?",
        action_type="file_delete",
        parameters={"file_path": "C:\\temp\\test.txt"},
        security_level="high",
        confirmation_type=ConfirmationType.YES_NO
    )
    
    print(f"\nApproval result:")
    print(f"  Approved: {result.approved}")
    print(f"  Status: {result.status.value}")
    print(f"  Response time: {result.response_time_seconds:.2f}s")
    print(f"  Comment: {result.user_comment}")
    
    # Test text input
    result2 = hitl.request_approval(
        title="Enter Password",
        message="Please enter your password to continue:",
        action_type="authentication",
        parameters={"auth_type": "password"},
        security_level="medium",
        confirmation_type=ConfirmationType.TEXT_INPUT
    )
    
    print(f"\nText input result:")
    print(f"  Approved: {result2.approved}")
    print(f"  Response: {'*' * len(str(result2.user_response)) if result2.user_response else 'None'}")
    
    # Show history
    print(f"\nApproval history: {len(hitl.get_approval_history())} entries")
    
    # Show status
    status = hitl.get_hitl_status()
    print(f"\nHITL Status:")
    print(f"  GUI Available: {status['gui_available']}")
    print(f"  Pending: {status['pending_requests']}")
    print(f"  History: {status['approval_history_size']}")