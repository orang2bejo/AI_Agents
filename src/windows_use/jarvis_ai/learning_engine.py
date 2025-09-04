"""Learning Engine Module

Implements machine learning and adaptive capabilities for the Jarvis AI system,
including user preference learning, command pattern recognition, and system optimization.
"""

import json
import logging
import pickle
import time
import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set, Union

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class LearningType(Enum):
    """Types of learning"""
    USER_PREFERENCES = "user_preferences"
    COMMAND_PATTERNS = "command_patterns"
    RESPONSE_OPTIMIZATION = "response_optimization"
    TASK_EFFICIENCY = "task_efficiency"
    ERROR_PREDICTION = "error_prediction"
    CONTEXT_AWARENESS = "context_awareness"
    LANGUAGE_ADAPTATION = "language_adaptation"

class ModelType(Enum):
    """Machine learning model types"""
    NAIVE_BAYES = "naive_bayes"
    LOGISTIC_REGRESSION = "logistic_regression"
    KMEANS_CLUSTERING = "kmeans_clustering"
    NEURAL_NETWORK = "neural_network"
    DECISION_TREE = "decision_tree"
    RANDOM_FOREST = "random_forest"

class DataType(Enum):
    """Types of learning data"""
    VOICE_COMMAND = "voice_command"
    USER_INTERACTION = "user_interaction"
    TASK_EXECUTION = "task_execution"
    ERROR_LOG = "error_log"
    PERFORMANCE_METRIC = "performance_metric"
    CONTEXT_DATA = "context_data"

@dataclass
class LearningData:
    """Learning data point"""
    data_id: str
    data_type: DataType
    timestamp: float
    features: Dict[str, Any]
    labels: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    user_id: Optional[str] = None
    session_id: Optional[str] = None

@dataclass
class ModelMetrics:
    """Model performance metrics"""
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    training_time: float = 0.0
    prediction_time: float = 0.0
    data_points: int = 0
    last_updated: float = field(default_factory=time.time)

@dataclass
class UserProfile:
    """User learning profile"""
    user_id: str
    preferences: Dict[str, Any] = field(default_factory=dict)
    command_patterns: List[str] = field(default_factory=list)
    interaction_history: List[Dict[str, Any]] = field(default_factory=list)
    language_preference: str = "en"
    response_style: str = "formal"
    task_priorities: Dict[str, float] = field(default_factory=dict)
    learning_rate: float = 0.1
    created_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)

class LearningConfig(BaseModel):
    """Learning engine configuration"""
    # Data collection
    max_data_points: int = 10000
    data_retention_days: int = 90
    auto_cleanup: bool = True
    
    # Model training
    min_training_samples: int = 50
    retrain_interval: float = 3600.0  # 1 hour
    auto_retrain: bool = True
    validation_split: float = 0.2
    
    # Feature extraction
    max_features: int = 1000
    ngram_range: Tuple[int, int] = (1, 2)
    min_df: int = 2
    max_df: float = 0.95
    
    # Clustering
    max_clusters: int = 20
    min_cluster_size: int = 5
    
    # User profiling
    max_interaction_history: int = 1000
    preference_decay_rate: float = 0.95
    
    # Performance
    enable_caching: bool = True
    cache_size: int = 1000
    parallel_training: bool = True
    
    # Storage
    models_dir: str = "models"
    data_dir: str = "learning_data"
    backup_interval: float = 86400.0  # 24 hours

