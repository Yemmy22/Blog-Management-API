#!/usr/bin/python3
"""
Entry point for the Flask application.

This module initializes the Flask application, configures the database,
and registers all blueprints and routes.
"""
from flask import Flask
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from models import Base
from config import DB_URI
from api.v1.auth.routes import auth_bp

def create_app():
    """
    Create and configure the Flask application.
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Enable CORS
    CORS(app)
    
    # Configure app
    app.config['SECRET_KEY'] = 'your-secret-key'  # Change this in production!
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    
    return app

def init_db():
    """Initialize the database and create all tables."""
    try:
        engine = create_engine(DB_URI, pool_pre_ping=True)
        Base.metadata.create_all(engine)
        
        # Create a default admin user and roles if they don't exist
        Session = sessionmaker(bind=engine)
        session = Session()
        
        from models.role import Role
        from models.user import User
        import bcrypt
        
        # Create default roles if they don't exist
        default_roles = ['admin', 'user']
        for role_name in default_roles:
            if not session.query(Role).filter_by(name=role_name).first():
                role = Role(name=role_name)
                session.add(role)
        
        # Create admin user if it doesn't exist
        admin_email = 'admin@example.com'
        if not session.query(User).filter_by(email=admin_email).first():
            hashed = bcrypt.hashpw('Admin123!'.encode('utf-8'), bcrypt.gensalt())
            admin = User(
                email=admin_email,
                username='admin',
                password=hashed
            )
            admin_role = session.query(Role).filter_by(name='admin').first()
            admin.roles.append(admin_role)
            session.add(admin)
        
        session.commit()
        print("Database and tables created successfully!")
        
    except SQLAlchemyError as e:
        print(f"An error occurred: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    app = create_app()
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
