#!/usr/bin/python3
"""
This module defines the User class and the user_roles association table.

The User class represents system users with extended profile information,
authentication capabilities, and security features.

Classes:
    User: Represents a user in the system with profile features

Tables:
    user_roles: Association table for User-Role many-to-many relationship
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Table, ForeignKey, Index
from sqlalchemy.orm import relationship, validates
from datetime import datetime
from models import Base
from .validators import validate_username, validate_email

user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

class User(Base):
    """
    Enhanced User model class with additional profile features.
    
    This class extends the basic User model with additional fields for
    profile information, authentication, and security features.
    
    Attributes:
        id (Column): Primary key of the user
        username (Column): Unique username for identification
        email (Column): User's email address
        password (Column): Hashed password for authentication
        first_name (Column): User's first name
        last_name (Column): User's last name
        bio (Column): User's biography or description
        avatar_url (Column): URL to user's profile picture
        is_active (Column): Flag indicating if the account is active
        last_login (Column): Timestamp of last login
        password_reset_token (Column): Token for password reset
        password_reset_expires (Column): Expiration of reset token
        created_at (Column): Timestamp of user creation
        updated_at (Column): Timestamp of last update
    """
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(30), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    
    # New profile fields
    first_name = Column(String(50))
    last_name = Column(String(50))
    bio = Column(Text)
    avatar_url = Column(String(255))
    
    # Authentication and security
    is_active = Column(Boolean, default=True, nullable=False)
    last_login = Column(DateTime)
    password_reset_token = Column(String(100), unique=True)
    password_reset_expires = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    roles = relationship('Role', secondary='user_roles', back_populates='users')
    posts = relationship('Post', back_populates='author')
    comments = relationship('Comment', back_populates='user')

    # Validators
    @validates('username')
    def validate_username(self, key, username):
        return validate_username(username)
    
    @validates('email')
    def validate_email(self, key, email):
        return validate_email(email)
    
    # Indexes
    __table_args__ = (
        Index('idx_username', 'username'),
        Index('idx_email', 'email'),
        Index('idx_reset_token', 'password_reset_token'),
    )

