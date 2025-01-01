#!/usr/bin/python3
"""
This module defines the Tag class and post_tags association table.

The Tag class represents labels or keywords that can be applied to posts.
The post_tags table manages the many-to-many relationship between posts and tags.

Classes:
    Tag: Represents a post tag

Tables:
    post_tags: Association table for Post-Tag many-to-many relationship
"""
from sqlalchemy import Column, Integer, String, DateTime, Table, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from models import Base

post_tags = Table(
    'post_tags',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('posts.id', ondelete='CASCADE'), 
           primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), 
           primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow)
)

class Tag(Base):
    """
    Tag model class representing post tags.
    
    This class defines the structure for post tags, enabling
    content organization and search functionality.
    
    Attributes:
        id (Column): Primary key of the tag
        name (Column): Unique name of the tag
        slug (Column): URL-friendly version of the tag name
        created_at (Column): Timestamp of tag creation
        posts (relationship): Many-to-many relationship with Post model
    """
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    slug = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    posts = relationship('Post', secondary=post_tags, back_populates='tags')

    # Indexes
    __table_args__ = (
        Index('idx_tag_name', name),
        Index('idx_tag_slug', slug),
    )
