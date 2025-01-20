#!/usr/bin/python3
"""
Rate Limiting Decorator for Flask Endpoints.

This module provides a decorator for rate-limiting Flask routes
using the RedisClient for managing rate limits.
"""
from flask import request, jsonify
from functools import wraps
from utils.redis_client import RedisClient

redis_client = RedisClient()

def rate_limit(limit: int, period: int = 60):
    """
    Decorator to apply rate limiting to a Flask route.

    Args:
        limit (int): Maximum number of requests allowed.
        period (int): Time period in seconds.

    Returns:
        Callable: Decorated Flask route.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Use the client's IP address as the rate limit key
            client_ip = request.remote_addr
            key = f"rate_limit:{client_ip}:{request.endpoint}"
            
            # Check rate limit
            if not redis_client.rate_limit(key, limit, period):
                return jsonify({"error": "Too many requests"}), 429
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

