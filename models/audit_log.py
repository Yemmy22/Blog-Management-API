#!/usr/bin/python3
"""
This module defines the AuditLog class for activity tracking.

The AuditLog class maintains a comprehensive record of system activities,
enabling accountability and compliance monitoring.

Classes:
    AuditActionType: Enum defining possible audit action types
    AuditLog: Represents a system activity log entry
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import json
from models import Base

class AuditActionType(enum.Enum):
    """
    Enum defining possible audit action types.

    Attributes:
        CREATE: Record creation action
        UPDATE: Record modification action
        DELETE: Record deletion action
        LOGIN: User login action
        LOGOUT: User logout action
    """
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"

class AuditLog(Base):
    """
    AuditLog model class for tracking system activities.

    This class maintains detailed records of user actions and system events,
    supporting accountability and compliance requirements.

    Attributes:
        id (Column): Primary key of the audit log entry
        user_id (Column): Foreign key to the user who performed the action
        action (Column): Type of action performed (from AuditActionType)
        entity_type (Column): Type of entity affected (e.g., 'User', 'Post')
        entity_id (Column): ID of the affected entity
        changes (Column): JSON string containing changed data
        ip_address (Column): IP address where action originated
        user_agent (Column): User agent string from request
        created_at (Column): Timestamp of log creation
        user (relationship): Many-to-one relationship with User model
    """
    __tablename__ = 'audit_logs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    action = Column(Enum(AuditActionType), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer)
    changes = Column(Text)
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship('User')

    # Indexes
    __table_args__ = (
        Index('idx_user_action', user_id, action),
        Index('idx_entity', entity_type, entity_id),
        Index('idx_created_at', created_at),
    )

    @staticmethod
    def log_action(session, user_id, action, entity_type, entity_id, changes,
                   ip_address=None, user_agent=None):
        """
        Create and save an audit log entry.

        Args:
            session: SQLAlchemy session
            user_id: ID of user performing action
            action: AuditActionType enum value
            entity_type: Type of entity affected
            entity_id: ID of affected entity
            changes: Dict of changes to be JSON serialized
            ip_address: Origin IP address
            user_agent: Browser/client user agent string
        """
        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            changes=json.dumps(changes) if changes else None,
            ip_address=ip_address,
            user_agent=user_agent
        )
        session.add(log_entry)
        session.commit()
