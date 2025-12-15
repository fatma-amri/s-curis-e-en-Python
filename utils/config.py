"""
Configuration manager for the secure P2P messenger.
Handles loading and accessing application configuration.
"""

import json
import os
from pathlib import Path


class Config:
    """Configuration manager for application settings."""
    
    def __init__(self, config_file='config.json'):
        """Initialize configuration from JSON file."""
        self.config_file = config_file
        self._config = self._load_config()
        self._ensure_directories()
    
    def _load_config(self):
        """Load configuration from JSON file."""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return self._default_config()
    
    def _default_config(self):
        """Return default configuration."""
        return {
            "network": {
                "default_port": 5555,
                "bind_address": "0.0.0.0",
                "connection_timeout": 10,
                "heartbeat_interval": 30,
                "max_message_size": 10485760
            },
            "security": {
                "rekeying_message_threshold": 1000,
                "rekeying_time_threshold": 86400,
                "salt_size": 32,
                "nonce_size": 12
            },
            "storage": {
                "database_path": "data/database/messenger.db",
                "keys_directory": "data/keys",
                "files_directory": "data/files",
                "logs_directory": "data/logs"
            },
            "ui": {
                "window_width": 900,
                "window_height": 600,
                "message_max_length": 10000
            },
            "logging": {
                "level": "INFO",
                "max_file_size": 10485760,
                "backup_count": 5
            }
        }
    
    def _ensure_directories(self):
        """Ensure all required directories exist."""
        dirs = [
            self._config['storage']['keys_directory'],
            self._config['storage']['files_directory'],
            self._config['storage']['logs_directory'],
            os.path.dirname(self._config['storage']['database_path'])
        ]
        for directory in dirs:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def get(self, *keys):
        """Get configuration value by nested keys."""
        value = self._config
        for key in keys:
            value = value.get(key, {})
        return value
    
    def save(self):
        """Save current configuration to file."""
        with open(self.config_file, 'w') as f:
            json.dump(self._config, f, indent=4)


# Global configuration instance
config = Config()
