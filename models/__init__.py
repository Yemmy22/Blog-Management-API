#!/usr/bin/python3
"""
This module initializes the models package and defines the Base class.

This package contains SQLAlchemy ORM models representing the core entities
of the blog management system. It provides the foundation for database
operations and relationships between different models.

Classes:
    Base: SQLAlchemy declarative base class for all models
"""
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# Import all models
from models.role import Role
from models.user import User, user_roles
from models.category import Category
from models.tag import Tag, post_tags
from models.post import Post
from models.comment import Comment

all = [
    "Base", "User", "Role", "Post", "Category", 
    "Tag", "Comment", "user_roles", "post_tags"
]
