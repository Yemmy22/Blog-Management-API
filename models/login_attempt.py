#!/usr/bin/python3
"""
This module defines the `LoginAttempt` class, representing a user login attempt.

Attributes:
    id (int): Primary key of the login attempt.
    user_id (int): Foreign key referencing the user.
    success (bool): Indicates if the login attempt was successful.
    timestamp (datetime): Timestamp of the login attempt.
    ip_address (str): IP address of the user during the attempt.
"""

from sqlalchemy import Column, Integer, Boolean, DateTime, String, ForeignKey, Index
from datetime import datetime
from models import Base

class LoginAttempt(Base):
    __tablename__ = 'login_attempts'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    success = Column(Boolean, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45))

    # Relationships
    user = relationship('User', back_populates='login_attempts')

    # Indexes
    __table_args__ = (
        Index('idx_user_id', user_id),
        Index('idx_timestamp', timestamp),
    )
