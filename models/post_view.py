#!/usr/bin/python3
"""
This module defines the `PostView` class, representing a view on a post.

Attributes:
    id (int): Primary key of the view.
    post_id (int): Foreign key referencing the associated post.
    user_id (int): Foreign key referencing the viewing user (optional).
    viewed_at (datetime): Timestamp of the view.
"""

from sqlalchemy import Column, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from models import Base

class PostView(Base):
    __tablename__ = 'post_views'

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    viewed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    post = relationship('Post', back_populates='views')

    # Indexes
    __table_args__ = (
        Index('idx_post_id', post_id),
        Index('idx_user_id', user_id),
    )
