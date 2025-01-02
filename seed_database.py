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

It ensures proper relationships between all entities and checks for
existing data to avoid duplication when re-running the script.

Functions:
    hash_password: Hash a password using bcrypt
    seed_database: Seed the database with initial data
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
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        str: Hashed password
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def seed_database():
    """
    Seed the database with initial data.
    Creates roles, users, categories, tags, and sample content.
    Checks for existing data to avoid duplication.
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
        
        # Create roles if they don't exist
        print("Creating roles...")
        admin_role = session.query(Role).filter_by(name="Admin").first()
        if not admin_role:
            admin_role = Role(
                name="Admin",
                description="Full system access"
            )
            session.add(admin_role)
            
        editor_role = session.query(Role).filter_by(name="Editor").first()
        if not editor_role:
            editor_role = Role(
                name="Editor",
                description="Can manage content"
            )
            session.add(editor_role)
            
        session.flush()
        
        # Create test users if they don't exist
        print("Creating test users...")
        admin_user = session.query(User).filter_by(email="admin@example.com").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@example.com",
                password=hash_password("admin123"),
                first_name="Admin",
                last_name="User",
                is_active=True,
                roles=[admin_role]
            )
            session.add(admin_user)
            
        editor_user = session.query(User).filter_by(email="editor@example.com").first()
        if not editor_user:
            editor_user = User(
                username="editor",
                email="editor@example.com",
                password=hash_password("editor123"),
                first_name="Editor",
                last_name="User",
                is_active=True,
                roles=[editor_role]
            )
            session.add(editor_user)
            
        session.flush()
        
        # Create categories if they don't exist
        print("Creating categories...")
        category_names = ["Technology", "Travel", "Lifestyle"]
        categories = []
        for name in category_names:
            category = session.query(Category).filter_by(name=name).first()
            if not category:
                category = Category(name=name)
                session.add(category)
            categories.append(category)
            
        session.flush()
        
        # Create tags if they don't exist
        print("Creating tags...")
        tag_data = [
            {"name": "python", "slug": "python"},
            {"name": "web development", "slug": "web-development"},
            {"name": "tutorial", "slug": "tutorial"}
        ]
        tags = []
        for tag_info in tag_data:
            tag = session.query(Tag).filter_by(slug=tag_info["slug"]).first()
            if not tag:
                tag = Tag(**tag_info)
                session.add(tag)
            tags.append(tag)
            
        session.flush()
        
        # Create sample post if it doesn't exist
        print("Creating sample post...")
        sample_post = session.query(Post).filter_by(
            slug="getting-started-with-python"
        ).first()
        if not sample_post:
            sample_post = Post(
                title="Getting Started with Python",
                slug="getting-started-with-python",
                content="""# Getting Started with Python

Python is a versatile programming language that's perfect for beginners.
This guide will help you start your Python journey.

## Why Python?
- Easy to learn
- Readable syntax
- Large community
- Extensive libraries

## Basic Python Example
```python
def greet(name):
    return f"Hello, {name}!"

print(greet("World"))
```

Stay tuned for more Python tutorials!
""",
                status=PostStatus.PUBLISHED,
                meta_description="Learn the basics of Python programming in this beginner-friendly guide",
                reading_time=5,
                user_id=admin_user.id,
                category_id=categories[0].id,  # Technology category
                tags=tags[:2],  # Python and Web Development tags
                published_at=datetime.utcnow(),
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
                content="Great introduction to Python! Looking forward to more tutorials.",
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
