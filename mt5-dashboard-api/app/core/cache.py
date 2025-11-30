"""
Caching layer for improved VPS performance
Uses in-memory caching to reduce CSV read operations
"""
from functools import wraps
from typing import Callable, Any
from datetime import datetime, timedelta
import hashlib
import json
from cachetools import TTLCache
from .config import get_settings


# Global cache instance
_cache = None


def get_cache() -> TTLCache:
    """Get or create the global cache instance"""
    global _cache
    if _cache is None:
        settings = get_settings()
        _cache = TTLCache(
            maxsize=settings.cache_max_size,
            ttl=settings.cache_ttl
        )
    return _cache


def cache_key(*args, **kwargs) -> str:
    """Generate a cache key from function arguments"""
    key_data = {
        'args': str(args),
        'kwargs': str(sorted(kwargs.items()))
    }
    key_string = json.dumps(key_data, sort_keys=True)
    return hashlib.md5(key_string.encode()).hexdigest()


def cached(func: Callable) -> Callable:
    """
    Decorator to cache function results
    Useful for expensive operations like CSV parsing
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        cache = get_cache()
        key = f"{func.__name__}:{cache_key(*args, **kwargs)}"

        # Try to get from cache
        if key in cache:
            return cache[key]

        # Execute function and cache result
        result = func(*args, **kwargs)
        cache[key] = result
        return result

    return wrapper


def clear_cache():
    """Clear all cached data (useful for manual refresh)"""
    cache = get_cache()
    cache.clear()


def get_cache_stats() -> dict:
    """Get cache statistics for monitoring"""
    cache = get_cache()
    return {
        "size": len(cache),
        "max_size": cache.maxsize,
        "ttl": cache.ttl,
        "hits": getattr(cache, 'hits', 0),
        "misses": getattr(cache, 'misses', 0)
    }
