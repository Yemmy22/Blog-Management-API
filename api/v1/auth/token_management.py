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
from sqlalchemy import Column, String, DateTime
from models import Base
from sqlalchemy.exc import SQLAlchemyError


class BlacklistedToken(Base):
    """
    Model class for storing blacklisted tokens.
    
    This class represents tokens that have been invalidated
    through user logout or other security measures.
    
    Attributes:
        token (Column): The blacklisted token string
        blacklisted_at (Column): Timestamp of blacklisting
        expires_at (Column): Token expiration timestamp
    """
    __tablename__ = 'blacklisted_tokens'
    
    token = Column(String(100), primary_key=True)
    blacklisted_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=False)


class TokenManager:
    """
    Service class for token management operations.
    
    This class handles the generation, validation, and blacklisting
    of authentication tokens, providing a centralized token
    management solution.
    
    Attributes:
        _db: Database session instance
        _token_lifetime: Duration for token validity
    """
    
    def __init__(self, db, token_lifetime_hours: int = 24):
        """
        Initialize TokenManager.
        
        Args:
            db: Database session instance
            token_lifetime_hours: Token validity duration in hours
        """
        self._db = db
        self._token_lifetime = timedelta(hours=token_lifetime_hours)
    
    def generate_token(self, user_id: int) -> Tuple[str, datetime]:
        """
        Generate a new authentication token.
        
        Args:
            user_id: ID of the user requesting token
            
        Returns:
            Tuple containing token string and expiration timestamp
        """
        token = str(uuid4())
        expires_at = datetime.utcnow() + self._token_lifetime
        return token, expires_at
    
    def validate_token(self, token: str) -> bool:
        """
        Validate an authentication token.
        
        Args:
            token: Token string to validate
            
        Returns:
            Boolean indicating token validity
        """
        try:
            # Check if token is blacklisted
            blacklisted = self._db.session.query(BlacklistedToken).filter_by(
                token=token
            ).first()
            
            if blacklisted:
                return False
                
            return True
            
        except SQLAlchemyError:
            return False
    
    def blacklist_token(self, token: str, expires_at: datetime) -> None:
        """
        Blacklist an authentication token.
        
        Args:
            token: Token string to blacklist
            expires_at: Token expiration timestamp
        """
        try:
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
        """Remove expired tokens from blacklist."""
        try:
            self._db.session.query(BlacklistedToken).filter(
                BlacklistedToken.expires_at < datetime.utcnow()
            ).delete()
            self._db.session.commit()
            
        except SQLAlchemyError as e:
            self._db.session.rollback()
            raise ValueError(f"Failed to cleanup tokens: {str(e)}")
