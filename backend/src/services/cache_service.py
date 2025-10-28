"""Caching service for PrepSmart."""

import json
from datetime import datetime, timedelta
from typing import Any, Optional

from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class CacheService:
    """Simple in-memory cache with TTL support."""

    def __init__(self) -> None:
        """Initialize cache."""
        self._cache: dict[str, tuple[Any, datetime]] = {}

    def _generate_key(self, data: dict) -> str:
        """
        Generate cache key from data.

        Args:
            data: Data to generate key from

        Returns:
            Cache key string
        """
        # Create a stable JSON representation for cache key
        json_str = json.dumps(data, sort_keys=True)
        return json_str

    def get(self, data: dict) -> Optional[Any]:
        """
        Get cached value.

        Args:
            data: Data to look up

        Returns:
            Cached value or None if not found/expired
        """
        key = self._generate_key(data)

        if key not in self._cache:
            logger.debug(f"Cache miss for key: {key[:50]}...")
            return None

        value, expiry = self._cache[key]

        # Check if expired
        if datetime.utcnow() > expiry:
            logger.debug(f"Cache expired for key: {key[:50]}...")
            del self._cache[key]
            return None

        logger.debug(f"Cache hit for key: {key[:50]}...")
        return value

    def set(self, data: dict, value: Any, ttl: int = 3600) -> None:
        """
        Set cached value with TTL.

        Args:
            data: Data to use as key
            value: Value to cache
            ttl: Time to live in seconds (default: 1 hour)
        """
        key = self._generate_key(data)
        expiry = datetime.utcnow() + timedelta(seconds=ttl)
        self._cache[key] = (value, expiry)
        logger.debug(f"Cached value with TTL={ttl}s for key: {key[:50]}...")

    def clear(self) -> None:
        """Clear all cached values."""
        count = len(self._cache)
        self._cache.clear()
        logger.info(f"Cleared {count} cached items")

    def size(self) -> int:
        """Get current cache size."""
        return len(self._cache)
