#!/usr/bin/python3
"""Initial database setup script."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from models.role import Role
from config import DB_URI
import bcrypt

def setup_database():
    """Set up initial database state."""
    # Create engine
    engine = create_engine(DB_URI, pool_pre_ping=True)
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Create default roles if they don't exist
    default_roles = ['admin', 'user', 'moderator']
    
    for role_name in default_roles:
        if not session.query(Role).filter_by(name=role_name).first():
            role = Role(
                name=role_name,
                description=f"Default {role_name} role"
            )
            session.add(role)
    
    # Create admin user if it doesn't exist
    from models.user import User
    admin_email = "admin@example.com"
    
    if not session.query(User).filter_by(email=admin_email).first():
        # Create admin user
        hashed = bcrypt.hashpw("Admin123!".encode('utf-8'), bcrypt.gensalt())
        admin = User(
            username="admin",
            email=admin_email,
            password=hashed,
            is_active=True
        )
        
        # Assign admin role
        admin_role = session.query(Role).filter_by(name='admin').first()
        if admin_role:
            admin.roles.append(admin_role)
            
        session.add(admin)
    
    try:
        session.commit()
        print("Database setup completed successfully!")
    except Exception as e:
        session.rollback()
        print(f"Error during setup: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    setup_database()
