"""
System administration endpoints
Health checks, cache management, monitoring
"""
from fastapi import APIRouter
import psutil
from datetime import datetime

from app.core.config import get_settings, reload_config
from app.core.cache import clear_cache, get_cache_stats
from app.core.loader import get_available_eas, get_available_symbols, get_available_accounts

router = APIRouter(prefix="/system", tags=["System"])


@router.get("/health")
async def health_check():
    """
    System health check
    """
    settings = get_settings()

    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.version,
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/cache/stats")
async def cache_stats():
    """
    Get cache statistics
    """
    stats = get_cache_stats()
    return {
        "cache": stats,
        "timestamp": datetime.now().isoformat(),
    }


@router.post("/cache/clear")
async def clear_cache_endpoint():
    """
    Clear all cached data
    Use this after updating MT5 data files
    """
    clear_cache()
    return {
        "status": "success",
        "message": "Cache cleared successfully",
        "timestamp": datetime.now().isoformat(),
    }


@router.post("/config/reload")
async def reload_config_endpoint():
    """
    Reload configuration from YAML
    """
    reload_config()
    clear_cache()  # Clear cache when config changes

    return {
        "status": "success",
        "message": "Configuration reloaded",
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/info")
async def system_info():
    """
    Get system information (VPS monitoring)
    """
    settings = get_settings()

    # System metrics
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    # Data metrics
    eas = get_available_eas()
    symbols = get_available_symbols()
    accounts = get_available_accounts()

    return {
        "system": {
            "cpu_usage_percent": cpu_percent,
            "memory_usage_percent": memory.percent,
            "memory_available_mb": round(memory.available / (1024 * 1024), 2),
            "disk_usage_percent": disk.percent,
            "disk_free_gb": round(disk.free / (1024 * 1024 * 1024), 2),
        },
        "data": {
            "total_eas": len(eas),
            "total_symbols": len(symbols),
            "total_accounts": len(accounts),
        },
        "cache": get_cache_stats(),
        "settings": {
            "cache_ttl": settings.cache_ttl,
            "cache_max_size": settings.cache_max_size,
            "debug": settings.debug,
        },
        "timestamp": datetime.now().isoformat(),
    }
