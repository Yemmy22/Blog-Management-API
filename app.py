#!/usr/bin/python3
"""
Entry point for the Blog Management API.

This module initializes the application, sets up configurations,
and registers the API routes.
"""
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from models import Base
from api import api
from config import Config

# Initialize Flask application
app = Flask(__name__)
app.config.from_object(Config)

# Create engine and bind metadata
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Base.metadata.bind = engine
Base.metadata.create_all(engine)

# Initialize session
Session = scoped_session(sessionmaker(bind=engine))

# Register API Blueprint
app.register_blueprint(api, url_prefix='/api')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
