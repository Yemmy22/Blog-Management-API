#!/usr/bin/python3
"""
This module defines the Comment class for managing post comments.

The Comment class represents user comments on blog posts, supporting
threading capabilities and moderation features.

Classes:
    Comment: Represents a post comment
"""
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from models import Base

class Comment(Base):
    """
    Comment model class representing post comments.

    This class defines the structure for blog post comments,
    including threading support and moderation capabilities.

    Attributes:
        id (Column): Primary key of the comment
        post_id (Column): Foreign key to the associated post
        user_id (Column): Foreign key to the comment author
        parent_id (Column): Foreign key to parent comment (for threading)
        content (Column): Comment text content
        is_approved (Column): Moderation status flag
        created_at (Column): Timestamp of comment creation
        deleted_at (Column): Timestamp of comment deletion
        post (relationship): Many-to-one relationship with Post model
        user (relationship): Many-to-one relationship with User model
        parent (relationship): Self-referential relationship for threading
        replies (relationship): Reverse of the parent relationship
    """
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    parent_id = Column(Integer, ForeignKey('comments.id'))
    content = Column(Text, nullable=False)
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    post = relationship('Post', back_populates='comments')
    user = relationship('User', back_populates='comments')
    parent = relationship('Comment', remote_side=[id], backref='replies')

    # Indexes
    __table_args__ = (
        Index('idx_post_id', post_id),
        Index('idx_created_at', created_at),
    )
