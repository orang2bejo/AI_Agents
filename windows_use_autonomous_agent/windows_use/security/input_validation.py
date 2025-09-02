"""Input Validation and Sanitization Module

Provides comprehensive input validation and sanitization for security.
"""

import re
import os
import html
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple
import logging
from dataclasses import dataclass
from enum import Enum
import json
import base64
import hashlib

logger = logging.getLogger(__name__)

class ValidationLevel(Enum):
    """Validation strictness levels"""
    STRICT = "strict"
    MODERATE = "moderate"
    PERMISSIVE = "permissive"

class InputType(Enum):
    """Types of input to validate"""
    FILE_PATH = "file_path"
    DIRECTORY_PATH = "directory_path"
    URL = "url"
    EMAIL = "email"
    COMMAND = "command"
    SQL_QUERY = "sql_query"
    SCRIPT_CODE = "script_code"
    API_KEY = "api_key"
    USER_INPUT = "user_input"
    JSON_DATA = "json_data"
    XML_DATA = "xml_data"
    HTML_CONTENT = "html_content"
    REGEX_PATTERN = "regex_pattern"
    ENVIRONMENT_VAR = "environment_var"

@dataclass
class ValidationResult:
    """Result of input validation"""
    is_valid: bool
    sanitized_value: Any
    original_value: Any
    errors: List[str]
    warnings: List[str]
    risk_level: str  # low, medium, high, critical
    validation_level: ValidationLevel

