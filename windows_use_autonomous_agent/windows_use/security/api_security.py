"""API Security Module

Provides API key validation, encryption, and secure storage functionality.
"""

import base64
import hashlib
import hmac
import os
import re
import secrets
import time
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Dict, List, Optional, Tuple, Union
import logging
from dataclasses import dataclass
from enum import Enum

from ..utils.error_handling import (
    dependency_manager,
    safe_import,
    handle_errors,
    DependencyError
)

logger = logging.getLogger(__name__)

class APIProvider(Enum):
    """Supported API providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    GROQ = "groq"
    COHERE = "cohere"
    HUGGINGFACE = "huggingface"
    AZURE = "azure"
    ELEVENLABS = "elevenlabs"
    SERPER = "serper"
    BING = "bing"
    MICROSOFT = "microsoft"

@dataclass
class APIKeyInfo:
    """API key information"""
    provider: APIProvider
    key: str
    encrypted: bool = False
    valid: bool = False
    last_validated: Optional[float] = None
    usage_count: int = 0
    rate_limit_remaining: Optional[int] = None
    expires_at: Optional[float] = None

class APIKeyValidator:
    """Validates API keys for different providers"""
    
    # API key patterns for validation
    KEY_PATTERNS = {
        APIProvider.OPENAI: r'^sk-[a-zA-Z0-9]{48}$',
        APIProvider.ANTHROPIC: r'^sk-ant-[a-zA-Z0-9\-_]{95}$',
        APIProvider.GOOGLE: r'^[a-zA-Z0-9\-_]{39}$',
        APIProvider.GROQ: r'^gsk_[a-zA-Z0-9]{52}$',
        APIProvider.COHERE: r'^[a-zA-Z0-9]{40}$',
        APIProvider.HUGGINGFACE: r'^hf_[a-zA-Z0-9]{37}$',
        APIProvider.ELEVENLABS: r'^[a-f0-9]{32}$',
        APIProvider.SERPER: r'^[a-f0-9]{32}$',
        APIProvider.BING: r'^[a-f0-9]{32}$',
    }
    
    @classmethod
    def validate_format(cls, provider: APIProvider, api_key: str) -> bool:
        """Validate API key format.
        
        Args:
            provider: API provider
            api_key: API key to validate
            
        Returns:
            True if format is valid, False otherwise
        """
        if not api_key or not isinstance(api_key, str):
            return False
        
        pattern = cls.KEY_PATTERNS.get(provider)
        if not pattern:
            # If no pattern defined, do basic validation
            return len(api_key) >= 16 and api_key.isprintable()
        
        return bool(re.match(pattern, api_key))
    
    @classmethod
    async def validate_key_active(cls, provider: APIProvider, api_key: str) -> Tuple[bool, Optional[str]]:
        """Validate if API key is active by making a test request.
        
        Args:
            provider: API provider
            api_key: API key to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if provider == APIProvider.OPENAI:
                return await cls._validate_openai_key(api_key)
            elif provider == APIProvider.ANTHROPIC:
                return await cls._validate_anthropic_key(api_key)
            elif provider == APIProvider.GOOGLE:
                return await cls._validate_google_key(api_key)
            elif provider == APIProvider.GROQ:
                return await cls._validate_groq_key(api_key)
            else:
                # For other providers, just validate format
                is_valid = cls.validate_format(provider, api_key)
                return is_valid, None if is_valid else "Invalid key format"
        
        except Exception as e:
            logger.error(f"Error validating {provider.value} API key: {e}")
            return False, str(e)
    
    @classmethod
    async def _validate_openai_key(cls, api_key: str) -> Tuple[bool, Optional[str]]:
        """Validate OpenAI API key"""
        if not dependency_manager.check_dependency('openai'):
            return cls.validate_format(APIProvider.OPENAI, api_key), None
        
        try:
            openai = dependency_manager.get_module('openai')
            client = openai.OpenAI(api_key=api_key)
            
            # Make a minimal request to validate the key
            response = await client.models.list()
            return True, None
        
        except Exception as e:
            return False, str(e)
    
    @classmethod
    async def _validate_anthropic_key(cls, api_key: str) -> Tuple[bool, Optional[str]]:
        """Validate Anthropic API key"""
        if not dependency_manager.check_dependency('anthropic'):
            return cls.validate_format(APIProvider.ANTHROPIC, api_key), None
        
        try:
            anthropic = dependency_manager.get_module('anthropic')
            client = anthropic.Anthropic(api_key=api_key)
            
            # Make a minimal request to validate the key
            response = await client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1,
                messages=[{"role": "user", "content": "Hi"}]
            )
            return True, None
        
        except Exception as e:
            return False, str(e)
    
    @classmethod
    async def _validate_google_key(cls, api_key: str) -> Tuple[bool, Optional[str]]:
        """Validate Google API key"""
        if not dependency_manager.check_dependency('google.generativeai', 'google-generativeai'):
            return cls.validate_format(APIProvider.GOOGLE, api_key), None
        
        try:
            genai = dependency_manager.get_module('google.generativeai')
            genai.configure(api_key=api_key)
            
            # List models to validate the key
            models = list(genai.list_models())
            return True, None
        
        except Exception as e:
            return False, str(e)
    
    @classmethod
    async def _validate_groq_key(cls, api_key: str) -> Tuple[bool, Optional[str]]:
        """Validate Groq API key"""
        if not dependency_manager.check_dependency('groq'):
            return cls.validate_format(APIProvider.GROQ, api_key), None
        
        try:
            groq = dependency_manager.get_module('groq')
            client = groq.Groq(api_key=api_key)
            
            # List models to validate the key
            models = client.models.list()
            return True, None
        
        except Exception as e:
            return False, str(e)

