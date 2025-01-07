#!/usr/bin/python3
"""
This module defines the PostRevision class for version control.

The PostRevision class maintains a history of changes made to blog posts,
enabling version tracking and content recovery.

Classes:
    PostRevision: Represents a historical version of a blog post
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from models import Base

class PostRevision(Base):
    """
    PostRevision model class for tracking post history.

    This class maintains historical versions of blog posts,
    tracking changes to content and metadata over time.

    Attributes:
        id (Column): Primary key of the revision
        post_id (Column): Foreign key to the associated post
        title (Column): Title at time of revision
        content (Column): Content at time of revision
        created_at (Column): Timestamp of revision creation
        created_by (Column): Foreign key to revision author
    """
    __tablename__ = 'post_revisions'

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Relationships
    post = relationship('Post', back_populates='revisions')
    author = relationship('User')

    # Indexes
    __table_args__ = (
        Index('idx_post_revision', 'post_id', 'created_at'),
    )
