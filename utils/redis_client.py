#!/usr/bin/python3
"""
Redis client utility module for caching and session management.

This module provides Redis connection and utility functions for
caching, session management, and rate limiting.

Classes:
    RedisClient: Singleton class for Redis connection management
"""
import redis
from typing import Optional, Any
import json
from datetime import timedelta

class RedisClient:
    """
    Singleton Redis client class for centralized Redis operations.

    This class manages Redis connections and provides utility methods
    for common Redis operations including caching and session management.

    Attributes:
        _instance: Singleton instance
        client: Redis client connection
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client = redis.Redis(
                host='localhost',
                port=6379,
                db=0,
                decode_responses=True
            )
        return cls._instance

    def cache_get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        data = self.client.get(key)
        return json.loads(data) if data else None

    def cache_set(self, key: str, value: Any, 
                  expire: Optional[int] = None) -> None:
        """Set value in cache with optional expiration."""
        self.client.set(key, json.dumps(value), ex=expire)

    def cache_delete(self, key: str) -> None:
        """Delete value from cache."""
        self.client.delete(key)

    def session_set(self, session_id: str, user_data: dict, 
                    expire: int = 3600) -> None:
        """Store session data with expiration."""
        self.cache_set(f"session:{session_id}", user_data, expire)

    def session_get(self, session_id: str) -> Optional[dict]:
        """Retrieve session data."""
        return self.cache_get(f"session:{session_id}")

    def session_delete(self, session_id: str) -> None:
        """Delete session data."""
        self.cache_delete(f"session:{session_id}")

    def rate_limit(self, key: str, limit: int, 
                   period: int = 3600) -> bool:
        """
        Implement rate limiting.
        
        Args:
            key: Rate limit key (e.g., "ip:123.45.67.89")
            limit: Maximum requests allowed
            period: Time period in seconds
            
        Returns:
            bool: True if within limit, False if exceeded
        """
        current = self.client.incr(key)
        if current == 1:
            self.client.expire(key, period)
        return current <= limit
