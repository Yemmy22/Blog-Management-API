#!/usr/bin/python3
"""
Redis client utility module for caching, session management, and rate limiting.

This module provides Redis connection and utility functions for
caching, session management, and rate limiting.

Classes:
    RedisClient: Singleton class for Redis connection management
"""
import redis
from typing import Optional, Any
import json
from datetime import timedelta
import logging

# Configure logging for debugging purposes
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedisClient:
    """
    Singleton Redis client class for centralized Redis operations.

    This class manages Redis connections and provides utility methods
    for common Redis operations including caching, session management, and rate limiting.

    Attributes:
        _instance: Singleton instance
        client: Redis client connection
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            try:
                cls._instance.client = redis.Redis(
                    host='localhost',
                    port=6379,
                    db=0,
                    decode_responses=True
                )
                # Test connection
                cls._instance.client.ping()
                logger.info("Connected to Redis successfully.")
            except redis.ConnectionError as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise e
        return cls._instance

    def cache_get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            data = self.client.get(key)
            return json.loads(data) if data else None
        except (redis.RedisError, json.JSONDecodeError) as e:
            logger.error(f"Failed to get cache for key {key}: {e}")
            return None

    def cache_set(self, key: str, value: Any, expire: Optional[int] = None) -> None:
        """Set value in cache with optional expiration."""
        try:
            self.client.set(key, json.dumps(value), ex=expire)
        except (redis.RedisError, TypeError) as e:
            logger.error(f"Failed to set cache for key {key}: {e}")

    def cache_delete(self, key: str) -> None:
        """Delete value from cache."""
        try:
            self.client.delete(key)
        except redis.RedisError as e:
            logger.error(f"Failed to delete cache for key {key}: {e}")

    def session_set(self, session_id: str, user_data: dict, expire: int = 3600) -> None:
        """Store session data with expiration."""
        try:
            self.cache_set(f"session:{session_id}", user_data, expire)
        except Exception as e:
            logger.error(f"Failed to set session for session_id {session_id}: {e}")

    def session_get(self, session_id: str) -> Optional[dict]:
        """Retrieve session data."""
        try:
            return self.cache_get(f"session:{session_id}")
        except Exception as e:
            logger.error(f"Failed to get session for session_id {session_id}: {e}")
            return None

    def session_delete(self, session_id: str) -> None:
        """Delete session data."""
        try:
            self.cache_delete(f"session:{session_id}")
        except Exception as e:
            logger.error(f"Failed to delete session for session_id {session_id}: {e}")

    def rate_limit(self, key: str, limit: int, period: int = 3600) -> bool:
        """
        Implement rate limiting.
        
        Args:
            key: Rate limit key (e.g., "ip:123.45.67.89")
            limit: Maximum requests allowed
            period: Time period in seconds
            
        Returns:
            bool: True if within limit, False if exceeded
        """
        try:
            current = self.client.incr(key)
            if current == 1:
                self.client.expire(key, period)
            if current > limit:
                logger.warning(f"Rate limit exceeded for key {key}. Limit: {limit}, Period: {period}s.")
                return False
            return True
        except redis.RedisError as e:
            logger.error(f"Failed to apply rate limiting for key {key}: {e}")
            return False

    def reset_rate_limit(self, key: str) -> None:
        """Manually reset the rate limit for a given key."""
        try:
            self.cache_delete(key)
        except redis.RedisError as e:
            logger.error(f"Failed to reset rate limit for key {key}: {e}")

