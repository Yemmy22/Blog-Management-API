#!/usr/bin/python3
"""
Entry point for the Blog Management API.

This module initializes the application, sets up configurations,
and registers the API routes.
"""
from flask import Flask
from db import Session, populate_roles
from api import api
from config import Config

# Initialize Flask application
app = Flask(__name__)
app.config.from_object(Config)

# Populate roles
populate_roles()

# Register API Blueprint
app.register_blueprint(api, url_prefix='/api')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
