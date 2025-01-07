#!/usr/bin/python3
"""
This module defines the Category class for blog post categorization.

The Category class represents high-level groupings for blog posts,
allowing for organized content management and filtering.

Classes:
    Category: Represents a blog post category
"""
from sqlalchemy import Column, Integer, String, Index
from sqlalchemy.orm import relationship
from models import Base

class Category(Base):
    """
    Category model class representing post categories.

    This class defines the structure for blog post categories,
    enabling content organization and filtering.

    Attributes:
        id (Column): Primary key of the category
        name (Column): Unique name of the category
        posts (relationship): One-to-many relationship with Post model
    """
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    # Relationships
    posts = relationship('Post', back_populates='category')

    # Indexes
    __table_args__ = (
        Index('idx_name', name),
    )
