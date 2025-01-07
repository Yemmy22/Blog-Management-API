#!/usr/bin/python3
"""
Database utilities for the Blog Management API.

This module provides:
- Functions to populate roles.
- Session initialization for database interactions.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from config import Config
from models import Role, User, Base

# Initialize the database engine and session
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Base.metadata.bind = engine
Session = scoped_session(sessionmaker(bind=engine))

def populate_roles():
    """
    Populate predefined roles in the database.

    Roles:
        - admin
        - writer
        - reader
    """
    session = Session()
    roles = ['admin', 'writer', 'reader']
    for role_name in roles:
        if not session.query(Role).filter_by(name=role_name).first():
            session.add(Role(name=role_name))
    session.commit()

def assign_role_to_user(username, role_name):
    """
    Assign a specific role to a user.

    Args:
        username (str): The username of the user.
        role_name (str): The name of the role to assign.

    Raises:
        ValueError: If the user or role does not exist.
    """
    session = Session()
    user = session.query(User).filter_by(username=username).first()
    role = session.query(Role).filter_by(name=role_name).first()

    if not user:
        raise ValueError(f"User '{username}' does not exist.")
    if not role:
        raise ValueError(f"Role '{role_name}' does not exist.")

    if role not in user.roles:
        user.roles.append(role)
        session.commit()

