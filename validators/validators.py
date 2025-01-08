#!/usr/bin/python3
"""
This module provides validation functions for data integrity.

These functions validate various types of input data and ensure
they meet the required format and constraints.
"""
import re
from typing import Optional

def validate_username(username: str) -> str:
    """
    Validate username format.

    Args:
        username: Username to validate

    Returns:
        str: Validated username

    Raises:
        ValueError: If username format is invalid
    """
    if not username:
        raise ValueError("Username cannot be empty")
    
    if not 3 <= len(username) <= 30:
        raise ValueError("Username must be between 3 and 30 characters")
    
    # Allow letters, numbers, underscore, hyphen
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        raise ValueError("Username can only contain letters, numbers, underscore, and hyphen")
    
    return username

def validate_email(email: str) -> str:
    """
    Validate email format.

    Args:
        email: Email address to validate

    Returns:
        str: Validated email address

    Raises:
        ValueError: If email format is invalid
    """
    if not email:
        raise ValueError("Email cannot be empty")
    
    # Basic email format validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValueError("Invalid email format")
    
    return email.lower()

def validate_slug(slug: str) -> str:
    """
    Validate and format URL slug.

    Args:
        slug: URL slug to validate

    Returns:
        str: Validated and formatted slug

    Raises:
        ValueError: If slug format is invalid
    """
    if not slug:
        raise ValueError("Slug cannot be empty")
    
    # Convert to lowercase and replace spaces with hyphens
    slug = slug.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    
    if len(slug) > 250:
        raise ValueError("Slug must be less than 250 characters")
    
    return slug

def estimate_reading_time(content: str, wpm: int = 200) -> int:
    """
    Estimate reading time for content in minutes.

    Args:
        content: Text content to analyze
        wpm: Words per minute reading speed (default: 200)

    Returns:
        int: Estimated reading time in minutes
    """
    if not content:
        return 0
        
    # Count words (split by whitespace)
    word_count = len(content.split())
    
    # Calculate reading time and round up to nearest minute
    minutes = max(1, round(word_count / wpm))
    
    return minutes
