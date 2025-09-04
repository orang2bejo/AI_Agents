"""Configuration management for the Self-Evolving Agent system.

This module provides configuration classes and utilities for managing
evolution engine settings, performance thresholds, and system parameters.
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class EvaluationConfig:
    """Configuration for performance evaluation."""
    accuracy_threshold: float = 0.8
    efficiency_threshold: float = 0.7
    success_rate_threshold: float = 0.85
    min_samples_for_evaluation: int = 10
    evaluation_window_hours: int = 24
    

@dataclass
class ReflectionConfig:
    """Configuration for behavioral reflection."""
    min_experiences_for_reflection: int = 20
    failure_analysis_threshold: float = 0.3
    success_pattern_threshold: float = 0.8
    confidence_threshold: float = 0.6
    max_insights_per_reflection: int = 5
    

@dataclass
class MutationConfig:
    """Configuration for behavioral mutations."""
    max_mutations_per_cycle: int = 3
    mutation_success_threshold: float = 0.7
    rollback_threshold: float = 0.5
    parameter_adjustment_range: float = 0.2
    timeout_adjustment_factor: float = 1.5
    

@dataclass
class MemoryConfig:
    """Configuration for experience memory."""
    max_experiences: int = 10000
    retention_days: int = 30
    cleanup_interval_hours: int = 24
    similarity_threshold: float = 0.8
    confidence_decay_rate: float = 0.95
    

@dataclass
class EvolutionConfig:
    """Main configuration for the evolution engine."""
    # Core settings
    evaluation_interval: int = 3600  # seconds
    enable_auto_evolution: bool = True
    max_evolution_cycles_per_day: int = 24
    
    # Component configurations
    evaluation: EvaluationConfig = None
    reflection: ReflectionConfig = None
    mutation: MutationConfig = None
    memory: MemoryConfig = None
    
    # Logging and monitoring
    log_level: str = "INFO"
    enable_metrics_export: bool = True
    metrics_export_interval: int = 300  # seconds
    
    # Safety settings
    enable_safety_checks: bool = True
    require_human_approval: bool = False
    emergency_stop_threshold: float = 0.3
    
    def __post_init__(self):
        if self.evaluation is None:
            self.evaluation = EvaluationConfig()
        if self.reflection is None:
            self.reflection = ReflectionConfig()
        if self.mutation is None:
            self.mutation = MutationConfig()
        if self.memory is None:
            self.memory = MemoryConfig()


class ConfigManager:
    """Manages configuration loading, saving, and validation."""
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir) if config_dir else Path.cwd() / "config"
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / "evolution_config.json"
        
    def load_config(self) -> EvolutionConfig:
        """Load configuration from file or create default."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                return self._dict_to_config(config_data)
            except Exception as e:
                print(f"Error loading config: {e}. Using default configuration.")
        
        # Return default configuration
        return EvolutionConfig()
    
    def save_config(self, config: EvolutionConfig) -> bool:
        """Save configuration to file."""
        try:
            config_data = self._config_to_dict(config)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def update_config(self, updates: Dict[str, Any]) -> EvolutionConfig:
        """Update configuration with new values."""
        config = self.load_config()
        config_dict = self._config_to_dict(config)
        
        # Apply updates
        self._deep_update(config_dict, updates)
        
        # Convert back to config object
        updated_config = self._dict_to_config(config_dict)
        
        # Save updated configuration
        self.save_config(updated_config)
        
        return updated_config
    
    def validate_config(self, config: EvolutionConfig) -> bool:
        """Validate configuration values."""
        try:
            # Validate evaluation config
            eval_config = config.evaluation
            assert 0 <= eval_config.accuracy_threshold <= 1
            assert 0 <= eval_config.efficiency_threshold <= 1
            assert 0 <= eval_config.success_rate_threshold <= 1
            assert eval_config.min_samples_for_evaluation > 0
            assert eval_config.evaluation_window_hours > 0
            
            # Validate reflection config
            refl_config = config.reflection
            assert refl_config.min_experiences_for_reflection > 0
            assert 0 <= refl_config.failure_analysis_threshold <= 1
            assert 0 <= refl_config.success_pattern_threshold <= 1
            assert 0 <= refl_config.confidence_threshold <= 1
            assert refl_config.max_insights_per_reflection > 0
            
            # Validate mutation config
            mut_config = config.mutation
            assert mut_config.max_mutations_per_cycle > 0
            assert 0 <= mut_config.mutation_success_threshold <= 1
            assert 0 <= mut_config.rollback_threshold <= 1
            assert mut_config.parameter_adjustment_range > 0
            assert mut_config.timeout_adjustment_factor > 0
            
            # Validate memory config
            mem_config = config.memory
            assert mem_config.max_experiences > 0
            assert mem_config.retention_days > 0
            assert mem_config.cleanup_interval_hours > 0
            assert 0 <= mem_config.similarity_threshold <= 1
            assert 0 <= mem_config.confidence_decay_rate <= 1
            
            # Validate main config
            assert config.evaluation_interval > 0
            assert config.max_evolution_cycles_per_day > 0
            assert config.log_level in ["DEBUG", "INFO", "WARNING", "ERROR"]
            assert config.metrics_export_interval > 0
            assert 0 <= config.emergency_stop_threshold <= 1
            
            return True
            
        except AssertionError as e:
            print(f"Configuration validation failed: {e}")
            return False
    
    def get_environment_overrides(self) -> Dict[str, Any]:
        """Get configuration overrides from environment variables."""
        overrides = {}
        
        # Environment variable mappings
        env_mappings = {
            "EVOLUTION_INTERVAL": ("evaluation_interval", int),
            "EVOLUTION_AUTO_ENABLE": ("enable_auto_evolution", lambda x: x.lower() == 'true'),
            "EVOLUTION_LOG_LEVEL": ("log_level", str),
            "EVOLUTION_SAFETY_CHECKS": ("enable_safety_checks", lambda x: x.lower() == 'true'),
            "EVOLUTION_HUMAN_APPROVAL": ("require_human_approval", lambda x: x.lower() == 'true'),
            "EVOLUTION_EMERGENCY_THRESHOLD": ("emergency_stop_threshold", float),
        }
        
        for env_var, (config_key, converter) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                try:
                    overrides[config_key] = converter(value)
                except (ValueError, TypeError) as e:
                    print(f"Invalid environment variable {env_var}: {e}")
        
        return overrides
    
    def _config_to_dict(self, config: EvolutionConfig) -> Dict[str, Any]:
        """Convert configuration object to dictionary."""
        return {
            "evaluation_interval": config.evaluation_interval,
            "enable_auto_evolution": config.enable_auto_evolution,
            "max_evolution_cycles_per_day": config.max_evolution_cycles_per_day,
            "log_level": config.log_level,
            "enable_metrics_export": config.enable_metrics_export,
            "metrics_export_interval": config.metrics_export_interval,
            "enable_safety_checks": config.enable_safety_checks,
            "require_human_approval": config.require_human_approval,
            "emergency_stop_threshold": config.emergency_stop_threshold,
            "evaluation": asdict(config.evaluation),
            "reflection": asdict(config.reflection),
            "mutation": asdict(config.mutation),
            "memory": asdict(config.memory)
        }
    
    def _dict_to_config(self, config_dict: Dict[str, Any]) -> EvolutionConfig:
        """Convert dictionary to configuration object."""
        # Extract component configs
        eval_config = EvaluationConfig(**config_dict.get("evaluation", {}))
        refl_config = ReflectionConfig(**config_dict.get("reflection", {}))
        mut_config = MutationConfig(**config_dict.get("mutation", {}))
        mem_config = MemoryConfig(**config_dict.get("memory", {}))
        
        # Create main config
        main_config_dict = {k: v for k, v in config_dict.items() 
                           if k not in ["evaluation", "reflection", "mutation", "memory"]}
        
        return EvolutionConfig(
            evaluation=eval_config,
            reflection=refl_config,
            mutation=mut_config,
            memory=mem_config,
            **main_config_dict
        )
    
    def _deep_update(self, base_dict: Dict[str, Any], update_dict: Dict[str, Any]):
        """Deep update dictionary with nested values."""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value


# Default configuration instance
default_config = EvolutionConfig()

# Configuration manager instance
config_manager = ConfigManager()