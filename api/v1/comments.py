#!/usr/bin/python3
"""
Comments API Blueprint for the Blog Management API.

This module provides endpoints for managing blog post comments,
including creating, reading, updating, and deleting comments.
"""
from flask import Blueprint, request, jsonify, g
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from models import Comment, Post, User
from config.database import SessionLocal
from api.v1.auth import require_auth
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
@require_auth
def create_comment(post_id):
    """
    Create a new comment on a post.
    """
    db = get_db()
    data = request.get_json()
    
    if not data or 'content' not in data:
        return jsonify({'error': 'Content is required'}), 400
    
    post = db.query(Post).get(post_id)
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    
    comment = Comment(
        post_id=post_id,
        user_id=g.user.id,
        content=data['content'],
        parent_id=data.get('parent_id'),
        is_approved='admin' in [role.name for role in g.user.roles]  # Auto-approve for admins
    )
    
    db.add(comment)
    db.commit()
    redis_client.cache_delete(f'post:{post_id}:comments')
    
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
    """
    db = get_db()
    cache_key = f'post:{post_id}:comments'
    cached_comments = redis_client.cache_get(cache_key)
    
    if cached_comments:
        return jsonify(cached_comments)
    
    comments = db.query(Comment)\
        .filter(Comment.post_id == post_id, Comment.is_approved == True)\
        .order_by(Comment.created_at.desc())\
        .all()
    
    response = [{
        'id': comment.id,
        'content': comment.content,
        'created_at': comment.created_at.isoformat(),
        'user': {'id': comment.user.id, 'username': comment.user.username},
        'parent_id': comment.parent_id
    } for comment in comments]
    
    redis_client.cache_set(cache_key, response, expire=300)
    return jsonify(response)

