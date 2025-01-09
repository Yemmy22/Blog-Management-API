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
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional

posts_bp = Blueprint('posts', __name__)
redis_client = RedisClient()

@posts_bp.route('/', methods=['POST'])
@require_auth
def create_post():
    """
    Create new blog post endpoint with improved error handling.
    
    Request body:
        title: Post title
        content: Post content
        category_id: Category ID
        tags: List of tag names
        status: Post status (draft/published)
        
    Returns:
        Created post object or error message
    """
    data = request.get_json()
    db = next(get_db())
    
    # Validate required fields
    required = ['title', 'content', 'category_id']
    missing_fields = [field for field in required if field not in data]
    if missing_fields:
        return jsonify({
            'error': 'Missing required fields',
            'missing_fields': missing_fields
        }), 400
    
    try:
        # Verify category exists
        category = db.query(Category).get(data['category_id'])
        if not category:
            return jsonify({
                'error': 'Invalid category',
                'details': f"Category with ID {data['category_id']} does not exist"
            }), 404

        # Generate slug from title
        try:
            slug = validate_slug(data['title'])
        except ValueError as e:
            return jsonify({
                'error': 'Invalid title',
                'details': str(e)
            }), 400

        # Validate status if provided
        if 'status' in data:
            try:
                status = PostStatus(data.get('status', 'draft'))
            except ValueError:
                return jsonify({
                    'error': 'Invalid status',
                    'details': f"Status must be one of: {[s.value for s in PostStatus]}"
                }), 400
        else:
            status = PostStatus.DRAFT

        # Create post
        post = Post(
            title=data['title'],
            slug=slug,
            content=data['content'],
            category_id=data['category_id'],
            user_id=request.user_id,
            status=status
        )
        
        # Handle optional fields with validation
        if 'meta_description' in data:
            if len(data['meta_description']) > 160:
                return jsonify({
                    'error': 'Invalid meta description',
                    'details': 'Meta description must be 160 characters or less'
                }), 400
            post.meta_description = data['meta_description']

        if 'featured_image_url' in data:
            if len(data['featured_image_url']) > 255:
                return jsonify({
                    'error': 'Invalid featured image URL',
                    'details': 'URL must be 255 characters or less'
                }), 400
            post.featured_image_url = data['featured_image_url']
            
        # Handle tags
        if 'tags' in data:
            if not isinstance(data['tags'], list):
                return jsonify({
                    'error': 'Invalid tags format',
                    'details': 'Tags must be provided as a list'
                }), 400
                
            for tag_name in data['tags']:
                if not isinstance(tag_name, str) or not tag_name.strip():
                    return jsonify({
                        'error': 'Invalid tag name',
                        'details': 'Tag names must be non-empty strings'
                    }), 400
                    
                tag = db.query(Tag).filter_by(name=tag_name).first()
                if not tag:
                    try:
                        tag = Tag(
                            name=tag_name,
                            slug=validate_slug(tag_name)
                        )
                        db.add(tag)
                    except ValueError as e:
                        return jsonify({
                            'error': 'Invalid tag name',
                            'details': str(e)
                        }), 400
                post.tags.append(tag)
                
        db.add(post)
        db.flush()  # Get post ID without committing
        
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
            'status': post.status.value,
            'category': {
                'id': category.id,
                'name': category.name
            },
            'tags': [tag.name for tag in post.tags]
        }), 201
        
    except SQLAlchemyError as e:
        db.rollback()
        return jsonify({
            'error': 'Database error',
            'details': str(e)
        }), 500
        
    except Exception as e:
        db.rollback()
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500
