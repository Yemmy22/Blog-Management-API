#!/usr/bin/python3
"""
This module defines the Role class for role-based access control.

The Role class represents different user roles in the system, enabling
granular access control and permission management.

Classes:
    Role: Represents a user role in the system
"""
from sqlalchemy import Column, Integer, String, Index
from sqlalchemy.orm import relationship
from models import Base

class Role(Base):
    """
    Role model class representing user roles.
    
    This class defines the structure for user roles in the system,
    enabling role-based access control (RBAC).
    
    Attributes:
        id (Column): Primary key of the role
        name (Column): Unique name of the role (e.g., 'admin', 'writer')
        description (Column): Detailed description of the role's purpose
        users (relationship): Many-to-many relationship with User model
    """
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200))
    
    # Relationships
    users = relationship('User', secondary='user_roles', back_populates='roles')
    
    # Indexes
    __table_args__ = (
        Index('idx_role_name', name),
    )
