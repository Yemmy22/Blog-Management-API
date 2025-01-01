#!/usr/bin/python3
"""
This module defines the `UserSession` class, representing an active user session.

Attributes:
    id (int): Primary key of the session.
    user_id (int): Foreign key referencing the user.
    token (str): Unique token for the session.
    created_at (datetime): Timestamp of session creation.
    expires_at (datetime): Expiration timestamp of the session.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from models import Base

class UserSession(Base):
    __tablename__ = 'user_sessions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)

    # Relationships
    user = relationship('User', back_populates='sessions')

    # Indexes
    __table_args__ = (
        Index('idx_user_id', user_id),
        Index('idx_token', token),
    )
