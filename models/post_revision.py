#!/usr/bin/python3
"""
This module defines the `PostRevision` class, representing a revision of a post.

Attributes:
    id (int): Primary key of the revision.
    post_id (int): Foreign key referencing the associated post.
    content (str): Content of the revision.
    created_at (datetime): Timestamp of revision creation.
"""

from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from models import Base

class PostRevision(Base):
    __tablename__ = 'post_revisions'

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    post = relationship('Post', back_populates='revisions')

    # Indexes
    __table_args__ = (
        Index('idx_post_id', post_id),
        Index('idx_created_at', created_at),
    )

