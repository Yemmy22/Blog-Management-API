#!/usr/bin/python3
"""
Configuration settings for the Blog Management API.

This module defines the configuration for the application, including
database connections, Redis settings, and secret keys.

Classes:
    Config: Centralized configuration class
"""
import os

class Config:
    """
    Configuration class for application settings.

    Attributes:
        SECRET_KEY (str): Secret key for session management and JWT.
        SQLALCHEMY_DATABASE_URI (str): Database connection URI.
        REDIS_HOST (str): Redis host address.
        REDIS_PORT (int): Redis port.
    """
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///blog.db')
    REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
