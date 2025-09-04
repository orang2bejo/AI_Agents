#!/usr/bin/env python3
"""
Voice Authentication Module for Windows Use Autonomous Agent

Integrated voice-based authentication and authorization capabilities,
including admin voice enrollment, user verification, and access control management.

Author: Jarvis AI Team
Date: 2024
"""

import os
import json
import hashlib
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from datetime import datetime, timedelta
import pickle
from pathlib import Path

try:
    import librosa
    import soundfile as sf
    from sklearn.mixture import GaussianMixture
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics.pairwise import cosine_similarity
    VOICE_AUTH_AVAILABLE = True
except ImportError:
    VOICE_AUTH_AVAILABLE = False
    logging.warning("Voice authentication dependencies not installed. Install librosa, soundfile, scikit-learn")

logger = logging.getLogger(__name__)

class AuthenticationLevel(Enum):
    """Authentication levels for different operations"""
    GUEST = "guest"
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class VoiceAuthStatus(Enum):
    """Voice authentication status"""
    SUCCESS = "success"
    FAILED = "failed"
    INSUFFICIENT_AUDIO = "insufficient_audio"
    NO_ENROLLMENT = "no_enrollment"
    EXPIRED_SESSION = "expired_session"
    BLOCKED = "blocked"

class PermissionType(Enum):
    """Types of permissions"""
    VOICE_COMMANDS = "voice_commands"
    SYSTEM_CONTROL = "system_control"
    FILE_ACCESS = "file_access"
    OFFICE_AUTOMATION = "office_automation"
    WEB_AUTOMATION = "web_automation"
    ADMIN_SETTINGS = "admin_settings"
    USER_MANAGEMENT = "user_management"

@dataclass
class VoiceProfile:
    """Voice profile for a user"""
    user_id: str
    username: str
    voice_features: List[float]
    enrollment_date: datetime
    last_verified: Optional[datetime] = None
    verification_count: int = 0
    failed_attempts: int = 0
    is_active: bool = True
    auth_level: AuthenticationLevel = AuthenticationLevel.USER

@dataclass
class UserPermissions:
    """User permissions configuration"""
    user_id: str
    permissions: Dict[PermissionType, bool]
    custom_commands: List[str]
    restricted_commands: List[str]
    session_timeout: int = 3600  # seconds
    max_daily_commands: int = 1000

@dataclass
class AuthSession:
    """Authentication session"""
    session_id: str
    user_id: str
    auth_level: AuthenticationLevel
    start_time: datetime
    last_activity: datetime
    permissions: UserPermissions
    is_active: bool = True

@dataclass
class VoiceAuthConfig:
    """Voice authentication configuration"""
    enrollment_duration: float = 10.0  # seconds
    verification_threshold: float = 0.85
    max_failed_attempts: int = 3
    session_timeout: int = 3600  # seconds
    feature_extraction_method: str = "mfcc"  # mfcc, mel_spectrogram, chroma
    model_type: str = "gmm"  # gmm, cosine_similarity
    audio_sample_rate: int = 16000
    min_audio_length: float = 2.0  # seconds
    data_directory: str = "voice_auth_data"
    profiles_file: str = "voice_profiles.json"
    models_directory: str = "voice_models"

