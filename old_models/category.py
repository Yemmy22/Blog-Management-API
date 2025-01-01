#!/usr/bin/python3
"""
This module defines the `Category` class, representing a category of blog posts.
Attributes:
    id (int): Primary key of the category.
    name (str): Name of the category.
    posts (relationship): One-to-many relationship with `Post`.
"""
from sqlalchemy import Column, Integer, String, Index
from sqlalchemy.orm import relationship
from models import Base

class Category(Base):
    """
    Represents a category for blog posts.
    
    Attributes:
        id (int): Unique identifier for the category.
        name (str): Name of the category.
        posts (relationship): Relationship to the `Post` model.
    """
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    posts = relationship('Post', back_populates='category', lazy=True)  # Modified this line
    
    # Indexes
    __table_args__ = (
        Index('idx_name', name),
    )
