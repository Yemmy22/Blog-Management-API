#!/usr/bin/python3
"""
This module defines the Post class for blog content management.

The Post class represents blog posts with support for categories,
tags, and engagement metrics.

Classes:
    Post: Represents a blog post
    PostStatus: Enum for post status values
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from models import Base
import enum

class PostStatus(enum.Enum):
    """Enum defining possible post statuses."""
    DRAFT = "draft"
    PUBLISHED = "published"

class Post(Base):
    """
    Post model class representing blog posts.
    
    This class defines the structure for blog posts, including content,
    metadata, and relationships with categories, tags, and comments.
    
    Attributes:
        id (Column): Primary key of the post
        title (Column): Post title
        slug (Column): URL-friendly version of the title
        content (Column): Main content of the post
        status (Column): Current status (draft/published)
        view_count (Column): Number of post views
        like_count (Column): Number of post likes
        created_at (Column): Timestamp of post creation
        updated_at (Column): Timestamp of last update
        user_id (Column): Foreign key to the author
        category_id (Column): Foreign key to the category
        author (relationship): Many-to-one relationship with User model
        category (relationship): Many-to-one relationship with Category model
        tags (relationship): Many-to-many relationship with Tag model
        comments (relationship): One-to-many relationship with Comment model
    """
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(250), unique=True, nullable=False)
    content = Column(Text, nullable=False)
    status = Column(Enum(PostStatus), default=PostStatus.DRAFT)
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    
    # Relationships
    author = relationship('User', back_populates='posts')
    category = relationship('Category', back_populates='posts')
    tags = relationship('Tag', secondary='post_tags', back_populates='posts')
    comments = relationship('Comment', back_populates='post')
    
    # Indexes
    __table_args__ = (
        Index('idx_slug', slug),
        Index('idx_created_at', created_at),
        Index('idx_category_id', category_id),
    )
