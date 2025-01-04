#!/usr/bin/python3
"""
User service module.

This module provides the UserService class which handles core user
management business logic including profile management and queries.

Classes:
    UserServiceError: Custom exception for user service failures
    UserService: Service class handling user operations
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc, asc
from models.user import User
from models.post import Post, PostStatus
from db import DB

class UserServiceError(Exception):
    """Custom exception for user service related errors."""
    pass

class UserService:
    """
    Service class for handling user operations.
    
    This class encapsulates core user management business logic,
    providing methods for profile management and queries.
    
    Attributes:
        _db: Database session instance
    """
    
    def __init__(self):
        """Initialize UserService with database session."""
        self._db = DB()
    
    def list_users(
        self,
        page: int = 1,
        per_page: int = 10,
        sort: str = 'created_at',
        order: str = 'desc'
    ) -> Dict[str, Any]:
        """
        Get paginated list of users.
        
        Args:
            page: Page number
            per_page: Items per page
            sort: Field to sort by
            order: Sort order (asc/desc)
            
        Returns:
            Dict containing users list and pagination metadata
            
        Raises:
            UserServiceError: If query fails
        """
        try:
            query = self._db.session.query(User)
            
            # Apply sorting
            if hasattr(User, sort):
                sort_field = getattr(User, sort)
                if order == 'desc':
                    query = query.order_by(desc(sort_field))
                else:
                    query = query.order_by(asc(sort_field))
            
            # Apply pagination
            total = query.count()
            users = query.offset((page - 1) * per_page).limit(per_page).all()
            
            return {
                "users": [user.to_dict() for user in users],
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "pages": (total + per_page - 1) // per_page
                }
            }
            
        except SQLAlchemyError as e:
            raise UserServiceError(f"Failed to retrieve users: {str(e)}")
    
    def get_user(self, user_id: int, current_user_id: int) -> Dict[str, Any]:
        """
        Get user profile by ID.
        
        Args:
            user_id: ID of user to retrieve
            current_user_id: ID of requesting user
            
        Returns:
            User profile data
            
        Raises:
            UserServiceError: If user not found or query fails
        """
        try:
            user = self._db.session.query(User).get(user_id)
            if not user:
                raise UserServiceError("User not found")
            
            # Return full profile for own user or admin
            # Get the current user to check if they're an admin
       current_user = self._db.session.query(User).get(current_user_id)
        if not current_user:
            raise UserServiceError("Current user not found")

       # Check if current user is an admin by looking for admin role
        is_admin = any(role.name == 'admin' for role in current_user.roles)

       # Include private data if user is viewing their own profile or is an admin
        include_private = user_id == current_user_id or is_admin

            return user.to_dict(include_private=include_private)
            
        except SQLAlchemyError as e:
            raise UserServiceError(f"Failed to retrieve user: {str(e)}")
    
    def update_user(self, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user profile.
        
        Args:
            user_id: ID of user to update
            data: Dictionary of fields to update
            
        Returns:
            Updated user profile
            
        Raises:
            UserServiceError: If update fails
        """
        try:
            user = self._db.session.query(User).get(user_id)
            if not user:
                raise UserServiceError("User not found")
            
            # Update fields
            for field in ['username', 'email', 'first_name', 
                         'last_name', 'bio', 'avatar_url']:
                if field in data:
                    setattr(user, field, data[field])
            
            self._db.session.commit()
            return user.to_dict(include_private=True)
            
        except SQLAlchemyError as e:
            self._db.session.rollback()
            raise UserServiceError(f"Failed to update user: {str(e)}")
    
    def delete_user(self, user_id: int) -> None:
        """
        Delete user account.
        
        Args:
            user_id: ID of user to delete
            
        Raises:
            UserServiceError: If deletion fails
        """
        try:
            user = self._db.session.query(User).get(user_id)
            if not user:
                raise UserServiceError("User not found")
            
            self._db.session.delete(user)
            self._db.session.commit()
            
        except SQLAlchemyError as e:
            self._db.session.rollback()
            raise UserServiceError(f"Failed to delete user: {str(e)}")
    
    def get_user_posts(
        self,
        user_id: int,
        page: int = 1,
        per_page: int = 10,
        status: Optional[str] = None,
        current_user_id: int = None
    ) -> Dict[str, Any]:
        """
        Get user's posts with pagination.
        
        Args:
            user_id: ID of user whose posts to retrieve
            page: Page number
            per_page: Items per page
            status: Optional status filter
            current_user_id: ID of requesting user
            
        Returns:
            Dict containing posts list and pagination metadata
            
        Raises:
            UserServiceError: If query fails
        """
        try:
            query = self._db.session.query(Post).filter(Post.user_id == user_id)
            
            # Apply status filter
            if status:
                query = query.filter(Post.status == PostStatus(status))
            elif current_user_id != user_id:
                # Show only published posts to other users
                query = query.filter(Post.status == PostStatus.PUBLISHED)
            
            # Apply pagination
            total = query.count()
            posts = query.order_by(desc(Post.created_at))\
                        .offset((page - 1) * per_page)\
                        .limit(per_page)\
                        .all()
            
            return {
                "posts": [post.to_dict() for post in posts],
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "pages": (total + per_page - 1) // per_page
                }
            }
            
        except SQLAlchemyError as e:
            raise UserServiceError(f"Failed to retrieve posts: {str(e)}")
