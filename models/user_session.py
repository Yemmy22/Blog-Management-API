#!/usr/bin/python3
"""
UserSession model for session management.

This module defines the `UserSession` class, representing active user sessions.

Classes:
    UserSession: Tracks user sessions, including session tokens and expiration.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from models import Base

class UserSession(Base):
    """
    UserSession model class for tracking active sessions.

    Attributes:
        id (int): Unique identifier for the session.
        user_id (int): Foreign key referencing the user.
        session_token (str): Session token for authentication.
        expires_at (datetime): Expiry timestamp of the session.
        created_at (datetime): Timestamp of when the session was created.
    """
    __tablename__ = 'user_sessions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_agent = Column(String(255))
    ip_address = Column(String(45))
    # Relationships
    user = relationship('User', back_populates='sessions')
