"""
Validation utilities for input data.
"""

import re
import os
from config.settings import Config


def validate_email(email):
    """
    Validate email address format.
    
    Args:
        email: Email address string
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password):
    """
    Validate password strength.
    
    Args:
        password: Password string
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    return True, None


def validate_file_extension(filename):
    """
    Check if file extension is allowed.
    
    Args:
        filename: Name of the file
        
    Returns:
        bool: True if extension is allowed
    """
    if not filename:
        return False
    
    ext = os.path.splitext(filename)[1].lower()
    return ext in Config.ALLOWED_EXTENSIONS


def validate_file_size(file_size):
    """
    Check if file size is within limit.
    
    Args:
        file_size: Size in bytes
        
    Returns:
        bool: True if size is acceptable
    """
    return file_size <= Config.MAX_FILE_SIZE


def validate_github_url(url):
    """
    Validate GitHub repository URL.
    
    Args:
        url: GitHub repository URL
        
    Returns:
        bool: True if valid GitHub URL
    """
    if not url:
        return False
    
    # Match github.com URLs
    pattern = r'^https?://github\.com/[\w-]+/[\w.-]+/?$'
    return bool(re.match(pattern, url.rstrip('/')))


def validate_project_name(name):
    """
    Validate project name.
    
    Args:
        name: Project name
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not name or not name.strip():
        return False, "Project name is required"
    
    if len(name) < 2:
        return False, "Project name must be at least 2 characters"
    
    if len(name) > 255:
        return False, "Project name must be less than 255 characters"
    
    return True, None

