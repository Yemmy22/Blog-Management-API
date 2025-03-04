#!/usr/bin/python3
"""
This module initializes the models package and defines the Base class.

This package contains SQLAlchemy ORM models representing the core entities
of the blog management system. It provides the foundation for database
operations and relationships between different models.

Attributes:
    Base: SQLAlchemy declarative base class for all models
"""
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# Import all models
from models.role import Role
from models.user_session import UserSession
from models.user import User, user_roles
from models.category import Category
from models.tag import Tag, post_tags
from models.post_revision import PostRevision
from models.post import Post, PostStatus
from models.comment import Comment

__all__ = [
    "Base", "User", "Role", "Post", "Category", 
    "Tag", "Comment", "user_roles", "post_tags",
    "UserSession"
]
