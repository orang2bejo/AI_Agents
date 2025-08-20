"""Intent Router untuk Windows Use Autonomous Agent

Module ini bertanggung jawab untuk:
1. Menerima parsed intent dari grammar parser
2. Mengarahkan ke handler yang sesuai (Office COM, System Tools, dll)
3. Fallback ke LLM jika grammar parser tidak confident
4. Koordinasi antara berbagai backend
"""

import logging
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from enum import Enum
import asyncio

from .grammar_id import GrammarParserID, ParsedIntent, IntentType

class RouterResult(Enum):
    """Hasil routing"""
    SUCCESS = "success"
    FAILED = "failed"
    FALLBACK_LLM = "fallback_llm"
    UNSUPPORTED = "unsupported"

@dataclass
class ExecutionResult:
    """Hasil eksekusi command"""
    status: RouterResult
    message: str
    data: Optional[Dict[str, Any]] = None
    execution_time: float = 0.0
    handler_used: str = ""

class IntentRouter:
    """Router untuk mengarahkan intent ke handler yang tepat"""
    
    def __init__(self, confidence_threshold: float = 0.7):
        """
        Args:
            confidence_threshold: Minimum confidence untuk fast path execution
        """
        self.confidence_threshold = confidence_threshold
        self.grammar_parser = GrammarParserID()
        self.handlers: Dict[IntentType, Callable] = {}
        self.fallback_handler: Optional[Callable] = None
        
        # Statistics
        self.stats = {
            "total_requests": 0,
            "fast_path_success": 0,
            "fallback_used": 0,
            "failures": 0
        }
        
        self.logger = logging.getLogger(__name__)
    
    def register_handler(self, intent_type: IntentType, handler: Callable):
        """Register handler untuk intent type tertentu
        
        Args:
            intent_type: Jenis intent
            handler: Function handler yang akan dipanggil
        """
        self.handlers[intent_type] = handler
        self.logger.info(f"Registered handler for {intent_type.value}")
    
    def register_fallback_handler(self, handler: Callable):
        """Register fallback handler (biasanya LLM-based)
        
        Args:
            handler: Fallback handler function
        """
        self.fallback_handler = handler
        self.logger.info("Registered fallback handler")
    
    async def route_and_execute(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> ExecutionResult:
        """Route user input dan eksekusi command
        
        Args:
            user_input: Input dari user
            context: Additional context (current app, file, dll)
            
        Returns:
            ExecutionResult
        """
        import time
        start_time = time.time()
        
        self.stats["total_requests"] += 1
        
        try:
            # Parse intent menggunakan grammar parser
            parsed_intent = self.grammar_parser.parse(user_input)
            
            self.logger.info(f"Parsed intent: {parsed_intent.intent_type.value} "
                           f"(confidence: {parsed_intent.confidence:.2f})")
            
            # Cek apakah confidence cukup untuk fast path
            if (parsed_intent.fast_path and 
                parsed_intent.confidence >= self.confidence_threshold and
                parsed_intent.intent_type != IntentType.UNKNOWN):
                
                # Fast path execution
                result = await self._execute_fast_path(parsed_intent, context)
                
                if result.status == RouterResult.SUCCESS:
                    self.stats["fast_path_success"] += 1
                    result.execution_time = time.time() - start_time
                    return result
            
            # Fallback ke LLM jika:
            # 1. Confidence rendah
            # 2. Intent unknown
            # 3. Fast path gagal
            if self.fallback_handler:
                self.logger.info("Using fallback handler (LLM)")
                result = await self._execute_fallback(user_input, parsed_intent, context)
                self.stats["fallback_used"] += 1
                result.execution_time = time.time() - start_time
                return result
            else:
                # No fallback available
                self.stats["failures"] += 1
                return ExecutionResult(
                    status=RouterResult.UNSUPPORTED,
                    message=f"Perintah tidak dikenali: {user_input}",
                    execution_time=time.time() - start_time
                )
                
        except Exception as e:
            self.logger.error(f"Error in routing: {e}")
            self.stats["failures"] += 1
            return ExecutionResult(
                status=RouterResult.FAILED,
                message=f"Error: {str(e)}",
                execution_time=time.time() - start_time
            )
    
    async def _execute_fast_path(self, intent: ParsedIntent, context: Optional[Dict[str, Any]]) -> ExecutionResult:
        """Execute menggunakan fast path (grammar-based)
        
        Args:
            intent: Parsed intent
            context: Execution context
            
        Returns:
            ExecutionResult
        """
        handler = self.handlers.get(intent.intent_type)
        
        if not handler:
            return ExecutionResult(
                status=RouterResult.UNSUPPORTED,
                message=f"No handler for {intent.intent_type.value}"
            )
        
        try:
            # Prepare execution parameters
            exec_params = {
                "action": intent.action,
                "parameters": intent.parameters,
                "context": context or {},
                "original_text": intent.original_text
            }
            
            # Execute handler
            if asyncio.iscoroutinefunction(handler):
                result = await handler(**exec_params)
            else:
                result = handler(**exec_params)
            
            return ExecutionResult(
                status=RouterResult.SUCCESS,
                message=result.get("message", "Command executed successfully"),
                data=result.get("data"),
                handler_used=f"fast_path_{intent.intent_type.value}"
            )
            
        except Exception as e:
            self.logger.error(f"Fast path execution failed: {e}")
            return ExecutionResult(
                status=RouterResult.FAILED,
                message=f"Execution failed: {str(e)}",
                handler_used=f"fast_path_{intent.intent_type.value}"
            )
    
    async def _execute_fallback(self, user_input: str, parsed_intent: ParsedIntent, 
                              context: Optional[Dict[str, Any]]) -> ExecutionResult:
        """Execute menggunakan fallback handler (LLM)
        
        Args:
            user_input: Original user input
            parsed_intent: Parsed intent (mungkin low confidence)
            context: Execution context
            
        Returns:
            ExecutionResult
        """
        try:
            fallback_params = {
                "user_input": user_input,
                "parsed_intent": parsed_intent,
                "context": context or {},
                "available_handlers": list(self.handlers.keys())
            }
            
            if asyncio.iscoroutinefunction(self.fallback_handler):
                result = await self.fallback_handler(**fallback_params)
            else:
                result = self.fallback_handler(**fallback_params)
            
            return ExecutionResult(
                status=RouterResult.FALLBACK_LLM,
                message=result.get("message", "Command executed via LLM"),
                data=result.get("data"),
                handler_used="fallback_llm"
            )
            
        except Exception as e:
            self.logger.error(f"Fallback execution failed: {e}")
            return ExecutionResult(
                status=RouterResult.FAILED,
                message=f"Fallback execution failed: {str(e)}",
                handler_used="fallback_llm"
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get router statistics
        
        Returns:
            Statistics dictionary
        """
        total = self.stats["total_requests"]
        if total == 0:
            return self.stats.copy()
        
        stats_with_percentages = self.stats.copy()
        stats_with_percentages.update({
            "fast_path_success_rate": (self.stats["fast_path_success"] / total) * 100,
            "fallback_rate": (self.stats["fallback_used"] / total) * 100,
            "failure_rate": (self.stats["failures"] / total) * 100
        })
        
        return stats_with_percentages
    
    def reset_stats(self):
        """Reset statistics"""
        self.stats = {
            "total_requests": 0,
            "fast_path_success": 0,
            "fallback_used": 0,
            "failures": 0
        }
    
    def get_supported_commands(self) -> Dict[str, List[str]]:
        """Get supported commands dari grammar parser
        
        Returns:
            Dictionary of supported commands
        """
        return self.grammar_parser.get_supported_commands()
    
    def set_confidence_threshold(self, threshold: float):
        """Update confidence threshold
        
        Args:
            threshold: New confidence threshold (0.0-1.0)
        """
        if 0.0 <= threshold <= 1.0:
            self.confidence_threshold = threshold
            self.logger.info(f"Updated confidence threshold to {threshold}")
        else:
            raise ValueError("Confidence threshold must be between 0.0 and 1.0")


class ContextManager:
    """Manage execution context untuk router"""
    
    def __init__(self):
        self.current_context = {
            "active_app": None,
            "current_file": None,
            "working_directory": None,
            "last_action": None,
            "session_data": {}
        }
    
    def update_context(self, **kwargs):
        """Update context dengan key-value pairs
        
        Args:
            **kwargs: Context updates
        """
        self.current_context.update(kwargs)
    
    def get_context(self) -> Dict[str, Any]:
        """Get current context
        
        Returns:
            Current context dictionary
        """
        return self.current_context.copy()
    
    def set_active_app(self, app_name: str):
        """Set currently active application
        
        Args:
            app_name: Name of active application
        """
        self.current_context["active_app"] = app_name
    
    def set_current_file(self, file_path: str):
        """Set currently active file
        
        Args:
            file_path: Path to current file
        """
        self.current_context["current_file"] = file_path
    
    def clear_context(self):
        """Clear all context"""
        self.current_context = {
            "active_app": None,
            "current_file": None,
            "working_directory": None,
            "last_action": None,
            "session_data": {}
        }


# Example usage dan testing
if __name__ == "__main__":
    import asyncio
    
    async def mock_office_handler(**kwargs):
        """Mock handler untuk Office operations"""
        action = kwargs.get("action")
        params = kwargs.get("parameters", {})
        
        return {
            "message": f"Executed {action} with params {params}",
            "data": {"success": True}
        }
    
    async def mock_fallback_handler(**kwargs):
        """Mock fallback handler"""
        user_input = kwargs.get("user_input")
        
        return {
            "message": f"LLM processed: {user_input}",
            "data": {"llm_used": True}
        }
    
    async def test_router():
        # Setup router
        router = IntentRouter(confidence_threshold=0.7)
        context_manager = ContextManager()
        
        # Register handlers
        router.register_handler(IntentType.OFFICE_EXCEL, mock_office_handler)
        router.register_handler(IntentType.OFFICE_WORD, mock_office_handler)
        router.register_fallback_handler(mock_fallback_handler)
        
        # Test commands
        test_commands = [
            "buka excel",
            "tambah sheet 'Laporan'",
            "perintah yang sangat kompleks dan tidak jelas",
            "ganti semua 'lama' jadi 'baru'"
        ]
        
        print("=== Intent Router Test ===")
        
        for cmd in test_commands:
            print(f"\nTesting: {cmd}")
            result = await router.route_and_execute(cmd, context_manager.get_context())
            
            print(f"Status: {result.status.value}")
            print(f"Message: {result.message}")
            print(f"Handler: {result.handler_used}")
            print(f"Time: {result.execution_time:.3f}s")
        
        # Print statistics
        print("\n=== Router Statistics ===")
        stats = router.get_stats()
        for key, value in stats.items():
            if isinstance(value, float):
                print(f"{key}: {value:.2f}")
            else:
                print(f"{key}: {value}")
    
    # Run test
    asyncio.run(test_router())