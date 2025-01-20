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


@comments_bp.route('/post/<int:post_id>', methods=['POST'])
@require_auth
def create_comment(post_id):
    """Create a new comment on a post."""
    try:
        db = next(get_db())
        data = request.get_json()

        if not data or 'content' not in data:
            return jsonify({'error': 'Content is required'}), 400

        # Check if post exists
        post = db.query(Post).filter_by(id=post_id, deleted_at=None).first()
        if not post:
            return jsonify({'error': 'Post not found'}), 404

        # Validate parent comment
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
            parent_id=parent_id,
            is_approved=True  # Change logic as needed for approval flow
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

        # Invalidate cache
        redis_client.cache_delete(f'post:{post_id}:comments')

        return jsonify({
            'id': comment.id,
            'content': comment.content,
            'created_at': comment.created_at.isoformat(),
            'user': {'id': comment.user_id},
            'is_approved': comment.is_approved,
            'parent_id': comment.parent_id
        }), 201

    except Exception as e:
        db.rollback()
        return jsonify({'error': 'Failed to create comment'}), 500


@comments_bp.route('/post/<int:post_id>', methods=['GET'])
def get_comments(post_id):
    """
    Get all approved comments for a post.

    Query params:
        include_deleted: Include soft-deleted comments (admin only)
    """
    try:
        db = next(get_db())
        print(f"Fetching comments for post_id: {post_id}")

        # Check if the post exists
        post = db.query(Post).filter_by(id=post_id, deleted_at=None).first()
        if not post:
            print(f"Post with ID {post_id} not found.")
            return jsonify({'error': 'Post not found'}), 404

        # Check cache
        cache_key = f'post:{post_id}:comments'
        cached_comments = redis_client.cache_get(cache_key)
        if cached_comments:
            print("Cache hit for comments")
            return jsonify(cached_comments)

        print("Cache miss, querying database")
        
        # Fetch comments
        comments = db.query(Comment).filter(
            Comment.post_id == post_id,
            Comment.is_approved == True,
            Comment.deleted_at == None
        ).order_by(Comment.created_at.desc()).all()

        print(f"Fetched {len(comments)} comments from database")

        # Format response
        response = [{
            'id': comment.id,
            'content': comment.content,
            'created_at': comment.created_at.isoformat(),
            'user': {'id': comment.user_id},
            'parent_id': comment.parent_id
        } for comment in comments]

        # Cache the response
        redis_client.cache_set(cache_key, response, COMMENT_CACHE_EXPIRY)
        print("Comments cached successfully")

        return jsonify(response)

    except Exception as e:
        print(f"Error fetching comments: {e}")
        return jsonify({'error': 'Failed to fetch comments'}), 500



@comments_bp.route('/<int:comment_id>', methods=['PUT'])
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

@comments_bp.route('/<int:comment_id>', methods=['DELETE'])
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

@comments_bp.route('/replies/<int:comment_id>', methods=['GET'])
def get_replies(comment_id):
    """Retrieve replies for a specific comment."""
    db = next(get_db())

    try:
        # Check if the parent comment exists
        parent_comment = db.query(Comment).filter_by(id=comment_id).first()
        if not parent_comment:
            return jsonify({'error': 'Comment not found'}), 404

        # Fetch replies
        replies = db.query(Comment).filter_by(parent_id=comment_id).all()

        # Format response
        response = [{
            'id': reply.id,
            'content': reply.content,
            'created_at': reply.created_at.isoformat(),
            'user': {'id': reply.user_id}
        } for reply in replies]

        return jsonify(response), 200

    except Exception as e:
        print(f"Error fetching replies: {e}")
        return jsonify({'error': 'Failed to fetch replies'}), 500
