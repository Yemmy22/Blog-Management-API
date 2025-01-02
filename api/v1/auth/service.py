#!/usr/bin/python3
"""
Authentication service module.

This module provides the AuthService class which handles all authentication
related business logic including user registration, login validation,
password management and session tracking.

Classes:
    AuthenticationError: Custom exception for authentication failures
    AuthService: Service class handling authentication operations
"""
import bcrypt
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from models.user import User
from models.role import Role
from uuid import uuid4
from db import DB


class AuthenticationError(Exception):
    """Custom exception for authentication-related errors."""
    pass


class AuthService:
    """
    Service class for handling authentication operations.

    This class encapsulates all authentication-related business logic,
    providing methods for user registration, login validation, password
    management, and session handling.

    Attributes:
        _db: Database session instance for database operations
    """

    def __init__(self):
        """Initialize the AuthService with a database session."""
        self._db = DB()

    def register_user(self, email: str, password: str, **kwargs) -> Dict[str, Any]:
        """
        Register a new user in the system.

        Args:
            email: User's email address
            password: User's password in plain text
            **kwargs: Additional user attributes (username, first_name, etc.)

        Returns:
            Dict containing user information and session token

        Raises:
            AuthenticationError: If registration fails or user already exists
            ValueError: If input validation fails
        """
        try:
            # Check if user already exists
            if self._db.session.query(User).filter_by(email=email).first():
                raise AuthenticationError("User with this email already exists")

            # Hash password
            hashed_password = bcrypt.hashpw(
                password.encode('utf-8'),
                bcrypt.gensalt()
            )

            # Create new user
            new_user = User(
                email=email,
                password=hashed_password,
                created_at=datetime.utcnow(),
                **kwargs
            )

            # Add default role
            default_role = self._db.session.query(Role).filter_by(
                name='user'
            ).first()
            if default_role:
                new_user.roles.append(default_role)

            # Save to database
            self._db.session.add(new_user)
            self._db.session.commit()

            # Generate session token
            session_token = self._generate_session_token(new_user.id)

            return {
                "user": new_user.to_dict(),
                "session_token": session_token
            }

        except SQLAlchemyError as e:
            self._db.session.rollback()
            raise AuthenticationError(f"Registration failed: {str(e)}")

    def validate_login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Validate user login credentials.

        Args:
            email: User's email address
            password: User's password in plain text

        Returns:
            Dict containing user information and session token

        Raises:
            AuthenticationError: If login validation fails
        """
        try:
            user = self._db.session.query(User).filter_by(email=email).first()
            if not user:
                raise AuthenticationError("Invalid credentials")

            # Verify password
            if not bcrypt.checkpw(
                password.encode('utf-8'),
                user.password
            ):
                raise AuthenticationError("Invalid credentials")

            # Update last login timestamp
            user.last_login = datetime.utcnow()
            self._db.session.commit()

            # Generate new session token
            session_token = self._generate_session_token(user.id)

            return {
                "user": user.to_dict(),
                "session_token": session_token
            }

        except SQLAlchemyError as e:
            self._db.session.rollback()
            raise AuthenticationError(f"Login failed: {str(e)}")

    def logout_user(self, user_id: int) -> None:
        """
        Log out a user by invalidating their session.

        Args:
            user_id: ID of the user to log out

        Raises:
            AuthenticationError: If logout operation fails
        """
        try:
            user = self._db.session.query(User).get(user_id)
            if user:
                user.password_reset_token = None
                self._db.session.commit()
        except SQLAlchemyError as e:
            self._db.session.rollback()
            raise AuthenticationError(f"Logout failed: {str(e)}")

    def generate_password_reset_token(self, email: str) -> str:
        """
        Generate a password reset token for a user.

        Args:
            email: Email of the user requesting password reset

        Returns:
            Generated reset token

        Raises:
            AuthenticationError: If user not found or token generation fails
        """
        try:
            user = self._db.session.query(User).filter_by(email=email).first()
            if not user:
                raise AuthenticationError("User not found")

            # Generate and save reset token
            reset_token = str(uuid4())
            user.password_reset_token = reset_token
            user.password_reset_expires = datetime.utcnow()
            self._db.session.commit()

            return reset_token

        except SQLAlchemyError as e:
            self._db.session.rollback()
            raise AuthenticationError(f"Token generation failed: {str(e)}")

    def reset_password(self, token: str, new_password: str) -> None:
        """
        Reset a user's password using a reset token.

        Args:
            token: Password reset token
            new_password: New password in plain text

        Raises:
            AuthenticationError: If password reset fails or token is invalid
        """
        try:
            user = self._db.session.query(User).filter_by(
                password_reset_token=token
            ).first()

            if not user:
                raise AuthenticationError("Invalid or expired reset token")

            # Hash and save new password
            hashed_password = bcrypt.hashpw(
                new_password.encode('utf-8'),
                bcrypt.gensalt()
            )
            user.password = hashed_password
            user.password_reset_token = None
            user.password_reset_expires = None

            self._db.session.commit()

        except SQLAlchemyError as e:
            self._db.session.rollback()
            raise AuthenticationError(f"Password reset failed: {str(e)}")

    def _generate_session_token(self, user_id: int) -> str:
        """
        Generate a unique session token for a user.

        Args:
            user_id: ID of the user

        Returns:
            Generated session token

        Note:
            This is a simple implementation. For production,
            consider using JWT or similar token standard.
        """
        return str(uuid4())