class APIKeyEncryption:
    """Handles encryption and decryption of API keys"""
    
    def __init__(self, master_key: Optional[str] = None):
        """Initialize encryption with master key.
        
        Args:
            master_key: Master encryption key. If None, will be generated.
        """
        if master_key:
            self.master_key = master_key.encode()
        else:
            self.master_key = self._generate_master_key()
        
        self._fernet = self._create_fernet()
    
    def _generate_master_key(self) -> bytes:
        """Generate a new master key"""
        return secrets.token_bytes(32)
    
    def _create_fernet(self) -> Fernet:
        """Create Fernet cipher from master key"""
        # Derive key using PBKDF2
        salt = b'jarvis_api_salt'  # In production, use random salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key))
        return Fernet(key)
    
    def encrypt_key(self, api_key: str) -> str:
        """Encrypt an API key.
        
        Args:
            api_key: Plain text API key
            
        Returns:
            Encrypted API key as base64 string
        """
        encrypted = self._fernet.encrypt(api_key.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_key(self, encrypted_key: str) -> str:
        """Decrypt an API key.
        
        Args:
            encrypted_key: Encrypted API key as base64 string
            
        Returns:
            Decrypted API key
        """
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_key.encode())
            decrypted = self._fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt API key: {e}")
            raise ValueError("Invalid encrypted key")
    
    def get_master_key_hash(self) -> str:
        """Get hash of master key for verification"""
        return hashlib.sha256(self.master_key).hexdigest()

