#!/usr/bin/python3
"""
User model for the Blog Management API.

Defines the `User` class, representing system users with profile
information, authentication capabilities, and security features.

Classes:
    User: Represents a user in the system.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Table, ForeignKey, Index
from sqlalchemy.orm import relationship, validates
from datetime import datetime
from models import Base
from validators.validators import validate_username, validate_email

user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

class User(Base):
    """
    Represents a user in the system.

    Attributes:
        id (int): Unique identifier for the user.
        username (str): Unique username.
        email (str): Unique email address.
        password (str): Hashed password.
        first_name (str): First name of the user.
        last_name (str): Last name of the user.
        is_active (bool): Account status.
        created_at (datetime): Timestamp of user creation.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(30), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    is_active = Column(Boolean, default=True, nullable=False)
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
    )
