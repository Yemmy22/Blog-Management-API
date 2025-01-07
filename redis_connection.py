#!/usr/bin/python3
"""
Redis connection module for the Blog Management API.

This module provides a singleton Redis client instance for managing 
password reset tokens and other ephemeral data.

Attributes:
    redis_client: Redis client instance.
"""
import redis
from config import Config

# Initialize Redis client
redis_client = redis.StrictRedis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    decode_responses=True
)
