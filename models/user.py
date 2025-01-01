#!/usr/bin/python3
"""
This module defines the User class and the user_roles association table.

The User class represents system users with authentication and authorization
capabilities. The user_roles table manages the many-to-many relationship
between users and roles.

Classes:
    User: Represents a user in the system

Tables:
    user_roles: Association table for User-Role many-to-many relationship
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Table, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from models import Base

user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

class User(Base):
    """
    User model class representing system users.
    
    This class defines the structure for user accounts, including authentication
    details and relationships with roles, posts, and comments.
    
    Attributes:
        id (Column): Primary key of the user
        username (Column): Unique username for identification
        email (Column): User's email address
        password (Column): Hashed password for authentication
        is_active (Column): Flag indicating if the account is active
        created_at (Column): Timestamp of user creation
        updated_at (Column): Timestamp of last update
        roles (relationship): Many-to-many relationship with Role model
        posts (relationship): One-to-many relationship with Post model
        comments (relationship): One-to-many relationship with Comment model
    """
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    roles = relationship('Role', secondary=user_roles, back_populates='users')
    posts = relationship('Post', back_populates='author')
    comments = relationship('Comment', back_populates='user')

    # Indexes
    __table_args__ = (
        Index('idx_username', username),
        Index('idx_email', email),
    )

