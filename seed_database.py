#!/usr/bin/python3
"""
Seed initial data into the database.

This script creates initial data in the database including:
- User roles (Admin, Editor)
- Test users
- Sample categories
- Sample tags
- Sample blog post
- Sample comment

It ensures proper relationships between all entities.
"""
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Base
from models.role import Role
from models.user import User
from models.category import Category
from models.tag import Tag
from models.post import Post, PostStatus
from models.comment import Comment
from config import DB_URI
from datetime import datetime
import bcrypt

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def seed_database():
    """
    Seed the database with initial data.
    Creates roles, users, categories, tags, and sample content.
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
        print("Creating roles...")
        admin_role = Role(
            name="Admin",
            description="Full system access"
        )
        editor_role = Role(
            name="Editor",
            description="Can manage content"
        )
        
        session.add_all([admin_role, editor_role])
        session.flush()
        
        # Create test users
        print("Creating test users...")
        admin_user = User(
            username="admin",
            email="admin@example.com",
            password=hash_password("admin123"),
            roles=[admin_role]
        )
        
        editor_user = User(
            username="editor",
            email="editor@example.com",
            password=hash_password("editor123"),
            roles=[editor_role]
        )
        
        session.add_all([admin_user, editor_user])
        session.flush()
        
        # Create categories
        print("Creating categories...")
        categories = [
            Category(name="Technology"),
            Category(name="Travel"),
            Category(name="Lifestyle")
        ]
        session.add_all(categories)
        session.flush()
        
        # Create tags
        print("Creating tags...")
        tags = [
            Tag(name="python", slug="python"),
            Tag(name="web development", slug="web-development"),
            Tag(name="tutorial", slug="tutorial")
        ]
        session.add_all(tags)
        session.flush()
        
        # Create sample post
        print("Creating sample post...")
        sample_post = Post(
            title="Getting Started with Python",
            slug="getting-started-with-python",
            content="This is a sample blog post about Python programming...",
            status=PostStatus.PUBLISHED,
            user_id=admin_user.id,
            category_id=categories[0].id,  # Technology category
            tags=tags[:2],  # Python and Web Development tags
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(sample_post)
        session.flush()
        
        # Create sample comment
        print("Creating sample comment...")
        sample_comment = Comment(
            post_id=sample_post.id,
            user_id=editor_user.id,
            content="Great introduction to Python!",
            is_approved=True,
            created_at=datetime.utcnow()
        )
        session.add(sample_comment)
        
        # Commit all changes
        session.commit()
        print("Database seeded successfully!")
        
    except Exception as e:
        print(f"An error occurred while seeding the database: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    seed_database()
