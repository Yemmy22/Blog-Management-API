# exceptions/api_errors.py

class APIError(Exception):
    """Base exception class for API errors."""
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status'] = 'error'
        return rv

class ValidationError(APIError):
    """Raised when input validation fails."""
    def __init__(self, message):
        super().__init__(message, 422)

class AuthenticationError(APIError):
    """Raised when authentication fails."""
    def __init__(self, message):
        super().__init__(message, 401)

class AuthorizationError(APIError):
    """Raised when user doesn't have required permissions."""
    def __init__(self, message):
        super().__init__(message, 403)

class ResourceNotFoundError(APIError):
    """Raised when requested resource is not found."""
    def __init__(self, message):
        super().__init__(message, 404)

class DatabaseError(APIError):
    """Raised when database operations fail."""
    def __init__(self, message):
        super().__init__(message, 500)
