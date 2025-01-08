#!/usr/bin/python3
"""Database initialization script"""
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from models import Base
from config.database import DATABASE_URL

def init_database():
    """Initialize the database and create all tables"""
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    # Create database if it doesn't exist
    if not database_exists(engine.url):
        create_database(engine.url)
        print(f"Created database: {engine.url.database}")
    
    # Create all tables
    Base.metadata.create_all(engine)
    print("Created all database tables")

def create_initial_roles(session):
    """Create default roles"""
    from models.role import Role
    
    default_roles = [
        {'name': 'admin', 'description': 'Administrator with full access'},
        {'name': 'editor', 'description': 'Can manage all content'},
        {'name': 'author', 'description': 'Can create and manage own content'},
        {'name': 'user', 'description': 'Basic user access'}
    ]
    
    for role_data in default_roles:
        existing_role = session.query(Role).filter_by(name=role_data['name']).first()
        if not existing_role:
            role = Role(**role_data)
            session.add(role)
    
    session.commit()
    print("Created default roles")

def create_admin_user(session):
    """Create initial admin user"""
    from models.user import User
    from models.role import Role
    from utils.password import hash_password
    
    # Get admin role
    admin_role = session.query(Role).filter_by(name='admin').first()
    
    # Create admin user
    admin_pass, _ = hash_password('admin123')  # Change this password in production!
    admin_user = User(
        username='admin',
        email='admin@example.com',
        password=admin_pass,
        first_name='Admin',
        last_name='User',
        is_active=True
    )
    admin_user.roles.append(admin_role)
    
    session.add(admin_user)
    session.commit()
    print("Created admin user")

if __name__ == '__main__':
    from sqlalchemy.orm import sessionmaker
    
    # Initialize database and tables
    init_database()
    
    # Create session
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Create initial data
        create_initial_roles(session)
        create_admin_user(session)
        print("Database initialization completed successfully!")
        
    except Exception as e:
        print(f"Error during initialization: {e}")
        session.rollback()
        
    finally:
        session.close()
