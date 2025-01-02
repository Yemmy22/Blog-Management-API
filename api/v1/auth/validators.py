#!/usr/bin/python3
"""
Authentication validation module.

This module provides validation utilities for authentication-related
data including email and password validation.

Functions:
    validate_password: Check password meets minimum requirements
    validate_email: Validate email format
"""
import re
from typing import Tuple


def validate_password(password: str) -> Tuple[bool, str]:
    """
    Validate password meets minimum security requirements.
    
    Args:
        password: Password string to validate
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    
    return True, ""


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    if not pattern.match(email):
        return False, "Invalid email format"
    
    return True, ""
