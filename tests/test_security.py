#!/usr/bin/env python3
"""
Unit Tests for Security Module

Tests for security guardrails, authentication, and validation components.

Author: Jarvis AI Team
Date: 2024
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from windows_use.security.guardrails import (
        GuardrailsEngine,
        SecurityLevel,
        ActionType,
        SecurityResult
    )
    from windows_use.security.input_validation import InputValidator
except ImportError as e:
    pytest.skip(f"Security modules not available: {e}", allow_module_level=True)


class TestGuardrailsEngine:
    """Test cases for GuardrailsEngine"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.engine = GuardrailsEngine()
    
    @pytest.mark.unit
    @pytest.mark.security
    def test_initialization(self):
        """Test GuardrailsEngine initialization"""
        assert self.engine is not None
        assert hasattr(self.engine, 'security_level')
    
    @pytest.mark.unit
    @pytest.mark.security
    def test_validate_command_safe(self):
        """Test validation of safe commands"""
        safe_commands = [
            "dir",
            "ls -la",
            "python --version",
            "echo hello"
        ]
        
        for cmd in safe_commands:
            result = self.engine.validate_command(cmd)
            assert isinstance(result, SecurityResult)
            assert result.is_allowed or result.action_type == ActionType.ALLOW
    
    @pytest.mark.unit
    @pytest.mark.security
    def test_validate_command_dangerous(self):
        """Test validation of dangerous commands"""
        dangerous_commands = [
            "rm -rf /",
            "del /f /s /q C:\\",
            "format C:",
            "shutdown -s -t 0",
            "dd if=/dev/zero of=/dev/sda"
        ]
        
        for cmd in dangerous_commands:
            result = self.engine.validate_command(cmd)
            assert isinstance(result, SecurityResult)
            assert not result.is_allowed or result.action_type == ActionType.BLOCK
    
    @pytest.mark.unit
    @pytest.mark.security
    def test_validate_file_path_safe(self):
        """Test validation of safe file paths"""
        safe_paths = [
            "./data/test.txt",
            "C:\\Users\\Public\\Documents\\test.doc",
            "/home/user/documents/file.pdf"
        ]
        
        for path in safe_paths:
            result = self.engine.validate_file_path(path)
            assert isinstance(result, SecurityResult)
    
    @pytest.mark.unit
    @pytest.mark.security
    def test_validate_file_path_dangerous(self):
        """Test validation of dangerous file paths"""
        dangerous_paths = [
            "C:\\Windows\\System32\\config\\SAM",
            "/etc/passwd",
            "../../../etc/shadow",
            "C:\\Windows\\System32\\drivers\\etc\\hosts"
        ]
        
        for path in dangerous_paths:
            result = self.engine.validate_file_path(path)
            assert isinstance(result, SecurityResult)
            # Should either block or require elevated permissions
    
    @pytest.mark.unit
    @pytest.mark.security
    def test_security_levels(self):
        """Test different security levels"""
        levels = [SecurityLevel.STRICT, SecurityLevel.MODERATE, SecurityLevel.PERMISSIVE]
        
        for level in levels:
            self.engine.set_security_level(level)
            assert self.engine.security_level == level
    
    @pytest.mark.unit
    @pytest.mark.security
    def test_domain_allowlist(self):
        """Test domain allowlist functionality"""
        # Test adding domains to allowlist
        safe_domains = ["github.com", "stackoverflow.com", "python.org"]
        
        for domain in safe_domains:
            self.engine.add_allowed_domain(domain)
        
        # Test domain validation
        for domain in safe_domains:
            assert self.engine.is_domain_allowed(domain)
        
        # Test blocked domains
        blocked_domains = ["malicious-site.com", "phishing-example.org"]
        for domain in blocked_domains:
            assert not self.engine.is_domain_allowed(domain)


class TestInputValidator:
    """Test cases for InputValidator"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.validator = InputValidator()
    
    @pytest.mark.unit
    @pytest.mark.security
    def test_sanitize_input(self):
        """Test input sanitization"""
        test_cases = [
            ("normal text", "normal text"),
            ("<script>alert('xss')</script>", "alert('xss')"),
            ("SELECT * FROM users; DROP TABLE users;", "SELECT * FROM users; DROP TABLE users;"),
            ("../../../etc/passwd", "../../../etc/passwd")
        ]
        
        for input_text, expected in test_cases:
            result = self.validator.sanitize_input(input_text)
            # Basic sanitization should remove dangerous patterns
            assert "<script>" not in result
    
    @pytest.mark.unit
    @pytest.mark.security
    def test_validate_email(self):
        """Test email validation"""
        valid_emails = [
            "user@example.com",
            "test.email+tag@domain.co.uk",
            "user123@test-domain.org"
        ]
        
        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "user@",
            "user space@domain.com"
        ]
        
        for email in valid_emails:
            assert self.validator.validate_email(email)
        
        for email in invalid_emails:
            assert not self.validator.validate_email(email)
    
    @pytest.mark.unit
    @pytest.mark.security
    def test_validate_url(self):
        """Test URL validation"""
        valid_urls = [
            "https://www.example.com",
            "http://localhost:8080",
            "https://api.github.com/repos"
        ]
        
        invalid_urls = [
            "not-a-url",
            "ftp://malicious-site.com",
            "javascript:alert('xss')"
        ]
        
        for url in valid_urls:
            assert self.validator.validate_url(url)
        
        for url in invalid_urls:
            assert not self.validator.validate_url(url)


@pytest.mark.integration
@pytest.mark.security
class TestSecurityIntegration:
    """Integration tests for security components"""
    
    def setup_method(self):
        """Set up integration test fixtures"""
        self.engine = GuardrailsEngine()
        self.validator = InputValidator()
    
    def test_end_to_end_validation(self):
        """Test end-to-end security validation"""
        # Simulate a complete validation workflow
        user_input = "python scripts/jarvis_main.py --help"
        
        # Step 1: Input validation
        sanitized_input = self.validator.sanitize_input(user_input)
        
        # Step 2: Command validation
        security_result = self.engine.validate_command(sanitized_input)
        
        # Step 3: Verify result
        assert isinstance(security_result, SecurityResult)
        assert security_result.is_allowed  # This should be a safe command
    
    def test_security_escalation_workflow(self):
        """Test security escalation for restricted operations"""
        restricted_command = "shutdown -s -t 0"
        
        # Should be blocked or require escalation
        result = self.engine.validate_command(restricted_command)
        assert isinstance(result, SecurityResult)
        
        # Should either be blocked or require human approval
        assert not result.is_allowed or result.requires_human_approval


if __name__ == "__main__":
    pytest.main([__file__, "-v"])