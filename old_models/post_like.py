#!/usr/bin/python3
"""
This module defines the `PostLike` class, representing a like on a post.

Attributes:
    id (int): Primary key of the like.
    post_id (int): Foreign key referencing the associated post.
    user_id (int): Foreign key referencing the liking user.
    created_at (datetime): Timestamp of like creation.
"""

from sqlalchemy import Column, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from models import Base

class PostLike(Base):
    __tablename__ = 'post_likes'

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    post = relationship('Post', back_populates='likes')

    # Indexes
    __table_args__ = (
        Index('idx_post_id', post_id),
        Index('idx_user_id', user_id),
    )
