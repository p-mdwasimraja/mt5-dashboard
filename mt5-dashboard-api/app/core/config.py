"""
Configuration management for MT5 Dashboard API
Optimized for VPS deployment with caching
"""
from pathlib import Path
from typing import List, Dict, Any
from pydantic import Field
from pydantic_settings import BaseSettings
import yaml


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # App metadata
    app_name: str = "MT5 Dashboard API"
    version: str = "1.0.0"
    debug: bool = False

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False

    # Cache settings (optimized for VPS)
    cache_ttl: int = 300  # 5 minutes cache
    cache_max_size: int = 100  # Max cached items

    # Data paths
    config_path: str = "config/settings.yaml"
    data_path: str = "data"
    logs_path: str = "logs"

    # Performance settings
    max_workers: int = 2  # Limit workers for low-resource VPS
    enable_gzip: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
_settings: Settings | None = None
_mt5_config: Dict[str, Any] | None = None


def get_settings() -> Settings:
    """Get cached settings instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def get_mt5_config() -> Dict[str, Any]:
    """Load MT5 sources configuration from YAML"""
    global _mt5_config

    if _mt5_config is not None:
        return _mt5_config

    settings = get_settings()
    config_file = Path(settings.config_path)

    if not config_file.exists():
        # Return default config if file doesn't exist
        return {
            "mt5_sources": [],
            "paths": {
                "raw_data": "data/raw",
                "processed_data": "data/processed",
                "backup_data": "data/backup"
            }
        }

    with open(config_file, 'r') as f:
        _mt5_config = yaml.safe_load(f)

    return _mt5_config


def get_enabled_sources() -> List[Dict[str, Any]]:
    """Get list of enabled MT5 sources"""
    config = get_mt5_config()
    sources = config.get("mt5_sources", [])
    return [src for src in sources if src.get("enabled", False)]


def reload_config():
    """Force reload configuration (useful for updates)"""
    global _mt5_config
    _mt5_config = None
    return get_mt5_config()
