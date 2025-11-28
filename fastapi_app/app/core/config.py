from pathlib import Path
from functools import lru_cache
from typing import Any, Dict, List

import yaml


BASE_DIR = Path(__file__).resolve().parent.parent  # app/
PROJECT_ROOT = BASE_DIR.parent                     # project root
CONFIG_PATH = PROJECT_ROOT / "config" / "settings.yaml"


class Settings:
    def __init__(self, raw: Dict[str, Any]) -> None:
        self.raw = raw
        self.app_name: str = raw.get("app", {}).get("name", "MT5 Portfolio Dashboard")
        self.version: str = raw.get("app", {}).get("version", "1.0")
        self.debug: bool = bool(raw.get("app", {}).get("debug", False))

        self.paths = raw.get("paths", {})
        self.raw_data = self.paths.get("raw_data", "./data/raw/")
        self.processed_data = self.paths.get("processed_data", "./data/processed/")
        self.backup_data = self.paths.get("backup_data", "./data/backups/")
        self.logs = self.paths.get("logs", "./logs/")

        self.mt5_sources: List[Dict[str, Any]] = raw.get("mt5_sources", [])

    def enabled_sources(self) -> List[Dict[str, Any]]:
        return [s for s in self.mt5_sources if s.get("enabled", True)]


@lru_cache()
def get_settings() -> "Settings":
    if not CONFIG_PATH.exists():
        default = {
            "app": {"name": "MT5 Portfolio Dashboard", "version": "1.0", "debug": True},
            "paths": {
                "raw_data": "./data/raw/",
                "processed_data": "./data/processed/",
                "backup_data": "./data/backups/",
                "logs": "./logs/",
            },
            "mt5_sources": [],
        }
        return Settings(default)

    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    return Settings(raw)
