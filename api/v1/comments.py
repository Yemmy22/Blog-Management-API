#!/usr/bin/python3
"""
Comments API Blueprint for the Blog Management API.

This module provides endpoints for managing blog post comments,
including creating, reading, updating, and deleting comments.
"""
from flask import Blueprint, request, jsonify, g
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from models import Comment, Post, User, AuditLog
from config.database import SessionLocal
from api.v1.auth import auth_required
from utils.redis_client import RedisClient

comments_bp = Blueprint('comments', __name__)
redis_client = RedisClient()

def get_db():
    """Get database session."""
    if 'db' not in g:
        g.db = SessionLocal()
    return g.db

@comments_bp.teardown_request
def teardown_request(exception=None):
    """Close database session."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

@comments_bp.route('/posts/<int:post_id>/comments', methods=['POST'])
@auth_required
def create_comment(post_id):
    """
    Create a new comment on a post.
    
    Args:
        post_id: ID of the post to comment on
    """
    db = get_db()
    data = request.get_json()
    
    # Validate input
    if not data or 'content' not in data or len(data['content']) > 500:
        return jsonify({'error': 'Content is required and must be less than 500 characters'}), 400
    
    # Check if post exists
    post = db.query(Post).get(post_id)
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    
    # Validate parent_id if provided
    parent_id = data.get('parent_id')
    if parent_id:
        parent_comment = db.query(Comment).get(parent_id)
        if not parent_comment or parent_comment.post_id != post_id:
            return jsonify({'error': 'Invalid parent comment'}), 400
    
    # Create comment
    comment = Comment(
        post_id=post_id,
        user_id=g.user.id,
        content=data['content'],
        parent_id=parent_id,
        is_approved=g.user.is_admin  # Auto-approve for admin users
    )
    try:
        db.add(comment)
        db.commit()
        
        # Log the action
        AuditLog.log_action(
            db,
            g.user.id,
            'create',
            'Comment',
            comment.id,
            {'content': data['content'], 'post_id': post_id},
            request.remote_addr,
            request.user_agent.string
        )

        # Clear cache
        cache_key = f'post:{post_id}:comments'
        redis_client.cache_delete(cache_key)
        
        return jsonify({
            'id': comment.id,
            'content': comment.content,
            'created_at': comment.created_at.isoformat(),
            'is_approved': comment.is_approved
        }), 201
    except IntegrityError:
        db.rollback()
        return jsonify({'error': 'Database error occurred'}), 500

@comments_bp.route('/posts/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    """
    Get all approved comments for a post.
    
    Args:
        post_id: ID of the post to get comments for
    """
    db = get_db()
    
    # Try to get from cache
    cache_key = f'post:{post_id}:comments'
    cached_comments = redis_client.cache_get(cache_key)
    if cached_comments:
        return jsonify(cached_comments)
    
    # Get comments from database
    comments = db.query(Comment)\
        .filter(Comment.post_id == post_id, Comment.is_approved == True)\
        .order_by(Comment.created_at.desc())\
        .all()
    
    # Format response
    response = [comment.to_dict() for comment in comments]
    
    # Cache results
    redis_client.cache_set(cache_key, response, expire=300)  # Cache for 5 minutes
    
    return jsonify(response)

@comments_bp.route('/comments/<int:comment_id>', methods=['PUT'])
@auth_required
def update_comment(comment_id):
    """
    Update a comment.
    
    Args:
        comment_id: ID of the comment to update
    """
    db = get_db()
    data = request.get_json()
    
    if not data or 'content' not in data or len(data['content']) > 500:
        return jsonify({'error': 'Content is required and must be less than 500 characters'}), 400
    
    comment = db.query(Comment).get(comment_id)
    if not comment:
        return jsonify({'error': 'Comment not found'}), 404
    
    # Check if user owns comment or has moderator privileges
    if comment.user_id != g.user.id and not g.user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    comment.content = data['content']
    comment.updated_at = datetime.utcnow()
    try:
        db.commit()
        
        # Log the action
        AuditLog.log_action(
            db,
            g.user.id,
            'update',
            'Comment',
            comment.id,
            {'content': data['content']},
            request.remote_addr,
            request.user_agent.string
        )

        # Clear cache
        cache_key = f'post:{comment.post_id}:comments'
        redis_client.cache_delete(cache_key)
        
        return jsonify(comment.to_dict())
    except IntegrityError:
        db.rollback()
        return jsonify({'error': 'Database error occurred'}), 500

@comments_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@auth_required
def delete_comment(comment_id):
    """
    Delete a comment.
    
    Args:
        comment_id: ID of the comment to delete
    """
    db = get_db()
    
    comment = db.query(Comment).get(comment_id)
    if not comment:
        return jsonify({'error': 'Comment not found'}), 404
    
    # Check if user owns comment or has moderator privileges
    if comment.user_id != g.user.id and not g.user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        db.delete(comment)
        db.commit()
        
        # Log the action
        AuditLog.log_action(
            db,
            g.user.id,
            'delete',
            'Comment',
            comment_id,
            None,
            request.remote_addr,
            request.user_agent.string
        )

        # Clear cache
        cache_key = f'post:{comment.post_id}:comments'
        redis_client.cache_delete(cache_key)
        
        return '', 204
    except IntegrityError:
        db.rollback()
        return jsonify({'error': 'Database error occurred'}), 500

@comments_bp.route('/comments/<int:comment_id>/approve', methods=['POST'])
@auth_required
def approve_comment(comment_id):
    """
    Approve a comment.
    
    Args:
        comment_id: ID of the comment to approve
    """
    db = get_db()
    
    # Check if user has moderator privileges
    if not g.user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    comment = db.query(Comment).get(comment_id)
    if not comment:
        return jsonify({'error': 'Comment not found'}), 404
    
    comment.is_approved = True
    try:
        db.commit()
        
        # Log the action
        AuditLog.log_action(
            db,
            g.user.id,
            'approve',
            'Comment',
            comment.id,
            None,
            request.remote_addr,
            request.user_agent.string
        )

        # Clear cache
        cache_key = f'post:{comment.post_id}:comments'
        redis_client.cache_delete(cache_key)
        
        return jsonify({'id': comment.id, 'is_approved': True})
    except IntegrityError:
        db.rollback()
        return jsonify({'error': 'Database error occurred'}), 500