class FeatureExtractor:
    """Extract features from various data types"""
    
    def __init__(self, config: LearningConfig):
        self.config = config
        self.vectorizers = {}
        self.scalers = {}
    
    def extract_text_features(self, texts: List[str], feature_name: str = "default") -> np.ndarray:
        """Extract TF-IDF features from text"""
        if feature_name not in self.vectorizers:
            self.vectorizers[feature_name] = TfidfVectorizer(
                max_features=self.config.max_features,
                ngram_range=self.config.ngram_range,
                min_df=self.config.min_df,
                max_df=self.config.max_df,
                stop_words='english'
            )
            
            # Fit vectorizer
            self.vectorizers[feature_name].fit(texts)
        
        return self.vectorizers[feature_name].transform(texts).toarray()
    
    def extract_numerical_features(self, data: List[Dict[str, Any]], feature_name: str = "default") -> np.ndarray:
        """Extract and normalize numerical features"""
        # Convert to numpy array
        features = []
        for item in data:
            feature_vector = []
            for key, value in item.items():
                if isinstance(value, (int, float)):
                    feature_vector.append(value)
                elif isinstance(value, bool):
                    feature_vector.append(1.0 if value else 0.0)
            features.append(feature_vector)
        
        features_array = np.array(features)
        
        # Scale features
        if feature_name not in self.scalers:
            self.scalers[feature_name] = StandardScaler()
            self.scalers[feature_name].fit(features_array)
        
        return self.scalers[feature_name].transform(features_array)
    
    def extract_command_features(self, commands: List[str]) -> Dict[str, Any]:
        """Extract features from voice commands"""
        features = {
            'command_length': [len(cmd.split()) for cmd in commands],
            'command_complexity': [len(set(cmd.lower().split())) for cmd in commands],
            'has_question': [1 if '?' in cmd else 0 for cmd in commands],
            'has_negation': [1 if any(neg in cmd.lower() for neg in ['not', 'no', 'never']) else 0 for cmd in commands],
            'urgency_words': [sum(1 for word in ['urgent', 'quickly', 'now', 'immediately'] if word in cmd.lower()) for cmd in commands]
        }
        
        return features
    
    def extract_temporal_features(self, timestamps: List[float]) -> Dict[str, Any]:
        """Extract temporal features"""
        datetimes = [datetime.fromtimestamp(ts) for ts in timestamps]
        
        features = {
            'hour_of_day': [dt.hour for dt in datetimes],
            'day_of_week': [dt.weekday() for dt in datetimes],
            'is_weekend': [1 if dt.weekday() >= 5 else 0 for dt in datetimes],
            'is_business_hours': [1 if 9 <= dt.hour <= 17 else 0 for dt in datetimes],
            'month': [dt.month for dt in datetimes]
        }
        
        return features

