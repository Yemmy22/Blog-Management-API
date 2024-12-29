#!/usr/bin/python3
"""
This module defines the association table for Post and Tag relationships.

This table manages the many-to-many relationship between posts and tags,
allowing posts to have multiple tags and tags to be applied to multiple posts.
"""

from sqlalchemy import Table, Column, Integer, DateTime, ForeignKey, Index
from datetime import datetime
from models import Base

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
