#!/usr/bin/python3
"""
Password utility module for secure password handling.

This module provides functions for password hashing and verification
using bcrypt encryption.
"""
import bcrypt
from typing import Tuple

def hash_password(password: str) -> Tuple[str, str]:
    """
    Hash a password using bcrypt with salt.

    Args:
        password: Plain text password

    Returns:
        Tuple[str, str]: (hashed password, salt)
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8'), salt.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        password: Plain text password to verify
        hashed: Stored hash to check against

    Returns:
        bool: True if password matches, False otherwise
    """
    return bcrypt.checkpw(
        password.encode('utf-8'),
        hashed.encode('utf-8')
    )
