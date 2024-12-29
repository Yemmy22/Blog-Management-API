#!/usr/bin/python3
"""
This module defines the `Comment` class, representing comments with moderation and threading support.

Attributes:
    id (int): Primary key of the comment.
    post_id (int): Foreign key referencing the associated post.
    user_id (int): Foreign key referencing the authoring user.
    parent_id (int): Foreign key referencing the parent comment for threading.
    content (str): Content of the comment.
    is_approved (bool): Indicates if the comment is approved.
    created_at (datetime): Timestamp of comment creation.
    deleted_at (datetime): Timestamp of soft deletion.
"""


from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from models import Base

class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    parent_id = Column(Integer, ForeignKey('comments.id'))
    content = Column(Text, nullable=False)
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    deleted_at = Column(DateTime)

    # Relationships using string references
    post = relationship('Post', back_populates='comments')
    user = relationship('User', back_populates='comments')
    parent = relationship('Comment', remote_side=[id], backref='replies')

    # Indexes
    __table_args__ = (
        Index('idx_post_id', post_id),
        Index('idx_created_at', created_at),
    )
