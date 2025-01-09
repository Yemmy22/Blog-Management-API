#!/usr/bin/python3
"""
Tags management API endpoints.

This module provides API endpoints for blog tag management,
including creation, retrieval, updating, and deletion of tags.

Classes:
    TagsAPI: Class containing tag-related API endpoints
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import func
from models.tag import Tag
from models.post import Post
from validators.validators import validate_slug
from api.v1.auth import require_auth, get_db
from models.audit_log import AuditLog, AuditActionType

tags_bp = Blueprint('tags', __name__)

@tags_bp.route('/', methods=['GET'])
def list_tags():
    """
    List all tags endpoint with optional filtering and statistics.
    
    Query params:
        include_stats: Boolean to include post counts (default: false)
        search: Search tag names
        sort: Sort order ('name' or 'posts', default: 'name')
        
    Returns:
        List of tags with optional post counts
    """
    db = next(get_db())
    
    # Base query
    query = db.query(Tag)
    
    # Apply search filter
    if 'search' in request.args:
        search = f"%{request.args['search']}%"
        query = query.filter(Tag.name.ilike(search))
    
    # Include post counts if requested
    include_stats = request.args.get('include_stats', '').lower() == 'true'
    if include_stats:
        query = db.query(Tag, func.count(Post.id).label('post_count')) \
                 .outerjoin(Tag.posts) \
                 .group_by(Tag.id)
    
    # Apply sorting
    sort = request.args.get('sort', 'name')
    if sort == 'posts' and include_stats:
        query = query.order_by(func.count(Post.id).desc(), Tag.name)
    else:
        query = query.order_by(Tag.name)
    
    # Execute query
    results = query.all()
    
    # Format response
    if include_stats:
        tags = [{
            'id': tag.id,
            'name': tag.name,
            'slug': tag.slug,
            'post_count': post_count,
            'created_at': tag.created_at.isoformat()
        } for tag, post_count in results]
    else:
        tags = [{
            'id': tag.id,
            'name': tag.name,
            'slug': tag.slug,
            'created_at': tag.created_at.isoformat()
        } for tag in results]
    
    return jsonify({'tags': tags})

@tags_bp.route('/', methods=['POST'])
@require_auth
def create_tag():
    """
    Create new tag endpoint.
    
    Request body:
        name: Tag name
        
    Returns:
        Created tag object
    """
    data = request.get_json()
    
    if 'name' not in data:
        return jsonify({'error': 'Name is required'}), 400
        
    db = next(get_db())
    
    # Check if tag already exists
    existing = db.query(Tag).filter_by(name=data['name']).first()
    if existing:
        return jsonify({'error': 'Tag already exists'}), 400
        
    try:
        # Create tag with validated slug
        tag = Tag(
            name=data['name'],
            slug=validate_slug(data['name'])
        )
        db.add(tag)
        
        # Log creation
        AuditLog.log_action(
            db,
            request.user_id,
            AuditActionType.CREATE,
            'Tag',
            tag.id,
            data,
            request.remote_addr,
            request.user_agent.string
        )
        
        db.commit()
        
        return jsonify({
            'id': tag.id,
            'name': tag.name,
            'slug': tag.slug
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': 'Failed to create tag'}), 500

@tags_bp.route('/<slug>', methods=['GET'])
def get_tag(slug):
    """
    Get single tag by slug endpoint.
    
    URL params:
        slug: Tag URL slug
        
    Returns:
        Tag object with related posts
    """
    db = next(get_db())
    
    tag = db.query(Tag).filter_by(slug=slug).first()
    if not tag:
        return jsonify({'error': 'Tag not found'}), 404
    
    # Get related posts
    posts = [{
        'id': post.id,
        'title': post.title,
        'slug': post.slug,
        'created_at': post.created_at.isoformat()
    } for post in tag.posts if post.deleted_at is None]
    
    return jsonify({
        'id': tag.id,
        'name': tag.name,
        'slug': tag.slug,
        'created_at': tag.created_at.isoformat(),
        'posts': posts
    })

@tags_bp.route('/<slug>', methods=['PUT'])
@require_auth
def update_tag(slug):
    """
    Update tag endpoint.
    
    URL params:
        slug: Tag URL slug
        
    Request body:
        name: New tag name
        
    Returns:
        Updated tag object
    """
    data = request.get_json()
    
    if 'name' not in data:
        return jsonify({'error': 'Name is required'}), 400
        
    db = next(get_db())
    
    tag = db.query(Tag).filter_by(slug=slug).first()
    if not tag:
        return jsonify({'error': 'Tag not found'}), 404
        
    try:
        # Update tag
        tag.name = data['name']
        tag.slug = validate_slug(data['name'])
        
        # Log update
        AuditLog.log_action(
            db,
            request.user_id,
            AuditActionType.UPDATE,
            'Tag',
            tag.id,
            data,
            request.remote_addr,
            request.user_agent.string
        )
        
        db.commit()
        
        return jsonify({
            'id': tag.id,
            'name': tag.name,
            'slug': tag.slug
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': 'Failed to update tag'}), 500

@tags_bp.route('/<slug>', methods=['DELETE'])
@require_auth
def delete_tag(slug):
    """
    Delete tag endpoint.
    
    URL params:
        slug: Tag URL slug
        
    Returns:
        Success message
    """
    db = next(get_db())
    
    tag = db.query(Tag).filter_by(slug=slug).first()
    if not tag:
        return jsonify({'error': 'Tag not found'}), 404
        
    try:
        # Remove tag from all posts
        tag.posts = []
        
        # Log deletion
        AuditLog.log_action(
            db,
            request.user_id,
            AuditActionType.DELETE,
            'Tag',
            tag.id,
            None,
            request.remote_addr,
            request.user_agent.string
        )
        
        # Delete tag
        db.delete(tag)
        db.commit()
        
        return jsonify({'message': 'Tag deleted successfully'})
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': 'Failed to delete tag'}), 500

@tags_bp.route('/merge', methods=['POST'])
@require_auth
def merge_tags():
    """
    Merge multiple tags into one endpoint.
    
    Request body:
        source_slugs: List of tag slugs to merge
        target_slug: Slug of tag to merge into
        
    Returns:
        Success message with merge results
    """
    data = request.get_json()
    
    if 'source_slugs' not in data or 'target_slug' not in data:
        return jsonify({'error': 'Source and target slugs are required'}), 400
        
    if len(data['source_slugs']) < 1:
        return jsonify({'error': 'At least one source tag is required'}), 400
        
    db = next(get_db())
    
    # Get target tag
    target_tag = db.query(Tag).filter_by(slug=data['target_slug']).first()
    if not target_tag:
        return jsonify({'error': 'Target tag not found'}), 404
        
    try:
        merged_count = 0
        for source_slug in data['source_slugs']:
            if source_slug == data['target_slug']:
                continue
                
            source_tag = db.query(Tag).filter_by(slug=source_slug).first()
            if source_tag:
                # Move all posts to target tag
                for post in source_tag.posts:
                    if target_tag not in post.tags:
                        post.tags.append(target_tag)
                
                # Delete source tag
                db.delete(source_tag)
                merged_count += 1
        
        # Log merge
        AuditLog.log_action(
            db,
            request.user_id,
            AuditActionType.UPDATE,
            'Tag',
            target_tag.id,
            {'merged_tags': data['source_slugs']},
            request.remote_addr,
            request.user_agent.string
        )
        
        db.commit()
        
        return jsonify({
            'message': f'Successfully merged {merged_count} tags',
            'target_tag': {
                'id': target_tag.id,
                'name': target_tag.name,
                'slug': target_tag.slug
            }
        })
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': 'Failed to merge tags'}), 500
