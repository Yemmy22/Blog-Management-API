#!/usr/bin/python3
"""
RBAC decorators for the Blog Management API.

This module provides decorators to enforce role-based access control (RBAC)
for API endpoints.

Functions:
    require_role: Restrict access to endpoints based on roles.
"""
from flask import request, jsonify
from functools import wraps
from services.token_service import TokenService
from db import Session
from models import User

def require_role(required_roles):
    """
    Decorator to restrict access to specific roles.

    Args:
        required_roles (list): List of roles allowed to access the endpoint.

    Returns:
        function: Decorated function enforcing role-based access control.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return jsonify({"error": "Authentication required"}), 401

            token = auth_header.split(" ")[1]
            user_id = TokenService.validate_session_token(token)
            if not user_id:
                return jsonify({"error": "Invalid or expired token"}), 401

            session = Session()
            user = session.query(User).get(user_id)
            if not user:
                return jsonify({"error": "User not found"}), 404

            user_roles = [role.name for role in user.roles]
            if not any(role in user_roles for role in required_roles):
                return jsonify({"error": "Access denied"}), 403

            return func(*args, **kwargs)
        return wrapper
    return decorator
