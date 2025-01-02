#!/usr/bin/python3
"""
This module defines the User class and the user_roles association table.

The User class represents system users with extended profile information,
authentication capabilities, and security features.

Classes:
    User: Represents a user in the system with profile features
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
    """Enhanced User model class with additional profile features."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(30), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    
    # Profile fields
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

    def to_dict(self):
        """
        Convert User object to dictionary.
        
        Returns:
            dict: User data dictionary (excluding sensitive information)
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'bio': self.bio,
            'avatar_url': self.avatar_url,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'roles': [role.name for role in self.roles]
        }

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
