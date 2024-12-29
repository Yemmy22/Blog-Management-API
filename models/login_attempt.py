#!/usr/bin/python3
"""
This module defines the `LoginAttempt` class for tracking user login attempts.

Attributes:
    id (int): Primary key of the login attempt.
    user_id (int): Foreign key referencing the user.
    success (bool): Indicates if the login attempt was successful.
    ip_address (str): IP address from which the attempt was made.
    timestamp (datetime): Timestamp of when the attempt occurred.
"""

from sqlalchemy import Column, Integer, Boolean, DateTime, String, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from models import Base

class LoginAttempt(Base):
    __tablename__ = 'login_attempts'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    success = Column(Boolean, nullable=False)
    ip_address = Column(String(45))
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship('User', back_populates='login_attempts')

    # Indexes
    __table_args__ = (
        Index('idx_user_id', user_id),
        Index('idx_timestamp', timestamp),
    )
