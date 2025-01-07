#!/usr/bin/python3
"""
User service for managing user-related operations.

This module provides the business logic for user management tasks
such as retrieving, updating, and deleting user profiles.

Classes:
    UserService: Handles user management operations.
"""
from models import User, Base
from sqlalchemy.orm import Session

class UserService:
    """
    Service class for user-related operations.

    Methods:
        get_user: Retrieve a user by ID.
        update_user: Update a user's profile.
        delete_user: Delete a user account.
    """

    @staticmethod
    def get_user(user_id):
        """
        Retrieve a user by ID.

        Args:
            user_id (int): The ID of the user to retrieve.

        Returns:
            User: The retrieved user object.

        Raises:
            ValueError: If the user does not exist.
        """
        session = Session(Base.metadata.bind)
        user = session.query(User).get(user_id)
        if not user:
            raise ValueError("User not found.")
        return user

    @staticmethod
    def update_user(user_id, data):
        """
        Update a user's profile.

        Args:
            user_id (int): The ID of the user to update.
            data (dict): The updated user data.

        Returns:
            User: The updated user object.

        Raises:
            ValueError: If the user does not exist.
        """
        session = Session(Base.metadata.bind)
        user = session.query(User).get(user_id)
        if not user:
            raise ValueError("User not found.")

        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        session.commit()
        return user

    @staticmethod
    def delete_user(user_id):
        """
        Delete a user account.

        Args:
            user_id (int): The ID of the user to delete.

        Raises:
            ValueError: If the user does not exist.
        """
        session = Session(Base.metadata.bind)
        user = session.query(User).get(user_id)
        if not user:
            raise ValueError("User not found.")

        session.delete(user)
        session.commit()
