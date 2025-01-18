#!/usr/bin/python3
"""
Comments API Blueprint for the Blog Management API.

This module provides endpoints for managing blog post comments,
including creating, reading, updating, and deleting comments.
"""
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from models.comment import Comment
from models.post import Post
from models.user import User
from models.audit_log import AuditLog, AuditActionType
from config.database import SessionLocal
from api.v1.auth import require_auth, get_db
from utils.redis_client import RedisClient
import logging

comments_bp = Blueprint('comments', __name__)
redis_client = RedisClient()

COMMENT_CACHE_EXPIRY = 300  # 5 minutes


@comments_bp.route('/posts/<int:post_id>', methods=['POST'])
@require_auth
def create_comment(post_id):
    print(f"Received request for post_id: {post_id}")
    # Create a new comment on a post.
    try:
        db = next(get_db())
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({'error': 'Content is required'}), 400
        
        # Check if post exists and is not deleted
        post = db.query(Post).filter_by(slug=slug).first()
        if not post:
            return jsonify({'error': 'Post not found'}), 404
            
        # Validate parent comment if provided
        parent_id = data.get('parent_id')
        if parent_id:
            parent_comment = db.query(Comment).filter_by(
                id=parent_id, 
                post_id=post_id,
                deleted_at=None
            ).first()
            if not parent_comment:
                return jsonify({'error': 'Parent comment not found'}), 404

        # Create comment
        comment = Comment(
            post_id=post_id,
            user_id=request.user_id,
            content=data['content'],
            parent_id=data.get('parent_id'),
            is_approved=True  # Could be based on user role/karma
        )
        
        db.add(comment)
        
        # Log creation
        AuditLog.log_action(
            db,
            request.user_id,
            AuditActionType.CREATE,
            'Comment',
            comment.id,
            data,
            request.remote_addr,
            request.user_agent.string
        )
        
        db.commit()
        
        # Invalidate caches
        redis_client.cache_delete(f'post:{post_id}:comments')
        redis_client.cache_delete(f'post:{post.slug}')  # Invalidate post cache too
        
        return jsonify({
            'id': comment.id,
            'content': comment.content,
            'created_at': comment.created_at.isoformat(),
            'user': {
                'id': comment.user_id,
                'username': comment.user.username
            },
            'is_approved': comment.is_approved,
            'parent_id': comment.parent_id
        }), 201
        
    except SQLAlchemyError as e:
        db.rollback()
        return jsonify({'error': 'Database error occurred'}), 500

@comments_bp.route('/posts/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    """
    Get all approved comments for a post.
    
    Query params:
        include_deleted: Include soft-deleted comments (admin only)
    """
    try:
        db = next(get_db())
        
        # Check if post exists
        post = db.query(Post).filter_by(id=post_id, deleted_at=None).first()
        if not post:
            return jsonify({'error': 'Post not found'}), 404
        
        # Try to get from cache first
        cache_key = f'post:{post_id}:comments'
        cached_comments = redis_client.cache_get(cache_key)
        if cached_comments:
            return jsonify(cached_comments)
        
        # Build query
        query = db.query(Comment).filter(
            Comment.post_id == post_id,
            Comment.is_approved == True
        )
        
        # Handle deleted comments
        if not request.headers.get('Authorization'):
            query = query.filter(Comment.deleted_at == None)
        
        # Get comments
        comments = query.order_by(Comment.created_at.desc()).all()
        
        # Format response
        response = [{
            'id': comment.id,
            'content': comment.content,
            'created_at': comment.created_at.isoformat(),
            'updated_at': comment.updated_at.isoformat() if comment.updated_at else None,
            'user': {
                'id': comment.user_id,
                'username': comment.user.username
            },
            'parent_id': comment.parent_id,
            'deleted': comment.deleted_at is not None
        } for comment in comments]
        
        # Cache the response
        if not request.headers.get('Authorization'):
            redis_client.cache_set(cache_key, response, COMMENT_CACHE_EXPIRY)
        
        return jsonify(response)
        
    except SQLAlchemyError:
        return jsonify({'error': 'Database error occurred'}), 500

@comments_bp.route('/comments/<int:comment_id>', methods=['PUT'])
@require_auth
def update_comment(comment_id):
    """
    Update a comment's content.
    Only comment owner can update.
    """
    try:
        db = next(get_db())
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({'error': 'Content is required'}), 400
            
        comment = db.query(Comment).filter_by(
            id=comment_id,
            deleted_at=None
        ).first()
        
        if not comment:
            return jsonify({'error': 'Comment not found'}), 404
            
        # Check ownership
        if comment.user_id != request.user_id:
            return jsonify({'error': 'Permission denied'}), 403
            
        # Update comment
        comment.content = data['content']
        comment.updated_at = datetime.utcnow()
        
        # Log update
        AuditLog.log_action(
            db,
            request.user_id,
            AuditActionType.UPDATE,
            'Comment',
            comment.id,
            data,
            request.remote_addr,
            request.user_agent.string
        )
        
        db.commit()
        
        # Invalidate caches
        redis_client.cache_delete(f'post:{comment.post_id}:comments')
        
        return jsonify({
            'id': comment.id,
            'content': comment.content,
            'updated_at': comment.updated_at.isoformat()
        })
        
    except SQLAlchemyError:
        db.rollback()
        return jsonify({'error': 'Database error occurred'}), 500

@comments_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@require_auth
def delete_comment(comment_id):
    """
    Soft delete a comment.
    Only comment owner or admin can delete.
    """
    try:
        db = next(get_db())
        comment = db.query(Comment).filter_by(
            id=comment_id,
            deleted_at=None
        ).first()
        
        if not comment:
            return jsonify({'error': 'Comment not found'}), 404
            
        # Check ownership
        if comment.user_id != request.user_id:
            # TODO: Add admin role check
            return jsonify({'error': 'Permission denied'}), 403
            
        # Soft delete
        comment.deleted_at = datetime.utcnow()
        
        # Log deletion
        AuditLog.log_action(
            db,
            request.user_id,
            AuditActionType.DELETE,
            'Comment',
            comment.id,
            None,
            request.remote_addr,
            request.user_agent.string
        )
        
        db.commit()
        
        # Invalidate caches
        redis_client.cache_delete(f'post:{comment.post_id}:comments')
        
        return jsonify({'message': 'Comment deleted successfully'})
        
    except SQLAlchemyError:
        db.rollback()
        return jsonify({'error': 'Database error occurred'}), 500
