#!/usr/bin/python3
"""
API initialization module for the Blog Management API.

This module initializes and configures the API routes for the application,
including versioning and namespace organization.

Attributes:
    api: Flask Blueprint for the API
"""
from flask import Blueprint

api = Blueprint('api', __name__)

# Import versioned routes
from api.v1.auth.routes import auth_bp
from api.v1.users.routes import users_bp

# Register blueprints
api.register_blueprint(auth_bp, url_prefix='/v1/auth')
api.register_blueprint(users_bp, url_prefix='/v1/users')
