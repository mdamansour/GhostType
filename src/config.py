"""
Configuration loader for GhostType.
Implements singleton pattern to ensure single config instance.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


class Config:
    """Singleton configuration loader."""
    
    _instance = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Load configuration from config.json."""
        config_path = self._find_config_file()
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
            logger.info(f"Loaded config from: {config_path}")
        except FileNotFoundError:
            logger.warning(f"Config file not found at {config_path}, using defaults")
            self._config = self._get_defaults()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            logger.warning("Loading default configuration")
            self._config = self._get_defaults()
    
    def _find_config_file(self) -> Path:
        """Find config.json in current directory."""
        # Check current directory
        current_dir = Path.cwd()
        config_path = current_dir / "config.json"
        
        if config_path.exists():
            return config_path
        
        # Check script directory
        script_dir = Path(__file__).parent.parent
        config_path = script_dir / "config.json"
        
        if config_path.exists():
            return config_path
        
        # Default location
        return Path("config.json")
    
    def _get_defaults(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            "version": "0.1.0",
            "hotkeys": {
                "ptt": "ctrl+alt"
            },
            "audio": {
                "device": "default",
                "sample_rate": 16000,
                "channels": 1,
                "chunk_duration_ms": 100
            },
            "speech": {
                "model_path": "./models/vosk-model-small-en-us-0.15",
                "language": "en-us"
            },
            "system": {
                "log_level": "INFO",
                "log_file": "ghosttype.log"
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        Example: config.get('audio.sample_rate')
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """
        Set configuration value using dot notation.
        Example: config.set('audio.sample_rate', 48000)
        """
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self, path: str = None):
        """Save configuration to file."""
        if path is None:
            path = self._find_config_file()
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2)
            logger.info(f"Saved config to: {path}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    @property
    def all(self) -> Dict[str, Any]:
        """Get all configuration as dictionary."""
        return self._config.copy()
