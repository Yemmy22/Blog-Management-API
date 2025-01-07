#!/usr/bin/python3
"""
Token service for managing password reset tokens.

This module provides functions for generating, storing, and validating
temporary tokens, such as those used for password resets.

Classes:
    TokenService: Handles token operations using Redis.
"""
import uuid
from redis_connection import redis_client

class TokenService:
    """
    Provides methods to generate and validate password reset tokens.

    Methods:
        generate_reset_token: Generate and store a reset token.
        validate_reset_token: Validate and delete a reset token.
    """

    @staticmethod
    def generate_reset_token(user_id, expires_in=3600):
        """
        Generate and store a password reset token.

        Args:
            user_id (int): The ID of the user.
            expires_in (int): Time-to-live for the token in seconds (default: 3600).

        Returns:
            str: The generated token.
        """
        token = str(uuid.uuid4())
        key = f"password_reset:{token}"
        redis_client.set(key, user_id, ex=expires_in)
        return token

    @staticmethod
    def validate_reset_token(token):
        """
        Validate and delete a password reset token.

        Args:
            token (str): The token to validate.

        Returns:
            int or None: The user ID associated with the token, or None if invalid.
        """
        key = f"password_reset:{token}"
        user_id = redis_client.get(key)
        if user_id:
            redis_client.delete(key)  # Ensure the token is single-use
        return user_id
