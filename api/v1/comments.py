#!/usr/bin/python3
"""
Comments API Blueprint for the Blog Management API.

This module provides endpoints for managing blog post comments,
including creating, reading, updating, and deleting comments.
"""
from flask import Blueprint, request, jsonify, g
from sqlalchemy.orm import Session
from datetime import datetime
from models import Comment, Post, User
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
    if not data or 'content' not in data:
        return jsonify({'error': 'Content is required'}), 400
    
    # Check if post exists
    post = db.query(Post).get(post_id)
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    
    # Create comment
    comment = Comment(
        post_id=post_id,
        user_id=g.user.id,
        content=data['content'],
        parent_id=data.get('parent_id'),
        is_approved=True if g.user.roles else False  # Auto-approve for users with roles
    )
    
    db.add(comment)
    db.commit()
    
    # Clear cache
    cache_key = f'post:{post_id}:comments'
    redis_client.cache_delete(cache_key)
    
    return jsonify({
        'id': comment.id,
        'content': comment.content,
        'created_at': comment.created_at.isoformat(),
        'is_approved': comment.is_approved
    }), 201

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
    response = [{
        'id': comment.id,
        'content': comment.content,
        'created_at': comment.created_at.isoformat(),
        'user': {
            'id': comment.user.id,
            'username': comment.user.username
        },
        'parent_id': comment.parent_id
    } for comment in comments]
    
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
    
    if not data or 'content' not in data:
        return jsonify({'error': 'Content is required'}), 400
    
    comment = db.query(Comment).get(comment_id)
    if not comment:
        return jsonify({'error': 'Comment not found'}), 404
    
    # Check if user owns comment or has moderator privileges
    if comment.user_id != g.user.id and not any(role.name in ['admin', 'editor'] for role in g.user.roles):
        return jsonify({'error': 'Unauthorized'}), 403
    
    comment.content = data['content']
    comment.updated_at = datetime.utcnow()
    db.commit()
    
    # Clear cache
    cache_key = f'post:{comment.post_id}:comments'
    redis_client.cache_delete(cache_key)
    
    return jsonify({
        'id': comment.id,
        'content': comment.content,
        'updated_at': comment.updated_at.isoformat()
    })

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
    if comment.user_id != g.user.id and not any(role.name in ['admin', 'editor'] for role in g.user.roles):
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.delete(comment)
    db.commit()
    
    # Clear cache
    cache_key = f'post:{comment.post_id}:comments'
    redis_client.cache_delete(cache_key)
    
    return '', 204

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
    if not any(role.name in ['admin', 'editor'] for role in g.user.roles):
        return jsonify({'error': 'Unauthorized'}), 403
    
    comment = db.query(Comment).get(comment_id)
    if not comment:
        return jsonify({'error': 'Comment not found'}), 404
    
    comment.is_approved = True
    db.commit()
    
    # Clear cache
    cache_key = f'post:{comment.post_id}:comments'
    redis_client.cache_delete(cache_key)
    
    return jsonify({
        'id': comment.id,
        'is_approved': True
    })