class ModelManager:
    """Manage machine learning models"""
    
    def __init__(self, config: LearningConfig):
        self.config = config
        self.models: Dict[str, Any] = {}
        self.metrics: Dict[str, ModelMetrics] = {}
        self.feature_extractors: Dict[str, FeatureExtractor] = {}
        
        # Create models directory
        self.models_dir = Path(config.models_dir)
        self.models_dir.mkdir(exist_ok=True)
    
    def create_model(self, model_name: str, model_type: ModelType, **kwargs) -> Any:
        """Create a new model"""
        if model_type == ModelType.NAIVE_BAYES:
            model = MultinomialNB(**kwargs)
        elif model_type == ModelType.LOGISTIC_REGRESSION:
            model = LogisticRegression(**kwargs)
        elif model_type == ModelType.KMEANS_CLUSTERING:
            n_clusters = kwargs.pop('n_clusters', 5)
            model = KMeans(n_clusters=n_clusters, random_state=42, **kwargs)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
        
        self.models[model_name] = model
        self.metrics[model_name] = ModelMetrics()
        
        logger.info(f"Created model: {model_name} ({model_type.value})")
        return model
    
    def train_model(
        self,
        model_name: str,
        X: np.ndarray,
        y: Optional[np.ndarray] = None,
        validation_split: float = None
    ) -> ModelMetrics:
        """Train a model"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        
        model = self.models[model_name]
        start_time = time.time()
        
        try:
            if y is not None:
                # Supervised learning
                if validation_split and validation_split > 0:
                    X_train, X_val, y_train, y_val = train_test_split(
                        X, y, test_size=validation_split, random_state=42
                    )
                    
                    # Train model
                    model.fit(X_train, y_train)
                    
                    # Validate
                    y_pred = model.predict(X_val)
                    accuracy = accuracy_score(y_val, y_pred)
                    
                    # Update metrics
                    metrics = self.metrics[model_name]
                    metrics.accuracy = accuracy
                    metrics.data_points = len(X)
                    metrics.training_time = time.time() - start_time
                    metrics.last_updated = time.time()
                    
                    logger.info(f"Model {model_name} trained with accuracy: {accuracy:.3f}")
                else:
                    # Train on all data
                    model.fit(X, y)
                    
                    metrics = self.metrics[model_name]
                    metrics.data_points = len(X)
                    metrics.training_time = time.time() - start_time
                    metrics.last_updated = time.time()
            else:
                # Unsupervised learning
                model.fit(X)
                
                metrics = self.metrics[model_name]
                metrics.data_points = len(X)
                metrics.training_time = time.time() - start_time
                metrics.last_updated = time.time()
                
                logger.info(f"Model {model_name} trained (unsupervised)")
            
            return self.metrics[model_name]
            
        except Exception as e:
            logger.error(f"Error training model {model_name}: {e}")
            raise
    
    def predict(self, model_name: str, X: np.ndarray) -> np.ndarray:
        """Make predictions with a model"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        
        model = self.models[model_name]
        start_time = time.time()
        
        try:
            predictions = model.predict(X)
            
            # Update prediction time metric
            prediction_time = time.time() - start_time
            self.metrics[model_name].prediction_time = prediction_time
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error making predictions with model {model_name}: {e}")
            raise
    
    def predict_proba(self, model_name: str, X: np.ndarray) -> np.ndarray:
        """Get prediction probabilities"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        
        model = self.models[model_name]
        
        if hasattr(model, 'predict_proba'):
            return model.predict_proba(X)
        else:
            raise ValueError(f"Model {model_name} does not support probability predictions")
    
    def save_model(self, model_name: str) -> bool:
        """Save model to disk"""
        if model_name not in self.models:
            return False
        
        try:
            model_path = self.models_dir / f"{model_name}.pkl"
            with open(model_path, 'wb') as f:
                pickle.dump({
                    'model': self.models[model_name],
                    'metrics': self.metrics[model_name]
                }, f)
            
            logger.info(f"Model {model_name} saved to {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving model {model_name}: {e}")
            return False
    
    def load_model(self, model_name: str) -> bool:
        """Load model from disk"""
        try:
            model_path = self.models_dir / f"{model_name}.pkl"
            if not model_path.exists():
                return False
            
            with open(model_path, 'rb') as f:
                data = pickle.load(f)
            
            self.models[model_name] = data['model']
            self.metrics[model_name] = data['metrics']
            
            logger.info(f"Model {model_name} loaded from {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {e}")
            return False
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get model information"""
        if model_name not in self.models:
            return None
        
        model = self.models[model_name]
        metrics = self.metrics[model_name]
        
        return {
            'name': model_name,
            'type': type(model).__name__,
            'metrics': metrics.__dict__,
            'parameters': getattr(model, 'get_params', lambda: {})(),
            'is_fitted': hasattr(model, 'classes_') or hasattr(model, 'cluster_centers_')
        }

