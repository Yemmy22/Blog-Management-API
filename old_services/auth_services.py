#!/usr/bin/python3
"""
This module provides authentication services for the application.

Classes:
    AuthService: Handles login attempts and account security.
"""

from datetime import datetime, timedelta
from models.login_attempt import LoginAttempt

class AuthService:
    """
    Service class for handling authentication-related operations.
    
    Attributes:
        db_session: SQLAlchemy session for database operations.
        max_attempts (int): Maximum number of failed login attempts allowed.
        lockout_duration (timedelta): Duration for which account remains locked.
    """

    def __init__(self, db_session):
        """Initialize the auth service with database session and config."""
        self.db_session = db_session
        self.max_attempts = 5
        self.lockout_duration = timedelta(minutes=30)

    def handle_login_attempt(self, user, success, ip_address):
        """
        Handle a login attempt and manage account lockout.
        
        Args:
            user: User object for the login attempt.
            success (bool): Whether the login attempt was successful.
            ip_address (str): IP address from which the attempt was made.
        """
        attempt = LoginAttempt(
            user_id=user.id,
            success=success,
            ip_address=ip_address
        )
        
        if not success:
            user.increment_failed_login()
        else:
            user.failed_login_count = 0
            user.locked_until = None
            user.last_login = datetime.utcnow()
        
        self.db_session.add(attempt)
        self.db_session.commit()