class VoiceAuthenticator:
    """Voice authentication system"""
    
    def __init__(self, config: Optional[VoiceAuthConfig] = None):
        if not VOICE_AUTH_AVAILABLE:
            raise ImportError("Voice authentication dependencies not available")
            
        self.config = config or VoiceAuthConfig()
        self.logger = logging.getLogger(__name__)
        self.profiles: Dict[str, VoiceProfile] = {}
        self.sessions: Dict[str, AuthSession] = {}
        self.models: Dict[str, Any] = {}
        self.scaler = StandardScaler()
        
        # Setup directories
        self._setup_directories()
        
        # Load existing profiles
        self._load_profiles()
        
        # Initialize default permissions
        self._init_default_permissions()
    
    def _setup_directories(self):
        """Setup required directories"""
        directories = [
            self.config.data_directory,
            self.config.models_directory
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def _load_profiles(self):
        """Load voice profiles from file"""
        profiles_path = Path(self.config.data_directory) / self.config.profiles_file
        
        if profiles_path.exists():
            try:
                with open(profiles_path, 'r', encoding='utf-8') as f:
                    profiles_data = json.load(f)
                    
                for user_id, profile_data in profiles_data.items():
                    # Convert datetime strings back to datetime objects
                    profile_data['enrollment_date'] = datetime.fromisoformat(profile_data['enrollment_date'])
                    if profile_data.get('last_verified'):
                        profile_data['last_verified'] = datetime.fromisoformat(profile_data['last_verified'])
                    
                    # Convert auth_level string to enum
                    profile_data['auth_level'] = AuthenticationLevel(profile_data['auth_level'])
                    
                    self.profiles[user_id] = VoiceProfile(**profile_data)
                    
                self.logger.info(f"Loaded {len(self.profiles)} voice profiles")
                
            except Exception as e:
                self.logger.error(f"Error loading profiles: {e}")
    
    def _save_profiles(self):
        """Save voice profiles to file"""
        profiles_path = Path(self.config.data_directory) / self.config.profiles_file
        
        try:
            profiles_data = {}
            for user_id, profile in self.profiles.items():
                profile_dict = asdict(profile)
                # Convert datetime objects to strings
                profile_dict['enrollment_date'] = profile.enrollment_date.isoformat()
                if profile.last_verified:
                    profile_dict['last_verified'] = profile.last_verified.isoformat()
                else:
                    profile_dict['last_verified'] = None
                    
                # Convert enum to string
                profile_dict['auth_level'] = profile.auth_level.value
                
                profiles_data[user_id] = profile_dict
            
            with open(profiles_path, 'w', encoding='utf-8') as f:
                json.dump(profiles_data, f, indent=2, ensure_ascii=False)
                
            self.logger.info("Voice profiles saved successfully")
            
        except Exception as e:
            self.logger.error(f"Error saving profiles: {e}")
    
    def _init_default_permissions(self):
        """Initialize default permissions for different auth levels"""
        self.default_permissions = {
            AuthenticationLevel.GUEST: {
                PermissionType.VOICE_COMMANDS: True,
                PermissionType.SYSTEM_CONTROL: False,
                PermissionType.FILE_ACCESS: False,
                PermissionType.OFFICE_AUTOMATION: False,
                PermissionType.WEB_AUTOMATION: False,
                PermissionType.ADMIN_SETTINGS: False,
                PermissionType.USER_MANAGEMENT: False
            },
            AuthenticationLevel.USER: {
                PermissionType.VOICE_COMMANDS: True,
                PermissionType.SYSTEM_CONTROL: True,
                PermissionType.FILE_ACCESS: True,
                PermissionType.OFFICE_AUTOMATION: True,
                PermissionType.WEB_AUTOMATION: True,
                PermissionType.ADMIN_SETTINGS: False,
                PermissionType.USER_MANAGEMENT: False
            },
            AuthenticationLevel.ADMIN: {
                PermissionType.VOICE_COMMANDS: True,
                PermissionType.SYSTEM_CONTROL: True,
                PermissionType.FILE_ACCESS: True,
                PermissionType.OFFICE_AUTOMATION: True,
                PermissionType.WEB_AUTOMATION: True,
                PermissionType.ADMIN_SETTINGS: True,
                PermissionType.USER_MANAGEMENT: True
            },
            AuthenticationLevel.SUPER_ADMIN: {
                PermissionType.VOICE_COMMANDS: True,
                PermissionType.SYSTEM_CONTROL: True,
                PermissionType.FILE_ACCESS: True,
                PermissionType.OFFICE_AUTOMATION: True,
                PermissionType.WEB_AUTOMATION: True,
                PermissionType.ADMIN_SETTINGS: True,
                PermissionType.USER_MANAGEMENT: True
            }
        }
    
    def extract_voice_features(self, audio_data: np.ndarray, sample_rate: int = None) -> np.ndarray:
        """Extract voice features from audio data"""
        if sample_rate is None:
            sample_rate = self.config.audio_sample_rate
        
        try:
            if self.config.feature_extraction_method == "mfcc":
                # Extract MFCC features
                mfccs = librosa.feature.mfcc(
                    y=audio_data,
                    sr=sample_rate,
                    n_mfcc=13,
                    n_fft=2048,
                    hop_length=512
                )
                # Calculate statistics
                features = np.concatenate([
                    np.mean(mfccs, axis=1),
                    np.std(mfccs, axis=1),
                    np.max(mfccs, axis=1),
                    np.min(mfccs, axis=1)
                ])
                
            elif self.config.feature_extraction_method == "mel_spectrogram":
                # Extract Mel-spectrogram features
                mel_spec = librosa.feature.melspectrogram(
                    y=audio_data,
                    sr=sample_rate,
                    n_mels=128,
                    n_fft=2048,
                    hop_length=512
                )
                mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
                features = np.concatenate([
                    np.mean(mel_spec_db, axis=1),
                    np.std(mel_spec_db, axis=1)
                ])
                
            else:  # chroma
                # Extract Chroma features
                chroma = librosa.feature.chroma(
                    y=audio_data,
                    sr=sample_rate,
                    hop_length=512
                )
                features = np.concatenate([
                    np.mean(chroma, axis=1),
                    np.std(chroma, axis=1)
                ])
            
            return features
            
        except Exception as e:
            self.logger.error(f"Feature extraction failed: {e}")
            raise
    
    def enroll_user(self, user_id: str, username: str, audio_data: np.ndarray, 
                   auth_level: AuthenticationLevel = AuthenticationLevel.USER) -> bool:
        """Enroll a new user with voice sample"""
        try:
            # Check audio length
            duration = len(audio_data) / self.config.audio_sample_rate
            if duration < self.config.min_audio_length:
                self.logger.warning(f"Audio too short: {duration}s < {self.config.min_audio_length}s")
                return False
            
            # Extract features
            features = self.extract_voice_features(audio_data)
            
            # Create voice profile
            profile = VoiceProfile(
                user_id=user_id,
                username=username,
                voice_features=features.tolist(),
                enrollment_date=datetime.now(),
                auth_level=auth_level
            )
            
            # Train model if using GMM
            if self.config.model_type == "gmm":
                model = GaussianMixture(n_components=2, random_state=42)
                # Reshape features for training
                features_reshaped = features.reshape(-1, 1)
                model.fit(features_reshaped)
                
                # Save model
                model_path = Path(self.config.models_directory) / f"{user_id}_model.pkl"
                with open(model_path, 'wb') as f:
                    pickle.dump(model, f)
                
                self.models[user_id] = model
            
            # Store profile
            self.profiles[user_id] = profile
            self._save_profiles()
            
            self.logger.info(f"User {username} enrolled successfully with {auth_level.value} level")
            return True
            
        except Exception as e:
            self.logger.error(f"Enrollment failed for user {username}: {e}")
            return False
    
    def verify_user(self, audio_data: np.ndarray, user_id: str = None) -> Tuple[VoiceAuthStatus, Optional[str]]:
        """Verify user identity from voice sample"""
        try:
            # Check audio length
            duration = len(audio_data) / self.config.audio_sample_rate
            if duration < self.config.min_audio_length:
                return VoiceAuthStatus.INSUFFICIENT_AUDIO, None
            
            # Extract features
            features = self.extract_voice_features(audio_data)
            
            best_match_id = None
            best_score = 0.0
            
            # If specific user_id provided, verify against that user only
            if user_id and user_id in self.profiles:
                profiles_to_check = {user_id: self.profiles[user_id]}
            else:
                profiles_to_check = self.profiles
            
            # Check against all profiles (or specific user)
            for profile_id, profile in profiles_to_check.items():
                if not profile.is_active:
                    continue
                
                # Check failed attempts
                if profile.failed_attempts >= self.config.max_failed_attempts:
                    continue
                
                score = self._calculate_similarity(features, np.array(profile.voice_features))
                
                if score > best_score and score >= self.config.verification_threshold:
                    best_score = score
                    best_match_id = profile_id
            
            if best_match_id:
                # Update profile
                profile = self.profiles[best_match_id]
                profile.last_verified = datetime.now()
                profile.verification_count += 1
                profile.failed_attempts = 0  # Reset failed attempts on success
                self._save_profiles()
                
                self.logger.info(f"User {profile.username} verified successfully (score: {best_score:.3f})")
                return VoiceAuthStatus.SUCCESS, best_match_id
            else:
                # Update failed attempts for all checked profiles
                for profile_id in profiles_to_check:
                    if profiles_to_check[profile_id].is_active:
                        profiles_to_check[profile_id].failed_attempts += 1
                
                self._save_profiles()
                
                self.logger.warning(f"Voice verification failed (best score: {best_score:.3f})")
                return VoiceAuthStatus.FAILED, None
                
        except Exception as e:
            self.logger.error(f"Verification error: {e}")
            return VoiceAuthStatus.FAILED, None
    
    def _calculate_similarity(self, features1: np.ndarray, features2: np.ndarray) -> float:
        """Calculate similarity between two feature vectors"""
        if self.config.model_type == "gmm":
            # Use GMM model for scoring
            # This is a simplified implementation
            return cosine_similarity([features1], [features2])[0][0]
        else:
            # Use cosine similarity
            return cosine_similarity([features1], [features2])[0][0]
    
    def create_session(self, user_id: str) -> Optional[str]:
        """Create authentication session for user"""
        if user_id not in self.profiles:
            return None
        
        profile = self.profiles[user_id]
        session_id = hashlib.md5(f"{user_id}_{datetime.now().isoformat()}".encode()).hexdigest()
        
        # Create user permissions
        permissions = UserPermissions(
            user_id=user_id,
            permissions=self.default_permissions[profile.auth_level].copy(),
            custom_commands=[],
            restricted_commands=[],
            session_timeout=self.config.session_timeout
        )
        
        # Create session
        session = AuthSession(
            session_id=session_id,
            user_id=user_id,
            auth_level=profile.auth_level,
            start_time=datetime.now(),
            last_activity=datetime.now(),
            permissions=permissions
        )
        
        self.sessions[session_id] = session
        
        self.logger.info(f"Session created for user {profile.username}: {session_id}")
        return session_id
    
    def validate_session(self, session_id: str) -> bool:
        """Validate if session is still active"""
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        
        # Check if session expired
        if datetime.now() - session.last_activity > timedelta(seconds=session.permissions.session_timeout):
            session.is_active = False
            return False
        
        # Update last activity
        session.last_activity = datetime.now()
        return session.is_active
    
    def get_session(self, session_id: str) -> Optional[AuthSession]:
        """Get session by ID"""
        return self.sessions.get(session_id)
    
    def check_permission(self, session_id: str, permission: PermissionType) -> bool:
        """Check if user has specific permission"""
        if not self.validate_session(session_id):
            return False
        
        session = self.sessions[session_id]
        return session.permissions.permissions.get(permission, False)
    
    def revoke_session(self, session_id: str) -> bool:
        """Revoke user session"""
        if session_id in self.sessions:
            self.sessions[session_id].is_active = False
            del self.sessions[session_id]
            return True
        return False
    
    def list_users(self) -> List[Dict[str, Any]]:
        """List all enrolled users"""
        users = []
        for user_id, profile in self.profiles.items():
            users.append({
                'user_id': user_id,
                'username': profile.username,
                'auth_level': profile.auth_level.value,
                'enrollment_date': profile.enrollment_date.isoformat(),
                'last_verified': profile.last_verified.isoformat() if profile.last_verified else None,
                'verification_count': profile.verification_count,
                'is_active': profile.is_active
            })
        return users
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user profile"""
        if user_id in self.profiles:
            # Remove profile
            del self.profiles[user_id]
            
            # Remove model file
            model_path = Path(self.config.models_directory) / f"{user_id}_model.pkl"
            if model_path.exists():
                model_path.unlink()
            
            # Remove from models dict
            if user_id in self.models:
                del self.models[user_id]
            
            # Revoke active sessions
            sessions_to_revoke = [sid for sid, session in self.sessions.items() if session.user_id == user_id]
            for session_id in sessions_to_revoke:
                self.revoke_session(session_id)
            
            self._save_profiles()
            
            self.logger.info(f"User {user_id} deleted successfully")
            return True
        
        return False

# Export main classes
__all__ = [
    'VoiceAuthenticator',
    'AuthenticationLevel',
    'VoiceAuthStatus',
    'PermissionType',
    'VoiceProfile',
    'UserPermissions',
    'AuthSession',
    'VoiceAuthConfig'
]