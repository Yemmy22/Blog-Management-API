#!/usr/bin/python3
"""
This module initializes the Base class for SQLAlchemy ORM.
Attributes:
    Base (declarative_base): Base class for all models.
"""
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# Import models
from models.user import User, user_roles  # Import user_roles from user.py
from models.role import Role
from models.post import Post
from models.post_revision import PostRevision
from models.post_like import PostLike
from models.post_view import PostView
from models.category import Category
from models.tag import Tag, post_tags  # Import post_tags from tag.py
from models.comment import Comment
from models.audit_log import AuditLog
from models.login_attempt import LoginAttempt
from models.user_session import UserSession

__all__ = [
    "Base", "User", "Role", "Post", "PostRevision", "PostLike", "PostView",
    "Category", "Tag", "post_tags", "Comment", "AuditLog", "LoginAttempt",
    "UserSession", "user_roles"
]
