import os
import yaml
from pathlib import Path
import logging

class Config:
    def __init__(self, config_path="config/settings.yaml"):
        self.config_path = config_path
        self.settings = {}
        self.load_config()
        
    def load_config(self):
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as file:
                self.settings = yaml.safe_load(file)
            
            # Ensure all directories exist
            self.create_directories()
            
        except FileNotFoundError:
            logging.warning(f"Config file {self.config_path} not found, using defaults")
            self.set_defaults()
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            self.set_defaults()
    
    def set_defaults(self):
        """Set default configuration"""
        self.settings = {
            'app': {'name': 'MT5 Auto Dashboard', 'version': '2.0', 'debug': False},
            'paths': {
                'raw_data': './data/raw/',
                'processed_data': './data/processed/',
                'backup_data': './data/backups/',
                'logs': './logs/'
            },
            'dashboard': {'port': 8050, 'host': '127.0.0.1', 'debug': False}
        }
    
    def create_directories(self):
        """Create necessary directories"""
        directories = [
            self.settings['paths']['raw_data'],
            self.settings['paths']['processed_data'],
            self.settings['paths']['backup_data'],
            self.settings['paths']['logs']
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def get(self, key, default=None):
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self.settings
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

# Global configuration instance
config = Config()