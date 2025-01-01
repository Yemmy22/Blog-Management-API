#!/usr/bin/python3
"""
This module defines the Post class for blog content management.

The Post class represents blog posts with support including tags and engagement metrics,
SEO optimization, content analysis, and version tracking.

Classes:
    PostStatus: Enum defining possible post statuses
    Post: Represents a blog post
"""


from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship, validates
from datetime import datetime
from models import Base
from models.validators import validate_slug
import enum

class PostStatus(enum.Enum):
    """
    Enum defining possible post statuses.
    
    Attributes:
        DRAFT: Initial working state
        AUTOSAVE: Automatically saved version
        PUBLISHED: Publicly visible state
        ARCHIVED: Removed from public view
    """
    DRAFT = "draft"
    AUTOSAVE = "autosave"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class Post(Base):
    """
    This class defines the structure for blog posts, including content, metadata, and relationships with categories, tags, and comments,
    SEO, content analysis, and version tracking.
    
    Attributes:
        id (Column): Primary key of the post
        title (Column): Post title
        slug (Column): URL-friendly version of the title
        content (Column): Main content of the post
        status (Column): Current status (draft/published)
        view_count (Column): Number of post views
        like_count (Column): Number of post likes
        created_at (Column): Timestamp of post creation
        updated_at (Column): Timestamp of last update
        user_id (Column): Foreign key to the author
        category_id (Column): Foreign key to the category
        author (relationship): Many-to-one relationship with User model
        category (relationship): Many-to-one relationship with Category model
        tags (relationship): Many-to-many relationship with Tag model
        comments (relationship): One-to-many relationship with Comment model
        meta_description (Column): SEO meta description
        featured_image_url (Column): URL to post's featured image
        reading_time (Column): Estimated reading duration
        published_at (Column): Timestamp of publication
        revisions (relationship): One-to-many relationship with PostRevision
    """
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(250), unique=True, nullable=False)
    content = Column(Text, nullable=False)

    # SEO and presentation
    meta_description = Column(String(160))  # Optimal SEO meta description length
    featured_image_url = Column(String(255))
    reading_time = Column(Integer)  # in minutes

    # Status and metrics
    status = Column(Enum(PostStatus), default=PostStatus.DRAFT)
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime)

    # Foreign keys
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)

    # Relationships
    author = relationship('User', back_populates='posts')
    category = relationship('Category', back_populates='posts')
    tags = relationship('Tag', secondary='post_tags', back_populates='posts')
    comments = relationship('Comment', back_populates='post')
    revisions = relationship('PostRevision', back_populates='post', order_by='PostRevision.created_at')

    # Validators
    @validates('slug')
    def validate_slug(self, key, slug):
        return validate_slug(slug)

    # Indexes
    __table_args__ = (
        Index('idx_slug', 'slug'),
        Index('idx_status', 'status'),
        Index('idx_created_at', 'created_at'),
        Index('idx_published_at', 'published_at'),
        Index('idx_category_id', 'category_id'),
    )

# Event listeners for automatic calculations
@event.listens_for(Post.content, 'set')
def update_reading_time(target, value, oldvalue, initiator):
    """Update reading time when content changes."""
    target.reading_time = estimate_reading_time(value)

@event.listens_for(Post.status, 'set')
def update_published_at(target, value, oldvalue, initiator):
    """Update published_at timestamp when post is published."""
    if value == PostStatus.PUBLISHED and oldvalue != PostStatus.PUBLISHED:
        target.published_at = datetime.utcnow()
