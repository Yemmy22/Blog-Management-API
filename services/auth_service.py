# services/auth_service.py

from werkzeug.security import generate_password_hash, check_password_hash
from utils.db import get_db_session
from models import User, Role
from exceptions.api_errors import AuthenticationError, ValidationError
from schemas.validators import UserSchema, LoginSchema
from services.token_service import TokenService
import re

class AuthService:
    """Service class for authentication-related operations."""
    
    PASSWORD_PATTERN = re.compile(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$')
    
    @staticmethod
    def validate_password_strength(password: str) -> bool:
        """
        Validate password strength.
        
        Args:
            password: The password to validate
            
        Returns:
            bool: True if password meets requirements
            
        Raises:
            ValidationError: If password is too weak
        """
        if not AuthService.PASSWORD_PATTERN.match(password):
            raise ValidationError(
                "Password must be at least 8 characters long and contain both letters and numbers"
            )
        return True

    @staticmethod
    def register(data: dict) -> dict:
        """
        Register a new user.
        
        Args:
            data: User registration data
            
        Returns:
            dict: Created user data
            
        Raises:
            ValidationError: If validation fails
            DatabaseError: If database operation fails
        """
        # Validate input
        schema = UserSchema()
        validated_data = schema.load(data)
        
        # Validate password strength
        AuthService.validate_password_strength(validated_data['password'])
        
        with get_db_session() as session:
            # Check existing user
            if session.query(User).filter(
                (User.email == validated_data['email']) |
                (User.username == validated_data['username'])
            ).first():
                raise ValidationError("Email or username already exists")
            
            # Create user
            hashed_password = generate_password_hash(validated_data['password'])
            new_user = User(
                username=validated_data['username'],
                email=validated_data['email'],
                password=hashed_password,
                first_name=validated_data.get('first_name'),
                last_name=validated_data.get('last_name')
            )
            
            # Assign default role
            reader_role = session.query(Role).filter_by(name='reader').first()
            if reader_role:
                new_user.roles.append(reader_role)
            
            session.add(new_user)
            session.commit()
            
            return schema.dump(new_user)

    @staticmethod
    def login(data: dict) -> dict:
        """
        Authenticate a user and return a token.
        
        Args:
            data: Login credentials
            
        Returns:
            dict: Authentication token and user data
            
        Raises:
            AuthenticationError: If authentication fails
            DatabaseError: If database operation fails
        """
        # Validate input
        schema = LoginSchema()
        validated_data = schema.load(data)
        
        with get_db_session() as session:
            user = session.query(User).filter_by(email=validated_data['email']).first()
            
            if not user or not check_password_hash(user.password, validated_data['password']):
                raise AuthenticationError("Invalid email or password")
            
            if not user.is_active:
                raise AuthenticationError("Account is disabled")
            
            # Generate token
            token = TokenService.generate_session_token(user.id)
            
            return {
                "token": token,
                "user": UserSchema().dump(user)
            }
