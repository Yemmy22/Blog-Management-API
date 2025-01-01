#!/usr/bin/python3
"""
This module provides validation utilities for model fields.

The module contains validation functions and patterns for ensuring
data integrity across the application's models. It includes email,
username, and slug validation, as well as utility functions for
content analysis.

Classes:
    ValidationError: Custom exception for validation failures

Functions:
    validate_username: Validates username format
    validate_email: Validates email format
    validate_slug: Validates slug format
    estimate_reading_time: Estimates content reading duration
"""
import re
from sqlalchemy import event
from sqlalchemy.orm import validates
from datetime import datetime

class ValidationError(Exception):
    """
    Custom exception for validation errors.
    
    This exception is raised when field validation fails,
    providing specific error messages about the validation failure.
    
    Attributes:
        message: Detailed description of the validation error
    """
    pass

# Regex patterns for validation
USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_]{3,30}$')
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
SLUG_PATTERN = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')

def validate_username(username):
    """
    Validate username format.
    
    Args:
        username (str): The username to validate
        
    Returns:
        str: The validated username
        
    Raises:
        ValidationError: If username format is invalid
    """
    if not USERNAME_PATTERN.match(username):
        raise ValidationError(
            "Username must be 3-30 characters long and contain only "
            "letters, numbers, and underscores"
        )
    return username

def validate_email(email):
    """
    Validate email format.
    
    Args:
        email (str): The email address to validate
        
    Returns:
        str: The validated email address
        
    Raises:
        ValidationError: If email format is invalid
    """
    if not EMAIL_PATTERN.match(email):
        raise ValidationError("Invalid email format")
    return email

def validate_slug(slug):
    """
    Validate slug format.
    
    Args:
        slug (str): The slug to validate
        
    Returns:
        str: The validated slug
        
    Raises:
        ValidationError: If slug format is invalid
    """
    if not SLUG_PATTERN.match(slug):
        raise ValidationError(
            "Slug must contain only lowercase letters, numbers, and hyphens"
        )
    return slug

def estimate_reading_time(content):
    """
    Estimate reading time in minutes based on content length.
    
    Args:
        content (str): The text content to analyze
        
    Returns:
        int: Estimated reading time in minutes (minimum 1)
    """
    words = len(content.split())
    minutes = round(words / 200)  # Assuming 200 words per minute
    return max(1, minutes)