class InputSanitizer:
    """Sanitizes various types of input"""
    
    # Dangerous patterns to detect
    DANGEROUS_PATTERNS = {
        'command_injection': [
            r'[;&|`$(){}\[\]<>]',  # Command separators and special chars
            r'\\x[0-9a-fA-F]{2}',  # Hex escape sequences
            r'%[0-9a-fA-F]{2}',    # URL encoded chars
        ],
        'path_traversal': [
            r'\.\.',              # Directory traversal
            r'[/\\]{2,}',         # Multiple slashes
            r'~[/\\]',            # Home directory access
        ],
        'script_injection': [
            r'<script[^>]*>',      # Script tags
            r'javascript:',        # JavaScript protocol
            r'on\w+\s*=',         # Event handlers
            r'eval\s*\(',         # Eval function
            r'exec\s*\(',         # Exec function
        ],
        'sql_injection': [
            r"'\s*(OR|AND)\s*'?",  # SQL injection patterns
            r'UNION\s+SELECT',      # Union select
            r'DROP\s+TABLE',        # Drop table
            r'DELETE\s+FROM',       # Delete from
            r'INSERT\s+INTO',       # Insert into
            r'UPDATE\s+\w+\s+SET',  # Update set
        ]
    }
    
    @classmethod
    def sanitize_file_path(cls, path: str, validation_level: ValidationLevel = ValidationLevel.STRICT) -> str:
        """Sanitize file path input.
        
        Args:
            path: File path to sanitize
            validation_level: Validation strictness
            
        Returns:
            Sanitized file path
        """
        if not path:
            return ""
        
        # Convert to Path object for normalization
        try:
            normalized_path = Path(path).resolve()
            sanitized = str(normalized_path)
        except (OSError, ValueError):
            # If path is invalid, return empty string
            return ""
        
        if validation_level == ValidationLevel.STRICT:
            # Remove any dangerous characters
            sanitized = re.sub(r'[<>:"|?*]', '', sanitized)
            
            # Ensure path doesn't go outside allowed directories
            if '..' in sanitized:
                sanitized = sanitized.replace('..', '')
        
        return sanitized
    
    @classmethod
    def sanitize_command(cls, command: str, validation_level: ValidationLevel = ValidationLevel.STRICT) -> str:
        """Sanitize command input.
        
        Args:
            command: Command to sanitize
            validation_level: Validation strictness
            
        Returns:
            Sanitized command
        """
        if not command:
            return ""
        
        sanitized = command.strip()
        
        if validation_level == ValidationLevel.STRICT:
            # Remove dangerous characters for command injection
            dangerous_chars = r'[;&|`$(){}\[\]<>]'
            sanitized = re.sub(dangerous_chars, '', sanitized)
            
            # Remove escape sequences
            sanitized = re.sub(r'\\x[0-9a-fA-F]{2}', '', sanitized)
            sanitized = re.sub(r'%[0-9a-fA-F]{2}', '', sanitized)
        
        return sanitized
    
    @classmethod
    def sanitize_html(cls, html_content: str, validation_level: ValidationLevel = ValidationLevel.STRICT) -> str:
        """Sanitize HTML content.
        
        Args:
            html_content: HTML content to sanitize
            validation_level: Validation strictness
            
        Returns:
            Sanitized HTML content
        """
        if not html_content:
            return ""
        
        sanitized = html_content
        
        if validation_level == ValidationLevel.STRICT:
            # Remove script tags and event handlers
            sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
            sanitized = re.sub(r'on\w+\s*=\s*["\'][^"\'>]*["\']', '', sanitized, flags=re.IGNORECASE)
            sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
            
            # Escape remaining HTML
            sanitized = html.escape(sanitized)
        
        elif validation_level == ValidationLevel.MODERATE:
            # Just escape HTML
            sanitized = html.escape(sanitized)
        
        return sanitized
    
    @classmethod
    def sanitize_url(cls, url: str, validation_level: ValidationLevel = ValidationLevel.STRICT) -> str:
        """Sanitize URL input.
        
        Args:
            url: URL to sanitize
            validation_level: Validation strictness
            
        Returns:
            Sanitized URL
        """
        if not url:
            return ""
        
        try:
            # Parse and reconstruct URL
            parsed = urllib.parse.urlparse(url)
            
            if validation_level == ValidationLevel.STRICT:
                # Only allow safe schemes
                allowed_schemes = {'http', 'https', 'ftp', 'ftps'}
                if parsed.scheme.lower() not in allowed_schemes:
                    return ""
            
            # Reconstruct URL
            sanitized = urllib.parse.urlunparse(parsed)
            return sanitized
        
        except Exception:
            return ""
    
    @classmethod
    def sanitize_json(cls, json_data: str, validation_level: ValidationLevel = ValidationLevel.STRICT) -> str:
        """Sanitize JSON data.
        
        Args:
            json_data: JSON string to sanitize
            validation_level: Validation strictness
            
        Returns:
            Sanitized JSON string
        """
        if not json_data:
            return ""
        
        try:
            # Parse and re-serialize to ensure valid JSON
            parsed = json.loads(json_data)
            
            if validation_level == ValidationLevel.STRICT:
                # Remove potentially dangerous keys/values
                parsed = cls._sanitize_json_object(parsed)
            
            return json.dumps(parsed, ensure_ascii=True)
        
        except (json.JSONDecodeError, TypeError):
            return ""
    
    @classmethod
    def _sanitize_json_object(cls, obj: Any) -> Any:
        """Recursively sanitize JSON object"""
        if isinstance(obj, dict):
            sanitized = {}
            for key, value in obj.items():
                # Skip dangerous keys
                if isinstance(key, str) and any(pattern in key.lower() for pattern in ['script', 'eval', 'exec', '__']):
                    continue
                sanitized[key] = cls._sanitize_json_object(value)
            return sanitized
        
        elif isinstance(obj, list):
            return [cls._sanitize_json_object(item) for item in obj]
        
        elif isinstance(obj, str):
            # Sanitize string values
            return cls.sanitize_html(obj, ValidationLevel.STRICT)
        
        else:
            return obj

