#!/usr/bin/python3
"""
This module defines the `Tag` class for categorizing blog posts.

Attributes:
    id (int): Primary key of the tag.
    name (str): Name of the tag.
    slug (str): URL-friendly version of the tag name.
    created_at (datetime): Timestamp of tag creation.
    updated_at (datetime): Timestamp of last update.
"""

from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from models import Base
from models.post_tags import post_tags

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
