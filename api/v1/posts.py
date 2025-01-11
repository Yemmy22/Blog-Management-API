#!/usr/bin/python3
"""
Posts management API endpoints.

This module provides API endpoints for blog post management,
including creation, retrieval, updating, and deletion of posts,
along with related features like tags and categories.

Classes:
    PostsAPI: Class containing post-related API endpoints
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from models.post import Post, PostStatus
from models.tag import Tag
from models.category import Category
from models.post_revision import PostRevision
from models.audit_log import AuditLog, AuditActionType
from utils.redis_client import RedisClient
from validators.validators import validate_slug
from datetime import datetime
from api.v1.auth import require_auth, get_db
from typing import List, Optional

posts_bp = Blueprint('posts', __name__)
redis_client = RedisClient()

# Cache configuration
POST_CACHE_EXPIRY = 3600  # 1 hour in seconds

def check_post_permissions(user_id: int, post: Post) -> bool:
    """
    Check if user has permission to modify post.
    
    Args:
        user_id: ID of user making request
        post: Post object to check
        
    Returns:
        bool: True if user has permission
    """
    # Authors can modify their own posts
    if post.user_id == user_id:
        return True
        
    # TODO: Add role-based checks (editors/admins)
    return False

@posts_bp.route('/', methods=['POST'])
@require_auth
def create_post():
    """
    Create new blog post endpoint.
    
    Request body:
        title: Post title
        content: Post content
        category_id: Category ID
        tags: List of tag names
        status: Post status (draft/published)
        
    Returns:
        Created post object
    """
    data = request.get_json()
    db = next(get_db())
    
    # Validate required fields
    required = ['title', 'content', 'category_id']
    if not all(field in data for field in required):
        return jsonify({'error': 'Missing required fields'}), 400
        
    try:
        # Generate slug from title
        slug = validate_slug(data['title'])
        
        # Create post
        post = Post(
            title=data['title'],
            slug=slug,
            content=data['content'],
            category_id=data['category_id'],
            user_id=request.user_id,
            status=PostStatus(data.get('status', 'draft'))
        )
        
        # Handle optional fields
        if 'meta_description' in data:
            post.meta_description = data['meta_description']
        if 'featured_image_url' in data:
            post.featured_image_url = data['featured_image_url']
            
        # Handle tags
        if 'tags' in data:
            for tag_name in data['tags']:
                tag = db.query(Tag).filter_by(name=tag_name).first()
                if not tag:
                    # Create new tag
                    tag = Tag(
                        name=tag_name,
                        slug=validate_slug(tag_name)
                    )
                    db.add(tag)
                post.tags.append(tag)
                
        db.add(post)
        db.commit()

        # Create initial revision
        revision = PostRevision(
            post_id=post.id,
            title=post.title,
            content=post.content,
            created_by=request.user_id
        )
        db.add(revision)
        
        # Log creation
        AuditLog.log_action(
            db,
            request.user_id,
            AuditActionType.CREATE,
            'Post',
            post.id,
            data,
            request.remote_addr,
            request.user_agent.string
        )
        
        db.commit()
        
        return jsonify({
            'id': post.id,
            'title': post.title,
            'slug': post.slug,
            'status': post.status.value
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': 'Failed to create post'}), 500

@posts_bp.route('/', methods=['GET'])
def list_posts():
    """
    List posts endpoint with filtering and pagination.
    
    Query params:
        page: Page number (default: 1)
        per_page: Items per page (default: 10)
        status: Filter by status
        category: Filter by category
        tag: Filter by tag
        search: Search in title/content
        
    Returns:
        List of posts with pagination metadata
    """
    db = next(get_db())
    
    # Pagination params
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 10)), 100)
    
    # Build query
    query = db.query(Post)
    
    # Apply filters
    if 'status' in request.args:
        query = query.filter(Post.status == PostStatus(request.args['status']))
    else:
        # Default to published posts for public API
        query = query.filter(Post.status == PostStatus.PUBLISHED)
        
    if 'category' in request.args:
        query = query.filter(Post.category_id == request.args['category'])
        
    if 'tag' in request.args:
        query = query.join(Post.tags).filter(Tag.slug == request.args['tag'])
        
    if 'search' in request.args:
        search = f"%{request.args['search']}%"
        query = query.filter(
            or_(
                Post.title.ilike(search),
                Post.content.ilike(search)
            )
        )
    
    # Execute query with pagination
    total = query.count()
    posts = query.order_by(Post.created_at.desc()) \
                 .offset((page - 1) * per_page) \
                 .limit(per_page) \
                 .all()
                 
    # Format response
    return jsonify({
        'posts': [{
            'id': post.id,
            'title': post.title,
            'slug': post.slug,
            'excerpt': post.content[:200] + '...' if len(post.content) > 200 else post.content,
            'author': {
                'id': post.author.id,
                'username': post.author.username
            },
            'category': {
                'id': post.category.id,
                'name': post.category.name
            },
            'tags': [tag.name for tag in post.tags],
            'created_at': post.created_at.isoformat(),
            'status': post.status.value
        } for post in posts],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page
        }
    })

@posts_bp.route('/<slug>', methods=['GET'])
def get_post(slug: str):
    """
    Get single post by slug endpoint.
    
    URL params:
        slug: Post URL slug
        
    Returns:
        Post object if found
    """
    # Check cache first
    cached = redis_client.cache_get(f'post:{slug}')
    if cached:
        return jsonify(cached)
        
    db = next(get_db())
    post = db.query(Post).filter_by(slug=slug).first()
    
    if not post:
        return jsonify({'error': 'Post not found'}), 404
        
    # Increment view count
    post.view_count += 1
    db.commit()
    
    # Format response
    response = {
        'id': post.id,
        'title': post.title,
        'slug': post.slug,
        'content': post.content,
        'meta_description': post.meta_description,
        'featured_image_url': post.featured_image_url,
        'author': {
            'id': post.author.id,
            'username': post.author.username
        },
        'category': {
            'id': post.category.id,
            'name': post.category.name
        },
        'tags': [tag.name for tag in post.tags],
        'created_at': post.created_at.isoformat(),
        'updated_at': post.updated_at.isoformat(),
        'status': post.status.value,
        'view_count': post.view_count,
        'like_count': post.like_count
    }
    
    # Cache response
    redis_client.cache_set(f'post:{slug}', response, POST_CACHE_EXPIRY)
    
    return jsonify(response)

@posts_bp.route('/<slug>', methods=['PUT'])
@require_auth
def update_post(slug: str):
    """
    Update post endpoint.
    
    URL params:
        slug: Post URL slug
        
    Request body:
        title: New title (optional)
        content: New content (optional)
        category_id: New category ID (optional)
        tags: New tag list (optional)
        status: New status (optional)
        
    Returns:
        Updated post object
    """
    data = request.get_json()
    db = next(get_db())
    
    post = db.query(Post).filter_by(slug=slug).first()
    if not post:
        return jsonify({'error': 'Post not found'}), 404
        
    # Check permissions
    if not check_post_permissions(request.user_id, post):
        return jsonify({'error': 'Permission denied'}), 403
        
    try:
        # Create revision before updating
        revision = PostRevision(
            post_id=post.id,
            title=post.title,
            content=post.content,
            created_by=request.user_id
        )
        db.add(revision)
        
        # Update fields
        if 'title' in data:
            post.title = data['title']
            post.slug = validate_slug(data['title'])
            
        if 'content' in data:
            post.content = data['content']
            
        if 'category_id' in data:
            post.category_id = data['category_id']
            
        if 'status' in data:
            post.status = PostStatus(data['status'])
            
        if 'meta_description' in data:
            post.meta_description = data['meta_description']
            
        if 'featured_image_url' in data:
            post.featured_image_url = data['featured_image_url']
            
        # Update tags
        if 'tags' in data:
            post.tags.clear()
            for tag_name in data['tags']:
                tag = db.query(Tag).filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(
                        name=tag_name,
                        slug=validate_slug(tag_name)
                    )
                    db.add(tag)
                post.tags.append(tag)
                
        # Log update
        AuditLog.log_action(
            db,
            request.user_id,
            AuditActionType.UPDATE,
            'Post',
            post.id,
            data,
            request.remote_addr,
            request.user_agent.string
        )
        
        db.commit()
        
        # Invalidate cache
        redis_client.cache_delete(f'post:{slug}')
        
        return jsonify({
            'id': post.id,
            'title': post.title,
            'slug': post.slug,
            'status': post.status.value
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': 'Failed to update post'}), 500

@posts_bp.route('/<slug>', methods=['DELETE'])
@require_auth
def delete_post(slug: str):
    """
    Delete post endpoint.
    
    URL params:
        slug: Post URL slug
        
    Returns:
        Success message
    """
    db = next(get_db())
    
    post = db.query(Post).filter_by(slug=slug).first()
    if not post:
        return jsonify({'error': 'Post not found'}), 404
        
    # Check permissions
    if not check_post_permissions(request.user_id, post):
        return jsonify({'error': 'Permission denied'}), 403
        
    try:
        # Soft delete
        post.deleted_at = datetime.utcnow()
        
        # Log deletion
        AuditLog.log_action(
            db,
            request.user_id,
            AuditActionType.DELETE,
            'Post',
            post.id,
            None,
            request.remote_addr,
            request.user_agent.string
        )
        
        db.commit()
        
        # Invalidate cache
        redis_client.cache_delete(f'post:{slug}')
        
        return jsonify({'message': 'Post deleted successfully'})
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': 'Failed to delete post'}), 500

@posts_bp.route('/<slug>/like', methods=['POST'])
@require_auth
def like_post(slug: str):
    """
    Like/unlike post endpoint.
    
    URL params:
        slug: Post URL slug
        
    Returns:
        Updated like count
    """
    db = next(get_db())
    
    post = db.query(Post).filter_by(slug=slug).first()
    if not post:
        return jsonify({'error': 'Post not found'}), 404
        
    # Toggle like
    like_key = f'post:{post.id}:likes:{request.user_id}'
    if redis_client.cache_get(like_key):
        # Unlike
        redis_client.cache_delete(like_key)
        post.like_count = max(0, post.like_count - 1)
    else:
        # Like
        redis_client.cache_set(like_key, True)
        post.like_count += 1
        
    db.commit()
    
    # Invalidate post cache
    redis_client.cache_delete(f'post:{slug}')
    
    return jsonify({
        'like_count': post.like_count,
        'liked': bool(redis_client.cache_get(like_key))
    })

