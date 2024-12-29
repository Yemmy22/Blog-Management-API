#!/usr/bin/python3
"""
This module defines the `AuditLog` class, representing an audit log entry.

Attributes:
    id (int): Primary key of the audit log.
    user_id (int): Foreign key referencing the user.
    action (str): Action performed by the user.
    timestamp (datetime): Timestamp of the action.
    details (str): Additional details about the action.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from models import Base

class AuditLog(Base):
    __tablename__ = 'audit_logs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    action = Column(String(100), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(Text)

    # Relationships
    user = relationship('User', back_populates='audit_logs')

    # Indexes
    __table_args__ = (
        Index('idx_user_id', user_id),
        Index('idx_timestamp', timestamp),
    )
