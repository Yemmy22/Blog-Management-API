#!/usr/bin/python3
"""
Token service for managing session tokens.

This module provides functions for generating, validating, and invalidating
tokens, such as those used for login sessions.

Classes:
    TokenService: Handles token operations using Redis.
"""
import uuid
from redis_connection import redis_client

class TokenService:
    """
    Provides methods to generate, validate, and invalidate session tokens.

    Methods:
        generate_session_token: Generate and store a session token.
        validate_session_token: Validate an existing session token.
        invalidate_token: Invalidate a session token.
    """

    @staticmethod
    def generate_session_token(user_id, expires_in=3600):
        """
        Generate and store a session token.

        Args:
            user_id (int): The ID of the user.
            expires_in (int): Time-to-live for the token in seconds (default: 3600).

        Returns:
            str: The generated token.
        """
        token = str(uuid.uuid4())
        key = f"session:{token}"
        redis_client.set(key, user_id, ex=expires_in)
        return token

    @staticmethod
    def validate_session_token(token):
        """
        Validate a session token.

        Args:
            token (str): The token to validate.

        Returns:
            int or None: The user ID associated with the token, or None if invalid.
        """
        key = f"session:{token}"
        user_id = redis_client.get(key)
        return user_id

    @staticmethod
    def invalidate_token(token):
        """
        Invalidate a session token.

        Args:
            token (str): The token to invalidate.
        """
        key = f"session:{token}"
        redis_client.delete(key)
