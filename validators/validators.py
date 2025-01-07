#!/usr/bin/python3
"""
Validation utilities for the Blog Management API.

This module contains reusable validation functions for fields such as email,
username, and slugs, as well as utilities for estimating reading time.

Functions:
    validate_email: Validate an email address.
    validate_username: Validate a username.
    validate_slug: Validate a URL-friendly slug.
    estimate_reading_time: Estimate reading time for text content.
"""
import re

def validate_email(email):
    """Validate an email address."""
    pattern = r'^[\w.%+-]+@[\w.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValueError("Invalid email address")
    return email

def validate_username(username):
    """Validate a username."""
    if len(username) < 3 or len(username) > 30:
        raise ValueError("Username must be between 3 and 30 characters")
    return username

def validate_slug(slug):
    """Validate a URL-friendly slug."""
    pattern = r'^[a-z0-9]+(?:-[a-z0-9]+)*$'
    if not re.match(pattern, slug):
        raise ValueError("Invalid slug format")
    return slug

def estimate_reading_time(content):
    """Estimate the reading time for text content."""
    words_per_minute = 200  # Average reading speed
    words = len(content.split())
    return max(1, words // words_per_minute)
