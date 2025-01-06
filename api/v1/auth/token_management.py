#!/usr/bin/python3
"""
Token management module.

This module provides functionality for managing authentication tokens
including generation, validation, and blacklisting of tokens.

Classes:
    TokenManager: Handles token operations and storage
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple
from uuid import uuid4
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Boolean
from models import Base
from sqlalchemy.exc import SQLAlchemyError

class TokenUser(Base):
    """Model class for storing token-user mappings."""
    __tablename__ = 'token_users'
    
    token = Column(String(100), primary_key=True)
    user_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)

class BlacklistedToken(Base):
    """Model class for storing blacklisted tokens."""
    __tablename__ = 'blacklisted_tokens'
    
    token = Column(String(100), primary_key=True)
    blacklisted_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=False)

class TokenManager:
    """Service class for token management operations."""
    
    def __init__(self, db, token_lifetime_hours: int = 24):
        self._db = db
        self._token_lifetime = timedelta(hours=token_lifetime_hours)
    
    def generate_token(self, user_id: int) -> Tuple[str, datetime]:
        """Generate a new authentication token."""
        token = str(uuid4())
        expires_at = datetime.utcnow() + self._token_lifetime
        
        try:
            # Store token-user mapping
            token_user = TokenUser(
                token=token,
                user_id=user_id,
                created_at=datetime.utcnow(),
                expires_at=expires_at,
                is_active=True
            )
            self._db.session.add(token_user)
            self._db.session.commit()
            
            return token, expires_at
            
        except SQLAlchemyError as e:
            self._db.session.rollback()
            raise ValueError(f"Token generation failed: {str(e)}")

    def validate_token(self, token: str) -> Tuple[bool, Optional[int]]:
        """
        Validate token and return user ID if valid.
        
        Returns:
            Tuple[bool, Optional[int]]: (is_valid, user_id)
        """
        try:
            # Check if token is blacklisted
            blacklisted = self._db.session.query(BlacklistedToken).filter_by(
                token=token
            ).first()
            
            if blacklisted:
                return False, None
            
            # Get user ID from token mapping
            token_user = self._db.session.query(TokenUser).filter_by(
                token=token,
                is_active=True
            ).first()
            
            if not token_user:
                return False, None
                
            # Check if token has expired
            if token_user.expires_at < datetime.utcnow():
                user_token.is_active = False
                self._db.session.commit()
                return False, None
                
            return True, token_user.user_id
            
        except SQLAlchemyError:
            return False, None
    
    def blacklist_token(self, token: str, expires_at: datetime) -> None:
        """Blacklist an authentication token."""
        try:
            # Remove token-user mapping
            user_token = self._db.session.query(TokenUser).filter_by(token=token)
            if user_token:
                user_token.is_active = False
            
            # Add to blacklist
            blacklisted_token = BlacklistedToken(
                token=token,
                blacklisted_at=datetime.utcnow(),
                expires_at=expires_at
            )
            self._db.session.add(blacklisted_token)
            self._db.session.commit()
            
        except SQLAlchemyError as e:
            self._db.session.rollback()
            raise ValueError(f"Failed to blacklist token: {str(e)}")
    
    def cleanup_expired_tokens(self) -> None:
        """Remove expired tokens from blacklist and token-user mappings."""
        try:
            now = datetime.utcnow()
            
            # Clean blacklisted tokens
            self._db.session.query(BlacklistedToken).filter(
                BlacklistedToken.expires_at < now
            ).delete()
            
            # Clean expired token-user mappings
            self._db.session.query(TokenUser).filter(
                TokenUser.expires_at < now
            ).delete()
            
            self._db.session.commit()
            
        except SQLAlchemyError as e:
            self._db.session.rollback()
            raise ValueError(f"Failed to cleanup tokens: {str(e)}")
