#!/usr/bin/python3
"""
Seed initial data into the database.

This script creates initial roles and users in the database.
It handles the creation of admin and editor roles,
and a test user with admin privileges.
"""

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Base
from models.role import Role
from models.user import User
from config import DB_URI

def seed_database():
    """
    Seed the database with initial data.
    Creates roles and users with proper relationships.
    """
    # Connect to the database
    engine = create_engine(DB_URI, pool_pre_ping=True)
    Session = sessionmaker(bind=engine)
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Start session
    session = Session()
    
    try:
        print("Starting database seeding...")
        
        # Create roles
        print("Creating admin role...")
        admin_role = Role(
            name="Admin",
            description="Administrator role"
        )
        
        print("Creating editor role...")
        editor_role = Role(
            name="Editor",
            description="Editor role"
        )
        
        # Add roles to session
        session.add(admin_role)
        session.add(editor_role)
        
        # Flush to get role IDs
        session.flush()
        
        print("Creating test user...")
        # Create test user
        test_user = User(
            username="testuser",
            email="test@example.com",
            password="hashedpassword"  # Note: In production, use proper password hashing
        )
        
        # Add role to user
        test_user.roles = [admin_role]
        
        # Add user to session
        session.add(test_user)
        
        # Commit all changes
        session.commit()
        print("Database seeded successfully!")
        
    except Exception as e:
        print(f"An error occurred while seeding the database: {str(e)}")
        print("Full error traceback:")
        import traceback
        print(traceback.format_exc())
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    seed_database()
