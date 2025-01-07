#!/usr/bin/python3
"""
Authentication service for the Blog Management API.

This module provides the business logic for user authentication,
including login, registration, and token generation.

Classes:
    AuthService: Handles authentication-related operations.
"""
from werkzeug.security import generate_password_hash, check_password_hash
from app import Session
from models import User
from services.token_service import TokenService

class AuthService:
    """
    Service class for authentication-related operations.

    Methods:
        login: Authenticate a user and return a token.
        register: Register a new user in the system.
    """

    @staticmethod
    def register(email, username, password):
        session = Session()
        if session.query(User).filter_by(email=email).first():
            raise ValueError("Email is already in use.")
        if session.query(User).filter_by(username=username).first():
            raise ValueError("Username is already in use.")

        hashed_password = generate_password_hash(password)
        new_user = User(email=email, username=username, password=hashed_password)

        # Assign default role (e.g., 'reader')
        default_role = session.query(Role).filter_by(name='reader').first()
        if default_role:
            new_user.roles.append(default_role)

        session.add(new_user)
        session.commit()

    @staticmethod
    def login(email, password):
        """
        Authenticate a user and return a token.

        Args:
            email (str): The user's email address.
            password (str): The user's password.

        Returns:
            str: A JWT token for the authenticated user.

        Raises:
            ValueError: If authentication fails.
        """
        session = Session()
        user = session.query(User).filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            raise ValueError("Invalid email or password.")

        token = TokenService.generate_reset_token(user.id)
        return token

    @staticmethod
    def register(email, username, password):
        """
        Register a new user in the system.

        Args:
            email (str): The user's email address.
            username (str): The user's username.
            password (str): The user's password.

        Raises:
            ValueError: If the email or username is already in use.
        """
        session = Session()

        if session.query(User).filter_by(email=email).first():
            raise ValueError("Email is already in use.")

        if session.query(User).filter_by(username=username).first():
            raise ValueError("Username is already in use.")

        hashed_password = generate_password_hash(password)
        new_user = User(email=email, username=username, password=hashed_password)

        # Assign default role (e.g., 'reader')
        default_role = session.query(Role).filter_by(name='reader').first()
        if default_role:
            new_user.roles.append(default_role)

        session.add(new_user)
        session.commit()
