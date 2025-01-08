# api/v1/auth.py

#!/usr/bin/python3
"""
Authentication and session management API endpoints.

This module provides API endpoints for user authentication,
session management, and related security features.

Classes:
    AuthAPI: Class containing authentication-related API endpoints
"""
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from models.user import User
from models.user_session import UserSession
from utils.password import verify_password, hash_password
from utils.redis_client import RedisClient
from datetime import datetime, timedelta
import uuid
from functools import wraps
import jwt
from config.database import SessionLocal
from models.audit_log import AuditLog, AuditActionType

auth_bp = Blueprint('auth', __name__)
redis_client = RedisClient()

# Configuration
JWT_SECRET = "your-secret-key"  # Move to environment variables in production
SESSION_EXPIRY = 24 * 60 * 60  # 24 hours in seconds

def get_db():
    """Database session context manager."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def require_auth(f):
    """Decorator to require authentication for routes."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'No token provided'}), 401
            
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
                
            # Verify JWT
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            
            # Check if session exists in Redis
            session = redis_client.session_get(payload['session_id'])
            if not session:
                return jsonify({'error': 'Invalid or expired session'}), 401
                
            # Add user info to request
            request.user_id = payload['user_id']
            request.session_id = payload['session_id']
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
            
        return f(*args, **kwargs)
    return decorated

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User login endpoint.
    
    Request body:
        username/email: User identifier
        password: User password
        
    Returns:
        JWT token and user info on success
        Error message on failure
    """
    data = request.get_json()
    db = next(get_db())
    
    # Get credentials
    identifier = data.get('username') or data.get('email')
    password = data.get('password')
    
    if not identifier or not password:
        return jsonify({'error': 'Missing credentials'}), 400
        
    # Find user
    user = db.query(User).filter(
        (User.username == identifier) | (User.email == identifier)
    ).first()
    
    # Verify credentials
    if not user or not verify_password(password, user.password):
        return jsonify({'error': 'Invalid credentials'}), 401
        
    if not user.is_active:
        return jsonify({'error': 'Account is inactive'}), 401
        
    # Create session
    session_id = str(uuid.uuid4())
    session_data = {
        'user_id': user.id,
        'username': user.username,
        'roles': [role.name for role in user.roles]
    }
    
    # Store in Redis
    redis_client.session_set(session_id, session_data, SESSION_EXPIRY)
    
    # Create JWT
    token = jwt.encode({
        'user_id': user.id,
        'session_id': session_id,
        'exp': datetime.utcnow() + timedelta(seconds=SESSION_EXPIRY)
    }, JWT_SECRET)
    
    # Update user last login
    user.last_login = datetime.utcnow()
    
    # Log login
    AuditLog.log_action(
        db,
        user.id,
        AuditActionType.LOGIN,
        'User',
        user.id,
        None,
        request.remote_addr,
        request.user_agent.string
    )
    
    db.commit()
    
    return jsonify({
        'token': token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'roles': [role.name for role in user.roles]
        }
    })

@auth_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    """
    User logout endpoint.
    
    Requires authentication token.
    Invalidates current session.
    """
    # Delete session from Redis
    redis_client.session_delete(request.session_id)
    
    # Log logout
    db = next(get_db())
    AuditLog.log_action(
        db,
        request.user_id,
        AuditActionType.LOGOUT,
        'User',
        request.user_id,
        None,
        request.remote_addr,
        request.user_agent.string
    )
    
    return jsonify({'message': 'Logged out successfully'})

@auth_bp.route('/reset-password', methods=['POST'])
def request_password_reset():
    """
    Request password reset endpoint.
    
    Request body:
        email: User's email address
        
    Sends password reset token to user's email.
    """
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
        
    db = next(get_db())
    user = db.query(User).filter_by(email=email).first()
    
    if not user:
        # Return success even if user not found (security)
        return jsonify({'message': 'Password reset instructions sent if email exists'})
        
    # Generate reset token
    reset_token = str(uuid.uuid4())
    expires = datetime.utcnow() + timedelta(hours=24)
    
    # Update user
    user.password_reset_token = reset_token
    user.password_reset_expires = expires
    db.commit()
    
    # TODO: Send email with reset token
    # In production, integrate with email service
    
    return jsonify({'message': 'Password reset instructions sent'})

@auth_bp.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    """
    Reset password endpoint.
    
    URL params:
        token: Password reset token
        
    Request body:
        password: New password
    """
    data = request.get_json()
    new_password = data.get('password')
    
    if not new_password:
        return jsonify({'error': 'New password is required'}), 400
        
    db = next(get_db())
    user = db.query(User).filter(
        User.password_reset_token == token,
        User.password_reset_expires > datetime.utcnow()
    ).first() 
    """
    user = db.query(User).filter_by(
        password_reset_token=token,
        password_reset_expires={'$gt': datetime.utcnow()}
    ).first()
    """
    
    if not user:
        return jsonify({'error': 'Invalid or expired reset token'}), 400
        
    # Update password
    hashed_password, _ = hash_password(new_password)
    user.password = hashed_password
    user.password_reset_token = None
    user.password_reset_expires = None
    
    # Log password reset
    AuditLog.log_action(
        db,
        user.id,
        AuditActionType.UPDATE,
        'User',
        user.id,
        {'password_reset': True},
        request.remote_addr,
        request.user_agent.string
    )
    
    db.commit()
    
    return jsonify({'message': 'Password reset successful'})

@auth_bp.route('/session/verify', methods=['GET'])
@require_auth
def verify_session():
    """
    Verify current session endpoint.
    
    Requires authentication token.
    Returns session/user info if valid.
    """
    session = redis_client.session_get(request.session_id)
    
    return jsonify({
        'valid': True,
        'session': session
    })
