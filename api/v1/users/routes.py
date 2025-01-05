#!/usr/bin/python3
"""
User routes module.

This module defines the routes for user management endpoints including
listing users, getting profiles, and managing user data.

Routes:
    GET  /users:          List all users (admin only)
    GET  /users/{id}:     Get user profile
    PUT  /users/{id}:     Update user profile
    DELETE /users/{id}:   Delete user (admin only)
    GET /users/{id}/posts: Get user's posts
"""
from flask import Blueprint, request, g, current_app
from .service import UserService, UserServiceError
from ..utils.responses import success_response, error_response
from ..utils.decorators import require_auth, validate_request, require_admin

# Initialize Blueprint
users_bp = Blueprint('users', __name__, url_prefix='/users')
user_service = UserService()

@users_bp.route('', methods=['GET'])
@require_auth
@require_admin
def list_users():
    """
    List all users endpoint (admin only).
    
    Query Parameters:
        page: Page number for pagination
        per_page: Items per page
        sort: Sort field
        order: Sort order (asc/desc)
        
    Returns:
        List of user profiles with pagination metadata
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        sort = request.args.get('sort', 'created_at')
        order = request.args.get('order', 'desc')

        current_app.logger.info(f'Listing users: page={page}, per_page={per_page}, sort={sort}, order={order}')
        
        result = user_service.list_users(page, per_page, sort, order)
        return success_response("Users retrieved successfully", result)
    except UserServiceError as e:
        current_app.logger.error(f'Error listing users: {str(e)}')
        return error_response(str(e), 400)

    except Exception as e:
        current_app.logger.error(f'Unexpected error listing users: {str(e)}')
        return error_response("Internal server error", 500)

@users_bp.route('/<int:user_id>', methods=['GET'])
@require_auth
def get_user(user_id):
    """
    Get user profile endpoint.
    
    Args:
        user_id: ID of the user to retrieve
        
    Returns:
        User profile data
    """
    try:
        result = user_service.get_user(user_id, g.current_user.id)
        return success_response("User retrieved successfully", result)
    except UserServiceError as e:
        return error_response(str(e), 404)

@users_bp.route('/<int:user_id>', methods=['PUT'])
@require_auth
@validate_request({
    'username': {'required': False},
    'email': {'required': False},
    'first_name': {'required': False},
    'last_name': {'required': False},
    'bio': {'required': False},
    'avatar_url': {'required': False}
})
def update_user(user_id):
    """
    Update user profile endpoint.
    
    Args:
        user_id: ID of the user to update
        
    Request Body:
        username: New username (optional)
        email: New email (optional)
        first_name: New first name (optional)
        last_name: New last name (optional)
        bio: New bio (optional)
        avatar_url: New avatar URL (optional)
        
    Returns:
        Updated user profile
    """
    if user_id != g.current_user.id and not g.current_user.is_admin:
        return error_response("Unauthorized", 403)
        
    try:
        data = request.get_json()
        result = user_service.update_user(user_id, data)
        return success_response("User updated successfully", result)
    except UserServiceError as e:
        return error_response(str(e), 400)

@users_bp.route('/<int:user_id>', methods=['DELETE'])
@require_auth
@require_admin
def delete_user(user_id):
    """
    Delete user endpoint (admin only).
    
    Args:
        user_id: ID of the user to delete
        
    Returns:
        Success message
    """
    try:
        user_service.delete_user(user_id)
        return success_response("User deleted successfully")
    except UserServiceError as e:
        return error_response(str(e), 400)

@users_bp.route('/<int:user_id>/posts', methods=['GET'])
@require_auth
def get_user_posts(user_id):
    """
    Get user's posts endpoint.
    
    Args:
        user_id: ID of the user whose posts to retrieve
        
    Query Parameters:
        page: Page number for pagination
        per_page: Items per page
        status: Post status filter
        
    Returns:
        List of user's posts with pagination metadata
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status', None)
        
        result = user_service.get_user_posts(
            user_id,
            page,
            per_page,
            status,
            g.current_user.id
        )
        return success_response("Posts retrieved successfully", result)
    except UserServiceError as e:
        return error_response(str(e), 400)
