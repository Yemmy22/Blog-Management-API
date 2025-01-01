#!/usr/bin/python3
"""
This module initializes the Base class for SQLAlchemy ORM.
Attributes:
    Base (declarative_base): Base class for all models.
"""
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
# Import models
from models.role import Role
from models.user import User, user_roles
from models.category import Category
from models.tag import Tag
from models.post import Post
from models.post_tags import post_tags
from models.comment import Comment
from models.post_revision import PostRevision
from models.post_like import PostLike
from models.post_view import PostView
from models.audit_log import AuditLog
from models.login_attempt import LoginAttempt
from models.user_session import UserSession
all = [
    "Base", "User", "Role", "Post", "PostRevision", "PostLike", "PostView",
    "Category", "Tag", "post_tags", "Comment", "AuditLog", "LoginAttempt",
    "UserSession", "user_roles"
]
