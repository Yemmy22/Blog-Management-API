#!/usr/bin/python3
"""
This module defines the `User` class with enhanced security features.

Attributes:
    id (int): Primary key of the user.
    username (str): Unique username of the user.
    email (str): Email address of the user.
    password (str): Hashed password of the user.
    email_verified (bool): Status of email verification.
    is_active (bool): Indicates if the user account is active.
    failed_login_count (int): Count of consecutive failed login attempts.
    locked_until (datetime): Timestamp until which account is locked.
    password_changed_at (datetime): Timestamp of last password change.
    force_password_change (bool): Flag indicating if password change is required.
    last_login (datetime): Timestamp of the last successful login.
    created_at (datetime): Timestamp of user creation.
    updated_at (datetime): Timestamp of last update.
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, 
    Table, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
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

    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    failed_login_count = Column(Integer, default=0)
    locked_until = Column(DateTime)
    password_changed_at = Column(DateTime, default=datetime.utcnow)
    force_password_change = Column(Boolean, default=False)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    roles = relationship('Role', secondary=user_roles, back_populates='users')
    posts = relationship('Post', back_populates='author')
    comments = relationship('Comment', back_populates='user')
    audit_logs = relationship('AuditLog', back_populates='user')
    login_attempts = relationship('LoginAttempt', back_populates='user')

    # Indexes
    __table_args__ = (
        Index('idx_username', username),
        Index('idx_email', email),
    )

    @property
    def is_locked(self):
        """Check if the user account is currently locked."""
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False

    def increment_failed_login(self):
        """Increment failed login count and lock account if threshold reached."""
        self.failed_login_count += 1
        if self.failed_login_count >= 5:  # Configurable threshold
            self.locked_until = datetime.utcnow() + timedelta(minutes=30)
