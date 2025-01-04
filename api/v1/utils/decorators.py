#!/usr/bin/python3
"""
Utility decorators for authentication endpoints.

This module provides decorator functions for routes, including
request validation, authentication checks, and error handling.

Functions:
    require_auth: Decorator to verify authentication token
    validate_request: Decorator to validate request data
"""

from functools import wraps
from flask import request, g
from typing import Callable
from ..auth.service import AuthService
from .responses import error_response

auth_service = AuthService()

def require_auth(f: Callable) -> Callable:
    """
    Decorator to verify authentication token in request.

    Args:
        f: Route function to decorate

    Returns:
        Decorated function with authentication check
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or ' ' not in auth_header:
            return error_response("No authentication token provided", 401)

        try:
            # Add token verification
            token = auth_header.split(' ')[1]
            if not auth_service.validate_token(token):
                return error_response("Invalid authentication token", 401)
            # Verify token and set user in g
            return f(*args, **kwargs)
        except Exception as e:
            return error_response("Invalid authentication token", 401)

    return decorated


def validate_request(schema: dict) -> Callable:
    """
    Decorator to validate request data against a schema.

    Args:
        schema: Dictionary defining required request fields

    Returns:
        Decorated function with request validation
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            if not request.is_json:
                return error_response("Request must be JSON", 400)

            errors = {}
            data = request.get_json()

            for field, rules in schema.items():
                if rules.get('required', False) and field not in data:
                    errors[field] = "This field is required"

            if errors:
                return error_response("Validation failed", 400, errors)

            return f(*args, **kwargs)
        return decorated
    return decorator

def require_admin(f: Callable) -> Callable:
    """
    Decorator to verify the user has admin role.
    Must be used after @require_auth decorator.

    Args:
        f: Route function to decorate

    Returns:
        Decorated function with admin check
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not g.current_user:
            return error_response("Authentication required", 401)

        # Check if user has admin role
        if not g.current_user or not any(role.name == 'admin' for role in g.current_user.roles):
            return error_response("Admin access required", 403)

        return f(*args, **kwargs)
    return decorated