class DataManager:
    """Manage learning data"""
    
    def __init__(self, config: LearningConfig):
        self.config = config
        self.data: List[LearningData] = []
        self.data_lock = threading.RLock()
        
        # Create data directory
        self.data_dir = Path(config.data_dir)
        self.data_dir.mkdir(exist_ok=True)
    
    def add_data(self, data: LearningData):
        """Add learning data"""
        with self.data_lock:
            self.data.append(data)
            
            # Cleanup if needed
            if len(self.data) > self.config.max_data_points:
                self._cleanup_old_data()
    
    def get_data(
        self,
        data_type: Optional[DataType] = None,
        user_id: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        limit: Optional[int] = None
    ) -> List[LearningData]:
        """Get filtered learning data"""
        with self.data_lock:
            filtered_data = self.data.copy()
            
            # Apply filters
            if data_type:
                filtered_data = [d for d in filtered_data if d.data_type == data_type]
            
            if user_id:
                filtered_data = [d for d in filtered_data if d.user_id == user_id]
            
            if start_time:
                filtered_data = [d for d in filtered_data if d.timestamp >= start_time]
            
            if end_time:
                filtered_data = [d for d in filtered_data if d.timestamp <= end_time]
            
            # Sort by timestamp (newest first)
            filtered_data.sort(key=lambda x: x.timestamp, reverse=True)
            
            # Apply limit
            if limit:
                filtered_data = filtered_data[:limit]
            
            return filtered_data
    
    def _cleanup_old_data(self):
        """Remove old data points"""
        if not self.config.auto_cleanup:
            return
        
        cutoff_time = time.time() - (self.config.data_retention_days * 86400)
        
        original_count = len(self.data)
        self.data = [d for d in self.data if d.timestamp >= cutoff_time]
        
        # If still too many, remove oldest
        if len(self.data) > self.config.max_data_points:
            self.data.sort(key=lambda x: x.timestamp, reverse=True)
            self.data = self.data[:self.config.max_data_points]
        
        removed_count = original_count - len(self.data)
        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} old data points")
    
    def save_data(self) -> bool:
        """Save data to disk"""
        try:
            data_path = self.data_dir / "learning_data.json"
            
            with self.data_lock:
                data_dict = [{
                    'data_id': d.data_id,
                    'data_type': d.data_type.value,
                    'timestamp': d.timestamp,
                    'features': d.features,
                    'labels': d.labels,
                    'metadata': d.metadata,
                    'user_id': d.user_id,
                    'session_id': d.session_id
                } for d in self.data]
            
            with open(data_path, 'w') as f:
                json.dump(data_dict, f, indent=2)
            
            logger.info(f"Saved {len(data_dict)} data points to {data_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            return False
    
    def load_data(self) -> bool:
        """Load data from disk"""
        try:
            data_path = self.data_dir / "learning_data.json"
            if not data_path.exists():
                return False
            
            with open(data_path, 'r') as f:
                data_dict = json.load(f)
            
            with self.data_lock:
                self.data = []
                for item in data_dict:
                    data = LearningData(
                        data_id=item['data_id'],
                        data_type=DataType(item['data_type']),
                        timestamp=item['timestamp'],
                        features=item['features'],
                        labels=item.get('labels'),
                        metadata=item.get('metadata', {}),
                        user_id=item.get('user_id'),
                        session_id=item.get('session_id')
                    )
                    self.data.append(data)
            
            logger.info(f"Loaded {len(self.data)} data points from {data_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get data statistics"""
        with self.data_lock:
            stats = {
                'total_points': len(self.data),
                'by_type': {},
                'by_user': {},
                'time_range': None
            }
            
            if self.data:
                # Count by type
                for data in self.data:
                    data_type = data.data_type.value
                    stats['by_type'][data_type] = stats['by_type'].get(data_type, 0) + 1
                    
                    if data.user_id:
                        stats['by_user'][data.user_id] = stats['by_user'].get(data.user_id, 0) + 1
                
                # Time range
                timestamps = [d.timestamp for d in self.data]
                stats['time_range'] = {
                    'start': min(timestamps),
                    'end': max(timestamps),
                    'span_hours': (max(timestamps) - min(timestamps)) / 3600
                }
            
            return stats

class UserProfileManager:
    """Manage user learning profiles"""
    
    def __init__(self, config: LearningConfig):
        self.config = config
        self.profiles: Dict[str, UserProfile] = {}
        self.profiles_lock = threading.RLock()
        
        # Create profiles directory
        self.profiles_dir = Path(config.data_dir) / "profiles"
        self.profiles_dir.mkdir(exist_ok=True)
    
    def get_or_create_profile(self, user_id: str) -> UserProfile:
        """Get or create user profile"""
        with self.profiles_lock:
            if user_id not in self.profiles:
                self.profiles[user_id] = UserProfile(user_id=user_id)
                logger.info(f"Created new user profile: {user_id}")
            
            return self.profiles[user_id]
    
    def update_preferences(self, user_id: str, preferences: Dict[str, Any]):
        """Update user preferences"""
        profile = self.get_or_create_profile(user_id)
        
        with self.profiles_lock:
            # Apply decay to existing preferences
            for key in profile.preferences:
                if isinstance(profile.preferences[key], (int, float)):
                    profile.preferences[key] *= self.config.preference_decay_rate
            
            # Update with new preferences
            for key, value in preferences.items():
                if key in profile.preferences and isinstance(value, (int, float)):
                    # Weighted average
                    old_value = profile.preferences[key]
                    profile.preferences[key] = (
                        old_value * (1 - profile.learning_rate) + 
                        value * profile.learning_rate
                    )
                else:
                    profile.preferences[key] = value
            
            profile.last_updated = time.time()
    
    def add_interaction(self, user_id: str, interaction: Dict[str, Any]):
        """Add user interaction to history"""
        profile = self.get_or_create_profile(user_id)
        
        with self.profiles_lock:
            interaction['timestamp'] = time.time()
            profile.interaction_history.append(interaction)
            
            # Limit history size
            if len(profile.interaction_history) > self.config.max_interaction_history:
                profile.interaction_history = profile.interaction_history[-self.config.max_interaction_history:]
            
            profile.last_updated = time.time()
    
    def get_user_patterns(self, user_id: str) -> Dict[str, Any]:
        """Analyze user patterns"""
        profile = self.get_or_create_profile(user_id)
        
        with self.profiles_lock:
            patterns = {
                'command_frequency': {},
                'time_patterns': {},
                'task_preferences': {},
                'response_preferences': {}
            }
            
            # Analyze interaction history
            for interaction in profile.interaction_history:
                # Command frequency
                command = interaction.get('command', '')
                if command:
                    patterns['command_frequency'][command] = patterns['command_frequency'].get(command, 0) + 1
                
                # Time patterns
                timestamp = interaction.get('timestamp', time.time())
                hour = datetime.fromtimestamp(timestamp).hour
                patterns['time_patterns'][hour] = patterns['time_patterns'].get(hour, 0) + 1
                
                # Task preferences
                task_type = interaction.get('task_type', '')
                if task_type:
                    patterns['task_preferences'][task_type] = patterns['task_preferences'].get(task_type, 0) + 1
            
            return patterns
    
    def save_profile(self, user_id: str) -> bool:
        """Save user profile to disk"""
        if user_id not in self.profiles:
            return False
        
        try:
            profile_path = self.profiles_dir / f"{user_id}.json"
            profile = self.profiles[user_id]
            
            profile_dict = {
                'user_id': profile.user_id,
                'preferences': profile.preferences,
                'command_patterns': profile.command_patterns,
                'interaction_history': profile.interaction_history,
                'language_preference': profile.language_preference,
                'response_style': profile.response_style,
                'task_priorities': profile.task_priorities,
                'learning_rate': profile.learning_rate,
                'created_at': profile.created_at,
                'last_updated': profile.last_updated
            }
            
            with open(profile_path, 'w') as f:
                json.dump(profile_dict, f, indent=2)
            
            logger.info(f"Saved user profile: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving user profile {user_id}: {e}")
            return False
    
    def load_profile(self, user_id: str) -> bool:
        """Load user profile from disk"""
        try:
            profile_path = self.profiles_dir / f"{user_id}.json"
            if not profile_path.exists():
                return False
            
            with open(profile_path, 'r') as f:
                profile_dict = json.load(f)
            
            profile = UserProfile(
                user_id=profile_dict['user_id'],
                preferences=profile_dict.get('preferences', {}),
                command_patterns=profile_dict.get('command_patterns', []),
                interaction_history=profile_dict.get('interaction_history', []),
                language_preference=profile_dict.get('language_preference', 'en'),
                response_style=profile_dict.get('response_style', 'formal'),
                task_priorities=profile_dict.get('task_priorities', {}),
                learning_rate=profile_dict.get('learning_rate', 0.1),
                created_at=profile_dict.get('created_at', time.time()),
                last_updated=profile_dict.get('last_updated', time.time())
            )
            
            with self.profiles_lock:
                self.profiles[user_id] = profile
            
            logger.info(f"Loaded user profile: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading user profile {user_id}: {e}")
            return False

class LearningEngine:
    """Main learning engine for Jarvis AI"""
    
    def __init__(self, config: LearningConfig = None):
        self.config = config or LearningConfig()
        
        # Components
        self.data_manager = DataManager(self.config)
        self.model_manager = ModelManager(self.config)
        self.profile_manager = UserProfileManager(self.config)
        self.feature_extractor = FeatureExtractor(self.config)
        
        # Control
        self.is_running = False
        self.training_thread: Optional[threading.Thread] = None
        
        # Initialize models
        self._initialize_models()
        
        logger.info("Learning Engine initialized")
    
    def _initialize_models(self):
        """Initialize default models"""
        # Command classification model
        self.model_manager.create_model(
            "command_classifier",
            ModelType.NAIVE_BAYES,
            alpha=1.0
        )
        
        # User preference clustering
        self.model_manager.create_model(
            "preference_clusters",
            ModelType.KMEANS_CLUSTERING,
            n_clusters=5
        )
        
        # Response optimization
        self.model_manager.create_model(
            "response_optimizer",
            ModelType.LOGISTIC_REGRESSION,
            random_state=42
        )
    
    def start(self):
        """Start learning engine"""
        if self.is_running:
            logger.warning("Learning engine is already running")
            return
        
        self.is_running = True
        
        # Load existing data and models
        self.data_manager.load_data()
        self._load_models()
        
        # Start training thread
        if self.config.auto_retrain:
            self.training_thread = threading.Thread(target=self._training_loop, daemon=True)
            self.training_thread.start()
        
        logger.info("Learning Engine started")
    
    def stop(self):
        """Stop learning engine"""
        if not self.is_running:
            return
        
        logger.info("Stopping Learning Engine...")
        
        self.is_running = False
        
        # Wait for training thread
        if self.training_thread and self.training_thread.is_alive():
            self.training_thread.join(timeout=10.0)
        
        # Save data and models
        self.data_manager.save_data()
        self._save_models()
        
        logger.info("Learning Engine stopped")
    
    def learn_from_command(self, command_text: str, user_id: str, success: bool, metadata: Dict[str, Any] = None):
        """Learn from voice command execution"""
        data = LearningData(
            data_id=f"cmd_{int(time.time() * 1000)}",
            data_type=DataType.VOICE_COMMAND,
            timestamp=time.time(),
            features={
                'command_text': command_text,
                'command_length': len(command_text.split()),
                'has_question': '?' in command_text,
                'success': success
            },
            labels={'success': success},
            metadata=metadata or {},
            user_id=user_id
        )
        
        self.data_manager.add_data(data)
        
        # Update user profile
        interaction = {
            'type': 'voice_command',
            'command': command_text,
            'success': success,
            'metadata': metadata or {}
        }
        self.profile_manager.add_interaction(user_id, interaction)
        
        logger.debug(f"Learned from command: {command_text[:50]}...")
    
    def learn_from_task(self, task_type: str, user_id: str, execution_time: float, success: bool, metadata: Dict[str, Any] = None):
        """Learn from task execution"""
        data = LearningData(
            data_id=f"task_{int(time.time() * 1000)}",
            data_type=DataType.TASK_EXECUTION,
            timestamp=time.time(),
            features={
                'task_type': task_type,
                'execution_time': execution_time,
                'success': success,
                'hour_of_day': datetime.now().hour,
                'day_of_week': datetime.now().weekday()
            },
            labels={'success': success, 'execution_time': execution_time},
            metadata=metadata or {},
            user_id=user_id
        )
        
        self.data_manager.add_data(data)
        
        # Update user task priorities
        profile = self.profile_manager.get_or_create_profile(user_id)
        if success:
            current_priority = profile.task_priorities.get(task_type, 0.5)
            profile.task_priorities[task_type] = min(1.0, current_priority + 0.1)
        
        logger.debug(f"Learned from task: {task_type}")
    
    def predict_command_success(self, command_text: str, user_id: str) -> float:
        """Predict likelihood of command success"""
        try:
            # Extract features
            features = self.feature_extractor.extract_text_features([command_text], "command_success")
            
            # Get prediction
            model_name = "command_classifier"
            if model_name in self.model_manager.models:
                probabilities = self.model_manager.predict_proba(model_name, features)
                if len(probabilities) > 0 and len(probabilities[0]) > 1:
                    return probabilities[0][1]  # Probability of success
            
            return 0.5  # Default neutral probability
            
        except Exception as e:
            logger.error(f"Error predicting command success: {e}")
            return 0.5
    
    def get_user_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get personalized recommendations for user"""
        profile = self.profile_manager.get_or_create_profile(user_id)
        patterns = self.profile_manager.get_user_patterns(user_id)
        
        recommendations = []
        
        # Most used commands
        command_freq = patterns.get('command_frequency', {})
        if command_freq:
            top_commands = sorted(command_freq.items(), key=lambda x: x[1], reverse=True)[:3]
            recommendations.append({
                'type': 'frequent_commands',
                'title': 'Your Most Used Commands',
                'items': [cmd for cmd, _ in top_commands]
            })
        
        # Time-based suggestions
        current_hour = datetime.now().hour
        time_patterns = patterns.get('time_patterns', {})
        if current_hour in time_patterns:
            recommendations.append({
                'type': 'time_based',
                'title': f'Common Actions at {current_hour}:00',
                'items': ['Based on your usage patterns']
            })
        
        # Task preferences
        task_prefs = patterns.get('task_preferences', {})
        if task_prefs:
            top_tasks = sorted(task_prefs.items(), key=lambda x: x[1], reverse=True)[:3]
            recommendations.append({
                'type': 'preferred_tasks',
                'title': 'Your Preferred Task Types',
                'items': [task for task, _ in top_tasks]
            })
        
        return recommendations
    
    def optimize_response_style(self, user_id: str, response_text: str, user_feedback: float) -> str:
        """Optimize response style based on user feedback"""
        profile = self.profile_manager.get_or_create_profile(user_id)
        
        # Update preferences based on feedback
        preferences = {
            'response_length': len(response_text.split()),
            'formality': 1.0 if any(word in response_text.lower() for word in ['please', 'thank you', 'sir', 'madam']) else 0.0,
            'directness': 1.0 if len(response_text.split()) < 10 else 0.0,
            'feedback_score': user_feedback
        }
        
        self.profile_manager.update_preferences(user_id, preferences)
        
        # Adjust response style
        if profile.preferences.get('directness', 0.5) > 0.7:
            profile.response_style = 'direct'
        elif profile.preferences.get('formality', 0.5) > 0.7:
            profile.response_style = 'formal'
        else:
            profile.response_style = 'casual'
        
        return profile.response_style
    
    def _training_loop(self):
        """Background training loop"""
        logger.info("Learning training loop started")
        
        while self.is_running:
            try:
                # Check if we have enough data for training
                data_stats = self.data_manager.get_statistics()
                
                if data_stats['total_points'] >= self.config.min_training_samples:
                    self._retrain_models()
                
                time.sleep(self.config.retrain_interval)
                
            except Exception as e:
                logger.error(f"Error in training loop: {e}")
                time.sleep(60.0)
        
        logger.info("Learning training loop stopped")
    
    def _retrain_models(self):
        """Retrain models with latest data"""
        logger.info("Starting model retraining...")
        
        try:
            # Retrain command classifier
            self._retrain_command_classifier()
            
            # Retrain preference clusters
            self._retrain_preference_clusters()
            
            logger.info("Model retraining completed")
            
        except Exception as e:
            logger.error(f"Error during model retraining: {e}")
    
    def _retrain_command_classifier(self):
        """Retrain command classification model"""
        # Get command data
        command_data = self.data_manager.get_data(data_type=DataType.VOICE_COMMAND)
        
        if len(command_data) < self.config.min_training_samples:
            return
        
        # Extract features and labels
        texts = [d.features.get('command_text', '') for d in command_data]
        labels = [d.labels.get('success', False) for d in command_data if d.labels]
        
        if len(texts) != len(labels):
            return
        
        # Extract text features
        X = self.feature_extractor.extract_text_features(texts, "command_success")
        y = np.array(labels, dtype=int)
        
        # Train model
        self.model_manager.train_model(
            "command_classifier",
            X, y,
            validation_split=self.config.validation_split
        )
        
        logger.info("Command classifier retrained")
    
    def _retrain_preference_clusters(self):
        """Retrain user preference clustering"""
        # Get user interaction data
        interaction_data = self.data_manager.get_data(data_type=DataType.USER_INTERACTION)
        
        if len(interaction_data) < self.config.min_training_samples:
            return
        
        # Extract numerical features
        feature_dicts = [d.features for d in interaction_data]
        X = self.feature_extractor.extract_numerical_features(feature_dicts, "user_preferences")
        
        # Determine optimal number of clusters
        n_clusters = min(self.config.max_clusters, max(2, len(X) // self.config.min_cluster_size))
        
        # Update model
        model = self.model_manager.models.get("preference_clusters")
        if model:
            model.n_clusters = n_clusters
        
        # Train model
        self.model_manager.train_model("preference_clusters", X)
        
        logger.info(f"Preference clusters retrained with {n_clusters} clusters")
    
    def _save_models(self):
        """Save all models"""
        for model_name in self.model_manager.models:
            self.model_manager.save_model(model_name)
    
    def _load_models(self):
        """Load all models"""
        model_files = list(self.model_manager.models_dir.glob("*.pkl"))
        
        for model_file in model_files:
            model_name = model_file.stem
            self.model_manager.load_model(model_name)
    
    def get_learning_statistics(self) -> Dict[str, Any]:
        """Get comprehensive learning statistics"""
        data_stats = self.data_manager.get_statistics()
        
        model_stats = {}
        for model_name in self.model_manager.models:
            model_info = self.model_manager.get_model_info(model_name)
            if model_info:
                model_stats[model_name] = model_info
        
        profile_stats = {
            'total_profiles': len(self.profile_manager.profiles),
            'active_profiles': len([
                p for p in self.profile_manager.profiles.values()
                if time.time() - p.last_updated < 86400  # Active in last 24h
            ])
        }
        
        return {
            'data': data_stats,
            'models': model_stats,
            'profiles': profile_stats,
            'is_running': self.is_running
        }

# Example usage
if __name__ == "__main__":
    import random
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create learning engine
    engine = LearningEngine()
    engine.start()
    
    try:
        # Simulate learning from commands
        commands = [
            "open excel", "create new document", "send email", "search for files",
            "play music", "set reminder", "check weather", "calculate sum"
        ]
        
        users = ["user1", "user2", "user3"]
        
        # Generate training data
        for _ in range(100):
            command = random.choice(commands)
            user = random.choice(users)
            success = random.random() > 0.2  # 80% success rate
            
            engine.learn_from_command(command, user, success)
            
            # Simulate task execution
            task_type = random.choice(["office", "web", "system", "media"])
            execution_time = random.uniform(0.5, 5.0)
            task_success = random.random() > 0.15  # 85% success rate
            
            engine.learn_from_task(task_type, user, execution_time, task_success)
        
        # Wait for training
        time.sleep(5)
        
        # Test predictions
        for command in commands[:3]:
            for user in users[:2]:
                success_prob = engine.predict_command_success(command, user)
                print(f"Command '{command}' for {user}: {success_prob:.3f} success probability")
        
        # Get recommendations
        for user in users[:2]:
            recommendations = engine.get_user_recommendations(user)
            print(f"\nRecommendations for {user}:")
            for rec in recommendations:
                print(f"  {rec['title']}: {rec['items']}")
        
        # Print statistics
        stats = engine.get_learning_statistics()
        print("\nLearning Statistics:")
        print(f"  Data points: {stats['data']['total_points']}")
        print(f"  Models: {len(stats['models'])}")
        print(f"  User profiles: {stats['profiles']['total_profiles']}")
        
    finally:
        # Stop engine
        engine.stop()