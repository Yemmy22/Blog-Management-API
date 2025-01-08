#!/usr/bin/python3
"""
Main Flask application for the Blog Management API.

This module initializes and configures the Flask application,
registers blueprints, and sets up error handlers.
"""
from flask import Flask
from api.v1.auth import auth_bp
from config.database import engine
from models import Base

def create_app():
    """
    Create and configure Flask application.
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'your-secret-key'  # Change in production
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    @app.route('/health')
    def health_check():
        """Basic health check endpoint."""
        return {'status': 'healthy'}, 200
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
