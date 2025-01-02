#!/usr/bin/python3
"""
Response utility functions for API endpoints.

This module provides standardized response formatting functions
for successful operations and error handling.

Functions:
    success_response: Format successful response
    error_response: Format error response
"""
from typing import Optional, Any, Dict
from flask import jsonify


def success_response(
    message: str,
    data: Optional[Any] = None,
    status_code: int = 200
) -> tuple:
    """
    Format a successful API response.

    Args:
        message: Success message
        data: Response data (optional)
        status_code: HTTP status code

    Returns:
        Tuple of (response, status_code)
    """
    response = {
        "status": "success",
        "message": message
    }
    if data is not None:
        response["data"] = data

    return jsonify(response), status_code


def error_response(
    message: str,
    status_code: int = 400,
    errors: Optional[Dict] = None
) -> tuple:
    """
    Format an error API response.

    Args:
        message: Error message
        status_code: HTTP status code
        errors: Dictionary of field-specific errors

    Returns:
        Tuple of (response, status_code)
    """
    response = {
        "status": "error",
        "message": message
    }
    if errors is not None:
        response["errors"] = errors

    return jsonify(response), status_code