class InputValidator:
    """Validates various types of input"""
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.STRICT):
        """Initialize validator.
        
        Args:
            validation_level: Default validation level
        """
        self.validation_level = validation_level
        self.sanitizer = InputSanitizer()
    
    def validate(self, value: Any, input_type: InputType, 
                validation_level: Optional[ValidationLevel] = None) -> ValidationResult:
        """Validate input value.
        
        Args:
            value: Value to validate
            input_type: Type of input
            validation_level: Validation level (overrides default)
            
        Returns:
            ValidationResult
        """
        level = validation_level or self.validation_level
        errors = []
        warnings = []
        risk_level = "low"
        
        # Convert value to string for validation
        str_value = str(value) if value is not None else ""
        
        try:
            if input_type == InputType.FILE_PATH:
                result = self._validate_file_path(str_value, level)
            elif input_type == InputType.DIRECTORY_PATH:
                result = self._validate_directory_path(str_value, level)
            elif input_type == InputType.URL:
                result = self._validate_url(str_value, level)
            elif input_type == InputType.EMAIL:
                result = self._validate_email(str_value, level)
            elif input_type == InputType.COMMAND:
                result = self._validate_command(str_value, level)
            elif input_type == InputType.API_KEY:
                result = self._validate_api_key(str_value, level)
            elif input_type == InputType.JSON_DATA:
                result = self._validate_json(str_value, level)
            elif input_type == InputType.HTML_CONTENT:
                result = self._validate_html(str_value, level)
            elif input_type == InputType.REGEX_PATTERN:
                result = self._validate_regex(str_value, level)
            else:
                result = self._validate_generic(str_value, level)
            
            return ValidationResult(
                is_valid=result['is_valid'],
                sanitized_value=result['sanitized_value'],
                original_value=value,
                errors=result.get('errors', []),
                warnings=result.get('warnings', []),
                risk_level=result.get('risk_level', 'low'),
                validation_level=level
            )
        
        except Exception as e:
            logger.error(f"Validation error for {input_type.value}: {e}")
            return ValidationResult(
                is_valid=False,
                sanitized_value="",
                original_value=value,
                errors=[f"Validation failed: {str(e)}"],
                warnings=[],
                risk_level="high",
                validation_level=level
            )
    
    def _validate_file_path(self, path: str, level: ValidationLevel) -> Dict[str, Any]:
        """Validate file path"""
        errors = []
        warnings = []
        risk_level = "low"
        
        if not path:
            errors.append("Empty file path")
            return {'is_valid': False, 'sanitized_value': "", 'errors': errors}
        
        # Check for path traversal
        if '..' in path:
            errors.append("Path traversal detected")
            risk_level = "high"
        
        # Check for dangerous characters
        dangerous_chars = r'[<>:"|?*]'
        if re.search(dangerous_chars, path):
            warnings.append("Dangerous characters in path")
            risk_level = "medium"
        
        # Sanitize path
        sanitized = self.sanitizer.sanitize_file_path(path, level)
        
        # Check if path exists (warning only)
        try:
            if not Path(sanitized).exists():
                warnings.append("Path does not exist")
        except (OSError, ValueError):
            warnings.append("Invalid path format")
        
        is_valid = len(errors) == 0
        
        return {
            'is_valid': is_valid,
            'sanitized_value': sanitized,
            'errors': errors,
            'warnings': warnings,
            'risk_level': risk_level
        }
    
    def _validate_directory_path(self, path: str, level: ValidationLevel) -> Dict[str, Any]:
        """Validate directory path"""
        result = self._validate_file_path(path, level)
        
        # Additional check for directory
        if result['is_valid'] and result['sanitized_value']:
            try:
                path_obj = Path(result['sanitized_value'])
                if path_obj.exists() and not path_obj.is_dir():
                    result['warnings'].append("Path exists but is not a directory")
            except (OSError, ValueError):
                pass
        
        return result
    
    def _validate_url(self, url: str, level: ValidationLevel) -> Dict[str, Any]:
        """Validate URL"""
        errors = []
        warnings = []
        risk_level = "low"
        
        if not url:
            errors.append("Empty URL")
            return {'is_valid': False, 'sanitized_value': "", 'errors': errors}
        
        try:
            parsed = urllib.parse.urlparse(url)
            
            # Check scheme
            if not parsed.scheme:
                errors.append("Missing URL scheme")
            elif level == ValidationLevel.STRICT:
                allowed_schemes = {'http', 'https', 'ftp', 'ftps'}
                if parsed.scheme.lower() not in allowed_schemes:
                    errors.append(f"Unsafe URL scheme: {parsed.scheme}")
                    risk_level = "high"
            
            # Check for suspicious patterns
            if 'javascript:' in url.lower():
                errors.append("JavaScript URL detected")
                risk_level = "critical"
            
            sanitized = self.sanitizer.sanitize_url(url, level)
            
        except Exception as e:
            errors.append(f"Invalid URL format: {e}")
            sanitized = ""
        
        is_valid = len(errors) == 0
        
        return {
            'is_valid': is_valid,
            'sanitized_value': sanitized,
            'errors': errors,
            'warnings': warnings,
            'risk_level': risk_level
        }
    
    def _validate_email(self, email: str, level: ValidationLevel) -> Dict[str, Any]:
        """Validate email address"""
        errors = []
        warnings = []
        risk_level = "low"
        
        if not email:
            errors.append("Empty email")
            return {'is_valid': False, 'sanitized_value': "", 'errors': errors}
        
        # Basic email regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            errors.append("Invalid email format")
        
        # Check for suspicious patterns
        if any(char in email for char in ['<', '>', '"', "'"]):
            warnings.append("Suspicious characters in email")
            risk_level = "medium"
        
        sanitized = email.strip().lower()
        is_valid = len(errors) == 0
        
        return {
            'is_valid': is_valid,
            'sanitized_value': sanitized,
            'errors': errors,
            'warnings': warnings,
            'risk_level': risk_level
        }
    
    def _validate_command(self, command: str, level: ValidationLevel) -> Dict[str, Any]:
        """Validate command input"""
        errors = []
        warnings = []
        risk_level = "low"
        
        if not command:
            errors.append("Empty command")
            return {'is_valid': False, 'sanitized_value': "", 'errors': errors}
        
        # Check for command injection patterns
        for pattern_type, patterns in self.sanitizer.DANGEROUS_PATTERNS.items():
            if pattern_type == 'command_injection':
                for pattern in patterns:
                    if re.search(pattern, command):
                        errors.append(f"Command injection pattern detected: {pattern}")
                        risk_level = "critical"
        
        # Check for dangerous commands
        dangerous_commands = ['rm', 'del', 'format', 'fdisk', 'mkfs', 'dd']
        command_lower = command.lower()
        for dangerous_cmd in dangerous_commands:
            if dangerous_cmd in command_lower:
                warnings.append(f"Potentially dangerous command: {dangerous_cmd}")
                risk_level = "high"
        
        sanitized = self.sanitizer.sanitize_command(command, level)
        is_valid = len(errors) == 0
        
        return {
            'is_valid': is_valid,
            'sanitized_value': sanitized,
            'errors': errors,
            'warnings': warnings,
            'risk_level': risk_level
        }
    
    def _validate_api_key(self, api_key: str, level: ValidationLevel) -> Dict[str, Any]:
        """Validate API key"""
        errors = []
        warnings = []
        risk_level = "low"
        
        if not api_key:
            errors.append("Empty API key")
            return {'is_valid': False, 'sanitized_value': "", 'errors': errors}
        
        # Basic validation
        if len(api_key) < 16:
            errors.append("API key too short")
        
        if not api_key.isprintable():
            errors.append("API key contains non-printable characters")
        
        # Check for suspicious patterns
        if any(char in api_key for char in [' ', '\t', '\n', '\r']):
            warnings.append("API key contains whitespace")
        
        sanitized = api_key.strip()
        is_valid = len(errors) == 0
        
        return {
            'is_valid': is_valid,
            'sanitized_value': sanitized,
            'errors': errors,
            'warnings': warnings,
            'risk_level': risk_level
        }
    
    def _validate_json(self, json_data: str, level: ValidationLevel) -> Dict[str, Any]:
        """Validate JSON data"""
        errors = []
        warnings = []
        risk_level = "low"
        
        if not json_data:
            errors.append("Empty JSON data")
            return {'is_valid': False, 'sanitized_value': "", 'errors': errors}
        
        try:
            # Try to parse JSON
            parsed = json.loads(json_data)
            sanitized = self.sanitizer.sanitize_json(json_data, level)
        
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON format: {e}")
            sanitized = ""
        
        # Check for suspicious content
        if 'script' in json_data.lower() or 'eval' in json_data.lower():
            warnings.append("Potentially dangerous content in JSON")
            risk_level = "medium"
        
        is_valid = len(errors) == 0
        
        return {
            'is_valid': is_valid,
            'sanitized_value': sanitized,
            'errors': errors,
            'warnings': warnings,
            'risk_level': risk_level
        }
    
    def _validate_html(self, html_content: str, level: ValidationLevel) -> Dict[str, Any]:
        """Validate HTML content"""
        errors = []
        warnings = []
        risk_level = "low"
        
        if not html_content:
            return {'is_valid': True, 'sanitized_value': "", 'errors': [], 'warnings': [], 'risk_level': 'low'}
        
        # Check for script injection patterns
        for pattern_type, patterns in self.sanitizer.DANGEROUS_PATTERNS.items():
            if pattern_type == 'script_injection':
                for pattern in patterns:
                    if re.search(pattern, html_content, re.IGNORECASE):
                        warnings.append(f"Script injection pattern detected: {pattern}")
                        risk_level = "high"
        
        sanitized = self.sanitizer.sanitize_html(html_content, level)
        is_valid = True  # HTML is always "valid" after sanitization
        
        return {
            'is_valid': is_valid,
            'sanitized_value': sanitized,
            'errors': errors,
            'warnings': warnings,
            'risk_level': risk_level
        }
    
    def _validate_regex(self, pattern: str, level: ValidationLevel) -> Dict[str, Any]:
        """Validate regex pattern"""
        errors = []
        warnings = []
        risk_level = "low"
        
        if not pattern:
            errors.append("Empty regex pattern")
            return {'is_valid': False, 'sanitized_value': "", 'errors': errors}
        
        try:
            # Try to compile regex
            re.compile(pattern)
            
            # Check for potentially dangerous patterns
            if '.*' in pattern and len(pattern) > 100:
                warnings.append("Potentially inefficient regex pattern")
                risk_level = "medium"
            
            sanitized = pattern
        
        except re.error as e:
            errors.append(f"Invalid regex pattern: {e}")
            sanitized = ""
        
        is_valid = len(errors) == 0
        
        return {
            'is_valid': is_valid,
            'sanitized_value': sanitized,
            'errors': errors,
            'warnings': warnings,
            'risk_level': risk_level
        }
    
    def _validate_generic(self, value: str, level: ValidationLevel) -> Dict[str, Any]:
        """Generic validation for unknown input types"""
        errors = []
        warnings = []
        risk_level = "low"
        
        # Basic sanitization
        sanitized = value.strip() if value else ""
        
        # Check for suspicious patterns
        for pattern_type, patterns in self.sanitizer.DANGEROUS_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, value, re.IGNORECASE):
                    warnings.append(f"Suspicious pattern detected ({pattern_type}): {pattern}")
                    risk_level = "medium"
        
        is_valid = True  # Generic input is always valid after sanitization
        
        return {
            'is_valid': is_valid,
            'sanitized_value': sanitized,
            'errors': errors,
            'warnings': warnings,
            'risk_level': risk_level
        }
    
    def validate_batch(self, inputs: List[Tuple[Any, InputType]], 
                      validation_level: Optional[ValidationLevel] = None) -> List[ValidationResult]:
        """Validate multiple inputs.
        
        Args:
            inputs: List of (value, input_type) tuples
            validation_level: Validation level for all inputs
            
        Returns:
            List of ValidationResult objects
        """
        results = []
        for value, input_type in inputs:
            result = self.validate(value, input_type, validation_level)
            results.append(result)
        return results
    
    def get_validation_summary(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Get summary of validation results.
        
        Args:
            results: List of validation results
            
        Returns:
            Summary dictionary
        """
        total = len(results)
        valid = sum(1 for r in results if r.is_valid)
        invalid = total - valid
        
        risk_counts = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
        for result in results:
            risk_counts[result.risk_level] += 1
        
        return {
            'total_inputs': total,
            'valid_inputs': valid,
            'invalid_inputs': invalid,
            'validation_rate': valid / total if total > 0 else 0,
            'risk_distribution': risk_counts,
            'highest_risk': max(risk_counts.keys(), key=lambda k: risk_counts[k]) if total > 0 else 'low'
        }

# Global validator instance
input_validator = InputValidator()

# Export main classes and functions
__all__ = [
    'ValidationLevel',
    'InputType',
    'ValidationResult',
    'InputSanitizer',
    'InputValidator',
    'input_validator',
]