"""
User model for authentication and user management.
"""

from config.database import get_db_cursor
from utils.validators import validate_email
import bcrypt


class User:
    """User model with authentication methods."""
    
    @staticmethod
    def create(name, email, password):
        """
        Create a new user with hashed password.
        
        Args:
            name: User's full name
            email: User's email address
            password: Plain text password (will be hashed)
            
        Returns:
            dict: User object (without password)
            
        Raises:
            ValueError: If email is invalid or already exists
        """
        # Validate email
        if not validate_email(email):
            raise ValueError("Invalid email address")
        
        # Check if email already exists
        if User.find_by_email(email):
            raise ValueError("Email already exists")
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Insert user
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO users (full_name, email, password_hash)
                VALUES (%s, %s, %s)
                RETURNING id, full_name, email, created_at
            """, (name, email, password_hash))
            
            user = cursor.fetchone()
            return dict(user)
    
    @staticmethod
    def find_by_id(user_id):
        """
        Find user by ID.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            dict: User object (without password) or None
        """
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT id, full_name, email, created_at
                FROM users
                WHERE id = %s
            """, (user_id,))
            
            user = cursor.fetchone()
            return dict(user) if user else None
    
    @staticmethod
    def find_by_email(email):
        """
        Find user by email (includes password hash for authentication).
        
        Args:
            email: User's email address
            
        Returns:
            dict: User object (with password_hash) or None
        """
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT id, full_name, email, password_hash, created_at
                FROM users
                WHERE email = %s
            """, (email,))
            
            user = cursor.fetchone()
            return dict(user) if user else None
    
    @staticmethod
    def verify_password(stored_password_hash, provided_password):
        """
        Verify a password against its hash.
        
        Args:
            stored_password_hash: Hashed password from database
            provided_password: Plain text password to verify
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return bcrypt.checkpw(
            provided_password.encode('utf-8'),
            stored_password_hash.encode('utf-8')
        )
    
    @staticmethod
    def authenticate(email, password):
        """
        Authenticate user with email and password.
        
        Args:
            email: User's email address
            password: Plain text password
            
        Returns:
            dict: User object (without password) if authenticated, None otherwise
        """
        user = User.find_by_email(email)
        
        if not user:
            return None
        
        if not User.verify_password(user['password_hash'], password):
            return None
        
        # Update last_login timestamp
        User.update_last_login(user['id'])
        
        # Remove password_hash from returned object
        user.pop('password_hash', None)
        return user
    
    @staticmethod
    def update_last_login(user_id):
        """
        Update the last_login timestamp for a user.
        
        Args:
            user_id: UUID of the user
        """
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                UPDATE users 
                SET last_login = NOW(), updated_at = NOW()
                WHERE id = %s
            """, (user_id,))