class APIKeyManager:
    """Manages API keys with validation, encryption, and secure storage"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """Initialize API key manager.
        
        Args:
            encryption_key: Master encryption key
        """
        self.encryption = APIKeyEncryption(encryption_key)
        self.validator = APIKeyValidator()
        self.keys: Dict[APIProvider, APIKeyInfo] = {}
        self._rate_limits: Dict[APIProvider, Dict[str, Union[int, float]]] = {}
    
    def add_key(self, provider: APIProvider, api_key: str, encrypt: bool = True) -> bool:
        """Add an API key.
        
        Args:
            provider: API provider
            api_key: API key
            encrypt: Whether to encrypt the key
            
        Returns:
            True if key was added successfully
        """
        try:
            # Validate format first
            if not self.validator.validate_format(provider, api_key):
                logger.error(f"Invalid {provider.value} API key format")
                return False
            
            # Encrypt if requested
            stored_key = api_key
            if encrypt:
                stored_key = self.encryption.encrypt_key(api_key)
            
            # Store key info
            self.keys[provider] = APIKeyInfo(
                provider=provider,
                key=stored_key,
                encrypted=encrypt,
                valid=True,  # Will be validated later
                last_validated=time.time()
            )
            
            logger.info(f"Added {provider.value} API key (encrypted: {encrypt})")
            return True
        
        except Exception as e:
            logger.error(f"Failed to add {provider.value} API key: {e}")
            return False
    
    def get_key(self, provider: APIProvider) -> Optional[str]:
        """Get decrypted API key.
        
        Args:
            provider: API provider
            
        Returns:
            Decrypted API key or None if not found
        """
        key_info = self.keys.get(provider)
        if not key_info:
            return None
        
        try:
            if key_info.encrypted:
                return self.encryption.decrypt_key(key_info.key)
            else:
                return key_info.key
        
        except Exception as e:
            logger.error(f"Failed to decrypt {provider.value} API key: {e}")
            return None
    
    async def validate_key(self, provider: APIProvider) -> bool:
        """Validate an API key.
        
        Args:
            provider: API provider
            
        Returns:
            True if key is valid
        """
        api_key = self.get_key(provider)
        if not api_key:
            return False
        
        is_valid, error = await self.validator.validate_key_active(provider, api_key)
        
        # Update key info
        if provider in self.keys:
            self.keys[provider].valid = is_valid
            self.keys[provider].last_validated = time.time()
        
        if not is_valid and error:
            logger.warning(f"{provider.value} API key validation failed: {error}")
        
        return is_valid
    
    async def validate_all_keys(self) -> Dict[APIProvider, bool]:
        """Validate all stored API keys.
        
        Returns:
            Dictionary of provider -> validation result
        """
        results = {}
        for provider in self.keys.keys():
            results[provider] = await self.validate_key(provider)
        return results
    
    def remove_key(self, provider: APIProvider) -> bool:
        """Remove an API key.
        
        Args:
            provider: API provider
            
        Returns:
            True if key was removed
        """
        if provider in self.keys:
            del self.keys[provider]
            logger.info(f"Removed {provider.value} API key")
            return True
        return False
    
    def list_providers(self) -> List[APIProvider]:
        """List all providers with stored keys."""
        return list(self.keys.keys())
    
    def get_key_info(self, provider: APIProvider) -> Optional[APIKeyInfo]:
        """Get API key information.
        
        Args:
            provider: API provider
            
        Returns:
            API key information or None
        """
        return self.keys.get(provider)
    
    def check_rate_limit(self, provider: APIProvider) -> bool:
        """Check if provider is within rate limits.
        
        Args:
            provider: API provider
            
        Returns:
            True if within rate limits
        """
        rate_limit_info = self._rate_limits.get(provider, {})
        
        # Simple rate limiting implementation
        current_time = time.time()
        last_request = rate_limit_info.get('last_request', 0)
        min_interval = rate_limit_info.get('min_interval', 1.0)  # 1 second default
        
        if current_time - last_request < min_interval:
            return False
        
        # Update last request time
        if provider not in self._rate_limits:
            self._rate_limits[provider] = {}
        self._rate_limits[provider]['last_request'] = current_time
        
        return True
    
    def update_usage(self, provider: APIProvider):
        """Update usage count for a provider.
        
        Args:
            provider: API provider
        """
        if provider in self.keys:
            self.keys[provider].usage_count += 1
    
    def get_security_status(self) -> Dict[str, Union[bool, int, str]]:
        """Get security status of API key management.
        
        Returns:
            Security status information
        """
        total_keys = len(self.keys)
        encrypted_keys = sum(1 for key_info in self.keys.values() if key_info.encrypted)
        valid_keys = sum(1 for key_info in self.keys.values() if key_info.valid)
        
        return {
            'total_keys': total_keys,
            'encrypted_keys': encrypted_keys,
            'valid_keys': valid_keys,
            'encryption_enabled': encrypted_keys > 0,
            'all_keys_encrypted': encrypted_keys == total_keys if total_keys > 0 else True,
            'master_key_hash': self.encryption.get_master_key_hash()[:16],  # First 16 chars for identification
        }

# Global API key manager instance
api_key_manager = APIKeyManager()

# Export main classes and functions
__all__ = [
    'APIProvider',
    'APIKeyInfo',
    'APIKeyValidator',
    'APIKeyEncryption',
    'APIKeyManager',
    'api_key_manager',
]