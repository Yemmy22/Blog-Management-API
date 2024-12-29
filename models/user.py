#!/usr/bin/python3
"""
This module defines the `User` class, representing a user in the blog system.

Attributes:
    id (int): Primary key of the user.
    username (str): Unique username of the user.
    email (str): Email address of the user.
    password (str): Hashed password of the user.
    email_verified (bool): Status of email verification.
    is_active (bool): Indicates if the user account is active.
    last_login (datetime): Timestamp of the last login.
    roles (relationship): Many-to-many relationship with `Role`.
    posts (relationship): One-to-many relationship with `Post`.
    comments (relationship): One-to-many relationship with `Comment`.
    audit_logs (relationship): One-to-many relationship with `AuditLog`.
    login_attempts (relationship): One-to-many relationship with `LoginAttempt`.
    sessions (relationship): One-to-many relationship with `UserSession`.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Table, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from models import Base

# Association Table for User and Role
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_login = Column(DateTime, default=None)

    # Relationships
    roles = relationship('Role', secondary=user_roles, back_populates='users')
    posts = relationship('Post', back_populates='author')
    comments = relationship('Comment', back_populates='user')
    audit_logs = relationship('AuditLog', back_populates='user')
    login_attempts = relationship('LoginAttempt', back_populates='user')
    sessions = relationship('UserSession', back_populates='user')

    # Indexes
    __table_args__ = (
        Index('idx_username', 'username'),
        Index('idx_email', 'email'),
    )

