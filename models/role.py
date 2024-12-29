#!/usr/bin/python3
"""
This module defines the `Role` class, representing a role for RBAC.

Attributes:
    id (int): Primary key of the role.
    name (str): Name of the role.
    description (str): Description of the role.
    users (relationship): Many-to-many relationship with `User`.
"""

from sqlalchemy import Column, Integer, String, Index
from sqlalchemy.orm import relationship
from models import Base
from models.user import user_roles

class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200))

    # Relationships
    users = relationship('User', secondary=user_roles, back_populates='roles')

    # Indexes
    __table_args__ = (
        Index('idx_role_name', name),
    )
