#!/usr/bin/python3
"""
This module defines the `Post` class with content management and analytics features.

Attributes:
    id (int): Primary key of the post.
    title (str): Title of the post.
    slug (str): SEO-friendly URL slug for the post.
    content (str): Main content of the post.
    view_count (int): Number of times the post has been viewed.
    like_count (int): Number of likes the post has received.
    status (str): Status of the post (draft, published, archived).
    created_at (datetime): Timestamp of post creation.
    updated_at (datetime): Timestamp of last update.
    published_at (datetime): Timestamp of publication.
    deleted_at (datetime): Timestamp of soft deletion.
    scheduled_at (datetime): Timestamp for scheduling the post.
    meta_title (str): SEO meta title for the post.
    meta_description (str): SEO meta description for the post.
    user_id (int): Foreign key referencing the authoring user.
    tags (relationship): Many-to-many relationship with `Tag`.
    comments (relationship): One-to-many relationship with `Comment`.
    likes (relationship): One-to-many relationship with `PostLike`.
    views (relationship): One-to-many relationship with `PostView`.
    revisions (relationship): One-to-many relationship with `PostRevision`.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from models import Base
import enum

class PostStatus(enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(250), unique=True, nullable=False)
    content = Column(Text, nullable=False)
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    status = Column(Enum(PostStatus), default=PostStatus.DRAFT)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime)
    deleted_at = Column(DateTime)
    scheduled_at = Column(DateTime)
    meta_title = Column(String(150))
    meta_description = Column(String(255))
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Relationships
    author = relationship('User', back_populates='posts')
    tags = relationship('Tag', secondary='post_tags', back_populates='posts')
    comments = relationship('Comment', back_populates='post')
    likes = relationship('PostLike', back_populates='post')
    views = relationship('PostView', back_populates='post')
    revisions = relationship('PostRevision', back_populates='post')

    # Indexes
    __table_args__ = (
        Index('idx_slug', slug),
        Index('idx_created_at', created_at),
    )
