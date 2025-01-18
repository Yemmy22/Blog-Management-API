#!/usr/bin/python3
"""
Categories management API endpoints.

This module provides API endpoints for blog category management,
including creation, retrieval, updating, and deletion of categories.
"""
from flask import Blueprint, request, jsonify
from models.category import Category
from api.v1.auth import require_auth, get_db

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/', methods=['POST'])
@require_auth
def create_category():
    """
    Create new category endpoint.
    
    Request body:
        name: Category name
        
    Returns:
        Created category object
    """
    data = request.get_json()
    
    if 'name' not in data:
        return jsonify({'error': 'Name is required'}), 400
        
    db = next(get_db())
    
    # Check if category already exists
    existing = db.query(Category).filter_by(name=data['name']).first()
    if existing:
        return jsonify({'error': 'Category already exists'}), 400
        
    try:
        category = Category(name=data['name'])
        db.add(category)
        db.commit()
        
        return jsonify({
            'id': category.id,
            'name': category.name
        }), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': 'Failed to create category'}), 500

@categories_bp.route('/', methods=['GET'])
def list_categories():
    """
    List all categories endpoint.
    
    Returns:
        List of categories
    """
    db = next(get_db())
    categories = db.query(Category).all()
    
    return jsonify({
        'categories': [{
            'id': category.id,
            'name': category.name
        } for category in categories]
    })
