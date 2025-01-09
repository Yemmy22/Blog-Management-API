#!/usr/bin/python3
"""
Main Flask application for the Blog Management API.

This module initializes and configures the Flask application,
registers blueprints, and sets up error handlers.
"""
from flask import Flask, jsonify
from api.v1.auth import auth_bp
from api.v1.posts import posts_bp
from api.v1.categories import categories_bp
from config.database import engine
from models import Base
from utils.redis_client import RedisClient

def create_app():
    """
    Create and configure Flask application.
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'your-secret-key'  # Change in production
    
    # Initialize Redis client
    redis_client = RedisClient()
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(posts_bp, url_prefix='/api/v1/posts')
    app.register_blueprint(categories_bp, url_prefix='/api/v1/categories')
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/health')
    def health_check():
        """Basic health check endpoint."""
        return {'status': 'healthy'}, 200
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
