#!/usr/bin/python3
"""
This module defines the `Tag` class and post_tags association table for blog post categorization.

Tables:
    tags: Stores tag information
    post_tags: Association table linking posts and tags

Attributes for Tag:
    id (int): Primary key of the tag.
    name (str): Name of the tag.
    slug (str): URL-friendly version of the tag name.
    created_at (datetime): Timestamp of tag creation.
    updated_at (datetime): Timestamp of last update.
"""

from sqlalchemy import Column, Integer, String, DateTime, Table, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from models import Base

# Association Table for Posts and Tags
post_tags = Table(
    'post_tags',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('posts.id', ondelete='CASCADE'), 
           primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), 
           primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow),
    Index('idx_post_tag', 'post_id', 'tag_id')
)

class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    slug = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    posts = relationship('Post', secondary=post_tags, back_populates='tags')

    # Indexes
    __table_args__ = (
        Index('idx_tag_name', name),
        Index('idx_tag_slug', slug),
    )
