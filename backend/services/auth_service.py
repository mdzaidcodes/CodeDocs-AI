"""
Authentication service for user registration and login.
Handles JWT token generation and validation.
"""

import jwt
from datetime import datetime, timedelta
from config.settings import Config
from models.user import User


class AuthService:
    """Service for handling authentication operations."""
    
    @staticmethod
    def register(first_name, last_name, email, password):
        """
        Register a new user.
        
        Args:
            first_name: User's first name
            last_name: User's last name
            email: Email address
            password: Plain text password
            
        Returns:
            dict: {token: JWT token, user: user object}
            
        Raises:
            ValueError: If validation fails or email exists
        """
        # Combine first and last name into full_name
        full_name = f"{first_name} {last_name}".strip()
        
        # Create user (User model handles validation and hashing)
        user = User.create(full_name, email, password)
        
        # Generate JWT token
        token = AuthService.generate_token(user['id'])
        
        return {
            'token': token,
            'user': user
        }
    
    @staticmethod
    def login(email, password):
        """
        Authenticate user and return JWT token.
        
        Args:
            email: Email address
            password: Plain text password
            
        Returns:
            dict: {token: JWT token, user: user object}
            
        Raises:
            ValueError: If authentication fails
        """
        # Authenticate user
        user = User.authenticate(email, password)
        
        if not user:
            raise ValueError("Invalid email or password")
        
        # Generate JWT token
        token = AuthService.generate_token(user['id'])
        
        return {
            'token': token,
            'user': user
        }
    
    @staticmethod
    def generate_token(user_id):
        """
        Generate JWT token for user.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            str: JWT token
        """
        expiration = datetime.utcnow() + timedelta(hours=Config.JWT_EXPIRATION_HOURS)
        
        payload = {
            'user_id': str(user_id),
            'exp': expiration,
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(
            payload,
            Config.JWT_SECRET_KEY,
            algorithm=Config.JWT_ALGORITHM
        )
        
        return token
    
    @staticmethod
    def verify_token(token):
        """
        Verify and decode JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            dict: Decoded payload with user_id
            
        Raises:
            jwt.InvalidTokenError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token,
                Config.JWT_SECRET_KEY,
                algorithms=[Config.JWT_ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
    
    @staticmethod
    def get_user_from_token(token):
        """
        Extract user object from JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            dict: User object or None
        """
        try:
            payload = AuthService.verify_token(token)
            user_id = payload.get('user_id')
            
            if user_id:
                return User.find_by_id(user_id)
            
            return None
        except Exception:
            return None

