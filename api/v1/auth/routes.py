#!/usr/bin/python3
"""
Authentication routes for the Blog Management API.

This module defines the routes for authentication, including
user login, registration, and logout.
"""
from flask import Blueprint, request, jsonify
from api.v1.auth.service import AuthService
from services.token_service import TokenService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Handle user login."""
    data = request.json
    email = data.get('email')
    password = data.get('password')
    try:
        token = AuthService.login(email, password)
        return jsonify({"token": token}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@auth_bp.route('/register', methods=['POST'])
def register():
    """Handle user registration."""
    data = request.json
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    try:
        AuthService.register(email, username, password)
        return jsonify({"message": "User registered successfully"}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Handle user logout."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Token required"}), 401

    token = auth_header.split(" ")[1]
    TokenService.invalidate_token(token)
    return jsonify({"message": "Logged out successfully"}), 200
