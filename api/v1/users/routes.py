#!/usr/bin/python3
"""
User management routes for the Blog Management API.

This module defines routes for managing user profiles and other
user-related operations.
"""
from flask import Blueprint, request, jsonify
from models import User, Base
from sqlalchemy.orm import Session

users_bp = Blueprint('users', __name__)

@users_bp.route('/profile/<int:user_id>', methods=['GET'])
def get_profile(user_id):
    """Retrieve a user's profile."""
    session = Session(Base.metadata.bind)
    user = session.query(User).get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_active": user.is_active
    }), 200

@users_bp.route('/profile/<int:user_id>', methods=['PUT'])
def update_profile(user_id):
    """Update a user's profile."""
    session = Session(Base.metadata.bind)
    user = session.query(User).get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.json
    user.first_name = data.get('first_name', user.first_name)
    user.last_name = data.get('last_name', user.last_name)
    session.commit()

    return jsonify({"message": "Profile updated successfully"}), 200

@users_bp.route('/profile/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user's account."""
    session = Session(Base.metadata.bind)
    user = session.query(User).get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    session.delete(user)
    session.commit()
    return jsonify({"message": "User deleted successfully"}), 200
