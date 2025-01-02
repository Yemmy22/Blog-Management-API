#!/usr/bin/python3
"""
Authentication service module.

This module provides the AuthService class which handles core authentication
business logic including user registration, login, and password management.

Classes:
    AuthenticationError: Custom exception for authentication failures
    AuthService: Service class handling authentication operations
"""
import bcrypt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.exc import SQLAlchemyError
from models.user import User
from models.role import Role
from uuid import uuid4
from db import DB
from .token_management import TokenManager


class AuthenticationError(Exception):
    """Custom exception for authentication-related errors."""
    pass


class AuthService:
    """
    Service class for handling authentication operations.
    
    This class encapsulates core authentication business logic,
    providing methods for registration, login, and password management.
    
    Attributes:
        _db: Database session instance
        _token_manager: Token management instance
    """
    
    def __init__(self):
        """Initialize AuthService with database session."""
        self._db = DB()
        self._token_manager = TokenManager(self._db)
    
    def register_user(self, email: str, password: str, **kwargs) -> Dict[str, Any]:
        """
        Register a new user.
        
        Args:
            email: User's email address
            password: User's password
            **kwargs: Additional user attributes
            
        Returns:
            Dict containing user information and token
            
        Raises:
            AuthenticationError: If registration fails
        """
        try:
            # Check existing user
            if self._db.session.query(User).filter_by(email=email).first():
                raise AuthenticationError("Email already registered")
            
            # Hash password
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Create user
            user = User(
                email=email,
                password=hashed,
                created_at=datetime.utcnow(),
                **kwargs
            )
            
            # Add default role
            default_role = self._db.session.query(Role).filter_by(
                name='user'
            ).first()
            if default_role:
                user.roles.append(default_role)
            
            self._db.session.add(user)
            self._db.session.commit()

          # Generate token
            token, expires_at = self._token_manager.generate_token(user.id)
            
            return {
                "user": user.to_dict(),
                "token": self._generate_token(user.id)
                "expires_at": expires_at.isoformat()
            }
            
        except SQLAlchemyError as e:
            self._db.session.rollback()
            raise AuthenticationError(f"Registration failed: {str(e)}")
    
    def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate a user login.
        
        Args:
            email: User's email
            password: User's password
            
        Returns:
            Dict containing user information and token
            
        Raises:
            AuthenticationError: If login fails
        """
        try:
            user = self._db.session.query(User).filter_by(email=email).first()
            if not user:
                raise AuthenticationError("Invalid credentials")
            
            if not bcrypt.checkpw(password.encode('utf-8'), user.password):
                raise AuthenticationError("Invalid credentials")
            
            user.last_login = datetime.utcnow()
            self._db.session.commit()
            
            return {
                "user": user.to_dict(),
                "token": self._generate_token(user.id),
                "expires_at": expires_at.isoformat()
            }
            
        except SQLAlchemyError as e:
            self._db.session.rollback()
            raise AuthenticationError(f"Login failed: {str(e)}")

    def validate_token(self, token: str) -> bool:
        """
        Validate an authentication token.

        Args:
            token: Token to validate

        Returns:
            Boolean indicating token validity
        """
        return self._token_manager.validate_token(token)
    
    def request_password_reset(self, email: str) -> str:
        """
        Generate password reset token.
        
        Args:
            email: User's email address
            
        Returns:
            Reset token
            
        Raises:
            AuthenticationError: If user not found
        """
        try:
            user = self._db.session.query(User).filter_by(email=email).first()
            if not user:
                raise AuthenticationError("User not found")
            
            token = str(uuid4())
            user.password_reset_token = token
            user.password_reset_expires = datetime.utcnow() + timedelta(hours=24)
            
            self._db.session.commit()
            return token
            
        except SQLAlchemyError as e:
            self._db.session.rollback()
            raise AuthenticationError(f"Reset request failed: {str(e)}")
    
    def reset_password(self, token: str, new_password: str) -> None:
        """
        Reset user password with token.
        
        Args:
            token: Reset token
            new_password: New password
            
        Raises:
            AuthenticationError: If reset fails or token invalid
        """
        try:
            user = self._db.session.query(User).filter_by(
                password_reset_token=token
            ).first()
            
            if not user or user.password_reset_expires < datetime.utcnow():
                raise AuthenticationError("Invalid or expired reset token")
            
            hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            user.password = hashed
            user.password_reset_token = None
            user.password_reset_expires = None
            
            self._db.session.commit()
            
        except SQLAlchemyError as e:
            self._db.session.rollback()
            raise AuthenticationError(f"Password reset failed: {str(e)}")
    
    def _generate_token(self, user_id: int) -> str:
        """
        Generate authentication token.
        
        Args:
            user_id: User's ID
            
        Returns:
            Authentication token
        """
        return str(uuid4())
