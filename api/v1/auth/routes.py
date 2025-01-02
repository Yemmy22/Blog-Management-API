#!/usr/bin/python3
"""
Authentication routes module.

This module defines the routes for authentication endpoints including
registration, login, logout and password reset functionality.

Routes:
    POST /auth/register:      Register new user
    POST /auth/login:         User login
    POST /auth/logout:        User logout  
    POST /auth/reset-password: Request password reset
    PUT  /auth/reset-password: Process password reset
"""
from flask import Blueprint, request, jsonify, g
from .service import AuthService, AuthenticationError
from .validators import validate_email, validate_password
from ..utils.responses import success_response, error_response
from ..utils.decorators import require_auth

# Initialize Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
auth_service = AuthService()

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register new user endpoint.
    
    Request Body:
        email: User's email address
        password: User's password
        username: User's username
    
    Returns:
        User data and authentication token
    """
    data = request.get_json()
    
    # Validate required fields
    if not all(k in data for k in ['email', 'password', 'username']):
        return error_response("Missing required fields", 400)
    
    # Validate input
    email_valid, email_error = validate_email(data['email'])
    if not email_valid:
        return error_response(email_error, 400)
    
    password_valid, password_error = validate_password(data['password'])
    if not password_valid:
        return error_response(password_error, 400)
    
    try:
        result = auth_service.register_user(**data)
        return success_response("Registration successful", result, 201)
    except AuthenticationError as e:
        return error_response(str(e), 400)

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User login endpoint.
    
    Request Body:
        email: User's email
        password: User's password
    
    Returns:
        User data and authentication token
    """
    data = request.get_json()
    
    if not all(k in data for k in ['email', 'password']):
        return error_response("Missing required fields", 400)
    
    try:
        result = auth_service.login_user(data['email'], data['password'])
        return success_response("Login successful", result)
    except AuthenticationError as e:
        return error_response(str(e), 401)

@auth_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    """
    User logout endpoint.
    
    Requires valid authentication token in Authorization header.
    Invalidates the provided token.
    
    Returns:
        Success message
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header or ' ' not in auth_header:
        return error_response("Invalid authorization header", 401)
    
    token = auth_header.split(' ')[1]
    
    try:
        auth_service.logout_user(token)
        return success_response("Logout successful")
    except AuthenticationError as e:
        return error_response(str(e), 400)

@auth_bp.route('/validate-token', methods=['GET'])
def validate_token():
    """
    Token validation endpoint.
    
    Validates the provided authentication token.
    
    Returns:
        Success message if token is valid
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header or ' ' not in auth_header:
        return error_response("Invalid authorization header", 401)
    
    token = auth_header.split(' ')[1]
    
    if auth_service.validate_token(token):
        return success_response("Token is valid")
    else:
        return error_response("Invalid or expired token", 401)

@auth_bp.route('/reset-password', methods=['POST'])
def request_reset():
    """
    Request password reset endpoint.
    
    Request Body:
        email: User's email
    
    Returns:
        Success message
    """
    data = request.get_json()
    
    if 'email' not in data:
        return error_response("Email is required", 400)
    
    try:
        token = auth_service.request_password_reset(data['email'])
        # In real app, send token via email
        return success_response(
            "Password reset instructions sent",
            {"token": token}  # Remove in production
        )
    except AuthenticationError as e:
        return error_response(str(e), 400)

@auth_bp.route('/reset-password', methods=['PUT'])
def reset_password():
    """
    Process password reset endpoint.
    
    Request Body:
        token: Reset token
        password: New password
    
    Returns:
        Success message
    """
    data = request.get_json()
    
    if not all(k in data for k in ['token', 'password']):
        return error_response("Missing required fields", 400)
    
    password_valid, password_error = validate_password(data['password'])
    if not password_valid:
        return error_response(password_error, 400)
    
    try:
        auth_service.reset_password(data['token'], data['password'])
        return success_response("Password reset successful")
    except AuthenticationError as e:
        return error_response(str(e), 400)
